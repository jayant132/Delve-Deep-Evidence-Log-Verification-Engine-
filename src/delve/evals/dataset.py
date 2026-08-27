EVAL_CASES = [
    {
        "case_id": "CASE_001",
        "title": "Payment failures spiking",
        "description": "5xx error rate on payment service jumped from 0.2% to 18% about 10 minutes after latest deployment",
        "expected_service": "payment-service",
        "expected_root_cause_keywords": ["pool_size", "connection pool", "50", "5"],
        "expected_historical_match": "INC-0042",
        "expected_min_confidence": "medium",
    },
]
