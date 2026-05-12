from __future__ import annotations

from interruption_detection.llm import LLMActionClient
from interruption_detection.policies.llm_action import LLMActionPolicy


class PolicyV1(LLMActionPolicy):
    """라벨 정의와 예시를 더해 공통 해석/행동 선택 흐름을 실행하는 정책."""

    def __init__(self, llm_client: LLMActionClient | None = None) -> None:
        super().__init__(
            name="policy_v1",
            description=(
                "Policy v1: interpret the customer signal and select action with "
                "label definitions and few-shot guidance."
            ),
            prompt_version="policy_v1_text_llm_v1",
            include_label_definitions=True,
            include_few_shots=True,
            include_tone_hint=True,
            llm_client=llm_client,
        )
