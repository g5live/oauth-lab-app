import logging
from permissions import is_allowed

logger = logging.getLogger(__name__)

DEMO_SECRETS = {
    "inventory-demo-secret": "dummy-inventory-value",
    "payroll-demo-secret": "dummy-payroll-value",}

def read_secret(principal: str, resource: str) -> str:
    allowed = is_allowed(principal, "read_secret", resource)
    logger.info(
        "principal=%s action=read_secret resource=%s allowed=%s",
        principal,
        resource,
        allowed,)
    if not allowed:
        raise PermissionError(
            f"{principal} cannot read {resource}")
    return DEMO_SECRETS[resource]

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",)
    principal = "inventory-worker"
    for resource in DEMO_SECRETS:
        try:
            value = read_secret(principal, resource)
            print(f"ALLOW: {resource} -> {value}")
        except PermissionError as error:
            print(f"DENY: {error}")