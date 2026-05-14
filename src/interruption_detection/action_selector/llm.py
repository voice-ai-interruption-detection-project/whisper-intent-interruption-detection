from __future__ import annotations

from interruption_detection.action_selector.base import ActionSelectorInput
from interruption_detection.llm import LLMActionJudgment
from interruption_detection.models import ActionSelection


class LLMBaselineActionSelector:
    """legacy one-shot LLM action candidate를 baseline action으로 채택한다."""

    name = "llm_baseline_action_selector"
    candidate_source = "legacy_llm_action_judgment"

    def select(self, selector_input: ActionSelectorInput) -> ActionSelection:
        """해석 결과를 기록하면서 legacy LLM action candidate를 반환한다."""
        judgment = selector_input.judgment

        if not isinstance(judgment, LLMActionJudgment):
            raise ValueError("LLMBaselineActionSelector requires LLMActionJudgment")

        event_type = selector_input.interpretation.predicted_event_type
        event_value = event_type.value if event_type is not None else "unknown"

        return ActionSelection(
            actual_action=judgment.actual_action,
            reason=judgment.reason,
            selector_source=self.name,
            selector_steps=[
                f"received_interpretation:{event_value}",
                f"use_candidate:{self.candidate_source}",
            ],
        )
