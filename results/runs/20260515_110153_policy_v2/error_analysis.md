# Error Analysis - 20260515_110153_policy_v2

## Summary

- total: 18
- correct: 14
- action_accuracy: 0.7778

## Primary failures

- false_stop: 0
- missed_switch: 3
- action_confusion: 0
- ambiguous_intent: 1
- STT_uncertainty: 0

## Failed cases

- policy_v3_challenge_return_to_refund_account_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- policy_v3_challenge_return_policy_to_refund_timing_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- policy_v3_challenge_shipping_to_cancel_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- policy_v3_challenge_ambiguous_control_001: expected_actions=['ask_clarifying'], actual=continue, primary=ambiguous_intent
