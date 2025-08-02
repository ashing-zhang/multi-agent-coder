import asyncio
from langchain_openai import ChatOpenAI
from langgraph_workflow import MultiNode

async def test_langgraph_workflow_async():
    # 创建LLM实例
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key="sk-09ef1979840d4761a31d959da730deb5",
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )
    
    # 创建MultiNode实例
    workflow = MultiNode(llm)
    await workflow.initialize()
    
    # 模拟用户需求
    user_requirement = "编写一个Python函数，计算斐波那契数列的第n项。"
    
    print(f"用户需求: {user_requirement}")
    print("开始处理...")
    
    # 运行工作流并获取响应
    async for chunk in workflow.handle_message_stream(user_requirement):
        if chunk:
            print(chunk, end='', flush=True)
    
    print("\n处理完成。")

if __name__ == "__main__":
    asyncio.run(test_langgraph_workflow_async())