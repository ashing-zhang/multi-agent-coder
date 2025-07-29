import asyncio
from backend.agents.agent_workflow import AgentWorkflow
from autogen_ext.models.openai import OpenAIChatCompletion

async def main():
    # Initialize the model client
    model_client = OpenAIChatCompletion(
        model="gpt-4",
        api_key="YOUR_API_KEY_HERE"  # Replace with your actual API key
    )
    
    # Initialize the workflow
    async with AgentWorkflow(model_client) as workflow:
        # Run a simple test
        async for chunk in workflow.run_stream("Write a simple 'Hello, World!' program in Python."):
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())