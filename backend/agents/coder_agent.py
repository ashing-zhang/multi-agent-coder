import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


class CoderAgent:
    """
    代码生成Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="CoderAgent",
            system_message="你是一个代码生成专家，根据用户需求编写高质量的 Python 代码。",
            model_client=model_client,
        )

    async def handle_message(self, task: str) -> str:
        """
        根据任务描述生成代码，调用AutoGen Agent。
        """
        response = await self.agent.on_messages(
            [TextMessage(content=task, source="user")], CancellationToken()
        )
        return response.chat_message.to_text()
