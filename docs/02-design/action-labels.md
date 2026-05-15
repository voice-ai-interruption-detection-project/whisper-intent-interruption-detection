# Action Labels: AI가 선택할 수 있는 6가지 행동

## 개요

Action label은 AI가 고객 발화를 본 뒤 선택하는 제품 행동입니다.

현재 MVP에서 action은 세 곳에서 같은 의미로 쓰입니다.

- scenario의 `expected_actions`
- policy 실행 결과인 `actual_action`
- run artifact의 `evaluation.json`, `decision_logs.jsonl`

평가는 `actual_action in expected_actions`로 계산합니다. 한 케이스에 자연스러운 행동이 여러 개일 수 있으므로, 정답은 단일 label이 아니라 action set입니다.

## 6가지 Action Label

### `continue`

AI가 현재 발화를 그대로 이어 갑니다.

대표 조건:

- 고객 발화 없음
- 배경음 또는 의미 없는 소리
- 흐름을 바꾸지 않는 짧은 반응

```text
AI: 배송은 내일 오후에 도착 예정이고...
고객: (침묵)
=> AI는 계속 설명
```

### `brief_ack`

AI가 고객의 짧은 반응을 인정하고 바로 이어 갑니다.

대표 조건:

- "네", "음", "알겠어요" 같은 backchannel
- 새 요청이나 확인 질문이 아닌 동의/수신 신호

```text
AI: 배송 상태를 확인해 드리겠습니다.
고객: 네.
=> AI: 네, 이어서 안내드리면...
```

`continue`와 `brief_ack`는 둘 다 현재 업무 흐름을 유지합니다. 차이는 AI가 짧은 인정 표현을 명시적으로 넣는지입니다.

### `respond_and_continue`

AI가 고객의 보충 질문에 답한 뒤 원래 흐름으로 돌아갑니다.

대표 조건:

- 같은 업무 안의 질문
- 현재 설명을 중단할 필요는 있지만, 상담 목적 자체는 바뀌지 않음

```text
AI: 배송은 내일 도착 예정입니다.
고객: 배송비는 따로 드나요?
=> AI는 배송비 질문에 답하고 배송 안내를 이어감
```

### `stop_and_switch`

AI가 현재 설명을 멈추고 고객의 새 요청으로 주제를 전환합니다.

대표 조건:

- 다른 업무 의도로 전환
- 지금 하던 안내보다 고객의 새 요청이 우선

```text
AI: 배송은 내일 도착 예정입니다.
고객: 아, 그게 아니라 환불받고 싶은데요.
=> AI는 배송 안내를 멈추고 환불 흐름으로 전환
```

### `ask_clarifying`

AI가 고객 의도를 확정하기 어렵다고 보고 확인 질문을 합니다.

대표 조건:

- 발화가 너무 짧거나 지시 대상이 불명확함
- 섣불리 계속하거나 전환하면 오해 가능성이 큼

```text
AI: 어떤 상품을 찾으세요?
고객: 음... 그거요.
=> AI는 어떤 상품을 말하는지 확인
```

### `handoff`

AI가 자동 응답으로 처리하기 어렵다고 보고 상담사 연결을 선택합니다.

대표 조건:

- 높은 강도의 불만
- 긴급하거나 민감한 상황
- AI가 계속 처리하면 고객 경험이 나빠질 가능성이 큼

```text
AI: 배송 상황은 정상으로 확인됩니다.
고객: 지금 당장 해결해야 해요. 상담사 연결해 주세요.
=> AI는 상담사 연결로 전환
```

## Event Type과의 관계

`event_type`은 scenario에 사람이 붙인 기준 라벨입니다. 정책 실행 중 LLM이 예측한 값은 `predicted_event_type`으로 따로 기록합니다.

| event_type | 주로 허용되는 action | 설명 |
| --- | --- | --- |
| `no_speech` | `continue` | 고객 발화 없음 |
| `noise` | `continue` | 판단할 의미가 없는 소리 |
| `backchannel` | `continue`, `brief_ack` | 흐름 유지 신호 |
| `same_intent_question` | `respond_and_continue` | 같은 업무 내 보충 질문 |
| `intent_shift` | `stop_and_switch` | 다른 업무로 전환 |
| `complaint` | `stop_and_switch`, `handoff` | 불만 또는 긴급 상황 |
| `ambiguous` | `ask_clarifying` | 의도 확인 필요 |

이 매핑은 시작 기준입니다. 실제 평가는 scenario별 `expected_actions`를 우선합니다.

## 현재 구현에서의 사용

정책 버전은 `baseline`, `policy_v1`, `policy_v2`, `policy_v3`, `policy_v3_1`로 등록되어 있습니다.

최신 MVP에서는 6개 action label 자체보다 다음 질문이 더 중요합니다.

- 고객이 단순 반응을 한 것인지, 새 요청을 한 것인지 구분되는가?
- 같은 업무의 보충 질문과 다른 업무로의 전환을 구분되는가?
- 애매한 발화를 성급하게 전환하거나 계속하지 않고 확인 질문으로 보낼 수 있는가?
- 불만 케이스에서 자동 처리와 상담사 연결 경계를 분리할 수 있는가?

## 다음

👉 [Event Types & Intents](./event-types.md)
