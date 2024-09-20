"""
GPT工具类
"""

import configparser
import json
import threading
import pandas
import numpy
import jaydebeapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from typing import Optional, Union
from sqlalchemy import engine

from utils.request import IntranetGPTRequest

##############################################################################################################################

average_similarity = None

def ComputeSimilarity(
    Answers: list,
    messages: list = [{}],
    TotalTestTimes: Optional[int] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection, jaydebeapi.Connection]] = None
):
    global average_similarity

    # Compute the similarity matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(Answers) # Transfer data into TF-IDF vector
    similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
    # Compute the average similarity
    num_of_elements = similarity_matrix.shape[0] * similarity_matrix.shape[1] - similarity_matrix.shape[0]
    sum_of_similarity = numpy.sum(similarity_matrix) - numpy.sum(numpy.diagonal(similarity_matrix))
    average_similarity = sum_of_similarity / num_of_elements

    # Save the test result
    TestResult = {
        'CodeInput': [messages[1]['content']],
        'Answer': [Answers[0]],
        'TestTimes': TotalTestTimes,
        'Similarity': [average_similarity]
    }
    TestResultDF = pandas.DataFrame(TestResult)
    jsonPath = './TestResult.json'
    if Path(jsonPath).exists():
        TestResultsDF = pandas.read_json(jsonPath, encoding = 'utf-8')
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[1]['content']]
        TestResultsDF = pandas.concat([TestResultsDF, TestResultDF])
        TestResultsDF.reset_index(inplace = True, drop = True)
    else:
        TestResultsDF = TestResultDF
    TestResultsDF.to_json(jsonPath)

    # Upload the test result to the database
    if sqlConnection is not None:
        TestResultsDF.to_sql(
            name = "Prompt Test Result",
            con = sqlConnection,
            if_exists = 'replace'
        )
        sqlConnection.close()


def GPTPromptTest(
    PFGateway: str = ...,
    GPTGateway: str = ...,
    APP_ID: Optional[str] = None,
    APP_Secret: str = ...,
    model: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True,
    TotalTestTimes: Optional[int] = None,
    threashold: float = 0.9,
    PromptReconstructor: Optional[str] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection, jaydebeapi.Connection]] = None
):
    global average_similarity

    # Test the GPT model
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime)
        for result, statuscode in IntranetGPTRequest(
            PFGateway = PFGateway,
            GPTGateway = GPTGateway,
            APP_ID = APP_ID,
            APP_Secret = APP_Secret,
            model = model,
            messages = messages,
            options = options,
            stream = False
        ): # This iteration would be only executed for once since the stream option is set to false
            Answers.append(result)
        CurrentTestTime += 1

    # Compute the test results' similarity
    recordingThread = threading.Thread(
        target = ComputeSimilarity,
        args = (Answers, messages, TotalTestTimes, sqlConnection)
    )
    recordingThread.start()

    # Analyze the test result
    yield "本次测试结果正在分析与计算中，请稍后...\n\n", 200
    for result, statuscode in IntranetGPTRequest(
        PFGateway = PFGateway,
        GPTGateway = GPTGateway,
        APP_ID = APP_ID,
        APP_Secret = APP_Secret,
        model = "gpt-4o",
        messages = [
            {
                'role': "user",
                'content': f"""
                    下面的列表中包含了针对同一问题的多个返回值，请计算它们的总体稳定性（若最后一个返回值不完整则直接将其忽略），要求结果为浮点型：
                    {Answers}
                """
            }
        ],
        stream = False
    ): # This iteration would be only executed for once since the stream option is set to false
        try:
            Stability = float(result)
        except:
            yield f"本次测试返回值的稳定性分析失败，将使用本次测试返回值的相似度计算结果作为替代\n\n", 200
            recordingThread.join()
            Stability = average_similarity
        if Stability >= threashold:
            return f"本次测试返回值的稳定性维持在：{Stability}\n\nprompt无需调优\n\n", 200 # Stop iteration if the success rate is higher than threashold
        elif Stability >= 0:
            yield f"本次测试返回值的稳定性维持在：{Stability}\n\n建议对prompt进行调优\n\n", 200

    # Evaluate the prompt
    yield "开始prompt调优, please stand by...\n\n", 200
    for Message in messages:
        if Message['role'] == 'system':
            Prompt = Message['content']
    for result, statuscode in IntranetGPTRequest(
        PFGateway = PFGateway,
        GPTGateway = GPTGateway,
        APP_ID = APP_ID,
        APP_Secret = APP_Secret,
        model = "claude-3-5-sonnet@20240620",
        messages = [
            {
                'role': "system",
                'content': PromptReconstructor
            },
            {
                'role': "user",
                'content': "```\n%s\n```" % Prompt
            }
        ],
        stream = stream
    ):
        if statuscode != 200:
            result = f"prompt调优失败"
        yield result, 200


class GPTClient(object):
    '''
    '''
    def __init__(self, ConfigPath, PromptDir):
        cf = configparser.ConfigParser()
        cf.read(ConfigPath, encoding = 'utf-8')
        self.PFGateway = cf.get("GetToken", "PFGateway")
        self.GPTGateway = cf.get("GetToken", "GPTGateway")
        self.access_key_id = cf.get("GetToken", "APPID")
        self.access_key_secret = cf.get("GetToken", "APPSecret")
        self.PromptPath = Path(PromptDir).joinpath(cf.get("Chat-GPT", "PromptFile")).as_posix()
        with open(self.PromptPath, 'r', encoding = 'utf-8') as f:
            self.Prompt = f.read()
        self.PromptReconstructorPath = Path(PromptDir).joinpath(cf.get("Chat-GPT", "PromptFile_Reconstructor")).as_posix()
        with open(self.PromptReconstructorPath, 'r', encoding = 'utf-8') as f:
            self.PromptReconstructor = f.read()
        '''
        self.jarPath = cf.get("Test-SQL", "jarPath")
        self.DriverName = cf.get("Test-SQL", "DriverName")
        self.UserName = cf.get("Test-SQL", "UserName")
        self.Password = cf.get("Test-SQL", "Password")
        self.sqlURL = cf.get("Test-SQL", "sqlURL")
        '''

    async def run(self,
        model: str = ...,
        messages: Union[str, list] = ...,
        options: Optional[dict] = None
    ):
        messages = [
            {
                'role': "system",
                'content': self.Prompt
            },
            {
                'role': "user",
                'content': str(messages),
            }
        ] if not (isinstance(messages, list) and isinstance(messages[0], dict)) else messages
        for result, statuscode in IntranetGPTRequest(
            PFGateway = self.PFGateway,
            GPTGateway = self.GPTGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            model = model,
            messages = messages,
            options = options,
            stream = True
        ):
            yield json.dumps(
                {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

    async def test(self,
        model: str = ...,
        messages: Union[str, list] = ...,
        options: Optional[dict] = None,
        testTimes: Optional[int] = None
    ):
        messages = [
            {
                'role': "system",
                'content': self.Prompt
            },
            {
                'role': "user",
                'content': messages,
            }
        ] if not (isinstance(messages, list) and isinstance(messages[0], dict)) else messages
        '''
        sqlConnection = jaydebeapi.connect(
            jclassname = self.DriverName,
            url = self.sqlURL,
            driver_args = [self.UserName, self.Password],
            jars = self.jarPath
        )
        '''
        for result, statuscode in GPTPromptTest(
            PFGateway = self.PFGateway,
            GPTGateway = self.GPTGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            model = model,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes,
            PromptReconstructor = self.PromptReconstructor,
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################