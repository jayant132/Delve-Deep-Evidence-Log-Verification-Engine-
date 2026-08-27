from datetime import datetime, timezone

from delve.data.simulated_logs import LOGS
from delve.guardrails.tool_guard import check_service_allowed


def search_logs(service: str, level: str = "ALL", minutes_back: int = 60) -> list[dict]:
    """Search application logs for a given service within a recent time window.

    Args:
        service: The service name to filter logs for (e.g. "payment-service").
        level: Minimum log level to include: "INFO", "WARN", "ERROR", or "ALL".
        minutes_back: How many minutes back from the most recent log entry to search.

    Returns:
        A list of matching log entries, each with timestamp, service, level, and message.
    """
    check_service_allowed(service)
    level_order = {"INFO": 0, "WARN": 1, "ERROR": 2}
    min_level = level_order.get(level, -1) if level != "ALL" else -1

    latest = max(datetime.fromisoformat(l["timestamp"].replace("Z", "+00:00")) for l in LOGS)
    cutoff = latest.timestamp() - (minutes_back * 60)

    results = []
    for entry in LOGS:
        entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        if entry["service"] != service:
            continue
        if entry_time.timestamp() < cutoff:
            continue
        if level_order.get(entry["level"], -1) < min_level:
            continue
        results.append(entry)

    return results

