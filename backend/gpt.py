"""
GPT工具类
"""

import configparser
import json
import threading
from sqlalchemy import engine
from pathlib import Path
from typing import Optional, Union

from utils.request_transsion import gptRequest
from utils.calc import ComputeSimilarity, average_similarity

##############################################################################################################################

def GPTPromptTest(
    pfGateway: str = ...,
    gptGateway: str = ...,
    appID: Optional[str] = None,
    appSecret: str = ...,
    model: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True,
    TotalTestTimes: Optional[int] = None,
    threashold: float = 0.9,
    PromptStabilityEvaluator: Optional[str] = None,
    PromptReconstructor: Optional[str] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection]] = None
):
    # Test the GPT model
    if TotalTestTimes is not None:
        assert TotalTestTimes > 0, 'Incorrect number!'
    else:
        return
    CurrentTestTime = 1
    Answers = []
    while CurrentTestTime <= TotalTestTimes:
        print('Current test time:', CurrentTestTime) #yield f'Current test time: {CurrentTestTime}\n\n', 200
        for result, statuscode in gptRequest(
            pfGateway = pfGateway,
            gptGateway = gptGateway,
            appID = appID,
            appSecret = appSecret,
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
        args = (Answers, messages[1]['content'], TotalTestTimes, sqlConnection)
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
        stream = False
    ): # This iteration would be only executed for once since the stream option is set to false
        try:
            assert statuscode == 200, '...'
            yield f"分析完毕：\n\n{result}\n\n", 200
            Stability = float(str(result).strip().strip('```'))
        except:
            yield f"本次测试返回值的稳定值提取失败，将使用本次测试返回值的相似度计算结果作为替代\n\n", 200
            recordingThread.join()
            Stability = average_similarity
        if Stability >= threashold:
            yield f"本次测试返回值的稳定性维持在：{Stability}\n\nprompt无需调优\n\n", 200
            return # Stop iteration if the success rate is higher than threashold
        elif Stability >= 0:
            yield f"本次测试返回值的稳定性维持在：{Stability}\n\n建议对prompt进行调优\n\n", 200

    # Evaluate the prompt
    yield "开始prompt调优, please stand by...\n\n", 200
    for Message in messages:
        if Message['role'] == 'system':
            Prompt = Message['content']
    for result, statuscode in gptRequest(
        pfGateway = pfGateway,
        gptGateway = gptGateway,
        appID = appID,
        appSecret = appSecret,
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
    """
    This class is used to interact with the GPT API
    """
    def __init__(self, sourceName, configPath, promptDir):
        cf = configparser.ConfigParser()
        cf.read(configPath, encoding = 'utf-8')
        self.pfGateway = cf.get("GetToken", "pfGateway")
        self.gptGateway = cf.get("GetToken", "gptGateway")
        self.access_key_id = cf.get("GetToken", "appID")
        self.access_key_secret = cf.get("GetToken", "appSecret")
        self.PromptPath = Path(promptDir).joinpath(cf.get("Chat-GPT", "promptFile")).as_posix()
        with open(self.PromptPath, 'r', encoding = 'utf-8') as f:
            self.Prompt = f.read()
        self.PromptStabilityEvaluatorPath = Path(promptDir).joinpath(cf.get("Chat-GPT", "promptFile_stabilityEvaluator")).as_posix()
        with open(self.PromptStabilityEvaluatorPath, 'r', encoding = 'utf-8') as f:
            self.PromptStabilityEvaluator = f.read()
        self.PromptReconstructorPath = Path(promptDir).joinpath(cf.get("Chat-GPT", "promptFile_reconstructor")).as_posix()
        with open(self.PromptReconstructorPath, 'r', encoding = 'utf-8') as f:
            self.PromptReconstructor = f.read()
        '''
        self.userName = cf.get("Test-SQL", "userName")
        self.password = cf.get("Test-SQL", "password")
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
        for result, statuscode in gptRequest(
            pfGateway = self.pfGateway,
            gptGateway = self.gptGateway,
            appID = self.access_key_id,
            appSecret = self.access_key_secret,
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
        sqlConnection = 
        '''
        for result, statuscode in GPTPromptTest(
            pfGateway = self.pfGateway,
            gptGateway = self.gptGateway,
            appID = self.access_key_id,
            appSecret = self.access_key_secret,
            model = model,
            messages = messages,
            options = options,
            TotalTestTimes = testTimes,
            PromptStabilityEvaluator = self.PromptStabilityEvaluator,
            PromptReconstructor = self.PromptReconstructor,
            stream = True
        ):
            yield json.dumps(
               {"code": statuscode, "message": "成功" if statuscode == 200 else "失败", "data": result}
            )

##############################################################################################################################