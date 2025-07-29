import asyncio
from backend.agents.agent_workflow import AgentWorkflow
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

async def test_full_workflow():
    # Initialize the model client (you'll need to set your API key)
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize the workflow
    async with AgentWorkflow(model_client) as workflow:
        # Run a simple task
        task = "Write a simple Python function to calculate the factorial of a number."
        
        print("Starting workflow...")
        async for chunk in workflow.run_stream(task):
            print(chunk, end="", flush=True)
        print("\nWorkflow completed.")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())