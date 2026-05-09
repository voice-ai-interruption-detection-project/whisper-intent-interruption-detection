# Schema Key Reference

이 문서는 scenario와 run log에서 보이는 key가 어떤 층위의 정보를 담는지 맞추기 위한 내부 기준 자료다.

핵심은 key와 value를 분리해서 읽는 것이다.

```text
event_type = intent_shift
^^^^^^^^^^   ^^^^^^^^^^^^
schema key   value
```

`event_type`은 값을 담는 자리이고, `intent_shift`는 그 자리에 들어가는 값이다. `expected_action = stop_and_switch`도 마찬가지다. `expected_action`은 기준 행동을 담는 key이고, `stop_and_switch`는 action label vocabulary의 값이다.

## Scenario 원본 key

`data/scenarios.json`은 사람이 정한 기준 원본이다. 이 파일에는 policy 실행 결과를 넣지 않는다.

| schema key | 값 예시 | 층위 | 정하는 주체 | 헷갈리지 말 것 |
| --- | --- | --- | --- | --- |
| `scenario_id` | `commerce_shipping_to_refund_001` | 식별자 | 사람 | 제품 기능명, policy version |
| `level` | `1`, `3`, `5` | 판단 난이도 | 사람 | event type의 우선순위 |
| `domain` | `commerce` | 업무 도메인 | 사람 | intent 자체 |
| `ai_current_intent` | `shipping_inquiry` | AI가 이어가던 업무 의도 | 사람 | 고객의 새 의도 |
| `ai_utterance` | `현재 상품은 배송 중이며...` | AI가 말하던 문장 | 사람 | input mode |
| `user_utterance` | `환불받고 싶은데요` | 고객이 끼어든 발화 | 사람 또는 transcript | event type |
| `has_user_speech` | `true`, `false` | 음성/발화 신호 여부 | 사람 또는 신호 처리 | 의미 있는 의도 여부 |
| `user_tone_hint` | `neutral`, `frustrated`, `urgent` | 톤 힌트 | 사람 또는 추론 | complaint label 자체 |
| `event_type` | `intent_shift` | 고객 신호의 종류 | 사람 또는 분류기 | AI가 해야 하는 행동 |
| `expected_user_intent` | `refund_request`, `null` | 고객 발화에서 읽히는 업무 의도 | 사람 또는 intent detector | AI의 현재 의도 |
| `expected_action` | `stop_and_switch` | 기준/정답 action label | 사람 | policy 실행 결과 |
| `notes` | `배송에서 환불로 전환` | 라벨링 근거 | 사람 | metric, decision log |

## Result 쪽 key

policy를 실행한 뒤 생기는 값은 `results/runs/{run_id}/`에 둔다. 기준 원본과 같은 파일에 섞지 않는다.

| result key | 값 예시 | 층위 | 생성 시점 | 위치 |
| --- | --- | --- | --- | --- |
| `policy_version` | `policy_v2` | 실행한 policy 식별자 | 실행 시점 | `run_meta.json`, `decision_logs.jsonl` |
| `actual_action` | `respond_and_continue` | policy가 낸 action label | 실행 후 | `decision_logs.jsonl` |
| `signals` | `{ "intent_similarity": 0.22 }` | 판단에 사용한 신호 | 실행 후 | `decision_logs.jsonl` |
| `reason` | `intent shift로 판단` | policy 판단 이유 | 실행 후 | `decision_logs.jsonl` |
| `is_correct` | `true`, `false` | expected/actual 일치 여부 | 평가 후 | `decision_logs.jsonl` |
| `action_accuracy` | `0.83` | 전체 action label 일치율 | 평가 후 | `evaluation.json` |

## 자주 헷갈리는 조합

| 보이는 표현 | 읽는 법 | 헷갈림 |
| --- | --- | --- |
| `event_type = backchannel` | 고객 신호가 맞장구라는 뜻 | AI 행동이 `backchannel`이라는 뜻이 아니다 |
| `expected_action = respond_and_continue` | 사람이 정한 기준 행동이 답하고 이어가기라는 뜻 | policy가 이미 그렇게 실행했다는 뜻이 아니다 |
| `actual_action = stop_and_switch` | policy가 실행 후 전환을 선택했다는 뜻 | scenario 원본의 정답을 바꾼다는 뜻이 아니다 |
| `expected_user_intent = null` | 고객 발화에서 업무 의도가 없거나 불명확하다는 뜻 | 고객 신호가 없다는 뜻은 아니다 |
| `has_user_speech = false` | 의미 있는 고객 발화가 없다는 뜻 | 항상 `no_speech`만 뜻하지 않는다. noise는 별도 event type일 수 있다 |

## 작성 체크

- schema key와 enum value를 같은 말처럼 설명하지 않았는가?
- `data/scenarios.json`에 `actual_action`, metric, decision log를 넣지 않았는가?
- `event_type`을 AI 행동처럼 설명하지 않았는가?
- `expected_action`을 policy 실행 결과처럼 설명하지 않았는가?
- `actual_action`을 action label 목록의 새 값처럼 설명하지 않았는가?
