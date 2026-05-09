from __future__ import annotations

from interruption_detection.models import (
    ActionLabel,
    EventType,
    PolicyDecision,
    RunnerInput,
    UserToneHint,
)


class PolicyV1:
    """이벤트 유형 중심으로 행동을 고르는 Day 2 텍스트 재생 정책."""

    name = "policy_v1"
    description = "Event-type mapping policy for Day 2 text replay."

    # 핵심 규칙은 이벤트 -> 행동 표로 두어 리뷰하기 쉽게 만든다.
    _mapping = {
        EventType.NO_SPEECH: ActionLabel.CONTINUE,
        EventType.NOISE: ActionLabel.CONTINUE,
        EventType.BACKCHANNEL: ActionLabel.BRIEF_ACK,
        EventType.SAME_INTENT_QUESTION: ActionLabel.RESPOND_AND_CONTINUE,
        EventType.INTENT_SHIFT: ActionLabel.STOP_AND_SWITCH,
        EventType.AMBIGUOUS: ActionLabel.ASK_CLARIFYING,
    }

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
        """입력 이벤트 유형과 톤을 보고 실제 행동을 결정한다."""
        # 불만 상황만 톤을 한 번 더 보고, 나머지 이벤트는 바로 매핑한다.
        if runner_input.event_type == EventType.COMPLAINT:
            action = self._complaint_action(runner_input)
        else:
            action = self._mapping[runner_input.event_type]

        return PolicyDecision(
            policy_name=self.name,
            actual_action=action,
            reason=self._reason(runner_input, action),
            signals={
                "event_type": runner_input.event_type.value,
                "expected_user_intent": runner_input.expected_user_intent,
                "user_tone_hint": runner_input.user_tone_hint.value,
                "has_user_speech": runner_input.has_user_speech,
            },
        )

    def snapshot(self) -> dict[str, object]:
        """정책의 이벤트/행동 매핑을 실행 산출물용 스냅샷으로 반환한다."""
        mapping = {event.value: action.value for event, action in self._mapping.items()}
        mapping[EventType.COMPLAINT.value] = {
            "urgent": ActionLabel.HANDOFF.value,
            "default": ActionLabel.STOP_AND_SWITCH.value,
        }
        return {
            "name": self.name,
            "version": "day2",
            "rule_mapping": mapping,
        }

    def _complaint_action(self, runner_input: RunnerInput) -> ActionLabel:
        """불만 상황에서 긴급 톤이면 handoff, 아니면 전환으로 판단한다."""
        if runner_input.user_tone_hint == UserToneHint.URGENT:
            return ActionLabel.HANDOFF
        return ActionLabel.STOP_AND_SWITCH

    def _reason(self, runner_input: RunnerInput, action: ActionLabel) -> str:
        """판단 결과를 판단 로그에 남길 짧은 이유 문장으로 만든다."""
        if runner_input.event_type == EventType.COMPLAINT:
            if action == ActionLabel.HANDOFF:
                return "urgent complaint; route to handoff candidate"
            return (
                "complaint without urgent tone; stop and switch to complaint handling"
            )
        return f"{runner_input.event_type.value} maps to {action.value}"
