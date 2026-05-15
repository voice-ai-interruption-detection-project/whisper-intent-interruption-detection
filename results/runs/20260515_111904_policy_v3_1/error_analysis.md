# Error Analysis - 20260515_111904_policy_v3_1

## Summary

- total: 18
- correct: 17
- action_accuracy: 0.9444

## Primary failures

- false_stop: 0
- missed_switch: 0
- action_confusion: 0
- ambiguous_intent: 1
- STT_uncertainty: 0

## Failed cases

- policy_v3_challenge_ambiguous_control_001: expected_actions=['ask_clarifying'], actual=continue, primary=ambiguous_intent
