from typing import Optional

from . import request_azure, request_deepseek, request_openai, request_transsion
from .auth import TokenParam, checkToken
from .io import write_file, read_file

##############################################################################################################################

class SourceName:
    azure = 'azure'
    deepseek = 'deepseek'
    openai = 'openai'
    transsion = 'transsion'


modelsInfo = {
    SourceName.azure: list(request_azure.chatURLs.keys()),
    SourceName.deepseek: list(request_deepseek.chatURLs.keys()),
    SourceName.openai: list(request_openai.chatURLs.keys()),
    SourceName.transsion: list(request_transsion.chatURLs.keys())
}


def gptRequest(
    sourceName: SourceName = SourceName.azure,
    **kwargs
):
    """
    """
    if sourceName == SourceName.azure:
        request = request_azure.gptRequest
    if sourceName == SourceName.deepseek:
        request = request_deepseek.gptRequest
    if sourceName == SourceName.openai:
        request = request_openai.gptRequest
    if sourceName == SourceName.transsion:
        request = request_transsion.gptRequest
    return request(**kwargs)


def assistantRequest(
    sourceName: SourceName = SourceName.azure,
    **kwargs
):
    """
    """
    if sourceName == SourceName.azure:
        pass #request = request_azure.assistantRequest
    if sourceName == SourceName.deepseek:
        pass #request = request_deepseek.assistantRequest
    if sourceName == SourceName.openai:
        pass #request = request_openai.assistantRequest
    if sourceName == SourceName.transsion:
        request = request_transsion.assistantRequest
    return request(**kwargs)

##############################################################################################################################