# Error Analysis - 20260509_124609_policy_v1

## Summary

- total: 30
- correct: 26
- action_accuracy: 0.8667

## Primary failures

- false_stop: 0
- missed_switch: 0
- action_confusion: 4
- ambiguous_intent: 0
- STT_uncertainty: 0

## Failed cases

- commerce_backchannel_001: expected=continue, actual=brief_ack, primary=action_confusion
- commerce_backchannel_003: expected=continue, actual=brief_ack, primary=action_confusion
- commerce_backchannel_004: expected=continue, actual=brief_ack, primary=action_confusion
- commerce_backchannel_006: expected=continue, actual=brief_ack, primary=action_confusion
