"""
Assistant工具类
"""

import json
import threading
from PyEasyUtils import configManager
from sqlalchemy import engine
from pathlib import Path
from typing import Optional, Union

from utils import SourceName, gptRequest, assistantRequest
from utils.calc import computeSimilarity, average_similarity

##############################################################################################################################

class AssistantClient(object):
    """
    This class is used to interact with the assistant API
    """
    def __init__(self, sourceName, configPath, promptDir):
        self.sourceName = sourceName

        cf = configManager(configPath)
        self.gateway = cf.getValue("Auth", "gateway", "")
        self.pfGateway = cf.getValue("Auth", "pfGateway", "")
        self.gptGateway = cf.getValue("Auth", "gptGateway", "")
        self.apiKey = cf.getValue("Auth", "apiKey", "")
        self.appID = cf.getValue("Auth", "appID", "")
        self.appSecret = cf.getValue("Auth", "appSecret", "")
        self.xHeaderTenant = cf.getValue("Chat-Assistant", "xHeaderTenant", "")
        self.chatURL = cf.getValue("Chat-Assistant", "chatURL")
        self.assistantCode = cf.getValue("Chat-Assistant", "assistantCode")
        self.promptStabilityEvaluatorPath = Path(promptDir).joinpath(cf.getValue("Chat-GPT", "promptFile_stabilityEvaluator")).as_posix()
        with open(self.promptStabilityEvaluatorPath, 'r', encoding = 'utf-8') as f:
            self.promptStabilityEvaluator = f.read()
        '''
        self.userName = cf.getValue("Test-SQL", "userName")
        self.password = cf.getValue("Test-SQL", "password")
        self.sqlURL = cf.getValue("Test-SQL", "sqlURL")
        '''

    def request(self,
        sourceName: SourceName,
        messages: list = [{}],
        options: Optional[dict] = None,
        stream: bool = True,
        **kwargs
    ):
        return assistantRequest(
            sourceName,
            **kwargs,
            messages = messages,
            options = options,
            stream = stream,
        )

    def promptTest(self,
        sourceName: SourceName,
        messages: list = [{}],
        options: Optional[dict] = None,
        stream: bool = True,
        totalTestTimes: Optional[int] = None,
        promptStabilityEvaluator: Optional[str] = None,
        sqlConnection: Optional[Union[engine.Engine, engine.Connection]] = None,
        **kwargs
    ):
        # Test the assistant
        if totalTestTimes is not None:
            assert totalTestTimes > 0, 'Incorrect number!'
        else:
            return
        CurrentTestTime = 1
        Answers = []
        while CurrentTestTime <= totalTestTimes:
            print('Current test time:', CurrentTestTime) #yield f'Current test time: {CurrentTestTime}\n\n', 200
            for result, statuscode in assistantRequest(
                sourceName,
                **kwargs,
                messages = messages,
                options = options,
                stream = False
            ): # This iteration would be only executed for once since the stream option is set to false
                Answers.append(result)
            CurrentTestTime += 1

        # Compute the test results' similarity
        recordingThread = threading.Thread(
            target = computeSimilarity,
            args = (Answers, messages[0]['content'], totalTestTimes, sqlConnection)
        )
        recordingThread.start()

        # Analyze the test result
        yield "本次测试结果正在分析与计算中，请稍后...\n\n", 200
        for result, statuscode in gptRequest(
            sourceName,
            **kwargs,
            model = "gpt-4o",
            messages = [
                {
                    'role': "system",
                    'content': promptStabilityEvaluator
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
        for result, statuscode in self.request(
            self.sourceName,
            gateway = self.gateway,
            pfGateway = self.pfGateway,
            apiKey = self.apiKey,
            appID = self.appID,
            appSecret = self.appSecret,
            chatURL = self.chatURL,
            xHeaderTenant = self.xHeaderTenant,
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
        for result, statuscode in self.promptTest(
            self.sourceName,
            gateway = self.gateway,
            pfGateway = self.pfGateway,
            apiKey = self.apiKey,
            appID = self.appID,
            appSecret = self.appSecret,
            chatURL = self.chatURL,
            xHeaderTenant = self.xHeaderTenant,
            assistantCode = self.assistantCode if assistantCode is None else assistantCode,
            messages = messages,
            options = options,
            totalTestTimes = testTimes,
            promptStabilityEvaluator = self.promptStabilityEvaluator,
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################