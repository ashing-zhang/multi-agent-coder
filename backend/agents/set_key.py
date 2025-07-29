from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_openai import ChatOpenAI

def create_langchain_llm(api_key):
    """
    创建LangChain需要的LLM实例
    
    :param api_key: DeepSeek API密钥
    :return: ChatOpenAI实例
    """
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )

def set_deepseek_api_key(api_key):
    """
    设置DeepSeek API密钥并创建AutoGen和LangChain的客户端
    
    :param api_key: DeepSeek API密钥
    :return: AutoGen客户端和LangChain LLM实例的元组
    """
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
    
    return client