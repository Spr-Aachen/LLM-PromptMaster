"""
GPT工具类
"""

import configparser
import json
import threading
import pandas
import jaydebeapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from typing import Optional, Union
from sqlalchemy import engine

from utils.request import IntranetGPTRequest

##############################################################################################################################

similarity_matrix = None

def ComputeSimilarity(
    Answers: list,
    messages: list = [{}],
    TotalTestTimes: Optional[int] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection, jaydebeapi.Connection]] = None
):
    global similarity_matrix

    # Compute the similarity matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(Answers) # Transfer data into TF-IDF vector
    similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
    print(f'The similarity matrix is:\n{similarity_matrix}')

    # Save the test result
    TestResult = {
        'CodeInput': [messages[1]['content']],
        'Answer': [Answers[0]],
        'TestTimes': TotalTestTimes,
        'SimilarityMatrix': [similarity_matrix]
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
    sqlConnection: Optional[Union[engine.Engine, engine.Connection, jaydebeapi.Connection]] = None
):
    global similarity_matrix

    # Test the GPT model
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        yield
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
    '''
    with open(jsonPath, 'r', encoding = 'utf-8') as f:
        result, statuscode = json.load(f), 200
    '''
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
                    请分析以下测试结果的相似性（若最后一个结果不完整则直接将其忽略），要求在进行详细分析前先计算总体的相似度百分比：
                    {Answers}
                """
            }
        ],
        stream = stream
    ):
        if statuscode != 200:
            result = f"测试结果分析失败，将为您展示相似性矩阵：\n\n{similarity_matrix}"
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
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################