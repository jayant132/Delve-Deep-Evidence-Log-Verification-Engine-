DEPLOYMENTS = [
    {
        "timestamp": "2026-08-25T14:00:00Z",
        "service": "payment-service",
        "version": "v2.4.1",
        "commit_sha": "a1b2c3d",
        "author": "j.smith",
        "changes_summary": "Refactored DB connection pooling config; reduced pool_size from 50 to 5",
    },
    {
        "timestamp": "2026-08-25T09:15:00Z",
        "service": "auth-service",
        "version": "v1.9.0",
        "commit_sha": "e4f5g6h",
        "author": "m.patel",
        "changes_summary": "Added rate limiting to login endpoint",
    },
    {
        "timestamp": "2026-08-24T16:30:00Z",
        "service": "order-service",
        "version": "v3.2.0",
        "commit_sha": "i7j8k9l",
        "author": "j.smith",
        "changes_summary": "Updated order confirmation email template",
    },
]
