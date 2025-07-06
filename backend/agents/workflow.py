from .requirement_agent import RequirementAgent
from .coder_agent import CoderAgent
from .reviewer_agent import ReviewerAgent
from .finalizer_agent import FinalizerAgent
from .doc_agent import DocAgent
from .test_agent import TestAgent

class AgentWorkflow:
    """
    多Agent协作工作流，将需求分析、代码生成、审查、整合、文档、测试等Agent串联为pipeline。
    支持异步调用。
    """
    def __init__(self):
        self.requirement_agent = RequirementAgent()
        self.coder_agent = CoderAgent()
        self.reviewer_agent = ReviewerAgent()
        self.finalizer_agent = FinalizerAgent()
        self.doc_agent = DocAgent()
        self.test_agent = TestAgent()

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
        # 6. 测试生成
        test_code = await self.test_agent.handle_message(final_code)
        return {
            "tasks": tasks,
            "codes": codes,
            "suggestions": suggestions,
            "final_code": final_code,
            "doc": doc,
            "test_code": test_code
        }
