# Error Analysis - 20260513_135758_baseline

## Summary

- total: 30
- correct: 26
- action_accuracy: 0.8667

## Primary failures

- false_stop: 0
- missed_switch: 4
- action_confusion: 0
- ambiguous_intent: 0
- STT_uncertainty: 0

## Failed cases

- commerce_return_to_shipping_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_product_to_shipping_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_complaint_001: expected_actions=['stop_and_switch'], actual=respond_and_continue, primary=missed_switch
- commerce_complaint_002: expected_actions=['handoff'], actual=respond_and_continue, primary=missed_switch
