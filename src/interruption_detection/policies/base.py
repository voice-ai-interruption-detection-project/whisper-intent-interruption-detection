from __future__ import annotations

from typing import Protocol

from interruption_detection.models import PolicyDecision, RunnerInput


class Policy(Protocol):
    name: str
    description: str

    def predict(self, runner_input: RunnerInput) -> PolicyDecision: ...

    def snapshot(self) -> dict[str, object]: ...
