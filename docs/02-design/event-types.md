# Event Types & Intents

## Event Type은 고객 신호 기준값이다

`event_type`은 사람이 판단 케이스에 붙인 기준 고객 신호입니다. AI가 실제로 선택하는 행동은 action label인 `actual_action`으로 따로 기록됩니다.

```text
고객 신호 기준값: event_type
runtime 해석 후보: predicted_event_type
AI 행동 결과: actual_action
```

policy prompt에는 `event_type`, `expected_user_intent`, `expected_actions`를 넣지 않습니다. 이 값들은 evaluator와 error analysis에서 기준으로 사용합니다.

## 7가지 Event Type

| event_type | 의미 | 기본 expected_actions |
| --- | --- | --- |
| `no_speech` | 고객 발화 없음 | `continue` |
| `noise` | 배경음, 비언어 소리 | `continue` |
| `backchannel` | "네", "음", "알겠어요" 같은 맞장구 | `continue` 또는 `brief_ack` |
| `same_intent_question` | 현재 업무 안의 보충 질문 | `respond_and_continue` |
| `intent_shift` | 다른 업무로 바뀐 요청 | `stop_and_switch` |
| `complaint` | 불만, 긴급, 강한 감정 신호 | `stop_and_switch` 또는 `handoff` |
| `ambiguous` | 의도가 불명확한 발화 | `ask_clarifying` |

## 경계 기준

### `backchannel` vs `ambiguous`

```text
고객: 네, 알겠어요.
-> backchannel
-> continue 또는 brief_ack

고객: 음... 그게 맞나?
-> ambiguous
-> ask_clarifying
```

수신 확인이면 `backchannel`, 고객이 뭔가 말하려는 의도가 불명확하면 `ambiguous`로 봅니다.

### `same_intent_question` vs `intent_shift`

```text
AI current intent: shipping_inquiry
고객: 배송비는 얼마예요?
-> same_intent_question
-> respond_and_continue

AI current intent: shipping_inquiry
고객: 환불받고 싶어요.
-> intent_shift
-> stop_and_switch
```

같은 업무 안의 보충 질문인지, 다른 업무 workflow로 넘어가는지 봅니다.

### `intent_shift` vs `complaint`

```text
고객: 반품하고 싶어요.
-> intent_shift

고객: 뭐 이거 벌써 2주 됐잖아요.
-> complaint
```

업무 변경이 중심이면 `intent_shift`, 불만/긴급 신호 자체가 AI 행동을 바꿀 만큼 중요하면 `complaint`로 봅니다.

## Intent

현재 core dataset의 주요 commerce intent는 아래처럼 정리됩니다.

| intent | 의미 |
| --- | --- |
| `shipping_inquiry` | 배송 상태, 배송비, 추적번호 |
| `refund_request` | 환불 요청, 환불 상태, 환불 계좌 |
| `return_request` | 반품 요청, 반품 수거, 반품 정책 |
| `payment_issue` | 결제 오류, 중복 결제, 결제 수단 |
| `product_inquiry` | 상품 정보, 사이즈, 색상 |
| `agent_connection` | 상담사 연결 요청 |

`expected_user_intent`는 사람이 붙인 기준 의도입니다. runtime 해석 결과는 `predicted_user_intent`로 decision log의 `signals`에 남깁니다.

## 실제 Scenario 예시

```json
{
  "scenario_id": "commerce_shipping_to_refund_001",
  "level": 4,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "아니 환불받고 싶어요.",
  "event_type": "intent_shift",
  "expected_user_intent": "refund_request",
  "expected_actions": ["stop_and_switch"],
  "has_user_speech": true,
  "user_tone_hint": "neutral",
  "notes": "배송 안내 중 환불 요청으로 업무가 전환되는 케이스"
}
```

## 다음

👉 [Evaluation Approach](./evaluation.md)
