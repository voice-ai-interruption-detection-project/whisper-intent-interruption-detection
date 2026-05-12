from __future__ import annotations

from interruption_detection.llm import LLMActionClient
from interruption_detection.policies.llm_action import LLMActionPolicy


class BaselinePolicy(LLMActionPolicy):
    """최소 transcript context로 공통 해석/행동 선택 흐름을 실행하는 baseline 정책."""

    def __init__(self, llm_client: LLMActionClient | None = None) -> None:
        super().__init__(
            name="baseline",
            description=(
                "Baseline: interpret the customer signal and select action from "
                "minimal transcript context."
            ),
            prompt_version="baseline_text_llm_v1",
            include_label_definitions=False,
            include_few_shots=False,
            include_tone_hint=False,
            llm_client=llm_client,
        )
