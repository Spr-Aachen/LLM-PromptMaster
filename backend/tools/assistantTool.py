"""
Assistant工具类
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

from utils.request import IntranetGPTRequest, IntranetAssistantRequest

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
        'CodeInput': [messages[0]['content']],
        'Answer': [Answers[0]],
        'TestTimes': TotalTestTimes,
        'Similarity': [average_similarity]
    }
    TestResultDF = pandas.DataFrame(TestResult)
    jsonPath = './TestResult.json'
    if Path(jsonPath).exists():
        TestResultsDF = pandas.read_json(jsonPath, encoding = 'utf-8')
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[0]['content']]
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


def AssistantPromptTest(
    PFGateway: str = ...,
    GPTGateway: str = ...,
    APP_ID: Optional[str] = None,
    APP_Secret: str = ...,
    ChatURL: str = ...,
    XHeaderTenant: str = ...,
    assistantCode: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True,
    TotalTestTimes: Optional[int] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection, jaydebeapi.Connection]] = None
):
    global average_similarity

    # Test the assistant
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime)
        for result, statuscode in IntranetAssistantRequest(
            PFGateway = PFGateway,
            APP_ID = APP_ID,
            APP_Secret = APP_Secret,
            ChatURL = ChatURL,
            XHeaderTenant = XHeaderTenant,
            assistantCode = assistantCode,
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
                    列表中包含了针对同一问题的多个返回值，请分析它们的总体稳定性（若最后一个返回值不完整则直接将其忽略），要求在进行详细分析前先计算总体的相似度百分比：
                    {Answers}
                """
            }
        ],
        stream = stream
    ):
        if statuscode != 200:
            yield f"本次测试返回值的稳定性分析失败，将使用本次测试返回值的相似度计算结果作为替代\n\n", 200
            recordingThread.join()
            Stability = average_similarity
            result = f"本次测试返回值的稳定性维持在：{Stability}\n\n建议对prompt进行调优\n\n"
        yield result, 200


class AssistantClient(object):
    '''
    '''
    def __init__(self, config_file):
        cf = configparser.ConfigParser()
        cf.read(config_file, encoding = 'utf-8')
        self.PFGateway = cf.get("GetToken", "PFGateway")
        self.GPTGateway = cf.get("GetToken", "GPTGateway")
        self.access_key_id = cf.get("GetToken", "APPID")
        self.access_key_secret = cf.get("GetToken", "APPSecret")
        self.ChatURL = cf.get("Chat-Assistant", "ChatURL")
        self.AssistantCode = cf.get("Chat-Assistant", "AssistantCode")
        self.XHeaderTenant = cf.get("Chat-Assistant", "XHeaderTenant")
        '''
        self.jarPath = cf.get("Test-SQL", "jarPath")
        self.DriverName = cf.get("Test-SQL", "DriverName")
        self.UserName = cf.get("Test-SQL", "UserName")
        self.Password = cf.get("Test-SQL", "Password")
        self.sqlURL = cf.get("Test-SQL", "sqlURL")
        '''

    async def run(self,
        assistantCode: Optional[str] = None,
        messages: Union[str, list] = ...,
        options: Optional[dict] = None
    ):
        messages = [
            {
                'role': "user",
                'content': str(messages),
            }
        ] if not (isinstance(messages, list) and isinstance(messages[0], dict)) else messages
        for result, statuscode in IntranetAssistantRequest(
            PFGateway = self.PFGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            ChatURL = self.ChatURL,
            XHeaderTenant = self.XHeaderTenant,
            assistantCode = self.AssistantCode if assistantCode is None else assistantCode,
            messages = messages,
            options = options,
            stream = False # There seems to be some problem with the assistant
        ):
            yield json.dumps(
                {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

    async def test(self,
        assistantCode: Optional[str] = None,
        messages: Union[str, list] = ...,
        options: Optional[dict] = None,
        testTimes: Optional[int] = None
    ):
        messages = [
            {
                'role': "user",
                'content': str(messages),
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
        for result, statuscode in AssistantPromptTest(
            PFGateway = self.PFGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            ChatURL = self.ChatURL,
            XHeaderTenant = self.XHeaderTenant,
            assistantCode = self.AssistantCode if assistantCode is None else assistantCode,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes,
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################