from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

class RequirementAgent:
    """
    需求分析Agent，基于AutoGen AssistantAgent实现。
    支持异步消息处理，便于多Agent协作。
    """
    def __init__(self,model_client):
        self.agent = AssistantAgent(
            name="RequirementAgent",
            system_message="你是需求分析专家，请将用户需求拆解为高内聚低耦合的开发任务列表。输出中文分点描述(需符合markdown语法)。",
            model_client=model_client,
            model_client_stream=True
        )

    async def handle_message(self, requirement: str) -> str:
        response = await self.agent.on_messages(
            [TextMessage(content=requirement, source="user")], CancellationToken()
        )
        return response.chat_message.to_text()

    async def handle_message_stream(self, requirement: str):
        # 使用on_messages_stream实现流式输出
        async for chunk in self.agent.on_messages_stream(
            [TextMessage(content=requirement, source="user")], CancellationToken()
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
        
        
        
