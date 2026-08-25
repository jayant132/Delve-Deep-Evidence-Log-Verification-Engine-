from datetime import datetime

from pydantic import BaseModel, ConfigDict

from delve.models.incident import IncidentStatus


class IncidentCreate(BaseModel):
    title: str
    description: str


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
