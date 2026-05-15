# Error Analysis - 20260515_112306_policy_v2

## Summary

- total: 30
- correct: 26
- action_accuracy: 0.8667

## Primary failures

- false_stop: 0
- missed_switch: 2
- action_confusion: 0
- ambiguous_intent: 2
- STT_uncertainty: 0

## Failed cases

- commerce_return_to_shipping_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_product_to_shipping_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_ambiguous_001: expected_actions=['brief_ack'], actual=continue, primary=ambiguous_intent
- commerce_ambiguous_002: expected_actions=['ask_clarifying'], actual=respond_and_continue, primary=ambiguous_intent
