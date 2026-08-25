from pydantic import BaseModel, Field


class PossibleCause(BaseModel):
    description: str = Field(description="A specific possible cause, stated as a hypothesis")
    confidence: str = Field(description="One of: low, medium, high — never 'confirmed'")
    reasoning: str = Field(description="Why this is plausible, based only on the incident text given")


class InitialAssessment(BaseModel):
    summary: str = Field(description="Neutral one-sentence restatement of the incident")
    likely_affected_systems: list[str] = Field(description="Systems the description suggests are involved")
    possible_causes: list[PossibleCause] = Field(description="Ranked hypotheses, NOT confirmed root causes")
    severity_guess: str = Field(description="One of: low, medium, high, critical")
    needs_investigation: list[str] = Field(description="What evidence would confirm or rule out each cause")
