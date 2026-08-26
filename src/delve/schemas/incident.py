from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from delve.models.incident import IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    triage_assessment: dict | None = None
    investigation_findings: dict | None = None
    root_cause_analysis: dict | None = None
