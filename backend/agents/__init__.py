from autogen_ext.models.openai import OpenAIChatCompletionClient

# 统一初始化模型客户端（全局只初始化一次）
model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    api_key="sk-540295e8fc944725af72cc468334cf59",
    base_url="https://api.deepseek.com/v1",
    model_info={
        "model_name": "deepseek-chat",
        "max_tokens": 32768,
        "capabilities": ["chat_completion"],
        "tokenizer": "cl100k_base",
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "family": "unknown"
    }
)


