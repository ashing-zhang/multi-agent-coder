from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
# 框架的mcp模块完成了JSON RPC的功能，使用户不用关心JSON RPC的细节，只需要关注业务逻辑。
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench
from .test_agent import TestAgent
from typing import AsyncGenerator, List
import asyncio

class AgentWorkflow:
    """
    AgentWorkflow 是一个异步上下文管理器，因为它实现了 __aenter__ 和 __aexit__ 方法。
    使用 AutoGen 框架实现的多 Agent 协作工作流，不支持人工介入。
    """
    def __init__(self, model_client, llm=None):
        # 配置LLM模型参数
        self.model_client = model_client
        self.llm = llm
        # 检查npx是否可用，如果不可用则使用备用配置
        try:
            import subprocess
            subprocess.run(['npx', '--version'], capture_output=True, check=True)
            self.server_params = StdioServerParams(
                command='npx',
                args=['-y','@upstash/context7-mcp']
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果npx不可用，使用备用MCP服务器配置
            # 这里可以配置一个本地的MCP服务器或者其他替代方案
            print("警告: npx不可用，使用备用MCP配置")
            self.server_params = None
        self.mcp_workbench = None
        
    async def __aenter__(self):
        """异步上下文管理器入口，初始化MCP工作台"""
        self.mcp_workbench = McpWorkbench(server_params=self.server_params)
        await self.mcp_workbench.__aenter__()
        
        # 创建专业Agent
        self.requirement_agent = AssistantAgent(
            name="requirement_agent",
            system_message="你是需求分析专家，负责将用户需求拆解为清晰的开发任务。",
            model_client=self.model_client,
            workbench=self.mcp_workbench
        )
        self.coder_agent = AssistantAgent(
            name="coder_agent",
            system_message="你是资深程序员，负责根据需求编写高质量代码。",
            model_client=self.model_client,
            workbench=self.mcp_workbench
        )
        self.reviewer_agent = AssistantAgent(
            name="reviewer_agent",
            system_message="你是代码审查专家，负责找出代码中的问题并提出改进建议。",
            model_client=self.model_client,
            workbench=self.mcp_workbench
        )
        self.finalizer_agent = AssistantAgent(
            name="finalizer_agent",
            system_message="你是代码整合专家，负责根据审查建议优化代码。",
            model_client=self.model_client,
            workbench=self.mcp_workbench
        )
        self.doc_agent = AssistantAgent(
            name="doc_agent",
            system_message="你是文档专家，负责为最终代码生成清晰的使用文档。",
            model_client=self.model_client,
            workbench=self.mcp_workbench
        )
        
        # 移除了用户代理（不支持人工介入）

        # 创建群聊环境
        self.agents: List[AssistantAgent] = [
            self.requirement_agent, self.coder_agent, 
            self.reviewer_agent, self.finalizer_agent, self.doc_agent
        ]
        # 定义Agent之间的流向规则
        allowed_transitions = {
            self.requirement_agent: [self.coder_agent],
            self.coder_agent: [self.reviewer_agent],
            self.reviewer_agent: [self.finalizer_agent],
            self.finalizer_agent: [self.doc_agent],
            self.doc_agent: [self.doc_agent]  # doc_agent是最终节点，不流向其他Agent
        }
        
        # 定义候选函数，根据allowed_transitions确定下一个Agent
        def candidate_func(context) -> List[AssistantAgent]:
            if not context:
                return [self.requirement_agent]
                
            last_speaker = context[-1].source
            # 检查last_speaker的类型，如果是字符串则直接使用，否则获取其name属性
            if isinstance(last_speaker, str):
                print(f"当前发言者: {last_speaker}")
                # 根据名称找到对应的agent对象
                speaker_agent = next((agent for agent in self.agents if agent.name == last_speaker), self.requirement_agent)
            else:
                print(f"当前发言者: {last_speaker.name}")
                speaker_agent = last_speaker
            return allowed_transitions.get(speaker_agent, [self.requirement_agent])
        
        # 导入StopMessageTermination
        from autogen_agentchat.conditions import StopMessageTermination
        
        # 实例化StopMessageTermination作为终止条件
        self.termination_condition = StopMessageTermination()

        self.team = SelectorGroupChat(
            participants=self.agents,
            model_client=self.model_client,
            model_client_streaming=True,
            candidate_func=candidate_func,  # 传递自定义的候选函数
            termination_condition=self.termination_condition,  # 传递终止条件实例
        )
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口，清理MCP工作台"""
        if self.mcp_workbench:
            await self.mcp_workbench.__aexit__(exc_type, exc_val, exc_tb)

    async def run_stream(self, user_requirement: str) -> AsyncGenerator[str, None]:
        """
        流式运行AutoGen多Agent工作流，实现token级别流式输出
        :param user_requirement: 用户需求
        :return: 流式结果
        """
        print('Starting team.run_stream')
        # run_stream：return -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]
        async for response_event in self.team.run_stream(task=user_requirement,output_task_messages=False):
            # 检查是否为StopMessage，如果是则终止流式输出
            from autogen_core.messages import StopMessage
            if isinstance(response_event, StopMessage):
                print("✅ 流程终止：收到StopMessage")
                break
            
            # 处理不同类型的流式输出项
            print('type of response_event:',type(response_event))
            if hasattr(response_event, 'messages'):
                # 如果是TaskResult，迭代其消息
                for message in response_event.messages:
                    if hasattr(message, 'content'):
                        yield message.content
                    else:
                        yield str(message)
            else:
                # 单个事件（BaseAgentEvent或BaseChatMessage）
                if hasattr(response_event, 'content'):
                    yield response_event.content
                else:
                    yield str(response_event)
    
    def _extract_final_code(self, chat_history):
        # 实现代码提取逻辑
        pass
        
    def _extract_test_code(self, chat_history):
        # 实现测试代码提取逻辑
        pass

    
        
