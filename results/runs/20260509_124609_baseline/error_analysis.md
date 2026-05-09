# Error Analysis - 20260509_124609_baseline

## Summary

- total: 30
- correct: 15
- action_accuracy: 0.5

## Primary failures

- false_stop: 12
- missed_switch: 0
- action_confusion: 1
- ambiguous_intent: 2
- STT_uncertainty: 0

## Failed cases

- commerce_backchannel_001: expected=continue, actual=stop_and_switch, primary=false_stop
- commerce_backchannel_002: expected=brief_ack, actual=stop_and_switch, primary=false_stop
- commerce_backchannel_003: expected=continue, actual=stop_and_switch, primary=false_stop
- commerce_backchannel_004: expected=continue, actual=stop_and_switch, primary=false_stop
- commerce_backchannel_005: expected=brief_ack, actual=stop_and_switch, primary=false_stop
- commerce_backchannel_006: expected=continue, actual=stop_and_switch, primary=false_stop
- commerce_shipping_follow_001: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_shipping_follow_002: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_refund_follow_001: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_return_follow_001: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_product_follow_001: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_payment_follow_001: expected=respond_and_continue, actual=stop_and_switch, primary=false_stop
- commerce_complaint_002: expected=handoff, actual=stop_and_switch, primary=action_confusion
- commerce_ambiguous_001: expected=ask_clarifying, actual=stop_and_switch, primary=ambiguous_intent
- commerce_ambiguous_002: expected=ask_clarifying, actual=stop_and_switch, primary=ambiguous_intent
