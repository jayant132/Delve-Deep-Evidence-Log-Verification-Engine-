from delve.tools.deployment_tools import get_deployment_changes

print("--- payment-service deployments (should show the pool_size regression) ---")
for d in get_deployment_changes("payment-service", hours_back=24):
    print(d)

print("\n--- auth-service deployments (unrelated) ---")
for d in get_deployment_changes("auth-service", hours_back=24):
    print(d)
