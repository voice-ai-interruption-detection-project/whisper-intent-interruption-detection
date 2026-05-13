# Error Analysis - 20260514_080614_policy_v1

## Summary

- total: 30
- correct: 28
- action_accuracy: 0.9333

## Primary failures

- false_stop: 1
- missed_switch: 0
- action_confusion: 0
- ambiguous_intent: 1
- STT_uncertainty: 0

## Failed cases

- commerce_payment_follow_001: expected_actions=['respond_and_continue'], actual=stop_and_switch, primary=false_stop
- commerce_ambiguous_001: expected_actions=['brief_ack'], actual=continue, primary=ambiguous_intent
