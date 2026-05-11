# Action Label Reference

이 문서는 action label 6종을 짧게 확인하기 위한 내부 reference다.

action label은 AI 행동 판단(AI Action Policy)이 선택할 수 있는 AI 행동 이름이다. 같은 값 집합이 `expected_action`과 `actual_action` 양쪽에서 쓰인다.

```text
expected_action = 사람이 정한 기준 action label
actual_action   = policy가 낸 결과 action label
```

## 6가지 action label

| action label | 개념 | 대표 행동 | 자주 연결되는 event_type | 개입 정도 | 자주 헷갈리는 값 |
| --- | --- | --- | --- | --- | --- |
| `continue` | 현재 발화를 그대로 이어간다 | 하던 설명 계속 | `no_speech`, `noise`, `backchannel` | 개입 없음 | `brief_ack` |
| `brief_ack` | 짧게 인정하고 이어간다 | "네, 알겠습니다. 이어서..." | `backchannel` | 가벼운 반응 | `continue` |
| `respond_and_continue` | 같은 주제 질문에 답하고 원래 흐름으로 돌아간다 | 배송 설명 중 배송비 질문에 답함 | `same_intent_question` | 가벼운 개입 | `stop_and_switch` |
| `stop_and_switch` | 현재 발화를 멈추고 새 의도로 전환한다 | 배송 설명을 멈추고 환불 흐름으로 전환 | `intent_shift`, `complaint` | 전환 | `respond_and_continue`, `handoff` |
| `ask_clarifying` | 의도가 불명확해 확인 질문을 한다 | "어떤 부분을 말씀하시는 걸까요?" | `ambiguous` | 확인 질문 | `stop_and_switch` |
| `handoff` | AI가 처리하기 어렵다고 보고 상담사 연결 후보로 보낸다 | "상담사께 연결해 드리겠습니다." | `complaint` | 이관 후보 | `stop_and_switch` |

## Expected와 Actual에서의 역할

| 위치 | 같은 값 예시 | 뜻 |
| --- | --- | --- |
| `expected_action` | `stop_and_switch` | 사람이 이 판단 케이스의 기준 행동을 전환으로 정했다 |
| `actual_action` | `stop_and_switch` | policy가 실행 후 전환을 선택했다 |

두 값이 같으면 action-level 평가에서 맞은 것이다. 두 값이 다르면 policy가 기준과 다른 action label을 고른 것이다.

```text
expected_action = stop_and_switch
actual_action   = respond_and_continue

=> 같은 action label vocabulary 안에서 기준과 결과가 다름
=> intent shift를 같은 주제 질문처럼 처리했을 가능성
```

## `pause`는 현재 label이 아니다

과거 문서에는 같은 주제 질문을 처리하는 label로 `pause`가 남아 있다. 현재 기준에서는 쓰지 않는다.

| 과거 표현 | 현재 표현 | 이유 |
| --- | --- | --- |
| `pause` | `respond_and_continue` | 단순히 멈추는 것이 아니라, 같은 주제 질문에 답하고 원래 설명으로 돌아가는 행동이기 때문 |

## 작성 체크

- action label을 고객 신호의 종류처럼 설명하지 않았는가?
- `respond_and_continue`를 `pause`로 되돌리지 않았는가?
- `expected_action`과 `actual_action`을 서로 다른 값 체계처럼 설명하지 않았는가?
- `handoff`는 확정 상담사 연결이 아니라 이관 후보로 설명했는가?
