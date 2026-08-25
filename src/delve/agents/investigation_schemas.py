from pydantic import BaseModel, Field


class InvestigationFindings(BaseModel):
    service_investigated: str = Field(description="The exact service name queried, e.g. 'payment-service'")
    observed_data: list[str] = Field(description="Raw, factual data points returned by the tool — no interpretation")
    anomaly_detected: bool = Field(description="Whether the data shows something outside normal/healthy behavior")
    summary: str = Field(description="Brief interpretation of what the observed data suggests — clearly your reading, not a confirmed fact")
