from datetime import datetime

from delve.data.simulated_metrics import METRICS


def get_metrics(service: str, metric: str = "ALL", minutes_back: int = 60) -> list[dict]:
    """Retrieve time-series metrics for a given service within a recent time window.

    Args:
        service: The service name to filter metrics for (e.g. "payment-service").
        metric: Specific metric name to filter by (e.g. "error_rate_pct", 
            "p99_latency_ms", "db_pool_utilization_pct"), or "ALL" for every metric.
        minutes_back: How many minutes back from the most recent data point to search.

    Returns:
        A list of matching metric data points, each with timestamp, service, 
        metric name, and value, ordered chronologically.
    """
    latest = max(datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) for m in METRICS)
    cutoff = latest.timestamp() - (minutes_back * 60)

    results = [
        m for m in METRICS
        if m["service"] == service
        and (metric == "ALL" or m["metric"] == metric)
        and datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).timestamp() >= cutoff
    ]
    return sorted(results, key=lambda m: m["timestamp"])
