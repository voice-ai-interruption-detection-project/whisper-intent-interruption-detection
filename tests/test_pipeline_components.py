from __future__ import annotations

from interruption_detection.action_selector.base import ActionSelectorInput
from interruption_detection.action_selector.rule_based import RuleBasedActionSelector
from interruption_detection.interpreter.base import CustomerSignalInterpreterInput
from interruption_detection.interpreter.llm import LLMStructuredSignalInterpreter
from interruption_detection.llm import LLMSignalJudgment
from interruption_detection.models import ActionLabel, EventType, PolicyInput


def make_input() -> PolicyInput:
    return PolicyInput(
        ai_current_intent="shipping_inquiry",
        ai_utterance="Shipping is in progress.",
        user_utterance="How much is shipping?",
        has_user_speech=True,
    )


def test_llm_structured_signal_interpreter_maps_legacy_intent_shift() -> None:
    interpreter = LLMStructuredSignalInterpreter()
    judgment = LLMSignalJudgment(
        confidence=0.7,
        predicted_event_type=None,
        predicted_user_intent=None,
        interpreted_user_intent="refund_or_return",
        is_intent_shift=True,
        ambiguity="medium",
    )

    interpretation = interpreter.interpret(
        CustomerSignalInterpreterInput(
            policy_input=make_input(),
            judgment=judgment,
        )
    )

    assert interpretation.predicted_event_type == EventType.INTENT_SHIFT
    assert interpretation.predicted_user_intent == "refund_or_return"
    assert interpretation.signal_source == "llm_structured_output"
    assert interpretation.interpreter_steps == ["llm_structured_signal_interpreter"]


def test_rule_based_action_selector_uses_interpretation_boundary() -> None:
    interpreter = LLMStructuredSignalInterpreter()
    selector = RuleBasedActionSelector()
    policy_input = make_input()
    judgment = LLMSignalJudgment(
        confidence=0.9,
        predicted_event_type=EventType.SAME_INTENT_QUESTION,
        predicted_user_intent="shipping",
        ambiguity="low",
    )
    interpretation = interpreter.interpret(
        CustomerSignalInterpreterInput(
            policy_input=policy_input,
            judgment=judgment,
        )
    )

    selection = selector.select(
        ActionSelectorInput(
            policy_input=policy_input,
            interpretation=interpretation,
            judgment=judgment,
        )
    )

    assert selection.actual_action == ActionLabel.RESPOND_AND_CONTINUE
    assert selection.selector_source == "rule_based_action_selector"
    assert selection.selector_steps == [
        "received_interpretation:same_intent_question",
        "use_rule:same_intent_question",
    ]


def test_rule_based_action_selector_rejects_contradictory_action_candidate() -> None:
    selector = RuleBasedActionSelector()
    policy_input = make_input()
    judgment = type(
        "ContradictoryJudgment",
        (),
        {"actual_action": ActionLabel.STOP_AND_SWITCH},
    )()
    interpretation = LLMSignalJudgment(
        confidence=0.9,
        predicted_event_type=EventType.BACKCHANNEL,
        predicted_user_intent=None,
        ambiguity="low",
    )
    signal = LLMStructuredSignalInterpreter().interpret(
        CustomerSignalInterpreterInput(
            policy_input=policy_input,
            judgment=interpretation,
        )
    )

    selection = selector.select(
        ActionSelectorInput(
            policy_input=policy_input,
            interpretation=signal,
            judgment=judgment,
        )
    )

    assert selection.actual_action == ActionLabel.CONTINUE
    assert selection.selector_steps == [
        "received_interpretation:backchannel",
        "use_rule:backchannel_without_response",
    ]
