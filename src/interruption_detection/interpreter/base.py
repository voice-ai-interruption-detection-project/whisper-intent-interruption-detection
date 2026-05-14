from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from interruption_detection.models import CustomerSignalInterpretation, PolicyInput


@dataclass(frozen=True)
class CustomerSignalInterpreterInput:
    """고객 신호 해석 컴포넌트가 받는 pipeline 내부 입력."""

    policy_input: PolicyInput
    judgment: object | None = None


class CustomerSignalInterpreter(Protocol):
    """고객 transcript/audio signal을 runtime 고객 신호로 해석하는 컴포넌트."""

    name: str

    def interpret(
        self,
        interpreter_input: CustomerSignalInterpreterInput,
    ) -> CustomerSignalInterpretation:
        """pipeline 내부 입력을 고객 신호 해석 결과로 변환한다."""
        ...
