# -*- coding: utf-8 -*-

import os
import sys
import psutil
import signal
import argparse
import uvicorn
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Optional
from pathlib import Path

from utils.auth import TokenParam, checkToken
from gpt import GPTClient
from assistant import AssistantClient

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--profile", help = "环境启动项", type = str)
parser.add_argument("-p", "--port",    help = "端口",       type = int)
args = parser.parse_args()


currentDir = Path(sys.argv[0]).parent.as_posix()

##############################################################################################################################

class PromptTestTool():
    '''
    '''
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

        # Set all tools
        self.setExceptionHandler()
        self.setNormalActuator()
        self.setCoreActuator()

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
        @self._app.get("/auth", summary = "验证token")
        async def auth(token: TokenParam = Depends(checkToken)):
            return {"data": token}

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

    def setCoreActuator(self):
        @self._app.get("/")
        async def default():
            return "Welcome To Prompt Test Service!"

        @self._app.post("/gpt")
        async def gpt(request: Request, source: str, model: str = "gpt-4o", testtimes: Optional[int] = None):
            reqJs = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{args.profile.strip()}.ini").as_posix()
            gptClient = GPTClient(source, configPath, promptDir)
            contentStream = gptClient.run(model, message, options) if testtimes is None else gptClient.test(model, message, options, testtimes)
            return StreamingResponse(
                content = contentStream,
                media_type = "application/json"
            )

        @self._app.post("/assistant")
        async def assistant(request: Request, source: str, code: Optional[str] = None, testtimes: Optional[int] = None):
            reqJs = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            promptDir = Path(currentDir).joinpath("prompt").as_posix()
            configPath = Path(currentDir).joinpath("config", source, f"config-{args.profile.strip()}.ini").as_posix()
            assistantClient = AssistantClient(source, configPath, promptDir)
            contentStream = assistantClient.run(code, message, options) if testtimes is None else assistantClient.test(code, message, options, testtimes)
            return StreamingResponse(
                content = contentStream,
                media_type = "application/json"
            )

    def run(self):
        uvicorn.run(
            app = self._app,
            host = "localhost",
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