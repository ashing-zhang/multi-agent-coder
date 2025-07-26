from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen import GroupChat, GroupChatManager
from .test_agent import TestAgent
from typing import AsyncGenerator, List
import asyncio

class AgentWorkflow:
    """
    使用AutoGen框架实现的多Agent协作工作流，支持人工介入和动态对话管理。
    """
    def __init__(self, model_client):
        # 配置LLM模型参数
        self.model_client = model_client
        llm_config = {
            "model": model_client.model,
            "api_key": model_client.api_key,
            "temperature": 0.7
        }

        # 创建专业Agent
        self.requirement_agent = AssistantAgent(
            name="requirement_agent",
            system_message="你是需求分析专家，负责将用户需求拆解为清晰的开发任务。",
            llm_config=llm_config
        )
        self.coder_agent = AssistantAgent(
            name="coder_agent",
            system_message="你是资深程序员，负责根据需求编写高质量代码。",
            llm_config=llm_config
        )
        self.reviewer_agent = AssistantAgent(
            name="reviewer_agent",
            system_message="你是代码审查专家，负责找出代码中的问题并提出改进建议。",
            llm_config=llm_config
        )
        self.finalizer_agent = AssistantAgent(
            name="finalizer_agent",
            system_message="你是代码整合专家，负责根据审查建议优化代码。",
            llm_config=llm_config
        )
        self.doc_agent = AssistantAgent(
            name="doc_agent",
            system_message="你是文档专家，负责为最终代码生成清晰的使用文档。",
            llm_config=llm_config
        )
        
        # 创建用户代理（支持人工介入）
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            system_message="人类用户的代理，负责传达需求和提供反馈。",
            human_input_mode="always",  # 始终请求人工输入
            is_termination_msg=lambda x: x.get("content", "").strip().endswith("terminate"),
            code_execution_config=False  # 禁用代码执行
        )

        # 创建群聊环境
        self.agents: List[AssistantAgent] = [
            self.requirement_agent, self.coder_agent, 
            self.reviewer_agent, self.finalizer_agent, self.doc_agent, self.test_agent
        ]
        self.group_chat = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin",  # 轮流向每个Agent提问
            allow_repeat_speaker=False
        )
        self.manager = GroupChatManager(groupchat=self.group_chat, llm_config=llm_config)

    async def run(self, user_requirement: str) -> dict:
        """
        运行AutoGen多Agent工作流
        :param user_requirement: 用户需求
        :return: 最终结果
        """
        # 启动群聊对话
        chat_result = await asyncio.to_thread(
            self.user_proxy.initiate_chat,
            self.manager,
            message=user_requirement,
            summary_method="reflection_with_llm"
        )

        # 提取对话摘要和结果
        return {
            'conversation': chat_result.chat_history,
            'summary': chat_result.summary,
            'final_code': self._extract_final_code(chat_result.chat_history),
            'test_code': self._extract_test_code(chat_result.chat_history)
        }

    async def run_stream(self, user_requirement: str) -> AsyncGenerator[dict, None]:
        """
        流式运行AutoGen多Agent工作流
        :param user_requirement: 用户需求
        :return: 流式结果
        """
        # 使用队列收集流式输出
        result_queue = asyncio.Queue()

        def callback(sender, message, recipient, request_id, **kwargs):
            result_queue.put_nowait({
                'stage': sender.name,
                'sender': sender.name,
                'message': message,
                'timestamp': asyncio.get_event_loop().time()
            })

        # 注册回调函数
        self.manager.register_callback(callback)

        # 在后台线程运行对话
        asyncio.create_task(
            asyncio.to_thread(
                self.user_proxy.initiate_chat,
                self.manager,
                message=user_requirement
            )
        )

        # 流式输出结果
        while True:
            try:
                result = await asyncio.wait_for(result_queue.get(), timeout=30)
                if result.get('stage') == 'terminate':
                    break
                yield result
            except asyncio.TimeoutError:
                break

    
        
