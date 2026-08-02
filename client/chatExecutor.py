# -*- coding: utf-8 -*-

import time
from typing import Optional

from api import ApiClient

##############################################################################################################################

class task_chatRequest:
    """
    聊天请求的线程封装: 透传 ApiClient 的流式帧并支持中途终止
    """
    def __init__(self, client: ApiClient):
        super().__init__()

        self.client = client
        self.terminateFlag = False

    def execute(self,
        historyID: str,
        sourceName: str = 'azure',
        env: Optional[str] = None,
        mode: str = 'chat',
        model: Optional[str] = None,
        code: Optional[str] = None,
        message: Optional[list[dict]] = None,
        options: Optional[dict] = None,
        apiKey: Optional[str] = None,
        testTimes: Optional[int] = None
    ):
        def _clean(strVar):
            return (None if strVar.strip() == "" else strVar.strip()) if isinstance(strVar, str) else None
        for result, statuscode in self.client.chatRequest(historyID, sourceName, _clean(env), mode, _clean(model), _clean(code), message, options, _clean(apiKey), testTimes):
            yield result
            time.sleep(0.03)
            if self.terminateFlag:
                break

    def terminate(self):
        self.terminateFlag = True

##############################################################################################################################