from __future__ import annotations

from interruption_detection.models import ActionLabel, EventType, RunnerInput
from interruption_detection.runner import run_input, run_scenario
from interruption_detection.scenarios import get_scenario_by_id


def test_run_scenario_uses_registered_policy() -> None:
    scenario = get_scenario_by_id("data/scenarios.json", "commerce_no_speech_001")

    decision = run_scenario(scenario, "baseline")

    assert decision.actual_action == ActionLabel.CONTINUE
    assert "policy_ms" in decision.stage_latencies_ms


def test_run_input_uses_policy_v1() -> None:
    runner_input = RunnerInput(
        ai_current_intent="shipping_inquiry",
        ai_utterance="Shipping takes three days.",
        user_utterance="How much is shipping?",
        event_type=EventType.SAME_INTENT_QUESTION,
        expected_user_intent="shipping_inquiry",
        has_user_speech=True,
    )

    decision = run_input(runner_input, "policy_v1")

    assert decision.actual_action == ActionLabel.RESPOND_AND_CONTINUE
    assert decision.policy_name == "policy_v1"
