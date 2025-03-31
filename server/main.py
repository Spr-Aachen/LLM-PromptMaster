# -*- coding: utf-8 -*-

import os
import psutil
import signal
import argparse
import uvicorn
from fastapi import FastAPI, Request, Response, status, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Optional, List
from pathlib import Path

from utils import TokenParam, checkToken, write_file, modelsInfo
from gpt import GPTClient
from assistant import AssistantClient
from wrapper import ChatManager
from config import currentDir

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
#parser.add_argument("--env",  help = "环境启动项", type = str, default = "prod")
parser.add_argument("--host", help = "主机地址",   type = str, default = "localhost")
parser.add_argument("--port", help = "端口",       type = int, default = 8080)
parser.add_argument("--profileDir", help = "配置目录", type = str, default = Path(currentDir).joinpath('Profile').as_posix())
args = parser.parse_args()

profileDir = args.profileDir


UPLOAD_DIR = Path(profileDir).joinpath('uploads').as_posix()

PROMPT_DIR = Path(profileDir).joinpath('prompts').as_posix()

HISTORY_DIR = Path(profileDir).joinpath('history').as_posix()
conversationDir = Path(HISTORY_DIR).joinpath('conversations').as_posix()
questionDir = Path(HISTORY_DIR).joinpath('questions').as_posix()

##############################################################################################################################

class PromptTestTool:
    """
    """
    def __init__(self, title, version: str, description: str):
        # App definition
        self._app = FastAPI(
            title = title,
            version = version,
            description = description,
        )

        # Set all CORS
        self._app.add_middleware(
            middleware_class = CORSMiddleware,
            allow_origins = ["*"],
            allow_origin_regex = None,
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"],
            expose_headers = ["*"],
            max_age = 600,
        )

        # Sever definition
        self.server = uvicorn.Server(uvicorn.Config(self._app))

        # Setup tools
        self.setExceptionHandler()
        self.setNormalActuator()
        self.setChatActuator()

        # Setup managers
        self.chatManager = ChatManager(
            promptDir = PROMPT_DIR,
            conversationDir = conversationDir,
            questionDir = questionDir
        )

    def app(self):
        return self._app

    def setExceptionHandler(self):
        @self._app.exception_handler(StarletteHTTPException)
        async def http_exceptionHandler(request: Request, exc: StarletteHTTPException):
            return JSONResponse(
                status_code = exc.status_code,
                content = jsonable_encoder(
                    {
                        "code": exc.status_code,
                        "message": str(exc.detail),
                        "data": None
                    }
                )
            )

        @self._app.exception_handler(RequestValidationError)
        async def validation_exceptionHandler(request: Request, exc: RequestValidationError):
            return JSONResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                content = jsonable_encoder(
                    {
                        "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "message": str(exc.errors()),
                        "data": str(exc.body)}
                )
            )

    def setNormalActuator(self):
        @self._app.get("/")
        async def default():
            return "Welcome To prompt Test Service!"

        @self._app.get("/auth", summary = "验证token")
        async def auth(token: TokenParam = Depends(checkToken)):
            return {"data": token}

        @self._app.post("/upload")
        async def upload_file(files: List[UploadFile]):
            os.makedirs(UPLOAD_DIR, exist_ok = True)
            for file in files:
                filePath = Path(UPLOAD_DIR).joinpath(file.filename).as_posix()
                os.remove(filePath) if Path(filePath).exists() else None
                await write_file(filePath, file)
            return {"status": "Succeeded"}

        @self._app.post("/shutdown")
        async def shutdown():
            self.server.should_exit = True
            Process = psutil.Process(os.getpid())
            ProcessList =  Process.children(recursive = True) + [Process]
            for Process in ProcessList:
                try:
                    os.kill(Process.pid, signal.SIGTERM)
                except:
                    pass
            #return {"message": "Shutting down, bye..."}

    def setChatActuator(self):
        @self._app.get("/info")
        async def init():
            return modelsInfo

        @self._app.get("/loadPrompts")
        async def loadPrompts():
            prompts = self.chatManager.loadPrompts()
            return prompts

        @self._app.get("/getPrompt")
        async def getPrompt(promptID):
            prompt = self.chatManager.getPrompt(promptID)
            return prompt

        @self._app.post("/createPrompt")
        async def createPrompt(name: str):
            promptID, promptName = self.chatManager.createPrompt(name)
            return promptID, promptName

        @self._app.post("/renamePrompt")
        async def renamePrompt(promptID, newName):
            self.chatManager.renamePrompt(promptID, newName)

        @self._app.post("/deletePrompt")
        async def deletePrompt(promptID):
            self.chatManager.deletePrompt(promptID)

        @self._app.post("/savePrompt")
        async def savePrompt(promptID, prompt):
            self.chatManager.savePrompt(promptID, prompt)

        @self._app.get("/loadHistories")
        async def loadHistories():
            histories = self.chatManager.loadHistories()
            return histories

        @self._app.get("/getHistory")
        async def getHistory(historyID):
            messages, question = self.chatManager.getHistory(historyID)
            return messages, question

        @self._app.post("/createConversation")
        async def createConversation(name):
            historyID, conversationName = self.chatManager.createConversation(name)
            return historyID, conversationName

        @self._app.post("/renameConversation")
        async def renameConversation(historyID, newName):
            self.chatManager.renameConversation(historyID, newName)

        @self._app.post("/deleteConversation")
        async def deleteConversation(historyID):
            self.chatManager.deleteConversation(historyID)

        # @self._app.post("/saveConversation")
        # async def saveConversation(historyID, messages):
        #     self.chatManager.saveConversation(historyID, messages)

        @self._app.post("/saveQuestion")
        async def saveQuestion(historyID, question):
            self.chatManager.saveQuestion(historyID, question)

        @self._app.post("/applyPrompt")
        async def applyPrompt(promptID):
            self.chatManager.applyPrompt(promptID)

        @self._app.post("/addUserMessage")
        async def addUserMessage(historyID, userMessage):
            self.chatManager.addUserMessage(historyID, eval(userMessage))

        @self._app.post("/recieveAnswer")
        async def recieveAnswer(historyID, recievedText):
            messages = self.chatManager.recieveAnswer(historyID, recievedText)
            return messages

        @self._app.post("/gpt")
        async def gpt(request: Request, historyID: str, source: str, env: Optional[str] = None, model: str = "gpt-4o", testtimes: Optional[int] = None):
            reqJs: dict = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            messages = self.chatManager._getConversationNameAndMessages(historyID)[1] + [message]
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{env.strip()}.ini" if env is not None else "config.ini").as_posix()
            gptClient = GPTClient(source, configPath, promptDir)
            contentStream = gptClient.run(model, messages, options) if testtimes is None else gptClient.test(model, messages, options, testtimes)
            return StreamingResponse(
                content = contentStream,
                media_type = "application/json"
            )

        @self._app.post("/assistant")
        async def assistant(request: Request, historyID: str, source: str, env: Optional[str] = None, code: Optional[str] = None, testtimes: Optional[int] = None):
            reqJs: dict = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            messages = self.chatManager._getConversationNameAndMessages(historyID)[1] + [message]
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{env.strip()}.ini" if env is not None else "config.ini").as_posix()
            assistantClient = AssistantClient(source, configPath, promptDir)
            contentStream = assistantClient.run(code, messages, options) if testtimes is None else assistantClient.test(code, messages, options, testtimes)
            return StreamingResponse(
                content = contentStream,
                media_type = "application/json"
            )

    def run(self):
        uvicorn.run(
            app = self._app,
            host = args.host,
            port = args.port
        )

##############################################################################################################################

if __name__ == "__main__":
    PromptTest = PromptTestTool(
        title = "PromptTestClient Demo",
        version = "1.0.0",
        description = "Just a demo"
    )
    PromptTest.run()

##############################################################################################################################