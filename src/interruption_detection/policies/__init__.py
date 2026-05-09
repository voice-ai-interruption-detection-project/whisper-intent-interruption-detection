from __future__ import annotations

from interruption_detection.policies.base import Policy
from interruption_detection.policies.baseline import BaselinePolicy
from interruption_detection.policies.policy_v1 import PolicyV1


_POLICIES: dict[str, Policy] = {
    "baseline": BaselinePolicy(),
    "policy_v1": PolicyV1(),
}


def get_policy(name: str) -> Policy:
    try:
        return _POLICIES[name]
    except KeyError as exc:
        available = ", ".join(sorted(_POLICIES))
        raise ValueError(f"unknown policy '{name}'. available: {available}") from exc


def list_policies() -> list[dict[str, object]]:
    return [
        {
            "name": policy.name,
            "description": policy.description,
            "snapshot": policy.snapshot(),
        }
        for policy in _POLICIES.values()
    ]
