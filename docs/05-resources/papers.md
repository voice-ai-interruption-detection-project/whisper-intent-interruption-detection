# Related Papers & References

## 이 페이지의 위치

이 페이지는 현재 MVP 구현 설명이 아니라, 후속 확장을 위한 참고 주제 목록입니다.

현재 MVP의 공식 구조는 아래를 기준으로 봅니다.

- LLM structured output 기반 action judgment
- 공통 runner/evaluator
- Text Replay와 Audio File Test adapter
- `results/runs/{run_id}/` artifact

## Speech / Audio

| 주제 | 왜 보는가 |
| --- | --- |
| VAD | 실제 음성 입력에서 speech/no-speech 구간을 다룰 때 필요 |
| Whisper / STT | Audio File Test와 Mic Trial에서 transcript를 얻는 입력 adapter 후보 |
| Audio signal summary | RMS, duration 같은 기본 신호를 run artifact에 남길 때 참고 |

현재 최종 수치는 STT 모델 성능 수치가 아니라, precomputed transcript 또는 text 기준 policy 판단 수치로 읽어야 합니다.

## Dialogue / Turn Taking

| 주제 | 왜 보는가 |
| --- | --- |
| Turn-taking | AI가 말하는 중 고객이 발화권을 가져오는 순간을 해석하기 위해 |
| Backchannel | "네", "음" 같은 수신 확인 신호를 과한 개입으로 보지 않기 위해 |
| Grounding | 고객 신호를 짧게 인정하고 이어가는 행동을 설명하기 위해 |

## Intent / Action Decision

현재 MVP는 LLM structured output으로 runtime 고객 신호 해석과 action 후보를 함께 받고, 이를 pipeline에서 구조화해 기록합니다.

후속 실험 후보:

- rule-based selector를 별도 component로 분리
- LLM interpreter와 LLM/action selector를 2단계로 분리
- sentence embedding 기반 intent 후보를 보조 신호로 추가
- complaint/handoff 기준을 별도 policy로 정리

## Evaluation

현재 공식 지표:

```text
actual_action in expected_actions
-> action_match
-> action_accuracy
```

후속으로 검토할 수 있는 지표:

- binary intervention precision/recall
- intent shift recall
- backchannel false stop rate
- STT transcript mismatch와 action failure의 관계

예시 label은 현재 action vocabulary를 기준으로 둡니다.

```python
y_true = ["continue", "stop_and_switch", "respond_and_continue"]
y_pred = ["continue", "respond_and_continue", "respond_and_continue"]
```

## 현재 다음 연구 질문

1. `policy_v3_1`의 LLM 변동성은 같은 dataset 반복 실행에서 얼마나 큰가?
2. complaint와 handoff는 action label을 어떻게 나눠야 하는가?
3. ambiguous 발화에서 `ask_clarifying`, `brief_ack`, `continue` 경계를 어떻게 정할 것인가?
4. Audio File Test에서 실제 Whisper transcript 오류가 policy 실패에 얼마나 영향을 주는가?

## 다음

👉 [Repository](./repo.md)
