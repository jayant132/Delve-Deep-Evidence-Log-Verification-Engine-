ALLOWED_SERVICES = {"payment-service", "auth-service", "order-service"}


def check_service_allowed(service: str) -> None:
    if service not in ALLOWED_SERVICES:
        raise ValueError(f"Service '{service}' is not an authorized target")
