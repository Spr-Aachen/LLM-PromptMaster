from typing import Optional

from . import request_azure, request_openai, request_transsion
from .auth import TokenParam, checkToken
from .io import write_file, read_file

##############################################################################################################################

class SourceName:
    azure = 'azure'
    openai = 'openai'
    transsion = 'transsion'


modelsInfo = {
    SourceName.azure: list(request_azure.chatURLs.keys()),
    SourceName.openai: list(request_openai.chatURLs.keys()),
    SourceName.transsion: list(request_transsion.ChatURLs.keys())
}


def gptRequest(
    sourceName: SourceName = SourceName.openai,
    **kwargs
):
    """
    """
    if sourceName == SourceName.azure:
        request = request_azure.gptRequest
    if sourceName == SourceName.openai:
        request = request_openai.gptRequest
    if sourceName == SourceName.transsion:
        request = request_transsion.gptRequest
    return request(**kwargs)


def assistantRequest(
    sourceName: SourceName = SourceName.openai,
    **kwargs
):
    """
    """
    if sourceName == SourceName.azure:
        pass #request = request_azure.assistantRequest
    if sourceName == SourceName.openai:
        pass #request = request_openai.assistantRequest
    if sourceName == SourceName.transsion:
        request = request_transsion.assistantRequest
    return request(**kwargs)

##############################################################################################################################