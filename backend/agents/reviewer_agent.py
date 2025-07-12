import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from typing import AsyncGenerator


class ReviewerAgent:
    """
    代码审查Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="ReviewerAgent",
            system_message="你是代码审查专家，请对给定的代码提出详细的优化建议。",
            model_client=model_client,
            model_client_stream=True
        )

    async def handle_message(self, code: str) -> str:
        response = await self.agent.on_messages(
            [TextMessage(content=f"请审查并优化如下代码：\n{code}", source="user")], CancellationToken()
        )
        return response.chat_message.to_text()

    async def handle_message_stream(self, code: str):
        # 使用on_messages_stream实现流式输出
        async for chunk in self.agent.on_messages_stream(
            [TextMessage(content=f"请审查并优化如下代码：\n{code}", source="user")], CancellationToken()
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
