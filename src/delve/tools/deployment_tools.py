from datetime import datetime

from delve.data.simulated_deployments import DEPLOYMENTS


def get_deployment_changes(service: str, hours_back: int = 24) -> list[dict]:
    """Retrieve recent deployment history for a given service.

    Args:
        service: The service name to filter deployments for (e.g. "payment-service").
        hours_back: How many hours back from the most recent deployment to search.

    Returns:
        A list of matching deployments, each with timestamp, version, commit_sha, 
        author, and a summary of changes, ordered most-recent-first.
    """
    latest = max(datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")) for d in DEPLOYMENTS)
    cutoff = latest.timestamp() - (hours_back * 3600)

    results = [
        d for d in DEPLOYMENTS
        if d["service"] == service
        and datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")).timestamp() >= cutoff
    ]
    return sorted(results, key=lambda d: d["timestamp"], reverse=True)
