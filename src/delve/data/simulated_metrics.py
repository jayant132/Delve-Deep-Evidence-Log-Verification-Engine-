METRICS = [
    # payment-service — before deploy (healthy baseline)
    {"timestamp": "2026-08-25T13:55:00Z", "service": "payment-service", "metric": "error_rate_pct", "value": 0.2},
    {"timestamp": "2026-08-25T13:55:00Z", "service": "payment-service", "metric": "p99_latency_ms", "value": 120},
    {"timestamp": "2026-08-25T13:55:00Z", "service": "payment-service", "metric": "db_pool_utilization_pct", "value": 18},

    # payment-service — after deploy, degrading
    {"timestamp": "2026-08-25T14:03:00Z", "service": "payment-service", "metric": "error_rate_pct", "value": 1.1},
    {"timestamp": "2026-08-25T14:03:00Z", "service": "payment-service", "metric": "p99_latency_ms", "value": 340},
    {"timestamp": "2026-08-25T14:03:00Z", "service": "payment-service", "metric": "db_pool_utilization_pct", "value": 92},

    {"timestamp": "2026-08-25T14:07:00Z", "service": "payment-service", "metric": "error_rate_pct", "value": 9.4},
    {"timestamp": "2026-08-25T14:07:00Z", "service": "payment-service", "metric": "p99_latency_ms", "value": 2800},
    {"timestamp": "2026-08-25T14:07:00Z", "service": "payment-service", "metric": "db_pool_utilization_pct", "value": 100},

    {"timestamp": "2026-08-25T14:10:00Z", "service": "payment-service", "metric": "error_rate_pct", "value": 18.0},
    {"timestamp": "2026-08-25T14:10:00Z", "service": "payment-service", "metric": "p99_latency_ms", "value": 5200},
    {"timestamp": "2026-08-25T14:10:00Z", "service": "payment-service", "metric": "db_pool_utilization_pct", "value": 100},

    # auth-service — unrelated, stays healthy throughout
    {"timestamp": "2026-08-25T14:03:00Z", "service": "auth-service", "metric": "error_rate_pct", "value": 0.1},
    {"timestamp": "2026-08-25T14:07:00Z", "service": "auth-service", "metric": "error_rate_pct", "value": 0.1},
    {"timestamp": "2026-08-25T14:10:00Z", "service": "auth-service", "metric": "error_rate_pct", "value": 0.15},
]
