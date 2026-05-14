# Error Analysis - 20260513_135902_policy_v1

## Summary

- total: 30
- correct: 28
- action_accuracy: 0.9333

## Primary failures

- false_stop: 0
- missed_switch: 0
- action_confusion: 0
- ambiguous_intent: 2
- STT_uncertainty: 0

## Failed cases

- commerce_ambiguous_001: expected_actions=['brief_ack'], actual=continue, primary=ambiguous_intent
- commerce_ambiguous_002: expected_actions=['ask_clarifying'], actual=respond_and_continue, primary=ambiguous_intent
