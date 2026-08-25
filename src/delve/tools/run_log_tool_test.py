from delve.tools.log_tools import search_logs

print("--- payment-service, ALL levels, last 60 min ---")
for entry in search_logs("payment-service", level="ALL", minutes_back=60):
    print(entry)

print("\n--- payment-service, ERROR only ---")
for entry in search_logs("payment-service", level="ERROR", minutes_back=60):
    print(entry)

print("\n--- auth-service (should be unrelated, normal activity) ---")
for entry in search_logs("auth-service", level="ALL", minutes_back=60):
    print(entry)
