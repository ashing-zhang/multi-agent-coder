import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from typing import AsyncGenerator


class TestAgent:
    """
    测试Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="TestAgent",
            system_message="你是单元测试专家，请为给定的Python代码生成高质量的pytest风格单元测试代码。",
            model_client=model_client,
            model_client_stream=True
        )

    async def handle_message(self, code: str) -> str:
        response = await self.agent.on_messages(
            [TextMessage(content=f"请为如下代码生成pytest单元测试：\n{code}", source="user")], CancellationToken()
        )
        return response.chat_message.to_text()

    async def handle_message_stream(self, code: str):
        # 使用on_messages_stream实现流式输出
        async for chunk in self.agent.on_messages_stream(
            [TextMessage(content=f"请为如下代码生成pytest单元测试：\n{code}", source="user")], CancellationToken()
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
