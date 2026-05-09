from __future__ import annotations

from interruption_detection.llm import LLMActionClient
from interruption_detection.policies.llm_action import LLMActionPolicy


class BaselinePolicy(LLMActionPolicy):
    """최소 transcript context만 쓰는 LLM 기반 baseline 정책."""

    def __init__(self, llm_client: LLMActionClient | None = None) -> None:
        super().__init__(
            name="baseline",
            description=(
                "Text LLM baseline: judge action from transcript and speech signal."
            ),
            prompt_version="baseline_text_llm_v1",
            include_label_definitions=False,
            include_few_shots=False,
            include_tone_hint=False,
            llm_client=llm_client,
        )
