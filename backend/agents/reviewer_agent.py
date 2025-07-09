import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


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
        )

    async def handle_message(self, code: str) -> str:
        response = await self.agent.on_messages(
            [TextMessage(content=f"请审查并优化如下代码：\n{code}", source="user")], CancellationToken()
        )
        return response.chat_message.to_text()
