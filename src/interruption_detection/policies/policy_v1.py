from __future__ import annotations

from interruption_detection.models import (
    ActionLabel,
    EventType,
    PolicyDecision,
    RunnerInput,
    UserToneHint,
)


class PolicyV1:
    name = "policy_v1"
    description = "Event-type mapping policy for Day 2 text replay."

    _mapping = {
        EventType.NO_SPEECH: ActionLabel.CONTINUE,
        EventType.NOISE: ActionLabel.CONTINUE,
        EventType.BACKCHANNEL: ActionLabel.BRIEF_ACK,
        EventType.SAME_INTENT_QUESTION: ActionLabel.RESPOND_AND_CONTINUE,
        EventType.INTENT_SHIFT: ActionLabel.STOP_AND_SWITCH,
        EventType.AMBIGUOUS: ActionLabel.ASK_CLARIFYING,
    }

    def predict(self, runner_input: RunnerInput) -> PolicyDecision:
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
        if runner_input.user_tone_hint == UserToneHint.URGENT:
            return ActionLabel.HANDOFF
        return ActionLabel.STOP_AND_SWITCH

    def _reason(self, runner_input: RunnerInput, action: ActionLabel) -> str:
        if runner_input.event_type == EventType.COMPLAINT:
            if action == ActionLabel.HANDOFF:
                return "urgent complaint; route to handoff candidate"
            return (
                "complaint without urgent tone; stop and switch to complaint handling"
            )
        return f"{runner_input.event_type.value} maps to {action.value}"
