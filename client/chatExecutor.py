# -*- coding: utf-8 -*-

import json_repair
import time
import requests
import PyEasyUtils as EasyUtils
from typing import Union, Optional

##############################################################################################################################

def chatRequest(
    host, port,
    historyID: str,
    sourceName: str = 'azure',
    env: Optional[str] = None,
    type: str = 'gpt',
    model: Optional[str] = None,
    code: Optional[str] = None,
    message: list[dict] = [{}],
    options: Optional[dict] = None,
    apiKey: Optional[str] = None,
    testTimes: Optional[int] = None,
    stream: bool = True
):
    # Post message
    payload = {
        'historyID': historyID,
        'source': sourceName,
        'env': env,
        'message': message,
        'options': options,
        'apiKey': apiKey,
        'testTimes': testTimes,
    }
    if type == 'gpt':
        payload['model'] = model
    if type == 'assistant':
        payload['code'] = code
    url = f"http://{host}:{port}/chat/{type}"
    with requests.post(
        url = url,
        json = payload,
        stream = stream
    ) as response:
        if response.status_code == 200:
            for content, statusCode in EasyUtils.responseParser(response, stream = stream):
                repairedContent = json_repair.loads(content)
                result = repairedContent['data']
                yield result, statusCode
        else:
            try:
                errorMessage = response.json().get("error", {}).get("message", "Request failed")
            except Exception:
                errorMessage = "Request failed"
            yield errorMessage, response.status_code


class task_chatRequest:
    """
    """
    def __init__(self):
        super().__init__()

        self.terminateFlag = False

    def execute(self,
        host, port,
        historyID: str,
        sourceName: str = 'azure',
        env: Optional[str] = None,
        type: str = 'gpt',
        model: Optional[str] = None,
        code: Optional[str] = None,
        message: list[dict] = [{}],
        options: Optional[dict] = None,
        apiKey: Optional[str] = None,
        testTimes: Optional[int] = None
    ):
        def _clean(strVar):
            return (None if strVar.strip() == "" else strVar.strip()) if isinstance(strVar, str) else None
        for result, statuscode in chatRequest(host, port, historyID, sourceName, _clean(env), type, _clean(model), _clean(code), message, options, _clean(apiKey), testTimes):
            yield result
            time.sleep(0.03)
            if self.terminateFlag:
                break

    def terminate(self):
        self.terminateFlag = True

##############################################################################################################################

def exitService(host, port):
    with requests.post(
        url = f"http://{host}:{port}/shutdown"
    ) as response:
        return True if response.status_code == 200 else False

##############################################################################################################################
