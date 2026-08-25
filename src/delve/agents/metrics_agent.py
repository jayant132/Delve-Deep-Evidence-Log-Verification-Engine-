from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from delve.tools.metrics_tools import get_metrics

_investigator = LlmAgent(
    name="metrics_investigator",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You are a metrics investigation agent for a production 
incident response system.

Known services: payment-service, auth-service, order-service.

Given an incident description, identify which service(s) are most likely 
affected, then call get_metrics for that service with metric="ALL". After 
the tool returns, write a short plain-text summary (not JSON) of the trend.
""",
    tools=[get_metrics],
)

_formatter = LlmAgent(
    name="metrics_formatter",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You will be given a previous agent's metrics investigation 
notes. Convert them into ONLY a single JSON object — no markdown, no code 
fences, no extra text — matching exactly:
{
  "service_investigated": "<service name>",
  "observed_data": ["<raw facts from the investigation notes>", ...],
  "anomaly_detected": <true or false>,
  "summary": "<interpretation, framed as a reading not a confirmed fact>"
}
""",
    output_key="metrics_findings",
)

metrics_agent = SequentialAgent(name="metrics_agent", sub_agents=[_investigator, _formatter])
