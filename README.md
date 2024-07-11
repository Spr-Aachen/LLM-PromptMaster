<div align = "center">

LLM Prompt Test

</div>

## Example

### Known Issues
- XXX

### Solution
1. 将格式规范作为Constrains中的一条加入Prompt模板
    - 减小请求头的字符量
    - 有效减小模型返回值的随机性
    - 有效提升模型返回的响应速度
2. 去除冗余的约束词并统一（标准化）不同的提示词
    - 提升Prompt的有效性
    - 增加模板的可读性
3. 优化Profile并调整Constrains的语句顺序
    - 提升Prompt的有效性

### Preview
- Request
    ```
    Paste the request here.
    ```
- Response (OpenAI GPT-4o)
    ```
    Paste the model response here.
    ```