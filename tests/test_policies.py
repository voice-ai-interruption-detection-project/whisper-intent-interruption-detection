from __future__ import annotations

import pytest

from interruption_detection.models import (
    ActionLabel,
    EventType,
    RunnerInput,
    UserToneHint,
)
from interruption_detection.policies.baseline import BaselinePolicy
from interruption_detection.policies import get_policy, list_policies
from interruption_detection.policies.policy_v1 import PolicyV1


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


def test_baseline_uses_llm_action_judgment(fake_llm_client) -> None:
    policy = BaselinePolicy(llm_client=fake_llm_client)

    decision = policy.predict(make_input(EventType.NO_SPEECH, has_user_speech=False))

    assert decision.actual_action == ActionLabel.CONTINUE
    assert decision.signals["mode"] == "llm_text_action_judgment"
    assert fake_llm_client.requests
    assert "expected_action" not in fake_llm_client.requests[-1].user_prompt
    assert "event_type" not in fake_llm_client.requests[-1].user_prompt


def test_policy_v1_uses_rich_llm_prompt(fake_llm_client) -> None:
    policy = PolicyV1(llm_client=fake_llm_client)

    decision = policy.predict(
        RunnerInput(
            ai_current_intent="shipping_inquiry",
            ai_utterance="Shipping is in progress.",
            user_utterance="How much is shipping?",
            event_type=EventType.SAME_INTENT_QUESTION,
            expected_user_intent="shipping_inquiry",
            user_tone_hint=UserToneHint.NEUTRAL,
            has_user_speech=True,
        )
    )

    assert decision.actual_action == ActionLabel.RESPOND_AND_CONTINUE
    request = fake_llm_client.requests[-1]
    assert "Action label definitions" in request.developer_prompt
    assert "Examples:" in request.developer_prompt
    assert "user_tone_hint" in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt


def test_policy_snapshot_contains_llm_metadata() -> None:
    snapshot = get_policy("policy_v1").snapshot()

    assert snapshot["name"] == "policy_v1"
    assert snapshot["mode"] == "llm_text_action_judgment"
    assert snapshot["llm"]["provider"] == "fake"
