# -*- coding: utf-8 -*-

import os
import io
import sys
import json
import uvicorn
import argparse
from typing import Union, Optional
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
#from sqlalchemy.orm import Session
#from sql import crud, models, schemas
#from sql.database import SessionLocal, engine

from utils.auth import TokenParam, checkToken
#from utils.logger import logger
from tools.gptTool import GPTClient
from tools.assistantTool import AssistantClient

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--profile", help = "环境启动项", type = str)
parser.add_argument("-p", "--port",    help = "端口",       type = int)
args = parser.parse_args()

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

        # Set all CORS enabled origins
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

        self.server = uvicorn.Server(uvicorn.Config(self._app))

        self.exception_handler()
        self.actuator()

    def get_app(self):
        return self._app

    def exception_handler(self):
        '''
        异常处理
        '''
        @self._app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
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
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return JSONResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                content = jsonable_encoder(
                    {
                        "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "message": str(exc.errors()),
                        "data": str(exc.body)}
                )
            )

    def actuator(self):
        '''
        健康检查接口
        '''
        @self._app.get("/actuator/health/liveness")
        async def health_liveness():
            return {"status": "UP"}

        @self._app.get("/actuator/health/readiness")
        async def health_readiness():
            return {"status": "UP"}

        @self._app.post("/actuator/shutdown")
        async def health_shutdown():
            # 处理优雅关机相关的逻辑
            self.server.should_exit = True
            return {"message": "Shutting down, bye..."}

    def run(self):
        CurrentDir = sys.path[0]
        PromptDir = f"{CurrentDir}{os.sep}prompt"
        ConfigPath = f"{CurrentDir}{os.sep}config{os.sep}config-{args.profile.strip()}.ini"

        gptClient = GPTClient(ConfigPath, PromptDir)
        assistantClient = AssistantClient(ConfigPath)

        @self._app.get("/auth", summary = "验证token")
        async def auth(token: TokenParam = Depends(checkToken)):
            return {"data": token}

        @self._app.get("/")
        async def index():
            return "Welcome To Prompt Test Service!"

        @self._app.post("/gpt")
        async def gpt(request: Request, model: str = "gpt-4o", testtimes: Optional[int] = None):
            reqJs = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            contentstream = gptClient.run(model, message, options) if testtimes is None else gptClient.test(model, message, options, testtimes)
            return StreamingResponse(
                content = contentstream,
                media_type = "application/json"
            )

        @self._app.post("/assistant")
        async def assistant(request: Request, code: Optional[str] = None, testtimes: Optional[int] = None):
            reqJs = await request.json()
            message = reqJs.get('message', None)
            options = reqJs.get('options', None)
            contentstream = assistantClient.run(code, message, options) if testtimes is None else assistantClient.test(code, message, options, testtimes)
            return StreamingResponse(
                content = contentstream,
                media_type = "application/json"
            )

        '''
        models.Base.metadata.create_all(bind = engine)

        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        @self._app.post("/users/", response_model=schemas.User)
        def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
            db_user = crud.get_user_by_email(db, email=user.email)
            if db_user:
                raise StarletteHTTPException(status_code=400, detail="Email already registered")
            return crud.create_user(db=db, user=user)

        @self._app.get("/users/", response_model=list[schemas.User])
        def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            users = crud.get_users(db, skip=skip, limit=limit)
            return users

        @self._app.get("/users/{user_id}", response_model=schemas.User)
        def read_user(user_id: int, db: Session = Depends(get_db)):
            db_user = crud.get_user(db, user_id=user_id)
            if db_user is None:
                raise StarletteHTTPException(status_code=404, detail="User not found")
            return db_user

        @self._app.post("/users/{user_id}/items/", response_model=schemas.Item)
        def create_item_for_user(
            user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
        ):
            return crud.create_user_item(db=db, item=item, user_id=user_id)

        @self._app.get("/items/", response_model=list[schemas.Item])
        def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            items = crud.get_items(db, skip=skip, limit=limit)
            return items
        '''

        uvicorn.run(
            app = self._app,
            host = "localhost",
            port = args.port
        )

##############################################################################################################################

if __name__ == "__main__":
    PromptTest = PromptTestTool(
        "PromptTestClient Demo",
        "1.0.0",
        "Just a demo"
    )
    PromptTest.run()

##############################################################################################################################