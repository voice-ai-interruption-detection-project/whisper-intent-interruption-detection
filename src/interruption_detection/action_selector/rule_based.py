from __future__ import annotations

from interruption_detection.action_selector.base import ActionSelectorInput
from interruption_detection.models import (
    ActionLabel,
    ActionSelection,
    EventType,
    UserToneHint,
)


AGENT_REQUEST_TERMS = (
    "agent",
    "human",
    "representative",
    "person",
    "사람",
    "상담",
    "상담원",
    "직원",
    "연결",
)
ACK_TERMS = ("알겠", "감사", "고마", "맞아", "네", "음", "ok", "okay", "thanks")
WAIT_TERMS = ("잠깐", "기다", "wait", "hold")
ESCALATION_TERMS = ("당장", "지금", "화나", "짜증", "이딴", "최악")


class RuleBasedActionSelector:
    """해석된 고객 신호를 deterministic action label로 매핑한다."""

    name = "rule_based_action_selector"

    def select(self, selector_input: ActionSelectorInput) -> ActionSelection:
        """LLM action 후보가 아니라 interpretation을 기준으로 다음 action을 고른다."""
        policy_input = selector_input.policy_input
        interpretation = selector_input.interpretation
        event_type = interpretation.predicted_event_type
        utterance = policy_input.user_utterance.strip()

        actual_action, rule = _select_action(
            event_type=event_type,
            predicted_user_intent=interpretation.predicted_user_intent,
            user_utterance=utterance,
            has_user_speech=policy_input.has_user_speech,
            tone_hint=policy_input.user_tone_hint,
        )
        event_value = event_type.value if event_type is not None else "unknown"

        return ActionSelection(
            actual_action=actual_action,
            reason=_selection_reason(
                actual_action=actual_action,
                rule=rule,
                event_value=event_value,
                predicted_user_intent=interpretation.predicted_user_intent,
            ),
            selector_source=self.name,
            selector_steps=[
                f"received_interpretation:{event_value}",
                f"use_rule:{rule}",
            ],
        )


def _select_action(
    *,
    event_type: EventType | None,
    predicted_user_intent: str | None,
    user_utterance: str,
    has_user_speech: bool,
    tone_hint: UserToneHint,
) -> tuple[ActionLabel, str]:
    """현재 action vocabulary를 runtime 고객 신호 해석에 매핑한다."""
    if not has_user_speech or not user_utterance:
        return ActionLabel.CONTINUE, "no_meaningful_user_speech"

    if event_type in {EventType.NO_SPEECH, EventType.NOISE}:
        return ActionLabel.CONTINUE, f"{event_type.value}_continues_flow"

    if event_type == EventType.BACKCHANNEL:
        if _contains_any(user_utterance, ACK_TERMS):
            return ActionLabel.BRIEF_ACK, "backchannel_acknowledgement"
        return ActionLabel.CONTINUE, "backchannel_without_response"

    if event_type == EventType.SAME_INTENT_QUESTION:
        return ActionLabel.RESPOND_AND_CONTINUE, "same_intent_question"

    if event_type == EventType.INTENT_SHIFT:
        if _is_agent_request(predicted_user_intent, user_utterance):
            return ActionLabel.HANDOFF, "intent_shift_agent_request"
        return ActionLabel.STOP_AND_SWITCH, "intent_shift"

    if event_type == EventType.COMPLAINT:
        if (
            _is_agent_request(predicted_user_intent, user_utterance)
            or tone_hint == UserToneHint.URGENT
            or _contains_any(user_utterance, ESCALATION_TERMS)
        ):
            return ActionLabel.HANDOFF, "urgent_complaint"
        return ActionLabel.STOP_AND_SWITCH, "complaint_requires_switch"

    if event_type == EventType.AMBIGUOUS:
        if _contains_any(user_utterance, WAIT_TERMS):
            return ActionLabel.BRIEF_ACK, "ambiguous_wait_cue"
        return ActionLabel.ASK_CLARIFYING, "ambiguous_signal"

    return ActionLabel.ASK_CLARIFYING, "unknown_signal"


def _selection_reason(
    *,
    actual_action: ActionLabel,
    rule: str,
    event_value: str,
    predicted_user_intent: str | None,
) -> str:
    """run artifact에서 selector 판단 근거가 보이도록 짧은 reason을 만든다."""
    intent_part = (
        f", predicted_user_intent={predicted_user_intent}"
        if predicted_user_intent
        else ""
    )
    return (
        f"Action selector mapped predicted_event_type={event_value}{intent_part} "
        f"to {actual_action.value} using rule {rule}."
    )


def _is_agent_request(
    predicted_user_intent: str | None,
    user_utterance: str,
) -> bool:
    intent = (predicted_user_intent or "").casefold()
    return (
        "agent" in intent
        or "human" in intent
        or _contains_any(user_utterance, AGENT_REQUEST_TERMS)
    )


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    lowered = value.casefold()
    return any(term.casefold() in lowered for term in terms)
