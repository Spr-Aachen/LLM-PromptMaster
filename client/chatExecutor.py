# -*- coding: utf-8 -*-

import json
import json_repair
import time
import requests
import PyEasyUtils as EasyUtils
from typing import Union, Optional
from PySide6.QtCore import QObject, Signal

##############################################################################################################################

def simpleRequest(
    reqMethod: EasyUtils.requestManager, host, port,
    pathParams: Union[str, list[str], None] = None,
    queryParams: Union[str, list[str], None] = None,
    *keys
):
    #return EasyUtils.simpleRequest(reqMethod, "http", host, port, pathParams, queryParams, *keys)

    if not EasyUtils.isConnected("http", host, port):
        return
    response = reqMethod.request("http", host, port, pathParams, queryParams, *keys)
    for parsed_content, _ in EasyUtils.responseParser(response):
        encodedResponse = parsed_content
    result = (encodedResponse.get(key, {}) for key in keys) if keys else encodedResponse
    return result

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
    testTimes: Optional[int] = None,
    stream: bool = True
):
    if not EasyUtils.isConnected("http", host, port):
        return

    # Get token
    Headers = {
        'P-Rtoken': "...",
        'P-Auth': "...",
        "P-AppId": "..."
    }
    response = requests.get(
        url = f"http://{host}:{port}/auth",
        headers = Headers
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
        query = f"historyID={historyID}&source={sourceName}{f'&env={env}' if env is not None else ''}&model={'gpt-4o' if model is None else model}{f'&testTimes={testTimes}' if testTimes is not None else ''}"
    if type == 'assistant':
        query = f"historyID={historyID}&source={sourceName}{f'&env={env}' if env is not None else ''}&code={'114514' if code is None else code}{f'&testTimes={testTimes}' if testTimes is not None else ''}"
    URL = f"http://{host}:{port}/{type}{f'?{query}' if len(query) > 0 else ''}"
    Headers = {
        'Authorization': oAuth_token
    }
    Payload = {
        'message': message,
        'options': options
    } if options is not None else {
        'message': message
    }
    with requests.post(
        url = URL,
        headers = Headers,
        data = json.dumps(Payload),
        stream = stream
    ) as response:
        if response.status_code == 200:
            for parsed_content, status_code in EasyUtils.responseParser(response, stream = True):
                result = parsed_content['data']
                yield result, status_code
        else:
            yield "Request failed", response.status_code
            return


class task_chatRequest(QObject):
    textReceived = Signal(str)

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
        testTimes: Optional[int] = None
    ):
        for result, statuscode in chatRequest(host, port, historyID, sourceName, env, type, model, code, message, options, testTimes):
            self.textReceived.emit(result)
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