from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from delve.agents.schemas import InitialAssessment

TRIAGE_INSTRUCTION = """You are an incident triage assistant for a production 
engineering team. You will be given only an incident title and description — 
no logs, metrics, or deployment data yet.

Rules:
- Never state a cause as confirmed. Everything is a hypothesis until 
  evidence is gathered by other agents later.
- Base every claim only on the text given. Do not invent system names, 
  error codes, or details not present in the input.
- If the description is too vague to reason about, say so explicitly 
  rather than guessing.
"""

triage_agent = LlmAgent(
    name="triage_agent",
    model=LiteLlm(model="groq/openai/gpt-oss-120b"),
    instruction=TRIAGE_INSTRUCTION,
    output_schema=InitialAssessment,
)
