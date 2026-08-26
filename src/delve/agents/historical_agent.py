from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

from delve.rag.retrieval_tool import search_historical_incidents

_investigator = LlmAgent(
    name="historical_investigator",
    model=LiteLlm(model="groq/openai/gpt-oss-20b", include_reasoning=False),
    instruction="""You are a historical incident retrieval agent for a 
production incident response system.

Given a new incident's title and description, call 
search_historical_incidents with the incident text as the query. Review 
the returned postmortems and write a short plain-text summary (not JSON) 
of whether any past incident closely matches this one — same failure 
pattern, not just same service. Name the specific incident file (e.g. 
INC-0042) if there is a strong match, and explain what makes it similar 
or different.
""",
    tools=[search_historical_incidents],
)

_formatter = LlmAgent(
    name="historical_formatter",
    model=LiteLlm(model="groq/openai/gpt-oss-20b", include_reasoning=False),
    instruction="""You will be given a previous agent's historical incident 
review notes. Convert them into ONLY a single JSON object — no markdown, 
no code fences, no extra text — matching exactly:
{
  "service_investigated": "<service name from the current incident>",
  "observed_data": ["<specific facts from matched postmortem(s), e.g. incident id and what happened>", ...],
  "anomaly_detected": <true if a strong historical match was found, false if none found>,
  "summary": "<whether this incident matches a known pattern, and which one, framed as a reading not confirmed fact>"
}
If no relevant historical incident was found, observed_data should be an 
empty list and summary should say so plainly.
""",
    output_key="historical_findings",
)

historical_agent = SequentialAgent(
    name="historical_agent", sub_agents=[_investigator, _formatter]
)
