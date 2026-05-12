from __future__ import annotations

from interruption_detection.interpreter.base import CustomerSignalInterpreterInput
from interruption_detection.llm import LLMActionJudgment
from interruption_detection.models import CustomerSignalInterpretation, EventType


class LLMStructuredSignalInterpreter:
    """legacy LLM structured judgment에서 고객 신호 해석만 추출한다."""

    name = "llm_structured_signal_interpreter"
    signal_source = "llm_structured_output"

    def interpret(
        self,
        interpreter_input: CustomerSignalInterpreterInput,
    ) -> CustomerSignalInterpretation:
        """LLM judgment의 signal 필드를 표준 interpretation 모델로 옮긴다."""
        judgment = interpreter_input.judgment

        if not isinstance(judgment, LLMActionJudgment):
            raise ValueError(
                "LLMStructuredSignalInterpreter requires LLMActionJudgment"
            )

        predicted_event_type = judgment.predicted_event_type

        if predicted_event_type is None and judgment.is_intent_shift is True:
            predicted_event_type = EventType.INTENT_SHIFT

        predicted_user_intent = (
            judgment.predicted_user_intent or judgment.interpreted_user_intent
        )

        return CustomerSignalInterpretation(
            predicted_event_type=predicted_event_type,
            predicted_user_intent=predicted_user_intent,
            confidence=judgment.confidence,
            ambiguity=judgment.ambiguity,
            signal_source=self.signal_source,
            interpreter_steps=judgment.interpreter_steps or [self.name],
        )
