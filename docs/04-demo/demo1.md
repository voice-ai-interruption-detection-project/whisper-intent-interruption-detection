# Demo 1: 맞장구를 과한 개입으로 보지 않기

## 상황

```text
AI: 현재 배송 중이며 내일 오후 도착 예정입니다.
고객: 네, 알겠어요.
```

고객은 새 요청을 한 것이 아니라 AI 설명을 들었다는 신호를 보냈습니다.

## 자연스러운 행동

`expected_actions`는 `continue` 또는 `brief_ack`입니다.

```text
continue:
AI가 하던 설명을 그대로 이어간다.

brief_ack:
"네, 이어서 안내드리겠습니다."처럼 짧게 인정한 뒤 이어간다.
```

## 현재 구현에서 보는 것

이 케이스는 단순 음성 감지보다 transcript 의미가 중요하다는 점을 보여줍니다.

정책은 prompt에 `event_type=backchannel` 정답을 받지 않습니다. 대신 runtime 입력인 `user_utterance`, `has_user_speech`, `ai_current_intent`, `ai_utterance`를 보고 판단합니다.

## 왜 중요한가

맞장구를 `stop_and_switch`로 판단하면 AI가 불필요하게 상담 흐름을 끊습니다. 현재 MVP에서는 이런 실패를 `false_stop`으로 분류합니다.

`policy_v2`는 backchannel, noise, no-speech 안정화를 겨냥한 guidance를 추가한 정책입니다. 최신 core run에서 `policy_v2`의 `false_stop`은 0건이었습니다.

- run_id: `20260515_112306_policy_v2`
- dataset: `data/scenarios.json`
- action_accuracy: `0.8667`
- failures: `missed_switch=2`, `ambiguous_intent=2`

## 다음

👉 [Demo 2: Intent Shift](./demo2.md)
