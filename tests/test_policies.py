from __future__ import annotations

import pytest

from interruption_detection.models import (
    ActionLabel,
    EventType,
    RunnerInput,
    UserToneHint,
)
from interruption_detection.policies import get_policy, list_policies


def make_input(
    event_type: EventType,
    *,
    has_user_speech: bool = True,
    tone: UserToneHint = UserToneHint.NEUTRAL,
) -> RunnerInput:
    return RunnerInput(
        ai_current_intent="shipping_inquiry",
        ai_utterance="Shipping is in progress.",
        user_utterance="ok" if has_user_speech else "",
        event_type=event_type,
        expected_user_intent=None,
        user_tone_hint=tone,
        has_user_speech=has_user_speech,
    )


def test_list_policies_returns_registry_entries() -> None:
    assert [item["name"] for item in list_policies()] == ["baseline", "policy_v1"]


def test_unknown_policy_fails() -> None:
    with pytest.raises(ValueError, match="unknown policy"):
        get_policy("missing")


def test_baseline_uses_speech_presence_only() -> None:
    policy = get_policy("baseline")

    assert (
        policy.predict(
            make_input(EventType.NO_SPEECH, has_user_speech=False)
        ).actual_action
        == ActionLabel.CONTINUE
    )
    assert (
        policy.predict(make_input(EventType.BACKCHANNEL)).actual_action
        == ActionLabel.STOP_AND_SWITCH
    )


@pytest.mark.parametrize(
    ("event_type", "expected"),
    [
        (EventType.NO_SPEECH, ActionLabel.CONTINUE),
        (EventType.NOISE, ActionLabel.CONTINUE),
        (EventType.BACKCHANNEL, ActionLabel.BRIEF_ACK),
        (EventType.SAME_INTENT_QUESTION, ActionLabel.RESPOND_AND_CONTINUE),
        (EventType.INTENT_SHIFT, ActionLabel.STOP_AND_SWITCH),
        (EventType.AMBIGUOUS, ActionLabel.ASK_CLARIFYING),
    ],
)
def test_policy_v1_event_mapping(event_type: EventType, expected: ActionLabel) -> None:
    policy = get_policy("policy_v1")

    assert policy.predict(make_input(event_type)).actual_action == expected


def test_policy_v1_complaint_urgent_routes_to_handoff() -> None:
    policy = get_policy("policy_v1")

    decision = policy.predict(make_input(EventType.COMPLAINT, tone=UserToneHint.URGENT))

    assert decision.actual_action == ActionLabel.HANDOFF
    assert "urgent" in decision.reason


def test_policy_snapshot_contains_mapping() -> None:
    snapshot = get_policy("policy_v1").snapshot()

    assert snapshot["name"] == "policy_v1"
    assert "rule_mapping" in snapshot
