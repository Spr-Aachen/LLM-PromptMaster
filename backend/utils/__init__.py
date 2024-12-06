from typing import Optional

from .auth import TokenParam, checkToken
from .io import write_file, read_file

##############################################################################################################################

class SourceName:
    openai = 'openai'
    transsion = 'transsion'


def gptRequest(
    sourceName: SourceName = SourceName.openai,
    **kwargs
):
    """
    """
    if sourceName == SourceName.openai:
        from .request_openai import gptRequest as request
    if sourceName == SourceName.transsion:
        from .request_transsion import gptRequest as request
    return request(**kwargs)


def assistantRequest(
    sourceName: SourceName = SourceName.openai,
    **kwargs
):
    """
    """
    if sourceName == SourceName.openai:
        pass #from .request_openai import assistantRequest as request
    if sourceName == SourceName.transsion:
        from .request_transsion import assistantRequest as request
    return request(**kwargs)

##############################################################################################################################