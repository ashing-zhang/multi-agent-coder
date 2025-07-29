import asyncio
from langchain_openai import ChatOpenAI
from langgraph_workflow import LangGraphWorkflow

def test_langgraph_workflow():
    # 创建LLM实例
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key="sk-09ef1979840d4761a31d959da730deb5",
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )
    
    # 创建LangGraphWorkflow实例
    workflow = LangGraphWorkflow(llm)
    
    # 检查是否加载了工具
    if hasattr(workflow, 'tools') and workflow.tools:
        print("成功加载以下工具:")
        for tool in workflow.tools:
            print(f"  - {tool.name}")
    else:
        print("未能加载工具")

if __name__ == "__main__":
    test_langgraph_workflow()