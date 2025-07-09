from autogen_ext.models.openai import OpenAIChatCompletionClient
from backend.agents.model_client_manager import set_model_client

def set_deepseek_api_key(api_key):
    client = OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key=api_key,    # 'sk-45052c02bba348c78f53739546ff3c3c'
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
    set_model_client(client)
    return True