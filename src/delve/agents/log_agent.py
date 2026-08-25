from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from delve.tools.log_tools import search_logs

_investigator = LlmAgent(
    name="log_investigator",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You are a log investigation agent for a production 
incident response system.

Known services: payment-service, auth-service, order-service.

Given an incident description, identify which service(s) are most likely 
affected, then call search_logs for that service (level="ALL" first, 
focus on WARN/ERROR in your notes). After the tool returns, write a short 
plain-text summary (not JSON) of what you found.
""",
    tools=[search_logs],
)

_formatter = LlmAgent(
    name="log_formatter",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", include_reasoning=False),
    instruction="""You will be given a previous agent's log investigation 
notes. Convert them into ONLY a single JSON object — no markdown, no code 
fences, no extra text — matching exactly:
{
  "service_investigated": "<service name>",
  "observed_data": ["<raw facts from the investigation notes>", ...],
  "anomaly_detected": <true or false>,
  "summary": "<interpretation, framed as a reading not a confirmed fact>"
}
""",
    output_key="log_findings",
)

log_agent = SequentialAgent(name="log_agent", sub_agents=[_investigator, _formatter])
