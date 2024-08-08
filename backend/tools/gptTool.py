"""
GPT工具类
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

ChatURLs_Norm = {
    'gpt-35-turbo': "api/azure/openai/chatCompletion?deploymentId=gpt-35-turbo",
    'gpt-4o': "api/azure/openai/chatCompletion?deploymentId=gpt-4o",
    'claude-3-5-sonnet@20240620': "api/azure/openai/chatCompletion?deploymentId=claude-3-5-sonnet@20240620",
}

ChatURLs_Paint = {
    'dall-e2': "api/azure/openai/generationImage",
    'dall-e3': "api/azure/openai/generateDell3Image?deploymentId=Dalle3",
}

ChatURLs = {**ChatURLs_Norm, **ChatURLs_Paint}


def IntranetGPTRequest(
    PFGateway: str = ...,
    GPTGateway: str = ...,
    APP_ID: Optional[str] = None,
    APP_Secret: str = ...,
    model: str = ...,
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
    # 请求GPT接口
    url = f"{GPTGateway}/{ChatURLs[model]}"
    Headers = {
        'Content-Type': 'application/json',
        'Authorization': oauth_token
    }
    if model in ChatURLs_Norm:
        Payload = {
            'messages': messages,
            **options
        } if options is not None else {
            'messages': messages
        }
    if model in ChatURLs_Paint:
        Payload = {
            'prompt': f"{messages[0]['content']}\n{messages[1]['content']}",
            **options
        } if options is not None else {
            'prompt': f"{messages[0]['content']}\n{messages[1]['content']}"
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
                    if model in ChatURLs_Norm:
                        result = parsed_content['data']['choices'][0]['message']['content']
                    if model in ChatURLs_Paint:
                        result = parsed_content['data']['data'][0]['url']
                    return result, response.status_code
                except json.JSONDecodeError:
                    continue
    else:
        return "Request failed", response.status_code


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
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime)
        result, statuscode = IntranetGPTRequest(
            PFGateway = PFGateway,
            GPTGateway = GPTGateway,
            APP_ID = APP_ID,
            APP_Secret = APP_Secret,
            model = model,
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
        'CodeInput': [messages[1]['content']],
        'Answer': [Answers[0]],
        'TestTimes ': TotalTestTimes,
        'SimilarityMatrix': [similarity_matrix]
    }
    TestResultDF = pandas.DataFrame(TestResult)
    '''
    csvPath = './TestResult.csv'
    if Path(csvPath).exists():
        TestResultsDF = pandas.read_csv(csvPath, encoding = 'utf-8')
        TestResultsDF.drop_duplicates()
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[1]['content']]
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
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != messages[1]['content']]
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


class GPTClient(object):
    '''
    '''
    def __init__(self, ConfigPath, PromptDir):
        cf = configparser.ConfigParser()
        cf.read(ConfigPath, encoding = 'utf-8')
        self.GPTGateway = cf.get("GetToken", "GPTGateway")
        self.PFGateway = cf.get("GetToken", "PFGateway")
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

    def run(self,
        model: str,
        messages: Union[str, list],
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
        return IntranetGPTRequest(
            PFGateway = self.PFGateway,
            GPTGateway = self.GPTGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            model = model,
            messages = messages,
            options = options
        )

    def test(self,
        model: str,
        messages: Union[str, list],
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
        return GPTPromptTest(
            PFGateway = self.PFGateway,
            GPTGateway = self.GPTGateway,
            APP_ID = self.access_key_id,
            APP_Secret = self.access_key_secret,
            model = model,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes
        )

##############################################################################################################################