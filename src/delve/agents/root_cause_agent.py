import asyncio
from typing import List, Literal

from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


class RootCauseAnalysis(BaseModel):
    root_cause_hypothesis: str = Field(
        description="The single most likely root cause, stated as a hypothesis, "
        "not a certainty. Must be traceable to specific evidence below."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="How strongly the combined evidence supports the hypothesis."
    )
    supporting_evidence: List[str] = Field(
        description="Specific facts drawn from the three agents' findings that "
        "support the hypothesis. Quote or closely paraphrase the original data points."
    )
    contradicting_or_unclear_evidence: List[str] = Field(
        default_factory=list,
        description="Anything in the findings that doesn't fit the hypothesis, "
        "is ambiguous, or where the three agents disagree. Empty list only if "
        "you genuinely found nothing.",
    )
    agents_in_agreement: bool = Field(
        description="True only if log, metrics, and deployment findings all "
        "point the same direction with no meaningful tension between them."
    )
    recommended_next_steps: List[str] = Field(
        description="Concrete actions an on-call engineer should take next, "
        "e.g. rollback, specific config to check, dashboards to watch."
    )


ROOT_CAUSE_AGENT_INSTRUCTION = """You are the root-cause synthesis agent in a
production incident response system. You do not have tools — your job is to
reason over evidence three specialist agents already gathered, not to gather
more.

LOG AGENT FINDINGS:
{log_findings}

METRICS AGENT FINDINGS:
{metrics_findings}

DEPLOYMENT AGENT FINDINGS:
{deployment_findings}

Your task:
1. Identify the single most likely root cause hypothesis, grounded ONLY in
   the observed_data fields above — never invent a fact that isn't present
   in one of the three findings.
2. Assess confidence honestly. If the evidence is circumstantial (e.g. a
   deployment happened before the incident but nothing directly proves it
   caused it), say so with "low" or "medium" confidence rather than
   overstating certainty.
3. Actively check whether the three agents' findings agree. Do not assume
   agreement — look for timing mismatches, findings that don't corroborate
   each other, or gaps where one agent found nothing relevant. Populate
   agents_in_agreement and contradicting_or_unclear_evidence honestly, even
   if that means reporting that everything lines up.
4. Recommend concrete next steps an on-call engineer could take right now.

Do not state the root cause as a proven fact. Frame it as the most likely
explanation given current evidence.
"""


async def wait_for_rate_limit_window(callback_context):
    await asyncio.sleep(6)
    return None

root_cause_agent = LlmAgent(
    name="root_cause_agent",
    model=LiteLlm(model="groq/openai/gpt-oss-120b", num_retries=5, include_reasoning=False),
    instruction=ROOT_CAUSE_AGENT_INSTRUCTION,
    output_schema=RootCauseAnalysis,
    output_key="root_cause_analysis",
    before_agent_callback=wait_for_rate_limit_window,
)
