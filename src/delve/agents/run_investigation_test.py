from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import re

from litellm.exceptions import RateLimitError

from google.adk.runners import InMemoryRunner
from google.genai import types

from delve.agents.investigation_team import investigation_team


MAX_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 30


def parse_findings(raw) -> dict | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def contains_rate_limit_error(exc: BaseException) -> bool:
    """Check if exc, or anything nested inside it (e.g. an ExceptionGroup
    from parallel_agent's TaskGroup), is a RateLimitError."""
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, BaseExceptionGroup):
        return any(contains_rate_limit_error(e) for e in exc.exceptions)
    return False


async def run_with_retry(runner, user_id, session_id, new_message):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=new_message
            ):
                if event.is_final_response() and event.author:
                    print(f"--- {event.author} finished ---")
            return
        except BaseException as e:
            if not contains_rate_limit_error(e):
                raise
            if attempt == MAX_ATTEMPTS:
                print(f"Rate limited on final attempt ({attempt}/{MAX_ATTEMPTS}), giving up.")
                raise
            print(
                f"Rate limited (attempt {attempt}/{MAX_ATTEMPTS}), "
                f"waiting {RETRY_WAIT_SECONDS}s..."
            )
            await asyncio.sleep(RETRY_WAIT_SECONDS)


async def main():
    runner = InMemoryRunner(agent=investigation_team, app_name="delve")
    session = await runner.session_service.create_session(app_name="delve", user_id="test_user")

    incident_text = (
        "Title: Payment failures spiking\n"
        "Description: 5xx error rate on the payment service jumped from "
        "0.2% to 18% about 10 minutes after the latest deployment finished."
    )

    await run_with_retry(
        runner=runner,
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=incident_text)]),
    )

    final_session = await runner.session_service.get_session(
        app_name="delve", user_id="test_user", session_id=session.id
    )
    print("\n=== SHARED SESSION STATE (parsed) ===")
    for key in ("log_findings", "metrics_findings", "deployment_findings", "root_cause_analysis"):
        raw = final_session.state.get(key)
        print(f"\n[{key}]")
        try:
            print(json.dumps(parse_findings(raw), indent=2))
        except (json.JSONDecodeError, TypeError) as e:
            print(f"PARSE FAILED: {e}\nRAW: {raw}")


asyncio.run(main())