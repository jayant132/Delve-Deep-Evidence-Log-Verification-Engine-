import json
import re

from google.adk.runners import InMemoryRunner
from google.genai import types

from delve.agents.investigation_team import investigation_team

FINDING_KEYS = (
    "log_findings",
    "metrics_findings",
    "deployment_findings",
    "root_cause_analysis",
)


def _parse_state_value(raw):
    """Log/metrics/deployment agents write raw JSON text; root_cause_agent
    writes a dict directly (ADK auto-parses output_schema results)."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


async def run_investigation(incident_text: str) -> dict:
    runner = InMemoryRunner(agent=investigation_team, app_name="delve")
    session = await runner.session_service.create_session(app_name="delve", user_id="system")

    async for _event in runner.run_async(
        user_id="system",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=incident_text)]),
    ):
        pass  # we only need final session state, not per-event content

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
