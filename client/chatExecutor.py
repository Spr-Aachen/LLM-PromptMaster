# -*- coding: utf-8 -*-

import json
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
    # Get token
    headers = {
        'P-Rtoken': "...",
        'P-Auth': "...",
        "P-AppId": "..."
    }
    response = requests.get(
        url = f"http://{host}:{port}/auth",
        headers = headers
    )
    if response.status_code == 200:
        res_token = response.json()
        Token = res_token.get("data", {})
        oAuth_token = f"Bearer {Token}"
    else:
        oAuth_token = ""
        yield "Request failed", response.status_code
        return

    # Post message
    if type == 'gpt':
        query = f"historyID={historyID}&source={sourceName}&env={env}&model={model}&apiKey={apiKey}&testTimes={testTimes}"
    if type == 'assistant':
        query = f"historyID={historyID}&source={sourceName}&env={env}&code={code}&apiKey={apiKey}&testTimes={testTimes}"
    url = f"http://{host}:{port}/chat/{type}{f'?{query}' if len(query) > 0 else ''}"
    headers = {
        'Authorization': oAuth_token
    }
    payload = {
        'message': message,
        'options': options
    } if options is not None else {
        'message': message
    }
    with requests.post(
        url = url,
        headers = headers,
        data = json.dumps(payload),
        stream = stream
    ) as response:
        if response.status_code == 200:
            for content, statusCode in EasyUtils.responseParser(response, stream = stream):
                repairedContent = json_repair.loads(content)
                result = repairedContent['data']
                yield result, statusCode
        else:
            yield "Request failed", response.status_code
            return


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