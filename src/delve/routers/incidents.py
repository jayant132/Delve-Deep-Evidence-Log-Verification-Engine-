import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from delve.agents.investigation_service import run_investigation
from delve.agents.triage_service import run_triage
from delve.db import SessionLocal
from delve.guardrails.action_guard import classify_action_risk
from delve.guardrails.evidence_guard import check_evidence_grounding
from delve.guardrails.input_guard import check_incident_input
from delve.models.action import Action
from delve.models.evidence import Evidence
from delve.models.execution_log import ExecutionLog
from delve.models.execution_log import ExecutionLog as _ExecLog
from delve.models.incident import Incident, IncidentStatus
from delve.schemas.action import ActionRead
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
    t0 = time.monotonic()
    try:
        assessment = await run_triage(incident_text)
        incident.triage_assessment = assessment.model_dump()
        incident.status = IncidentStatus.INVESTIGATING
        db.add(ExecutionLog(incident_id=incident.id, step_name="triage", status="success", duration_seconds=time.monotonic() - t0))
        db.commit()
        db.refresh(incident)
    except Exception as e:
        db.add(ExecutionLog(incident_id=incident.id, step_name="triage", status="failed", duration_seconds=time.monotonic() - t0, error_message=str(e)))
        db.commit()
        logger.exception("Triage failed for incident %s", incident.id)

    return incident


@router.post("/{incident_id}/investigate", response_model=IncidentRead)
async def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident_text = f"Title: {incident.title}\nDescription: {incident.description}"
    t0 = time.monotonic()
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

        all_facts = []
        for k in ("log_findings", "metrics_findings", "deployment_findings", "historical_findings"):
            f = results.get(k)
            if f:
                all_facts.extend(f.get("observed_data", []))
        flagged = check_evidence_grounding(incident.root_cause_analysis, all_facts)
        if flagged:
            logger.warning("Ungrounded evidence claims in incident %s: %s", incident.id, flagged)

        for step in incident.root_cause_analysis.get("recommended_next_steps", []):
            db.add(Action(
                incident_id=incident.id,
                description=step,
                risk_level=classify_action_risk(step),
            ))

        incident.status = IncidentStatus.AWAITING_APPROVAL
        db.commit()
        db.refresh(incident)
        db.add(ExecutionLog(incident_id=incident.id, step_name="investigation", status="success", duration_seconds=time.monotonic() - t0))
        db.commit()
    except Exception as e:
        db.add(ExecutionLog(incident_id=incident.id, step_name="investigation", status="failed", duration_seconds=time.monotonic() - t0, error_message=str(e)))
        db.commit()
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


@router.get("/{incident_id}/actions", response_model=list[ActionRead])
def list_actions(incident_id: str, db: Session = Depends(get_db)):
    return db.query(Action).filter(Action.incident_id == incident_id).all()


@router.post("/actions/{action_id}/approve", response_model=ActionRead)
def approve_action(action_id: str, db: Session = Depends(get_db)):
    action = db.query(Action).filter(Action.id == action_id).first()
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = "approved_simulated_executed"
    db.commit()
    db.refresh(action)
    return action


@router.get("/{incident_id}/logs")
def list_execution_logs(incident_id: str, db: Session = Depends(get_db)):
    logs = db.query(_ExecLog).filter(_ExecLog.incident_id == incident_id).all()
    return [{"step": l.step_name, "status": l.status, "duration_s": round(l.duration_seconds, 2), "error": l.error_message} for l in logs]
