import asyncio
from backend.agents.agent_workflow import AgentWorkflow
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

async def test_candidate_function():
    # Initialize the model client (you'll need to set your API key)
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize the workflow
    async with AgentWorkflow(model_client) as workflow:
        # Test the candidate function with a mock context
        # This is a simplified test - in practice, the context would be provided by the SelectorGroupChat
        mock_context = [
            type('MockMessage', (), {'source': 'requirement_agent'})()
        ]
        
        # Get the candidate function
        candidate_func = workflow.team.candidate_func
        
        # Test with string source
        next_agents = candidate_func(mock_context)
        print(f"Next agents: {[agent.name for agent in next_agents]}")

if __name__ == "__main__":
    asyncio.run(test_candidate_function())