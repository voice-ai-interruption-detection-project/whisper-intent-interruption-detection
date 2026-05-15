# Scenario Schema: 데이터 구조

## 개요

모든 판단 케이스는 `data/scenarios.json`의 `scenarios` 배열에 들어갑니다. scenario는 AI가 말하던 맥락, 고객 발화, 사람이 붙인 기준 라벨, 기대 action을 함께 담습니다.

```json
{
  "scenario_id": "commerce_shipping_to_refund_001",
  "level": 4,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "아니 환불받고 싶어요.",
  "event_type": "intent_shift",
  "expected_actions": ["stop_and_switch"],
  "expected_user_intent": "refund_request",
  "user_tone_hint": "neutral",
  "has_user_speech": true,
  "notes": "AI 발화 중 사용자가 다른 업무 의도를 제시한 케이스"
}
```

## 필드 계약

| field | type | required | 의미 |
| --- | --- | --- | --- |
| `scenario_id` | string | yes | `{domain}_{intent/type}_{number}` 형식의 고유 ID |
| `level` | integer | yes | 판단 난이도. 현재 core dataset은 1~5 사용 |
| `domain` | string | yes | 업무 도메인. 현재는 `commerce`만 사용 |
| `ai_current_intent` | string | yes | AI가 진행 중이던 비즈니스 의도 |
| `ai_utterance` | string | yes | AI가 말하던 발화 |
| `user_utterance` | string | yes | 고객의 개입 발화. 발화 없음/noise는 empty string |
| `has_user_speech` | boolean | yes | 고객 음성 여부. `false`이면 `user_utterance`는 empty string |
| `user_tone_hint` | string | yes | `neutral`, `frustrated`, `urgent` 중 하나 |
| `event_type` | string | yes | 사람이 붙인 사용자 신호 기준 라벨 |
| `expected_user_intent` | string/null | yes | 고객 발화의 기준 비즈니스 의도. 의도 없음은 `null` |
| `expected_actions` | string[] | yes | 자연스러운 AI 행동 목록. 복수 정답 허용 |
| `notes` | string | optional | 라벨링 근거 또는 특이사항 |

## 값 목록

| 구분 | 허용 값 |
| --- | --- |
| `ai_current_intent`, `expected_user_intent` | `shipping_inquiry`, `refund_request`, `return_request`, `payment_issue`, `product_inquiry`, `agent_connection`, `null` |
| `event_type` | `no_speech`, `noise`, `backchannel`, `same_intent_question`, `intent_shift`, `complaint`, `ambiguous` |
| `expected_actions` | `continue`, `brief_ack`, `respond_and_continue`, `stop_and_switch`, `ask_clarifying`, `handoff` |

`event_type`, `expected_user_intent`, `expected_actions`는 기준 라벨입니다. policy prompt에는 넣지 않고 evaluator와 error analysis에서 사용합니다.

## Core Dataset 분포

현재 공식 Test Bench 기준은 `data/scenarios.json`의 30개 케이스입니다.

**Event Type**

| event_type | 샘플 수 | 비율 |
| --- | ---: | ---: |
| `no_speech` | 4 | 13% |
| `noise` | 4 | 13% |
| `backchannel` | 6 | 20% |
| `same_intent_question` | 6 | 20% |
| `intent_shift` | 6 | 20% |
| `complaint` | 2 | 7% |
| `ambiguous` | 2 | 7% |
| **합계** | **30** | **100%** |

**Level**

| level | 의미 | 샘플 수 |
| --- | --- | ---: |
| 1 | 쉬움 | 9 |
| 2 | 쉬움/중간 | 8 |
| 3 | 중간 | 7 |
| 4 | 어려움 | 5 |
| 5 | 어려움 | 1 |

**AI current intent**

| intent | 샘플 수 |
| --- | ---: |
| `shipping_inquiry` | 11 |
| `refund_request` | 5 |
| `return_request` | 4 |
| `payment_issue` | 5 |
| `product_inquiry` | 5 |

## 어노테이션 기준

| 대상 | 기준 |
| --- | --- |
| `event_type` | 고객 발화 텍스트를 먼저 보고, 맞장구, 같은 업무 질문, 의도 전환, 불만, 모호함을 구분 |
| `expected_actions` | 고객 입장에서 자연스러운 AI 행동을 기준으로 하며, 자연스러운 행동이 여러 개이면 배열에 함께 기록 |
| `level` | policy가 판단하기 어려운 정도. 1~2는 명확, 3은 중간, 4~5는 경계가 모호한 케이스 |
| `notes` | 라벨링 근거가 불명확하거나 경계 케이스이면 기록 |

## 대표 예시

| 유형 | scenario_id | expected_actions | 핵심 |
| --- | --- | --- | --- |
| Backchannel | `commerce_backchannel_001` | `continue`, `brief_ack` | 맞장구는 현재 흐름을 유지 |
| Intent Shift | `commerce_shipping_to_refund_001` | `stop_and_switch` | 배송 안내 중 환불 요청으로 전환 |
| Same Intent Question | `commerce_shipping_follow_001` | `respond_and_continue` | 배송 업무 안의 보충 질문 |
| Noise | `commerce_noise_001` | `continue` | 의미 없는 소리는 무시하고 계속 |
| Complaint | `commerce_complaint_002` | `handoff` | 긴급 불만은 상담사 연결 |

## 파일 형식

```json
{
  "scenarios": [
    { "...": "scenario 1" },
    { "...": "scenario 2" }
  ]
}
```

[Scenario Bank](./bank.md)
