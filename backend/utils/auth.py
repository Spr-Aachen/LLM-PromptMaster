from fastapi import Header, HTTPException
from typing import Optional

##############################################################################################################################

# token 参数
class TokenParam:
    def __init__(self, rToken = None, uToken = None, AppId = None):
        self.rToken = rToken
        self.uToken = uToken
        self.AppId = AppId


async def checkToken(
    uToken: Optional[str] = Header(default = None, alias = "P-Rtoken"),
    rToken: Optional[str] = Header(default = None, alias = "P-Auth"),
    AppId: Optional[str] = Header(default = None, alias = "P-AppId"),
):
    def is_empty(*values):
        for value in values:
            if value is None:
                return True
            if isinstance(value, str) and value.strip() == "":
                return True
        return False
    assert not is_empty(rToken, uToken, AppId), HTTPException(status_code = 400, detail = "X-Key header invalid")
    return TokenParam(rToken, uToken, AppId)

##############################################################################################################################