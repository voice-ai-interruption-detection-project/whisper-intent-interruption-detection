from __future__ import annotations

from time import perf_counter
from typing import Protocol

from interruption_detection.action_selector.base import (
    ActionSelector,
    ActionSelectorInput,
)
from interruption_detection.interpreter.base import (
    CustomerSignalInterpreter,
    CustomerSignalInterpreterInput,
)
from interruption_detection.models import PolicyDecision, PolicyInput


class JudgmentProvider(Protocol):
    """pipeline에 LLM/action 후보 judgment를 제공하는 컴포넌트."""

    name: str

    def judge(self, policy_input: PolicyInput) -> object:
        """runtime 입력에서 해석/action 후보 judgment를 생성한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """run artifact에 남길 provider 설정을 반환한다."""
        ...

    def input_fields(self) -> list[str]:
        """provider prompt에 포함되는 runtime 입력 필드를 반환한다."""
        ...

    def excluded_fields(self) -> list[str]:
        """provider prompt에서 제외되는 평가/라벨 필드를 반환한다."""
        ...


class DecisionPipeline:
    """Text/Audio 입력이 합류한 뒤 고객 신호 해석과 action 선택을 실행한다."""

    def __init__(
        self,
        *,
        policy_name: str,
        prompt_version: str,
        judgment_provider: JudgmentProvider,
        interpreter: CustomerSignalInterpreter,
        action_selector: ActionSelector,
    ) -> None:
        self.policy_name = policy_name
        self.prompt_version = prompt_version
        self.judgment_provider = judgment_provider
        self.interpreter = interpreter
        self.action_selector = action_selector

    def run(self, policy_input: PolicyInput) -> PolicyDecision:
        """공통 runtime 입력을 최종 policy decision으로 조립한다."""
        judgment_started = perf_counter()
        judgment = self.judgment_provider.judge(policy_input)
        judgment_ms = _elapsed_ms(judgment_started)

        interpreter_started = perf_counter()
        interpretation = self.interpreter.interpret(
            CustomerSignalInterpreterInput(
                policy_input=policy_input,
                judgment=judgment,
            )
        )
        interpreter_ms = _elapsed_ms(interpreter_started)

        selector_started = perf_counter()
        selection = self.action_selector.select(
            ActionSelectorInput(
                policy_input=policy_input,
                interpretation=interpretation,
                judgment=judgment,
            )
        )
        selector_ms = _elapsed_ms(selector_started)

        provider_snapshot = self.judgment_provider.snapshot()

        return PolicyDecision(
            policy_name=self.policy_name,
            actual_action=selection.actual_action,
            reason=selection.reason,
            signals={
                "mode": "interpreter_pipeline_action_selector",
                "pipeline": self.snapshot(),
                "prompt_version": self.prompt_version,
                "llm": provider_snapshot.get("llm", {}),
                "judgment_provider": self.judgment_provider.name,
                **interpretation.to_signal_dict(),
                "selector_source": selection.selector_source,
                "selector_steps": selection.selector_steps,
                "input_fields": self.judgment_provider.input_fields(),
                "excluded_fields": self.judgment_provider.excluded_fields(),
            },
            stage_latencies_ms={
                "llm_judgment_provider_ms": judgment_ms,
                "customer_signal_interpreter_ms": interpreter_ms,
                "ai_action_selector_ms": selector_ms,
            },
        )

    def snapshot(self) -> dict[str, object]:
        """pipeline component 구성을 run artifact 친화적인 dict로 반환한다."""
        return {
            "judgment_provider": self.judgment_provider.name,
            "interpreter": self.interpreter.name,
            "action_selector": self.action_selector.name,
            "decision_assembler": "policy_decision",
        }


def _elapsed_ms(started: float) -> float:
    return round((perf_counter() - started) * 1000, 3)
