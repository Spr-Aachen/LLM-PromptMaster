# -*- coding: utf-8 -*-

import os
import psutil
import signal
import argparse
import PyEasyUtils as EasyUtils
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

##############################################################################################################################

# Get current path
currentPath = EasyUtils.getCurrentPath()

# Get current directory
currentDir = Path(currentPath).parent.as_posix()

# Set directory to load static dependencies
resourceDir = EasyUtils.getBaseDir(searchMEIPASS = True) or currentDir

# Check whether python file is compiled
_, isFileCompiled = EasyUtils.getFileInfo()

# Get current version (assume resourceDir is the name of current version after being compiled)
currentVersion = Path(resourceDir).name if isFileCompiled else 'beta version'

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
        # Initialize app
        self._app = FastAPI(
            title = title,
            version = version,
            description = description,
        )

        # Set CORS
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
        @self._app.get("/getModelsInfo")
        async def getModelsInfo():
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
        async def gpt(request: Request, historyID: str, source: str, env: Optional[str] = None, model: Optional[str] = None, apiKey: Optional[str] = None, testTimes: Optional[Union[int, str]] = None):
            reqJs: dict = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            messages = self.chatManager.getHistory(historyID)[0] + [message]
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{env.strip()}.ini" if EasyUtils.evalString(env) is not None else "config.ini").as_posix()
            gptClient = GPTClient(source, EasyUtils.evalString(apiKey), configPath, promptDir)
            contentStream = gptClient.run(EasyUtils.evalString(model), messages, options) if EasyUtils.evalString(testTimes) is None else gptClient.test(EasyUtils.evalString(model), messages, options, testTimes)
            return StreamingResponse(
                content = contentStream,
                media_type = "application/json"
            )

        @self._app.post("/assistant")
        async def assistant(request: Request, historyID: str, source: str, env: Optional[str] = None, code: Optional[str] = None, apiKey: Optional[str] = None, testTimes: Optional[Union[int, str]] = None):
            reqJs: dict = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            messages = self.chatManager.getHistory(historyID)[0] + [message]
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{env.strip()}.ini" if EasyUtils.evalString(env) is not None else "config.ini").as_posix()
            assistantClient = AssistantClient(source, EasyUtils.evalString(apiKey), configPath, promptDir)
            contentStream = assistantClient.run(EasyUtils.evalString(code), messages, options) if EasyUtils.evalString(testTimes) is None else assistantClient.test(EasyUtils.evalString(code), messages, options, testTimes)
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