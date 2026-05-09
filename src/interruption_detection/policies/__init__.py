from __future__ import annotations

from interruption_detection.policies.base import Policy
from interruption_detection.policies.baseline import BaselinePolicy
from interruption_detection.policies.policy_v1 import PolicyV1


# 모든 진입점이 같은 정책 이름과 스냅샷을 쓰도록 단일 등록소를 둔다.
_POLICIES: dict[str, Policy] = {
    "baseline": BaselinePolicy(),
    "policy_v1": PolicyV1(),
}


def get_policy(name: str) -> Policy:
    """정책 이름으로 등록소에 등록된 정책 객체를 가져온다."""
    try:
        return _POLICIES[name]
    except KeyError as exc:
        available = ", ".join(sorted(_POLICIES))
        raise ValueError(f"unknown policy '{name}'. available: {available}") from exc


def list_policies() -> list[dict[str, object]]:
    """UI/API가 표시할 정책 목록과 설정 스냅샷 정보를 반환한다."""
    return [
        {
            "name": policy.name,
            "description": policy.description,
            "snapshot": policy.snapshot(),
        }
        for policy in _POLICIES.values()
    ]
