# Error Analysis - 20260515_111953_policy_v3_1

## Summary

- total: 30
- correct: 27
- action_accuracy: 0.9

## Primary failures

- false_stop: 1
- missed_switch: 1
- action_confusion: 0
- ambiguous_intent: 1
- STT_uncertainty: 0

## Failed cases

- commerce_payment_follow_001: expected_actions=['respond_and_continue'], actual=stop_and_switch, primary=false_stop
- commerce_complaint_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_ambiguous_002: expected_actions=['ask_clarifying'], actual=brief_ack, primary=ambiguous_intent
