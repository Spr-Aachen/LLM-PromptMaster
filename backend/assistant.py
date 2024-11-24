"""
Assistant工具类
"""

import configparser
import json
import threading
from sqlalchemy import engine
from pathlib import Path
from typing import Optional, Union

from utils.request_transsion import gptRequest, assistantRequest
from utils.calc import ComputeSimilarity, average_similarity

##############################################################################################################################

def AssistantPromptTest(
    pfGateway: str = ...,
    gptGateway: str = ...,
    appID: Optional[str] = None,
    appSecret: str = ...,
    chatURL: str = ...,
    xheaderTenant: str = ...,
    assistantCode: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True,
    TotalTestTimes: Optional[int] = None,
    PromptStabilityEvaluator: Optional[str] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection]] = None
):
    # Test the assistant
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime) #yield f'Current test time: {CurrentTestTime}\n\n', 200
        for result, statuscode in assistantRequest(
            pfGateway = pfGateway,
            appID = appID,
            appSecret = appSecret,
            chatURL = chatURL,
            xheaderTenant = xheaderTenant,
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
        args = (Answers, messages[0]['content'], TotalTestTimes, sqlConnection)
    )
    recordingThread.start()

    # Analyze the test result
    yield "本次测试结果正在分析与计算中，请稍后...\n\n", 200
    for result, statuscode in gptRequest(
        pfGateway = pfGateway,
        gptGateway = gptGateway,
        appID = appID,
        appSecret = appSecret,
        model = "gpt-4o",
        messages = [
            {
                'role': "system",
                'content': PromptStabilityEvaluator
            },
            {
                'role': "user",
                'content': '\n,\n'.join(Answers)
            }
        ],
        stream = stream
    ):
        try:
            assert statuscode == 200, '...'
            yield f"分析完毕：\n\n{result}\n\n", 200
            Stability = float(str(result).strip().strip('```'))
        except:
            yield f"本次测试返回值的稳定值提取失败，将使用本次测试返回值的相似度计算结果作为替代\n\n", 200
            recordingThread.join()
            Stability = average_similarity
            result = f"本次测试返回值的稳定性维持在：{Stability}"
        yield result, 200


class AssistantClient(object):
    """
    This class is used to interact with the assistant API
    """
    def __init__(self, sourceName, configPath, promptDir):
        cf = configparser.ConfigParser()
        cf.read(configPath, encoding = 'utf-8')
        self.pfGateway = cf.get("GetToken", "pfGateway")
        self.gptGateway = cf.get("GetToken", "gptGateway")
        self.access_key_id = cf.get("GetToken", "appID")
        self.access_key_secret = cf.get("GetToken", "appSecret")
        self.chatURL = cf.get("Chat-Assistant", "chatURL")
        self.assistantCode = cf.get("Chat-Assistant", "assistantCode")
        self.xheaderTenant = cf.get("Chat-Assistant", "xheaderTenant")
        self.PromptStabilityEvaluatorPath = Path(promptDir).joinpath(cf.get("Chat-GPT", "promptFile_stabilityEvaluator")).as_posix()
        with open(self.PromptStabilityEvaluatorPath, 'r', encoding = 'utf-8') as f:
            self.PromptStabilityEvaluator = f.read()
        '''
        self.userName = cf.get("Test-SQL", "userName")
        self.password = cf.get("Test-SQL", "password")
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
        for result, statuscode in assistantRequest(
            pfGateway = self.pfGateway,
            appID = self.access_key_id,
            appSecret = self.access_key_secret,
            chatURL = self.chatURL,
            xheaderTenant = self.xheaderTenant,
            assistantCode = self.assistantCode if assistantCode is None else assistantCode,
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
        sqlConnection = 
        '''
        for result, statuscode in AssistantPromptTest(
            pfGateway = self.pfGateway,
            appID = self.access_key_id,
            appSecret = self.access_key_secret,
            chatURL = self.chatURL,
            xheaderTenant = self.xheaderTenant,
            assistantCode = self.assistantCode if assistantCode is None else assistantCode,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes,
            PromptStabilityEvaluator = self.PromptStabilityEvaluator,
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################