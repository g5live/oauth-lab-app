import json
from pathlib import Path

POLICY_FILE = Path(__file__).with_name("workload_policy.json")

def is_allowed(principal: str, action: str, resource: str) -> bool:
    with POLICY_FILE.open(encoding="utf-8") as file:
        policy = json.load(file)

    grants = policy.get(principal, [])

    return any(
        grant["action"] == action
        and grant["resource"] == resource
        for grant in grants)