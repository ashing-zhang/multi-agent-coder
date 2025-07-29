import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    async def lookup_hotel(location: str) -> str:
        return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

    async def lookup_flight(origin: str, destination: str) -> str:
        return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

    async def book_trip() -> str:
        return "Your trip is booked!"

    travel_advisor = AssistantAgent(
        "Travel_Advisor",
        model_client,
        tools=[book_trip],
        description="Helps with travel planning.",
    )
    hotel_agent = AssistantAgent(
        "Hotel_Agent",
        model_client,
        tools=[lookup_hotel],
        description="Helps with hotel booking.",
    )
    flight_agent = AssistantAgent(
        "Flight_Agent",
        model_client,
        tools=[lookup_flight],
        description="Helps with flight booking.",
    )
    termination = TextMentionTermination("TERMINATE")
    team = SelectorGroupChat(
        [travel_advisor, hotel_agent, flight_agent],
        model_client=model_client,
        termination_condition=termination,
    )
    await Console(team.run_stream(task="Book a 3-day trip to new york."))
asyncio.run(main())
