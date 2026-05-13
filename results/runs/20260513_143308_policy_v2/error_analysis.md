# Error Analysis - 20260513_143308_policy_v2

## Summary

- total: 11
- correct: 10
- action_accuracy: 0.9091

## Primary failures

- false_stop: 0
- missed_switch: 0
- action_confusion: 0
- ambiguous_intent: 1
- STT_uncertainty: 0

## Failed cases

- policy_v2_ambiguous_pause_001: expected_actions=['ask_clarifying'], actual=continue, primary=ambiguous_intent
