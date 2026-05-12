from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from interruption_detection.models import (
    ActionSelection,
    CustomerSignalInterpretation,
    PolicyInput,
)


@dataclass(frozen=True)
class ActionSelectorInput:
    """action selector가 받는 pipeline 내부 입력."""

    policy_input: PolicyInput
    interpretation: CustomerSignalInterpretation
    judgment: object | None = None


class ActionSelector(Protocol):
    """고객 신호 해석을 바탕으로 다음 action을 선택하는 컴포넌트."""

    name: str

    def select(self, selector_input: ActionSelectorInput) -> ActionSelection:
        """해석된 고객 신호를 다음 action으로 변환한다."""
        ...
