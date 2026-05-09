from __future__ import annotations

from interruption_detection.models import ActionLabel, PolicyDecision, RunnerInput


class BaselinePolicy:
    """사용자 발화 여부만 보는 비교 기준 정책."""

    name = "baseline"
    description = "Speech-event baseline: stop when user speech is present."

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
        """사용자 발화가 있으면 전환, 없으면 계속 진행으로 판단한다."""
        # 비교 기준이라 의도적으로 단순하게 둔다: 발화가 있으면 끼어듦.
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
        """기준 정책 규칙을 실행 산출물에 남길 형태로 반환한다."""
        return {
            "name": self.name,
            "version": "day2",
            "rule": {
                "has_user_speech=false": ActionLabel.CONTINUE.value,
                "has_user_speech=true": ActionLabel.STOP_AND_SWITCH.value,
            },
        }
