import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

def test_mcp_connection():
    """测试MCP Server连接和工具加载"""
    async def _test_async():
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@upstash/context7-mcp"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("MCP Server连接成功")
                await session.initialize()
                print("MCP Server初始化完成")
                tools = await load_mcp_tools(session)
                print(f"成功加载{len(tools)}个工具:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:50]}...")
                return tools
    
    try:
        # 创建新事件循环并运行测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tools = loop.run_until_complete(_test_async())
        print("\n测试完成，工具加载成功")
        return tools
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_mcp_connection()