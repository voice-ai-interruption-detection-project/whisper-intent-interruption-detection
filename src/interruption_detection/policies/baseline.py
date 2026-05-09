from __future__ import annotations

from interruption_detection.models import ActionLabel, PolicyDecision, RunnerInput


class BaselinePolicy:
    name = "baseline"
    description = "Speech-event baseline: stop when user speech is present."

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
        if runner_input.has_user_speech:
            action = ActionLabel.STOP_AND_SWITCH
            reason = "user speech detected; baseline stops and switches"
        else:
            action = ActionLabel.CONTINUE
            reason = "no user speech detected; baseline continues"

        return PolicyDecision(
            policy_name=self.name,
            actual_action=action,
            reason=reason,
            signals={
                "has_user_speech": runner_input.has_user_speech,
                "event_type": runner_input.event_type.value,
            },
        )

    def snapshot(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": "day2",
            "rule": {
                "has_user_speech=false": ActionLabel.CONTINUE.value,
                "has_user_speech=true": ActionLabel.STOP_AND_SWITCH.value,
            },
        }
