'''
    简单例子：使用autogen接口实现一个多Agent协作的代码生成和优化流程。
'''
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 初始化模型客户端
model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",  # DeepSeek 支持的模型名，如 deepseek-chat、deepseek-coder 等
    api_key="sk-540295e8fc944725af72cc468334cf59",
    base_url="https://api.deepseek.com/v1",  # DeepSeek 的 OpenAI 兼容 API 地址
    model_info={
        "model_name": "deepseek-chat", 
        "max_tokens": 32768,
        "capabilities": ["chat_completion"],
        "tokenizer": "cl100k_base",
        "vision": False,
        "function_calling": True,
        "json_output":True,
        "structured_output": True,
        "family":"unknown"
    }
)

# 1. 代码生成 Agent
coder = AssistantAgent(
    name="CoderAgent",
    system_message="你是一个代码生成专家，根据用户需求编写高质量的 Python 代码。",
    model_client=model_client,
)

# 2. 代码优化建议 Agent
reviewer = AssistantAgent(
    name="ReviewerAgent",
    system_message="你是代码审查专家，请对给定的代码提出详细的优化建议。",
    model_client=model_client,
)

# 3. 代码整合 Agent
finalizer = AssistantAgent(
    name="FinalizerAgent",
    system_message="你是代码整合专家，请结合原始代码和优化建议，输出最终优化后的完整代码。",
    model_client=model_client,
)

async def main():
    user_requirement = "写一个斐波那契数列的 Python 函数，返回前 n 项。"

    # 第一步：CoderAgent 生成初版代码
    coder_response = await coder.on_messages(
        [TextMessage(content=user_requirement, source="user")], CancellationToken()
    )
    code = coder_response.chat_message.to_text()
    print("CoderAgent 生成的代码：\n", code)

    # 第二步：ReviewerAgent 给出优化建议
    reviewer_response = await reviewer.on_messages(
        [TextMessage(content=f"请审查并优化如下代码：\n{code}", source="user")], CancellationToken()
    )
    suggestions = reviewer_response.chat_message.to_text()
    print("ReviewerAgent 优化建议：\n", suggestions)

    # 第三步：FinalizerAgent 输出最终代码
    finalizer_response = await finalizer.on_messages(
        [TextMessage(content=f"原始代码：\n{code}\n优化建议：\n{suggestions}\n请输出最终优化后的完整代码。", source="user")],
        CancellationToken()
    )
    final_code = finalizer_response.chat_message.to_text()
    print("FinalizerAgent 最终代码：\n", final_code)

    await model_client.close()

def run_main():
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    pass
                loop.run_until_complete(main())
            else:
                loop.run_until_complete(main())
        else:
            raise

if __name__ == "__main__":
    run_main()
