from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_openai import ChatOpenAI

def create_langchain_llm(api_key,base_url):
    """
    创建LangChain需要的LLM实例
    懒加载 (Lazy Initialization)，并不会立即与 DEEPSEEK_BASE_URL 
    建立一个真正的网络连接。这是一种常见的设计模式，为了节省资源，
    只有在第一次真正需要它（即第一次调用 ainvoke 或类似方法）时，
    它才会去执行网络握手、身份验证、建立连接池等一系列耗时操作。
    :param api_key: DeepSeek API密钥
    :return: ChatOpenAI实例
    """
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url=base_url,
        temperature=0.7
    )

def set_deepseek_api_key(api_key,base_url):
    """
    设置DeepSeek API密钥并创建AutoGen和LangChain的客户端
    
    :param api_key: DeepSeek API密钥
    :return: AutoGen客户端和LangChain LLM实例的元组
    """
    client = OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key=api_key,    # 'sk-45052c02bba348c78f53739546ff3c3c'
        base_url=base_url,
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