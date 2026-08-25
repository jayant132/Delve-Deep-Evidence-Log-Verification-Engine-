from google.adk.runners import InMemoryRunner
from google.genai import types

from delve.agents.schemas import InitialAssessment
from delve.agents.triage_agent import triage_agent


async def run_triage(incident_text: str) -> InitialAssessment:
    runner = InMemoryRunner(agent=triage_agent, app_name="delve")
    session = await runner.session_service.create_session(app_name="delve", user_id="system")

    result_text = None
    async for event in runner.run_async(
        user_id="system",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=incident_text)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text and not getattr(part, "thought", False):
                    result_text = part.text

    if result_text is None:
        raise RuntimeError("Triage agent returned no final response")

    return InitialAssessment.model_validate_json(result_text)
