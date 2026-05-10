# Scenario Worked Example

이 문서는 한 scenario가 상황 요약, schema key/value, policy 판단, 평가 결과로 어떻게 이어지는지 보여주는 내부 기준 예시다.

`Project Language Map`이 용어의 지도를 잡는 문서라면, 이 문서는 실제 한 케이스를 끝까지 따라가며 층위를 연결한다.

## 읽는 순서

아래 순서로 읽는다.

```text
상황 요약
-> scenario card
-> transcript / speech signal 구성
   (입력 adapter는 이 앞단에서만 다름)
-> AI Action Policy 판단
-> expected_action / actual_action 비교
-> failure taxonomy
```

schema key의 나열 순서가 곧 실행 순서는 아니다. schema는 한 scenario card에 필요한 정보를 담는 그릇이고, pipeline은 그 정보를 어떤 순서로 처리하는지 나타낸다.

`event_type`, `expected_user_intent`, `expected_action`은 사람이 붙인 기준 annotation이다. 현재 LLM action judge의 prompt에는 `expected_action`, `event_type`, `expected_user_intent`를 넣지 않는다.

## 예시 A. Intent Shift

### 상황 요약

AI가 배송 상태를 설명하고 있다. 고객이 중간에 끼어들어 "그게 아니라 환불받고 싶은데요"라고 말한다.

이 장면에서 중요한 것은 고객이 말을 했다는 사실 자체가 아니라, 고객의 업무 의도가 배송 조회에서 환불 요청으로 바뀌었다는 점이다.

### Scenario Card

```json
{
  "scenario_id": "commerce_shipping_to_refund_001",
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "그게 아니라 환불받고 싶은데요.",
  "event_type": "intent_shift",
  "expected_user_intent": "refund_request",
  "expected_action": "stop_and_switch",
  "has_user_speech": true,
  "user_tone_hint": "neutral"
}
```

### Key별 의미

| key | 값 | 층위 |
| --- | --- | --- |
| `ai_current_intent` | `shipping_inquiry` | AI가 지금 이어가던 업무 주제 |
| `ai_utterance` | 배송 상태 설명 | AI가 말하던 문장 |
| `user_utterance` | 환불 요청 | 고객이 끼어든 발화 |
| `event_type` | `intent_shift` | 고객 신호의 종류 |
| `expected_user_intent` | `refund_request` | 고객 발화에서 읽히는 새 업무 의도 |
| `expected_action` | `stop_and_switch` | 사람이 정한 자연스러운 AI 행동 |

`event_type`은 고객 신호이고, `expected_action`은 AI 행동이다. 이 둘은 같은 층위가 아니다.

### Expected와 Actual의 역할

scenario card에는 `expected_action`만 있다. `actual_action`은 policy를 실행한 뒤에 생긴다.

두 값은 서로 다른 label 체계가 아니라 같은 action label vocabulary를 다른 역할로 쓰는 것이다.

| 이름 | 이 예시의 값 | 역할 |
| --- | --- | --- |
| `expected_action` | `stop_and_switch` | 사람이 미리 정한 기준/정답 |
| `actual_action` | policy 실행 후 결정 | policy가 실제로 낸 결과/예측 |

따라서 `actual_action = respond_and_continue`가 나오면 "다른 종류의 action 용어"가 나온 것이 아니라, 같은 action label 집합 안에서 policy가 기준과 다른 선택을 한 것이다.

### Pipeline에서의 흐름

```text
텍스트 입력
-> user_utterance를 고객 transcript처럼 사용
-> ai_current_intent / ai_utterance / transcript / speech signal로 policy input 구성
-> AI Action Policy 실행
-> actual_action 생성
-> expected_action과 actual_action 비교
```

오디오 파일 입력이나 마이크 입력 후보로 넘어가도 뒤쪽 판단 구조는 같다. 달라지는 것은 `user_utterance`가 바로 들어오느냐, 오디오가 STT/signal 단계를 거쳐 transcript와 speech signal로 바뀌느냐다. `event_type`과 `expected_user_intent`는 policy 입력이 아니라 evaluation과 error analysis에서 케이스 의미를 해석하는 기준 annotation으로 본다.

### 평가 해석

| actual_action | 해석 |
| --- | --- |
| `stop_and_switch` | expected와 일치 |
| `respond_and_continue` | 의도 전환을 놓쳤으므로 `missed_switch` |
| `continue` | 의도 전환을 놓쳤으므로 `missed_switch` |
| `ask_clarifying` | 확신 부족 대응. 기준에 따라 `action_confusion` 또는 별도 분석 대상 |

## 예시 B. Backchannel

### 상황 요약

AI가 배송 상태를 설명하고 있다. 고객이 "네, 알겠어요"라고 짧게 맞장구를 친다.

이 장면에서 중요한 것은 고객 발화가 있다는 사실이 아니라, 고객이 새 업무를 요청하지 않았다는 점이다.

### Scenario Card

```json
{
  "scenario_id": "commerce_backchannel_001",
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "네, 알겠어요.",
  "event_type": "backchannel",
  "expected_user_intent": null,
  "expected_action": "continue",
  "has_user_speech": true,
  "user_tone_hint": "neutral"
}
```

### 왜 false stop이 생기나

과거 VAD-only placeholder나 단순 speech-event 기준은 고객 발화가 있으면 의미를 보지 않고 개입으로 판단하기 쉽다.

```text
has_user_speech = true
-> "사용자가 말했으니 AI가 멈춘다"
-> backchannel에서도 멈춤
-> false_stop
```

현재 `policy_v1`의 목표는 이 케이스를 줄이는 것이다. 고객 발화가 있어도 transcript와 tone hint를 보고 단순 backchannel이면 현재 설명을 계속하거나 짧게 인정하고 이어간다.

### 평가 해석

| actual_action | 해석 |
| --- | --- |
| `continue` | expected와 일치 |
| `brief_ack` | 허용 기준에 따라 자연스러운 응답으로 볼 수 있음 |
| `respond_and_continue` | 불필요한 개입이므로 `false_stop` |
| `stop_and_switch` | 불필요한 전환이므로 `false_stop` |

## 자주 생기는 오해

| 헷갈리는 생각 | 정정 |
| --- | --- |
| `input_mode`는 AI가 말하는 방식이다 | 아니다. 같은 판단 케이스를 텍스트, 오디오 파일, 마이크 후보 중 어떤 입력 경로로 실행할지 나타내는 보조 필드다 |
| `event_type`은 policy가 내는 결과다 | 아니다. 고객 신호의 종류를 나타낸다 |
| `expected_action`은 policy 실행 결과다 | 아니다. 사람이 정한 기준 행동이다 |
| `expected_action`과 `actual_action`은 서로 다른 action 체계다 | 아니다. 같은 action label vocabulary를 기준/결과 역할로 나눈 것이다 |
| `actual_action`을 `data/scenarios.json`에 넣어도 된다 | 아니다. 실행 결과는 `results/runs/{run_id}/`에 둔다 |
| Text Replay는 음성 프로젝트에서 벗어난다 | 아니다. audio/STT 앞단을 고정하고 policy 판단만 먼저 검증하는 텍스트 입력 경로다 |
| scenario는 전체 상담 플로우다 | 아니다. policy 평가 가능한 한 순간의 테스트 카드다 |

## 문서 작성 패턴

새 용어나 설명을 추가할 때는 아래 순서를 지킨다.

1. 상황을 먼저 한 문장으로 요약한다.
2. 그 장면이 어떤 schema key/value로 표현되는지 쓴다.
3. 어떤 값이 policy input이고 어떤 값이 기준 annotation/정답인지 나눈다.
4. `expected_action`과 `actual_action`을 비교한다.
5. 틀렸다면 primary failure 5종 중 하나로 설명한다.

이 순서를 지키면 용어 설명이 사전식 나열로 흐르지 않고, 팀원이 실제 판단 흐름을 따라갈 수 있다.
