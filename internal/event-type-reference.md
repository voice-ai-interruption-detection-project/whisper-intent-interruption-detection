# Event Type Reference

이 문서는 `event_type` 값 7종을 짧게 확인하기 위한 내부 reference다.

`event_type`은 고객이 보낸 신호의 종류다. AI가 해야 하는 행동은 action label로 따로 표현한다.

```text
고객 신호 -> event_type
AI 행동   -> action label
```

## 7가지 event_type

| event_type | 개념 | 대표 워딩/신호 | expected_user_intent | 기본 expected_action | 자주 헷갈리는 값 |
| --- | --- | --- | --- | --- | --- |
| `no_speech` | 고객 발화 없음 | 침묵, 응답 없음 | `null` | `continue` | `noise` |
| `noise` | 의미 없는 소리나 배경음 | 기침, 주변 소리, 문 닫는 소리 | `null` | `continue` | `no_speech`, `backchannel` |
| `backchannel` | 이해/동의/수신 확인 신호 | "네", "음", "알겠어요", "그렇군요" | `null` | `continue` 또는 `brief_ack` | `ambiguous`, `same_intent_question` |
| `same_intent_question` | 같은 업무 안의 보충 질문 | "배송비는요?", "몇 시쯤 와요?" | 현재 업무 intent와 같음 | `respond_and_continue` | `intent_shift` |
| `intent_shift` | 다른 업무 의도로 전환 | "환불받고 싶은데요", "반품은 어떻게 해요?" | 새 업무 intent | `stop_and_switch` | `same_intent_question`, `complaint` |
| `complaint` | 불만, 긴급, 강한 감정 신호 | "너무 늦잖아요", "지금 당장 해줘요" | 상황에 따라 `null` 또는 관련 intent | `stop_and_switch` 또는 `handoff` | `intent_shift`, `ambiguous` |
| `ambiguous` | 의도가 불명확한 발화 | "잠깐만요", "음...", "아니..." | `null` | `ask_clarifying` | `backchannel`, `complaint` |

## 판단 순서

event type을 붙일 때는 아래 순서로 본다.

```text
1. 고객 발화나 의미 있는 신호가 있는가?
2. 의미 없는 배경음/비언어 소리인가?
3. 이해나 동의에 가까운 짧은 반응인가?
4. 현재 업무 안의 보충 질문인가?
5. 다른 업무 intent로 바뀌었는가?
6. 불만/긴급도가 행동 선택을 바꿀 만큼 강한가?
7. 위 기준으로도 의도가 불명확한가?
```

이 순서는 코드 구현 순서를 고정하지 않는다. 사람이 라벨을 읽을 때 층위를 잃지 않기 위한 기준이다.

## 경계 기준

| 경계 | 먼저 볼 것 | 기준 |
| --- | --- | --- |
| `backchannel` vs `ambiguous` | 고객이 AI에게 "계속해도 된다"는 신호를 줬는가? | 수신 확인이면 `backchannel`, 말하려는 의도가 불명확하면 `ambiguous` |
| `same_intent_question` vs `intent_shift` | 고객 발화가 현재 업무 intent 안에 남아 있는가? | 같은 업무 안의 보충 질문이면 `same_intent_question`, 다른 업무 요청이면 `intent_shift` |
| `intent_shift` vs `complaint` | 새 업무 요청보다 감정/긴급 대응이 중심인가? | 업무 전환이면 `intent_shift`, 불만 자체가 우선 신호면 `complaint` |
| `no_speech` vs `noise` | 신호가 아예 없는가, 의미 없는 소리가 있는가? | 침묵이면 `no_speech`, 배경음/비언어 소리면 `noise` |

## 작성 체크

- event type을 action label처럼 쓰지 않았는가?
- 대표 워딩만 보고 기계적으로 판단하지 않고, 현재 AI intent와의 관계를 봤는가?
- `same_intent_question`은 `respond_and_continue`, `intent_shift`는 `stop_and_switch`와 기본 연결된다는 점을 유지했는가?
- `complaint`와 `ambiguous`는 판단 근거를 `notes`에 남겼는가?
