import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from delve.agents.investigation_service import run_investigation
from delve.agents.triage_service import run_triage
from delve.db import SessionLocal
from delve.guardrails.input_guard import check_incident_input
from delve.models.evidence import Evidence
from delve.models.incident import Incident, IncidentStatus
from delve.schemas.evidence import EvidenceRead
from delve.schemas.incident import IncidentCreate, IncidentRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=IncidentRead, status_code=201)
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    check_incident_input(payload.title, payload.description)

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


@router.post("/{incident_id}/investigate", response_model=IncidentRead)
async def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident_text = f"Title: {incident.title}\nDescription: {incident.description}"
    try:
        results = await run_investigation(incident_text)
        incident.investigation_findings = {
            "log_findings": results["log_findings"],
            "metrics_findings": results["metrics_findings"],
            "deployment_findings": results["deployment_findings"],
            "historical_findings": results["historical_findings"],
        }
        incident.root_cause_analysis = results["root_cause_analysis"]

        for agent_key in ("log_findings", "metrics_findings", "deployment_findings", "historical_findings"):
            finding = results[agent_key]
            if not finding:
                continue
            service = finding.get("service_investigated", "unknown")
            for fact in finding.get("observed_data", []):
                db.add(Evidence(
                    incident_id=incident.id,
                    source_agent=agent_key.replace("_findings", "_agent"),
                    service=service,
                    content=fact,
                ))

        incident.status = IncidentStatus.HYPOTHESIS_FORMED
        db.commit()
        db.refresh(incident)
    except Exception:
        logger.exception("Investigation failed for incident %s", incident.id)

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


@router.get("/{incident_id}/evidence", response_model=list[EvidenceRead])
def list_evidence(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return (
        db.query(Evidence)
        .filter(Evidence.incident_id == incident_id)
        .order_by(Evidence.created_at)
        .all()
    )
