LOGS = [
    # --- payment-service: normal, before deploy ---
    {"timestamp": "2026-08-25T13:55:00Z", "service": "payment-service", "level": "INFO",
     "message": "Payment processed successfully for order_id=88213"},
    {"timestamp": "2026-08-25T13:58:00Z", "service": "payment-service", "level": "INFO",
     "message": "Health check passed"},

    # --- deployment event ---
    {"timestamp": "2026-08-25T14:00:00Z", "service": "payment-service", "level": "INFO",
     "message": "Deployment v2.4.1 completed, service restarted"},

    # --- degradation begins ---
    {"timestamp": "2026-08-25T14:03:12Z", "service": "payment-service", "level": "WARN",
     "message": "DB connection pool utilization at 92% (pool_size=5)"},
    {"timestamp": "2026-08-25T14:07:45Z", "service": "payment-service", "level": "ERROR",
     "message": "TimeoutError: could not obtain DB connection from pool within 3000ms"},
    {"timestamp": "2026-08-25T14:08:10Z", "service": "payment-service", "level": "ERROR",
     "message": "TimeoutError: could not obtain DB connection from pool within 3000ms"},
    {"timestamp": "2026-08-25T14:09:30Z", "service": "payment-service", "level": "ERROR",
     "message": "Request failed: 503 Service Unavailable, order_id=88240"},
    {"timestamp": "2026-08-25T14:10:00Z", "service": "payment-service", "level": "ERROR",
     "message": "DB connection pool exhausted, pool_size=5, active=5, waiting=42"},

    # --- unrelated noise: auth-service, normal ---
    {"timestamp": "2026-08-25T14:02:00Z", "service": "auth-service", "level": "INFO",
     "message": "User login successful, user_id=5521"},
    {"timestamp": "2026-08-25T14:06:00Z", "service": "auth-service", "level": "INFO",
     "message": "Token refresh successful, user_id=9012"},

    # --- unrelated noise: order-service, normal ---
    {"timestamp": "2026-08-25T14:04:00Z", "service": "order-service", "level": "INFO",
     "message": "Order created, order_id=88239"},
    {"timestamp": "2026-08-25T14:09:00Z", "service": "order-service", "level": "WARN",
     "message": "Order confirmation email delayed, retrying"},
]
