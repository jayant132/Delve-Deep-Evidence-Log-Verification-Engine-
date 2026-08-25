from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from delve.tools.deployment_tools import get_deployment_changes

_investigator = LlmAgent(
    name="deployment_investigator",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You are a deployment investigation agent for a production 
incident response system.

Known services: payment-service, auth-service, order-service.

Given an incident description, identify which service(s) are most likely 
affected, then call get_deployment_changes for that service with 
hours_back=24. After the tool returns, write a short plain-text summary 
(not JSON) of what you found and whether it looks related to the incident.
""",
    tools=[get_deployment_changes],
)

_formatter = LlmAgent(
    name="deployment_formatter",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You will be given a previous agent's deployment 
investigation notes. Convert them into ONLY a single JSON object — no 
markdown, no code fences, no extra text — matching exactly:
{
  "service_investigated": "<service name>",
  "observed_data": ["<raw facts from the investigation notes>", ...],
  "anomaly_detected": <true or false>,
  "summary": "<interpretation, framed as a reading not a confirmed fact>"
}
""",
    output_key="deployment_findings",
)

deployment_agent = SequentialAgent(
    name="deployment_agent",
    sub_agents=[_investigator, _formatter],
)
