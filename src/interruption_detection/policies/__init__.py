from __future__ import annotations

from interruption_detection.llm import LLMActionClient
from interruption_detection.policies.base import Policy
from interruption_detection.policies.baseline import BaselinePolicy
from interruption_detection.policies.policy_v1 import PolicyV1
from interruption_detection.policies.policy_v2 import PolicyV2
from interruption_detection.policies.policy_v3 import PolicyV3, PolicyV31


def build_policy_registry(
    llm_client: LLMActionClient | None = None,
) -> dict[str, Policy]:
    """같은 LLM client 설정으로 기본 정책 등록소를 만든다."""
    return {
        "baseline": BaselinePolicy(llm_client=llm_client),
        "policy_v1": PolicyV1(llm_client=llm_client),
        "policy_v2": PolicyV2(llm_client=llm_client),
        "policy_v3": PolicyV3(llm_client=llm_client),
        "policy_v3_1": PolicyV31(llm_client=llm_client),
    }


# 모든 진입점이 같은 정책 이름과 스냅샷을 쓰도록 단일 등록소를 둔다.
_POLICIES: dict[str, Policy] = build_policy_registry()


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


def replace_policy_registry_for_testing(policies: dict[str, Policy]) -> None:
    """테스트에서 실제 LLM 호출 없이 정책 등록소를 교체한다."""
    global _POLICIES

    _POLICIES = policies


def reset_policy_registry() -> None:
    """테스트가 교체한 정책 등록소를 기본 설정으로 되돌린다."""
    global _POLICIES

    _POLICIES = build_policy_registry()
