import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from typing import AsyncGenerator


class DocAgent:
    """
    文档Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="DocAgent",
            system_message="你是一个开发文档专家，根据给定的代码生成高质量的中文开发文档（包括函数说明、参数、返回值、用法示例等）。",
            model_client=model_client,
            model_client_stream=True
        )

    async def handle_message(self, code: str) -> str:
        """
        根据代码生成文档，调用AutoGen Agent。
        """
        response = await self.agent.on_messages(
            [TextMessage(content=f"请为如下代码生成详细中文开发文档：\n{code}", source="user")], CancellationToken()
        )
        return response.chat_message.to_text()

    async def handle_message_stream(self, code: str):
        # 使用on_messages_stream实现流式输出
        async for chunk in self.agent.on_messages_stream(
            [TextMessage(content=f"请为如下代码生成详细中文开发文档：\n{code}", source="user")], CancellationToken()
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
