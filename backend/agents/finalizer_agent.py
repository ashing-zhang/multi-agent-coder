import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from typing import AsyncGenerator


class FinalizerAgent:
    """
    代码整合Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="FinalizerAgent",
            system_message="你是代码整合专家，请结合原始代码和优化建议，输出最终优化后的完整代码。",
            model_client=model_client,
            model_client_stream=True
        )

    async def handle_message(self, code: str, suggestions: str) -> str:
        prompt = f"原始代码：\n{code}\n优化建议：\n{suggestions}\n请输出最终优化后的完整代码。"
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")], CancellationToken()
        )
        return response.chat_message.to_text()

    async def handle_message_stream(self, code: str, suggestions: str):
        prompt = f"原始代码：\n{code}\n优化建议：\n{suggestions}\n请输出最终优化后的完整代码。"
        # 使用on_messages_stream实现流式输出
        async for chunk in self.agent.on_messages_stream(
            [TextMessage(content=prompt, source="user")], CancellationToken()
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
