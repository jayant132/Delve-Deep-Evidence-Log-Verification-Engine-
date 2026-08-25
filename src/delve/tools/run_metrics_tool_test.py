from delve.tools.metrics_tools import get_metrics

print("--- payment-service, db_pool_utilization_pct trend ---")
for m in get_metrics("payment-service", metric="db_pool_utilization_pct"):
    print(m["timestamp"], m["value"])

print("\n--- payment-service, ALL metrics ---")
for m in get_metrics("payment-service", metric="ALL"):
    print(m)

print("\n--- auth-service (should stay flat/healthy) ---")
for m in get_metrics("auth-service", metric="ALL"):
    print(m)
