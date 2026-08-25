from dotenv import load_dotenv
load_dotenv()

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from delve.agents.triage_agent import triage_agent


async def main():
    runner = InMemoryRunner(agent=triage_agent, app_name="delve")
    session = await runner.session_service.create_session(
        app_name="delve", user_id="test_user"
    )

    incident_text = (
        "Title: Payment failures spiking\n"
        "Description: 5xx error rate on the payment service jumped from "
        "0.2% to 18% about 10 minutes after the latest deployment finished."
    )

    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=incident_text)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text and not getattr(part, "thought", False):
                    print(part.text)


asyncio.run(main())
