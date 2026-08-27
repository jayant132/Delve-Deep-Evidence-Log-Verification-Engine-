import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from delve.db import Base


class IncidentStatus(str, enum.Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    HYPOTHESIS_FORMED = "hypothesis_formed"
    AWAITING_APPROVAL = "awaiting_approval"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.DETECTED, nullable=False
    
    )
    triage_assessment: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    investigation_findings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    root_cause_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )