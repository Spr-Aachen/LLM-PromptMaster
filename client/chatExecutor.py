# -*- coding: utf-8 -*-

import json_repair
import time
import requests
import PyEasyUtils as EasyUtils
from typing import Union, Optional

##############################################################################################################################

# 调用方式 -> 路由段, 与 server/routers.py 的 /chat/* 保持一致
chatRoutes = {
    'chat': 'completions',
    'assistant': 'assistant',
}


def iterFrames(response):
    """
    按行解析服务端 NDJSON 帧 (一行一帧), 避免把多个 JSON 对象拼在一起解析
    """
    buffer = b""
    statusCode = response.status_code
    for content, statusCode in EasyUtils.responseParser(response, stream = True):
        chunk = content if isinstance(content, bytes) else str(content).encode("utf-8")
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            if line.strip():
                yield line.decode("utf-8", errors = "replace"), statusCode
    if buffer.strip():
        yield buffer.decode("utf-8", errors = "replace"), statusCode


def chatRequest(
    host, port,
    historyID: str,
    sourceName: str = 'azure',
    env: Optional[str] = None,
    mode: str = 'chat',
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
    if mode == 'chat':
        payload['model'] = model
    if mode == 'assistant':
        payload['code'] = code
    route = chatRoutes.get(mode)
    if route is None:
        raise ValueError(f"未知的调用方式: {mode}")
    url = f"http://{host}:{port}/chat/{route}"
    with requests.post(
        url = url,
        json = payload,
        stream = stream
    ) as response:
        if response.status_code == 200:
            for line, statusCode in iterFrames(response):
                frame = json_repair.loads(line)
                if not isinstance(frame, dict) or 'data' not in frame:
                    continue
                yield frame['data'], statusCode
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
        mode: str = 'chat',
        model: Optional[str] = None,
        code: Optional[str] = None,
        message: list[dict] = [{}],
        options: Optional[dict] = None,
        apiKey: Optional[str] = None,
        testTimes: Optional[int] = None
    ):
        def _clean(strVar):
            return (None if strVar.strip() == "" else strVar.strip()) if isinstance(strVar, str) else None
        for result, statuscode in chatRequest(host, port, historyID, sourceName, _clean(env), mode, _clean(model), _clean(code), message, options, _clean(apiKey), testTimes):
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