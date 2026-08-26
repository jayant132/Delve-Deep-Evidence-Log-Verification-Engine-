import asyncio
import json
import re

from litellm.exceptions import RateLimitError

from google.adk.runners import InMemoryRunner
from google.genai import types

from delve.agents.investigation_team import investigation_team

FINDING_KEYS = (
    "log_findings",
    "metrics_findings",
    "deployment_findings",
    "root_cause_analysis",
)

MAX_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 60


def _parse_state_value(raw):
    """Log/metrics/deployment agents write raw JSON text; root_cause_agent
    writes a dict directly (ADK auto-parses output_schema results)."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def _contains_rate_limit_error(exc: BaseException) -> bool:
    """Check if exc, or anything nested inside it (e.g. an ExceptionGroup
    from parallel_agent's TaskGroup), is a RateLimitError."""
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, BaseExceptionGroup):
        return any(_contains_rate_limit_error(e) for e in exc.exceptions)
    return False


async def run_investigation(incident_text: str) -> dict:
    runner = InMemoryRunner(agent=investigation_team, app_name="delve")
    session = await runner.session_service.create_session(app_name="delve", user_id="system")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async for _event in runner.run_async(
                user_id="system",
                session_id=session.id,
                new_message=types.Content(role="user", parts=[types.Part(text=incident_text)]),
            ):
                pass  # we only need final session state, not per-event content
            break
        except BaseException as e:
            if not _contains_rate_limit_error(e):
                raise
            if attempt == MAX_ATTEMPTS:
                raise
            await asyncio.sleep(RETRY_WAIT_SECONDS)

    final_session = await runner.session_service.get_session(
        app_name="delve", user_id="system", session_id=session.id
    )

    results = {}
    for key in FINDING_KEYS:
        raw = final_session.state.get(key)
        results[key] = _parse_state_value(raw)

    if results["root_cause_analysis"] is None:
        raise RuntimeError("Investigation team returned no root cause analysis")

    return results
