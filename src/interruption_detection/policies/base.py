from __future__ import annotations

from typing import Protocol

from interruption_detection.models import PolicyDecision, RunnerInput


class Policy(Protocol):
    """모든 정책 구현체가 맞춰야 하는 최소 인터페이스."""

    name: str
    description: str

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
        """RunnerInput 하나에 대한 정책 판단을 반환한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """run artifact에 남길 정책 설정 스냅샷을 반환한다."""
        ...
