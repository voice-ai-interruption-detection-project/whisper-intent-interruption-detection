from __future__ import annotations

import pytest

from interruption_detection.models import (
    ActionLabel,
    EventType,
    PolicyInput,
    RunnerInput,
    UserToneHint,
)
from interruption_detection.policies.baseline import BaselinePolicy
from interruption_detection.policies import get_policy, list_policies
from interruption_detection.policies.policy_v1 import PolicyV1
from interruption_detection.policies.policy_v2 import PolicyV2
from interruption_detection.policies.policy_v3 import PolicyV3, PolicyV31


def make_input(
    *,
    has_user_speech: bool = True,
    tone: UserToneHint = UserToneHint.NEUTRAL,
) -> PolicyInput:
    return PolicyInput(
        ai_current_intent="shipping_inquiry",
        ai_utterance="Shipping is in progress.",
        user_utterance="ok" if has_user_speech else "",
        user_tone_hint=tone,
        has_user_speech=has_user_speech,
    )


def test_list_policies_returns_registry_entries() -> None:
    assert [item["name"] for item in list_policies()] == [
        "baseline",
        "policy_v1",
        "policy_v2",
        "policy_v3",
        "policy_v3_1",
    ]


def test_unknown_policy_fails() -> None:
    with pytest.raises(ValueError, match="unknown policy"):
        get_policy("missing")


def test_baseline_uses_llm_action_judgment(fake_llm_client) -> None:
    policy = BaselinePolicy(llm_client=fake_llm_client)

    decision = policy.predict(make_input(has_user_speech=False))

    assert decision.actual_action == ActionLabel.CONTINUE
    assert decision.signals["mode"] == "interpreter_pipeline_action_selector"
    assert decision.signals["pipeline"] == {
        "judgment_provider": "legacy_llm_action_judgment_provider",
        "interpreter": "llm_structured_signal_interpreter",
        "action_selector": "llm_baseline_action_selector",
        "decision_assembler": "policy_decision",
    }
    assert decision.signals["judgment_provider"] == (
        "legacy_llm_action_judgment_provider"
    )
    assert decision.signals["predicted_event_type"] == "no_speech"
    assert decision.signals["predicted_user_intent"] is None
    assert decision.signals["signal_source"] == "llm_structured_output"
    assert decision.signals["interpreter_steps"] == [
        "read_transcript",
        "classify_customer_signal",
    ]
    assert decision.signals["selector_source"] == "llm_baseline_action_selector"
    assert decision.signals["selector_steps"] == [
        "received_interpretation:no_speech",
        "use_candidate:legacy_llm_action_judgment",
    ]
    assert set(decision.stage_latencies_ms) == {
        "llm_judgment_provider_ms",
        "customer_signal_interpreter_ms",
        "ai_action_selector_ms",
    }
    assert fake_llm_client.requests
    assert len(fake_llm_client.requests) == 1
    assert "expected_action" not in fake_llm_client.requests[-1].user_prompt
    assert "expected_actions" not in fake_llm_client.requests[-1].user_prompt
    assert "event_type" not in fake_llm_client.requests[-1].user_prompt


def test_policy_v1_uses_label_definitions_and_examples_without_tone_hint(
    fake_llm_client,
) -> None:
    policy = PolicyV1(llm_client=fake_llm_client)

    decision = policy.predict(
        PolicyInput(
            ai_current_intent="shipping_inquiry",
            ai_utterance="Shipping is in progress.",
            user_utterance="How much is shipping?",
            user_tone_hint=UserToneHint.NEUTRAL,
            has_user_speech=True,
        )
    )

    assert decision.actual_action == ActionLabel.RESPOND_AND_CONTINUE
    assert decision.signals["predicted_event_type"] == "same_intent_question"
    assert decision.signals["predicted_user_intent"] == "shipping"
    assert decision.signals["interpreted_user_intent"] == "shipping"
    assert decision.signals["is_intent_shift"] is False
    assert decision.signals["legacy_signal_aliases"] == {
        "interpreted_user_intent": "predicted_user_intent",
        "is_intent_shift": "predicted_event_type == intent_shift",
    }
    request = fake_llm_client.requests[-1]
    assert request.prompt_version == "policy_v1_label_examples_no_tone_v1"
    assert "Action label definitions" in request.developer_prompt
    assert "Examples:" in request.developer_prompt
    assert "user_tone_hint" not in request.user_prompt
    assert request.metadata["input_fields"] == [
        "ai_current_intent",
        "ai_utterance",
        "user_utterance",
        "has_user_speech",
    ]
    assert "event_type" not in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt
    assert "expected_actions" not in request.user_prompt
    assert "policy_guidance" not in request.metadata


def test_policy_v2_adds_backchannel_noise_guidance(fake_llm_client) -> None:
    policy = PolicyV2(llm_client=fake_llm_client)

    decision = policy.predict(make_input(has_user_speech=False))

    assert decision.actual_action == ActionLabel.CONTINUE
    request = fake_llm_client.requests[-1]
    assert request.policy_name == "policy_v2"
    assert request.prompt_version == "policy_v2_backchannel_noise_v1"
    assert "Policy-specific guidance" in request.developer_prompt
    assert "backchannel_noise_no_speech_stabilization" in request.developer_prompt
    assert "has_user_speech is false" in request.developer_prompt
    assert "환불요." in request.developer_prompt
    assert "user_tone_hint" in request.user_prompt
    assert request.metadata["policy_guidance"]["target_failure"] == "false_stop"
    assert "event_type" not in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt
    assert "expected_actions" not in request.user_prompt


def test_policy_v3_adds_same_intent_boundary_guidance(fake_llm_client) -> None:
    policy = PolicyV3(llm_client=fake_llm_client)

    decision = policy.predict(
        PolicyInput(
            ai_current_intent="shipping_inquiry",
            ai_utterance="배송 상태는 현재 물류센터 출고 단계입니다.",
            user_utterance="아 그럼 배송 추적번호도 알려주세요.",
            user_tone_hint=UserToneHint.NEUTRAL,
            has_user_speech=True,
        )
    )

    assert decision.actual_action == ActionLabel.RESPOND_AND_CONTINUE
    request = fake_llm_client.requests[-1]
    assert request.policy_name == "policy_v3"
    assert request.prompt_version == "policy_v3_same_intent_boundary_v1"
    assert "Policy-specific guidance" in request.developer_prompt
    assert "same_intent_question_intent_shift_boundary" in request.developer_prompt
    assert "그럼 배송비는 얼마예요?" in request.developer_prompt
    assert "결제 말고 배송지는 지금 바꿀 수 있어요?" in request.developer_prompt
    assert "user_tone_hint" in request.user_prompt
    assert request.metadata["policy_guidance"]["target_failure"] == (
        "false_stop_on_same_intent_question"
    )
    assert "event_type" not in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt
    assert "expected_actions" not in request.user_prompt


def test_policy_v3_1_adds_return_refund_boundary_guidance(fake_llm_client) -> None:
    policy = PolicyV31(llm_client=fake_llm_client)

    decision = policy.predict(
        PolicyInput(
            ai_current_intent="return_policy",
            ai_utterance="개봉하지 않은 상품은 수령 후 7일 이내 반품할 수 있습니다.",
            user_utterance="그럼 환불금은 언제 들어와요?",
            user_tone_hint=UserToneHint.NEUTRAL,
            has_user_speech=True,
        )
    )

    assert decision.actual_action == ActionLabel.STOP_AND_SWITCH
    request = fake_llm_client.requests[-1]
    assert request.policy_name == "policy_v3_1"
    assert request.prompt_version == "policy_v3_1_return_refund_boundary_v1"
    assert "return_refund_adjacent_workflow_boundary" in request.developer_prompt
    assert "return and refund as adjacent but separate workflows" in (
        request.developer_prompt
    )
    assert "환불금은 언제 들어와요?" in request.developer_prompt
    assert "환불 계좌는 어디서 바꿔요?" in request.developer_prompt
    assert request.metadata["policy_guidance"]["target_failure"] == (
        "missed_switch_between_return_and_refund"
    )
    assert "event_type" not in request.user_prompt
    assert "expected_user_intent" not in request.user_prompt
    assert "expected_actions" not in request.user_prompt


def test_runner_input_strips_evaluation_fields_before_policy() -> None:
    runner_input = RunnerInput(
        ai_current_intent="shipping_inquiry",
        ai_utterance="Shipping is in progress.",
        user_utterance="How much is shipping?",
        event_type=EventType.SAME_INTENT_QUESTION,
        expected_user_intent="shipping_inquiry",
        user_tone_hint=UserToneHint.NEUTRAL,
        has_user_speech=True,
    )

    policy_input = runner_input.to_policy_input()

    assert isinstance(policy_input, PolicyInput)
    assert not hasattr(policy_input, "event_type")
    assert not hasattr(policy_input, "expected_user_intent")


def test_policy_snapshot_contains_llm_metadata() -> None:
    snapshot = get_policy("policy_v1").snapshot()

    assert snapshot["name"] == "policy_v1"
    assert snapshot["mode"] == "interpreter_pipeline_action_selector"
    assert snapshot["prompt_version"] == "policy_v1_label_examples_no_tone_v1"
    assert snapshot["input_fields"] == [
        "ai_current_intent",
        "ai_utterance",
        "user_utterance",
        "has_user_speech",
    ]
    assert snapshot["pipeline"] == {
        "judgment_provider": "legacy_llm_action_judgment_provider",
        "interpreter": "llm_structured_signal_interpreter",
        "action_selector": "llm_baseline_action_selector",
        "decision_assembler": "policy_decision",
    }
    assert snapshot["llm"]["provider"] == "fake"


def test_policy_v2_snapshot_exposes_guidance() -> None:
    snapshot = get_policy("policy_v2").snapshot()

    assert snapshot["name"] == "policy_v2"
    assert snapshot["prompt_version"] == "policy_v2_backchannel_noise_v1"
    assert snapshot["policy_guidance"]["focus"] == (
        "backchannel_noise_no_speech_stabilization"
    )
    assert snapshot["policy_guidance"]["target_failure"] == "false_stop"
    assert snapshot["input_fields"] == [
        "ai_current_intent",
        "ai_utterance",
        "user_utterance",
        "has_user_speech",
        "user_tone_hint",
    ]
    assert snapshot["excluded_fields"] == [
        "expected_actions",
        "event_type",
        "expected_user_intent",
    ]


def test_policy_v3_snapshot_exposes_guidance() -> None:
    snapshot = get_policy("policy_v3").snapshot()

    assert snapshot["name"] == "policy_v3"
    assert snapshot["prompt_version"] == "policy_v3_same_intent_boundary_v1"
    assert snapshot["policy_guidance"]["focus"] == (
        "same_intent_question_intent_shift_boundary"
    )
    assert snapshot["policy_guidance"]["target_failure"] == (
        "false_stop_on_same_intent_question"
    )
    assert snapshot["input_fields"] == [
        "ai_current_intent",
        "ai_utterance",
        "user_utterance",
        "has_user_speech",
        "user_tone_hint",
    ]
    assert snapshot["excluded_fields"] == [
        "expected_actions",
        "event_type",
        "expected_user_intent",
    ]


def test_policy_v3_1_snapshot_exposes_return_refund_guidance() -> None:
    snapshot = get_policy("policy_v3_1").snapshot()

    assert snapshot["name"] == "policy_v3_1"
    assert snapshot["prompt_version"] == "policy_v3_1_return_refund_boundary_v1"
    assert snapshot["policy_guidance"]["focus"] == (
        "return_refund_adjacent_workflow_boundary"
    )
    assert snapshot["policy_guidance"]["target_failure"] == (
        "missed_switch_between_return_and_refund"
    )
    assert snapshot["input_fields"] == [
        "ai_current_intent",
        "ai_utterance",
        "user_utterance",
        "has_user_speech",
        "user_tone_hint",
    ]
    assert snapshot["excluded_fields"] == [
        "expected_actions",
        "event_type",
        "expected_user_intent",
    ]
