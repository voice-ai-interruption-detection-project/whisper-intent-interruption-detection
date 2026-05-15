# Demo 2: 같은 주제 질문과 의도 전환 구분

## 상황 A: 같은 업무 안의 보충 질문

```text
AI current intent: shipping_inquiry
AI: 현재 상품은 배송 중이며 내일 오후 도착 예정입니다.
고객: 배송비는 얼마예요?
```

자연스러운 행동은 `respond_and_continue`입니다. 배송 업무 안의 보충 질문에 답하고 원래 흐름을 이어가면 됩니다.

## 상황 B: 다른 업무로 전환

```text
AI current intent: shipping_inquiry
AI: 현재 상품은 배송 중이며 내일 오후 도착 예정입니다.
고객: 아니 환불받고 싶어요.
```

자연스러운 행동은 `stop_and_switch`입니다. 고객은 배송이 아니라 환불 업무로 흐름을 바꾸려 합니다.

## 현재 MVP의 접근

현재 MVP는 LLM structured output을 사용해 runtime 입력에서 고객 신호와 다음 행동 후보를 구조화합니다.

정책은 runtime 입력을 보고 아래 값을 decision log의 `signals`에 남깁니다.

```text
predicted_event_type
predicted_user_intent
confidence
ambiguity
interpreter_steps
```

최종 평가는 `actual_action`이 `expected_actions`에 포함되는지로 봅니다.

## 최신 실험에서 드러난 경계

`policy_v3_1`은 return/refund처럼 가까운 업무를 별도 workflow로 보도록 guidance를 강화했습니다.

challenge dataset 결과:

| policy | run_id | action_accuracy | missed_switch |
| --- | --- | ---: | ---: |
| `policy_v2` | `20260515_110153_policy_v2` | 0.7778 | 3 |
| `policy_v3` | `20260515_110243_policy_v3` | 0.8333 | 2 |
| `policy_v3_1` | `20260515_111904_policy_v3_1` | 0.9444 | 0 |

core dataset에서도 `policy_v3_1`은 `policy_v2`보다 missed switch가 줄었습니다.

| policy | run_id | action_accuracy | missed_switch |
| --- | --- | ---: | ---: |
| `policy_v2` | `20260515_112306_policy_v2` | 0.8667 | 2 |
| `policy_v3_1` | `20260515_111953_policy_v3_1` | 0.9000 | 1 |

## 추가 확인 케이스

core run에서는 아래 케이스를 추가로 확인했습니다.

| scenario_id | expected_actions | actual_action | primary_failure |
| --- | --- | --- | --- |
| `commerce_payment_follow_001` | `respond_and_continue` | `stop_and_switch` | `false_stop` |
| `commerce_complaint_001` | `stop_and_switch` | `respond_and_continue` | `missed_switch` |

따라서 `policy_v3_1`은 현재 MVP에서 가장 나은 prompt-only 후보로 보고, 후속 기준 정리에 활용합니다.

## 다음

👉 [Team & Timeline](../05-resources/team.md)
