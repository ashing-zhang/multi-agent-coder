import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain_openai import ChatOpenAI
from langgraph_workflow import LangGraphWorkflow

def test_mcp_tools():
    """测试异步初始化的LangGraphWorkflow中的MCP工具"""
    async def run_test():
        # 创建一个模拟的LLM实例
        llm = ChatOpenAI(api_key="your-api-key-here")
        
        # 实例化LangGraphWorkflow
        workflow = LangGraphWorkflow(llm)
        
        # 异步初始化
        await workflow.initialize()
        
        # 检查工具是否加载成功
        if workflow.tools:
            print("工具加载成功:")
            for tool in workflow.tools:
                print(f"  - {tool.name}")
        else:
            print("工具加载失败")
    
    # 运行异步测试
    asyncio.run(run_test())

if __name__ == "__main__":
    test_mcp_tools()