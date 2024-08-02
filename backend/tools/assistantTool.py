"""
Assistant工具类
"""

import configparser
import requests
import json
import pandas
import jaydebeapi
import requests.adapters
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from typing import Optional, Union
from sqlalchemy import engine

##############################################################################################################################

def IntranetAssistantRequest(
    PFGateway: str = ...,
    APP_ID: Optional[str] = None,
    APP_Secret: str = ...,
    ChatURL: str = ...,
    XHeaderTenant: str = ...,
    assistantCode: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True
):
    # 初始化会话
    session = requests.session()
    session.keep_alive = False
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries = 3))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries = 3))
    # 获取令牌
    url = f"{PFGateway}/service-pf-open-gateway/oauth/token?grant_type=client_credentials&client_id={APP_ID}&client_secret={APP_Secret}"
    response = requests.get(
        url = url
    )
    if response.status_code == 200:
        res_token = response.json()
        accessToken = res_token.get("data", {}).get("access_token", "")
        oauth_token = f"Bearer {accessToken}"
    else:
        return "Request failed", response.status_code
    # 请求智库接口
    url = f"{PFGateway}/{ChatURL}/{assistantCode}"
    Headers = {
        'Content-Type': 'application/json',
        'x-header-tenant': XHeaderTenant,
        'Authorization': oauth_token
    }
    Payload = {
        'messages': messages,
        'options': options
    } if options is not None else {
        'messages': messages
    }
    response = requests.post(
        url = url,
        headers = Headers,
        data = json.dumps(Payload),
        stream = stream
    )
    print(f"请求智库返回响应结果:\n{json.loads(response.text)}")
    if response.status_code == 200:
        content = ""
        for chunk in response.iter_content(chunk_size = 1024, decode_unicode = True):
            #chunk = ast.literal_eval(chunk)
            if chunk:
                content += chunk#.decode('utf-8')
                try:
                    parsed_content = json.loads(content)
                    try:
                        result = parsed_content['data']['data']['choices'][0]['message']['content']
                    except:
                        result = parsed_content['data']['dataContent']
                    return result, response.status_code
                except json.JSONDecodeError:
                    continue
    else:
        return "Request failed", response.status_code


def AssistantPromptTest(
    PFGateway: str = ...,
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
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime)
        result, statuscode = IntranetAssistantRequest(
            PFGateway = PFGateway,
            APP_ID = APP_ID,
            APP_Secret = APP_Secret,
            ChatURL = ChatURL,
            XHeaderTenant = XHeaderTenant,
            assistantCode = assistantCode,
            messages = messages,
            options = options,
            stream = stream
        )
        Answers.append(result)
        CurrentTestTime += 1
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(Answers) # Transfer data into TF-IDF vector
    similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
    print(f'The similarity matrix is:\n{similarity_matrix}')

    # Save the test result
    TestResult = {
        'CodeInput': [messages[0]['content']],
        'Answer': [Answers[0]],
        'TestTimes': TotalTestTimes,
        'SimilarityMatrix': [similarity_matrix]
    }
    TestResultDF = pandas.DataFrame(TestResult)
    '''
    csvPath = './TestResult.csv'
    if Path(csvPath).exists():
        TestResultsDF = pandas.read_csv(csvPath, encoding = 'utf-8')
        TestResultsDF.drop_duplicates()
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[0]['content']]
        TestResultsDF = pandas.concat([TestResultsDF, TestResultDF])
        TestResultsDF.reset_index(inplace = True)
    else:
        TestResultsDF = TestResultDF
    TestResultsDF.to_csv(csvPath, index = False, encoding = 'utf-8')
    with open(csvPath, 'r', encoding = 'utf-8') as f:
        result, statuscode = f.read(), 200
    '''
    jsonPath = './TestResult.json'
    if Path(jsonPath).exists():
        TestResultsDF = pandas.read_json(jsonPath, encoding = 'utf-8')
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[0]['content']]
        TestResultsDF = pandas.concat([TestResultsDF, TestResultDF])
        TestResultsDF.reset_index(inplace = True, drop = True)
    else:
        TestResultsDF = TestResultDF
    TestResultsDF.to_json(jsonPath)
    with open(jsonPath, 'r', encoding = 'utf-8') as f:
        result, statuscode = json.load(f), 200

    if sqlConnection is not None:
        TestResultsDF.to_sql(
            name = "Prompt Test Result",
            con = sqlConnection,
            if_exists = 'replace'
        )
        sqlConnection.close()
        result += "\n测试结果已上传到数据库"

    return result, statuscode


class AssistantClient(object):
    '''
    '''
    def __init__(self, config_file):
        cf = configparser.ConfigParser()
        cf.read(config_file, encoding = 'utf-8')
        self.PFGateway = cf.get("GetToken", "PFGateway")
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

    def run(self,
        messages: Union[str, list],
        options: Optional[dict] = None
    ):
        messages = [
            {
                'role': "user",
                'content': str(messages),
            }
        ] if not (isinstance(messages, list) and isinstance(messages[0], dict)) else messages
        return IntranetAssistantRequest(
            PFGateway = self.PFGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            ChatURL = self.ChatURL,
            XHeaderTenant = self.XHeaderTenant,
            assistantCode = self.AssistantCode,
            messages = messages,
            options = options
        )

    def test(self,
        messages: Union[str, list],
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
        return AssistantPromptTest(
            PFGateway = self.PFGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            ChatURL = self.ChatURL,
            XHeaderTenant = self.XHeaderTenant,
            assistantCode = self.AssistantCode,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes
        )

##############################################################################################################################