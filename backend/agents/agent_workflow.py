from .requirement_agent import RequirementAgent
from .coder_agent import CoderAgent
from .reviewer_agent import ReviewerAgent
from .finalizer_agent import FinalizerAgent
from .doc_agent import DocAgent
from .test_agent import TestAgent
from typing import AsyncGenerator

class AgentWorkflow:
    """
    多Agent协作工作流，将需求分析、代码生成、审查、整合、文档、测试等Agent串联为pipeline。
    支持异步调用。
    """
    def __init__(self, model_client):
        self.requirement_agent = RequirementAgent(model_client)
        self.coder_agent = CoderAgent(model_client)
        self.reviewer_agent = ReviewerAgent(model_client)
        self.finalizer_agent = FinalizerAgent(model_client)
        self.doc_agent = DocAgent(model_client)

    async def run(self, user_requirement: str) -> dict:
        # 1. 需求分析
        tasks = await self.requirement_agent.handle_message(user_requirement)
        if isinstance(tasks, str):
            tasks = [t for t in tasks.split("\n") if t.strip()]
        # 2. 针对每个任务生成代码
        codes = []
        for task in tasks:
            code = await self.coder_agent.handle_message(task)
            codes.append(code)
        # 3. 合并所有代码进行审查
        all_code = "\n\n".join(codes)
        suggestions = await self.reviewer_agent.handle_message(all_code)
        # 4. 代码整合
        final_code = await self.finalizer_agent.handle_message(all_code, suggestions)
        # 5. 文档生成
        doc = await self.doc_agent.handle_message(final_code)
    
        return {
            "final_code": final_code,
            "doc": doc
        }

    async def run_stream(self, user_requirement: str) -> AsyncGenerator[str, None]:
        task = await self.requirement_agent.handle_message(user_requirement)
        code = await self.coder_agent.handle_message(task)
        suggestions = await self.reviewer_agent.handle_message(code)
        yield "【代码】\n"
        async for token in self.finalizer_agent.handle_message_stream(code, suggestions):
            yield token
        final_code = await self.finalizer_agent.handle_message(code, suggestions)
        yield "\n\n【文档】\n"
        async for token in self.doc_agent.handle_message_stream(final_code):
            yield token
        
