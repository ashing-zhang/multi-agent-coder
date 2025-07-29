import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

async def main() -> None:
    params = StdioServerParams(
        command="uvx",
        args=["mcp-server-fetch"],
        read_timeout_seconds=60,
    )

    # You can also use `start()` and `stop()` to manage the session.
    async with McpWorkbench(server_params=params) as workbench:
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        assistant = AssistantAgent(
            name="Assistant",
            model_client=model_client,
            workbench=workbench,
            reflect_on_tool_use=True,
        )
        await Console(
            assistant.run_stream(task="Go to https://github.com/microsoft/autogen and tell me what you see.")
        )
asyncio.run(main())
