import logging

from delve.agents.triage_service import run_triage
from delve.models.incident import IncidentStatus

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from delve.db import SessionLocal
from delve.models.incident import Incident
from delve.schemas.incident import IncidentCreate, IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=IncidentRead, status_code=201)
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(title=payload.title, description=payload.description)
    db.add(incident)
    db.commit()
    db.refresh(incident)

    incident_text = f"Title: {incident.title}\nDescription: {incident.description}"
    try:
        assessment = await run_triage(incident_text)
        incident.triage_assessment = assessment.model_dump()
        incident.status = IncidentStatus.INVESTIGATING
        db.commit()
        db.refresh(incident)
    except Exception:
        logger.exception("Triage failed for incident %s", incident.id)

    return incident

@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
