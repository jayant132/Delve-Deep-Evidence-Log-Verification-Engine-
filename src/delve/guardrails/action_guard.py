import re

HIGH_RISK_PATTERNS = [r"rollback", r"restart", r"redeploy", r"revert"]
CRITICAL_RISK_PATTERNS = [r"delete", r"drop table", r"truncate", r"database migration"]


def classify_action_risk(action_text: str) -> str:
    text = action_text.lower()
    if any(re.search(p, text) for p in CRITICAL_RISK_PATTERNS):
        return "critical"
    if any(re.search(p, text) for p in HIGH_RISK_PATTERNS):
        return "high"
    return "low"
