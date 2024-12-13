import requests
import json
import json_repair
import requests.adapters
from typing import Optional, Union

##############################################################################################################################

ChatURLs_Norm = {
    'gpt-35-turbo': "openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-10-21",
    'gpt-4o': "openai/deployments/gpt-4o/chat/completions?api-version=2024-10-21",
}

ChatURLs_Paint = {
    'dall-e2': "openai/deployments/dall-e2/images/generations?api-version=2024-10-21",
    'dall-e3': "openai/deployments/dall-e3/images/generations?api-version=2024-10-21",
}

ChatURLs = {**ChatURLs_Norm, **ChatURLs_Paint}


def gptRequest(
    gateway: str = ...,
    apiKey: Optional[str] = None,
    model: str = ...,
    messages: list = [{}],
    options: Optional[dict] = None,
    stream: bool = True,
    **kwargs
):
    # 初始化会话
    session = requests.session()
    session.keep_alive = False
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries = 3))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries = 3))
    # 请求GPT接口
    url = f"{gateway}/{ChatURLs[model]}"
    Headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-key': apiKey
    }
    if model in ChatURLs_Norm:
        Payload = {
            'messages': messages,
        }
    if model in ChatURLs_Paint:
        Payload = {
            'prompt': f"{messages[0]['content']}\n{messages[1]['content']}",
        }
        stream = False # 图片生成接口不支持流式输出
    Payload = {
        **Payload,
        **(options if options is not None else {}),
        'stream': stream
    }
    try:
        response = requests.post(
            url = url,
            headers = Headers,
            data = json.dumps(Payload),
            stream = stream
        )
    except Exception as e:
        yield str(e), 500
    else:
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size = 1024 if stream else None, decode_unicode = False):
                if chunk:
                    buffer = chunk.decode('utf-8', errors = 'ignore')
                    if stream:
                        buffer = "".join(line[len("data:"):] if line.startswith("data:") else line for line in buffer.splitlines()) # remove all the 'data:' suffix
                    try:
                        parsed_content = json_repair.loads(buffer)
                        #print('buffer successfully parsed:\n', buffer)
                        if model in ChatURLs_Norm:
                            result = parsed_content['choices'][0]['delta']['content'] if stream else parsed_content['choices'][0]['message']['content']
                        if model in ChatURLs_Paint:
                            result = parsed_content['data'][0]['url']
                        yield result, response.status_code
                    except:
                        #print('failed to load buffer:\n', buffer)
                        continue
        else:
            yield "Request failed", response.status_code

##############################################################################################################################