from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    incident_id: str
    description: str
    risk_level: str
    status: str
    created_at: datetime
