# Solution Overview: 판단 구조와 정책 비교

## 판단 흐름

Wind의 MVP는 입력 방식을 새로 실험하는 것보다, 같은 상황을 넣었을 때 정책이 어떤 판단을 내리는지 검증하고 비교하는 데 초점을 둡니다.

```text
Text Replay / Audio File Test / Mic Trial
-> RunnerInput
-> PolicyInput
-> 고객 신호 해석
-> AI 행동 선택
-> actual_action
-> expected_actions와 비교
-> run artifact 기록
```

텍스트, 오디오 파일, 마이크 입력은 각각의 제품 모드가 아니라, 동일한 판단 구조를 시험해 보는 여러 입력 경로입니다.

## 공통 실행 경로

현재 CLI, Backend API, Playground, Test Bench는 모두 같은 runner 계층을 탑니다.

| 계층 | 역할 |
| --- | --- |
| `RunnerInput` | API, UI, evaluator가 같이 쓰는 입력 형식. 기준값인 `event_type`, `expected_user_intent`까지 포함 |
| `PolicyInput` | policy가 판단할 때 필요한 runtime 필드만 남긴 입력. `expected_actions`, `event_type`, `expected_user_intent`는 의도적으로 제외 |
| `DecisionPipeline` | LLM이 만든 judgment를 받아 고객 신호 해석과 AI 행동 선택 결과로 구조화 |
| evaluator | `actual_action in expected_actions`인지로 맞았는지 평가 |
| run artifact | 실행 조건, 지표, decision log, 실패 분석 결과를 기록 |

policy prompt에 정답이 되는 필드가 들어가지 않도록, 먼저 해당 필드들을 필터링해서 제외합니다.

```yaml
excluded_fields:
  - expected_actions
  - event_type
  - expected_user_intent
```

## 정책 버전

policy version은 서로 다른 제품이 아니라, 같은 판단 파이프라인 위에 어떤 기준과 guidance를 추가했는지 비교하는 단위입니다.

| policy | 현재 의미 |
| --- | --- |
| `baseline` | 최소 transcript context로 판단하는 LLM-backed 기준선 |
| `policy_v1` | action label 정의와 예시를 더한 비교 대상 |
| `policy_v2` | backchannel, noise, no-speech에서 `false_stop`을 줄이는 prompt guidance |
| `policy_v3` | same-intent follow-up과 intent shift 경계를 강화하는 prompt-only 후보 |
| `policy_v3_1` | return/refund 인접 workflow 경계를 더 명시한 prompt-only 후보 |

## 구현 기준

현재 MVP는 LLM의 structured output을 공통 runner/evaluator에 연결해, 같은 판단 구조를 여러 policy로 반복 실행하고 성능을 비교하는 형태로 구현돼 있습니다.

`DecisionPipeline`은 runtime 입력을 받아 고객 신호 해석과 AI 행동 선택 결과를 한 번에 구조화하고, 이 결과를 CLI, Backend API, Playground, Test Bench가 같은 방식으로 공유하도록 맞춰 줍니다. 그래서 어떤 입력 경로와 UI를 쓰더라도 동일한 판단 로직과 평가 체계 위에서 실험할 수 있습니다.

## 최신 결과 요약

| dataset | policy | action_accuracy | 주요 실패 |
| --- | --- | ---: | --- |
| core | `policy_v2` | 0.8667 | missed_switch 2, ambiguous_intent 2 |
| core | `policy_v3_1` | 0.9000 | false_stop 1, missed_switch 1, ambiguous_intent 1 |
| challenge | `policy_v2` | 0.7778 | missed_switch 3, ambiguous_intent 1 |
| challenge | `policy_v3_1` | 0.9444 | ambiguous_intent 1 |

수치 출처:

- `results/runs/20260515_112306_policy_v2/evaluation.json`
- `results/runs/20260515_111953_policy_v3_1/evaluation.json`
- `results/runs/20260515_110153_policy_v2/evaluation.json`
- `results/runs/20260515_111904_policy_v3_1/evaluation.json`

## 다음

👉 [Action Labels](./action-labels.md)
