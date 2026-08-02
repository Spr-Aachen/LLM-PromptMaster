# -*- coding: utf-8 -*-

import json_repair
import requests
from typing import Iterator, Optional

##############################################################################################################################

# 普通请求超时 (秒); 流式请求默认不设超时, 避免长回答被提前中断
DEFAULT_TIMEOUT = 30.0

# 调用方式 -> 路由段, 与 server/app/api/chat.py 的 /chat/* 保持一致
chatRoutes = {
    'chat': 'completions',
    'assistant': 'assistant',
}

##############################################################################################################################

class ApiError(Exception):
    """
    服务端统一错误: {error: {code, message, details}}
    """
    def __init__(self, code: str, message: str, statusCode: Optional[int] = None, details = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.statusCode = statusCode
        self.details = details


def iterFrames(response: requests.Response):
    """
    按行解析服务端 NDJSON 帧 (一行一帧), 避免把多个 JSON 对象拼在一起解析
    """
    buffer = b""
    statusCode = response.status_code
    for chunk in response.iter_content(chunk_size = 1024):
        if not chunk:
            continue
        buffer += chunk if isinstance(chunk, bytes) else str(chunk).encode("utf-8")
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            if line.strip():
                yield line.decode("utf-8", errors = "replace"), statusCode
    if buffer.strip():
        yield buffer.decode("utf-8", errors = "replace"), statusCode

##############################################################################################################################

class ApiClient:
    """
    服务端 HTTP 接口封装: 统一 baseUrl、超时、错误码与流式解析
    """
    def __init__(self,
        host: str = "localhost",
        port: int = 8080,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        streamTimeout: Optional[float] = None,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.streamTimeout = streamTimeout
        self.baseUrl = f"http://{host}:{port}"

    ######################################################################

    def _url(self, path: str) -> str:
        return f"{self.baseUrl}/{path.lstrip('/')}"

    def _parseError(self, response: requests.Response) -> ApiError:
        """
        解析服务端错误体, 非 JSON 响应回退为 HTTP 状态说明
        """
        try:
            error = response.json().get("error", {})
        except ValueError:
            error = {}
        if not isinstance(error, dict):
            error = {}
        return ApiError(
            code = error.get("code", "http_error"),
            message = error.get("message", f"请求失败 (HTTP {response.status_code})"),
            statusCode = response.status_code,
            details = error.get("details"),
        )

    def _request(self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
        stream: bool = False,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        response = requests.request(
            method = method,
            url = self._url(path),
            params = params,
            json = payload,
            stream = stream,
            timeout = timeout if timeout is not None else (self.streamTimeout if stream else self.timeout),
        )
        if response.status_code != 200:
            error = self._parseError(response)
            response.close()
            raise error
        return response

    def get(self, path: str, params: Optional[dict] = None):
        with self._request("GET", path, params = params) as response:
            return response.json()

    def post(self, path: str, params: Optional[dict] = None, payload: Optional[dict] = None):
        with self._request("POST", path, params = params, payload = payload) as response:
            return response.json()

    ######################################################################

    #==== Prompt ====
    def loadPrompts(self) -> dict:
        return self.get("chat/loadPrompts")

    def getPrompt(self, promptID: str) -> str:
        return self.get("chat/getPrompt", params = {"promptID": promptID})

    def createPrompt(self, name: str) -> list:
        return self.post("chat/createPrompt", payload = {"name": name})

    def renamePrompt(self, promptID: str, newName: str):
        return self.post("chat/renamePrompt", payload = {"promptID": promptID, "newName": newName})

    def deletePrompt(self, promptID: str):
        return self.post("chat/deletePrompt", params = {"promptID": promptID})

    def savePrompt(self, promptID: str, prompt: str):
        return self.post("chat/savePrompt", payload = {"promptID": promptID, "prompt": prompt})

    #==== Conversation ====
    def loadHistories(self) -> dict:
        return self.get("chat/loadHistories")

    def getHistory(self, historyID: str) -> list:
        return self.get("chat/getHistory", params = {"historyID": historyID})

    def createConversation(self, name: str) -> list:
        return self.post("chat/createConversation", payload = {"name": name})

    def renameConversation(self, historyID: str, newName: str):
        return self.post("chat/renameConversation", payload = {"historyID": historyID, "newName": newName})

    def deleteConversation(self, historyID: str):
        return self.post("chat/deleteConversation", params = {"historyID": historyID})

    def saveQuestion(self, historyID: str, question: str):
        return self.post("chat/saveQuestion", payload = {"historyID": historyID, "question": question})

    def applyPrompt(self, promptID: str):
        return self.post("chat/applyPrompt", params = {"promptID": promptID})

    def addUserMessage(self, historyID: str, message: dict):
        return self.post("chat/addUserMessage", payload = {"historyID": historyID, "message": message})

    def recieveAnswer(self, historyID: str, recievedText: str) -> list:
        return self.post("chat/recieveAnswer", payload = {"historyID": historyID, "recievedText": recievedText})

    #==== Meta ====
    def getCapabilities(self) -> dict:
        return self.get("chat/getCapabilities")

    def getModelsInfo(self) -> dict:
        return self.get("chat/getModelsInfo")

    def getMetaModels(self, refresh: bool = False) -> dict:
        return self.get("api/meta/models", params = {"refresh": refresh} if refresh else None)

    def getProviders(self) -> list:
        return self.get("api/providers")

    def getUsage(self, rangeName: str = "today") -> dict:
        return self.get("api/usage", params = {"range": rangeName})

    #==== Chat ====
    def chatRequest(self,
        historyID: str,
        sourceName: str = 'azure',
        env: Optional[str] = None,
        mode: str = 'chat',
        model: Optional[str] = None,
        code: Optional[str] = None,
        message: Optional[list[dict]] = None,
        options: Optional[dict] = None,
        apiKey: Optional[str] = None,
        testTimes: Optional[int] = None,
    ) -> Iterator[tuple]:
        """
        发起对话请求并按行产出 (数据帧, HTTP 状态码)
        """
        route = chatRoutes.get(mode)
        if route is None:
            raise ValueError(f"未知的调用方式: {mode}")
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
        response = requests.post(
            url = self._url(f"chat/{route}"),
            json = payload,
            stream = True,
            timeout = self.streamTimeout,
        )
        with response:
            if response.status_code != 200:
                error = self._parseError(response)
                yield error.message, response.status_code
                return
            for line, statusCode in iterFrames(response):
                frame = json_repair.loads(line)
                if not isinstance(frame, dict) or 'data' not in frame:
                    continue
                yield frame['data'], statusCode

    #==== Service ====
    def shutdown(self, timeout: float = 5.0) -> bool:
        """
        请求服务端退出; 服务端已不可达时返回 False 而不是抛出
        """
        try:
            with self._request("POST", "shutdown", timeout = timeout) as response:
                return response.status_code == 200
        except (ApiError, requests.RequestException):
            return False

##############################################################################################################################