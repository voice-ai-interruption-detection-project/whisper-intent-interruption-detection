# Evaluation and Results Contract

이 문서는 평가 지표, 실패 분류, run artifact 위치를 맞추기 위한 내부 기준 자료다.

`docs/`에 성능 수치나 평가 설명을 옮기기 전, 이 계약을 먼저 기준으로 본다.

## Source of Truth 분리

| 영역 | 담는 것 | 담지 않는 것 |
| --- | --- | --- |
| `data/scenarios.json` | 기준 원본, expected action, 라벨링 근거 | actual action, metric, decision log |
| `results/runs/{run_id}/` | policy 실행 결과, metric, decision log, run metadata | 기준 판단 케이스 원본 수정본 |
| `context/internal/` | 평가 기준 초안, 용어, 계약 설명 | 외부 인용 가능한 확정 수치 |
| `docs/` | 공개/공유용으로 다듬은 설명 | 출처 없는 수치, 실험 전 단정 |

`expected_actions`는 사람이 정한 기준 행동 목록이고, `actual_action`은 policy 실행 결과다. 두 값이 같은 파일에 섞이면 기준이 바뀐 것인지 policy가 바뀐 것인지 추적하기 어렵다.

`expected_actions`와 `actual_action`은 같은 action label vocabulary를 쓴다. 차이는 label 종류가 아니라 평가에서 맡는 역할이다.

| 항목 | 평가 역할 | 예시 값 | 저장 위치 |
| --- | --- | --- | --- |
| `expected_actions` | 기준/정답 목록 | `["stop_and_switch"]`, `["continue", "brief_ack"]` | `data/scenarios.json` |
| `actual_action` | policy 결과/예측 | `respond_and_continue` | `results/runs/{run_id}/decision_logs.jsonl` |

`action_accuracy`는 `actual_action`이 해당 케이스의 `expected_actions`에 포함되는지 비교한 비율이다. 대부분의 케이스는 기준 행동 하나만 허용하지만, `backchannel` 케이스는 팀 검증 기준에 따라 `continue`와 `brief_ack`를 모두 허용한다.

복수 정답을 허용하는 케이스에서는 단일 primary label 기준으로 공식 평가하지 않는다. evaluator는 `actual_action in expected_actions`만 공식 match로 보고, 틀린 케이스만 `mismatch_matrix`에 집계한다.

한 판단 케이스(`scenario`)가 `expected_actions`와 `actual_action` 비교로 이어지는 구체 예시는 [Scenario Worked Example](scenario-worked-example.md)을 본다.

## 행동 평가와 고객 신호 해석 점검

현재 공식 평가는 AI가 고른 `actual_action`이 케이스별 `expected_actions`에 포함되는지 보는 데 둔다. 대부분은 기준 행동 하나와 비교하지만, `backchannel`은 `continue`와 `brief_ack`를 모두 자연스러운 행동으로 인정한다. 공통 판단 흐름에 고객 신호 해석(`Interpreter Pipeline`)을 추가한 뒤에도, 최종 평가는 AI가 고른 `actual_action`이 기준과 맞는지 확인하는 방식으로 유지한다.

고객 신호 해석 결과는 처음부터 성능 점수로 세우기보다, 실패 이유를 보는 보조 점검값으로 먼저 남긴다.

| 기준값 | 실행 중 나온 값 후보 | 역할 |
| --- | --- | --- |
| `event_type` | `predicted_event_type` | 고객 신호 해석이 기준과 맞는지 보는 보조 점검 |
| `expected_user_intent` | `predicted_user_intent` | 고객 의도 해석이 기준과 맞는지 보는 보조 점검 |
| `expected_actions` | `actual_action` | 최종 행동 평가 |

`predicted_event_type`과 `predicted_user_intent`가 추가되더라도 바로 `action_accuracy`와 같은 대표 성능 수치로 말하지 않는다. 먼저 `decision_logs.jsonl`의 `signals`나 별도 점검 필드에 남기고, 실제로 어떤 실패를 설명해 주는지 본다. 공유 문서나 발표에서는 `action_accuracy`와 섞어 말하지 않고, 필요할 때만 "고객 신호 해석 점검값"처럼 조건을 붙여 쓴다.

주의할 점은 사람이 정한 `scenario.event_type`을 policy 실행 중 곧바로 action으로 바꾸지 않는 것이다. 실행 중에는 transcript/signal을 보고 고객 신호를 따로 해석하고, 그 결과를 AI 행동 선택(`AI Action Selector`)이 참고하는 흐름만 허용한다.

기존에도 LLM user prompt에는 `event_type`, `expected_user_intent`, `expected_actions`를 넣지 않았다. 이번 구현은 그 guard를 유지하면서, API/evaluator 경계의 `RunnerInput`을 policy 호출 시 runtime 판단에 필요한 필드만 담은 `PolicyInput`으로 변환해 policy 입력 표면을 좁힌다.

## Run Artifact 최소 계약

새 평가 결과는 아래 구조를 기준으로 둔다.

```text
results/runs/{run_id}/
├── run_meta.json
├── evaluation.json
├── decision_logs.jsonl
└── error_analysis.md
```

`run_id`는 `{YYYYMMDD_HHMMSS}_{policy_name}` 패턴을 쓴다.

| 파일 | 역할 |
| --- | --- |
| `run_meta.json` | 실행 조건. `run_id`, `timestamp`, `source`, `mode`, `target`, `changed`, `dataset`, `policy_version`, `policy_snapshot`, `criteria_snapshot`, `latency_ms`, `command`를 포함한다 |
| `evaluation.json` | 전체 metric, mismatch matrix, failure summary, latency |
| `decision_logs.jsonl` | 판단 케이스별 signals, reason, expected_actions, actual_action, action_match |
| `error_analysis.md` | 실패 케이스 해석과 다음 실험 후보 |

같은 `run_id` 폴더를 덮어쓰지 않는다.

공통 파이프라인에서는 `decision_logs.jsonl`의 `signals`에 `predicted_event_type`, `predicted_user_intent`, `confidence`, `ambiguity`, `signal_source`, `interpreter_steps` 같은 점검값을 남긴다. 이 값들은 기준 원본인 `data/scenarios.json`에 쓰지 않는다.

## 지표 이름

| 지표 | 의미 | 인용 조건 |
| --- | --- | --- |
| `action_accuracy` | `actual_action`이 `expected_actions`에 포함된 비율 | `evaluation.json`에서 확인 |
| `binary_metrics.accuracy` | intervention 필요 여부를 이진으로 본 정확도 | binary 기준을 함께 설명 |
| `false_stop_rate` | 멈추지 말아야 할 때 개입으로 판단한 비율 | 어떤 event/action 기준인지 명시 |
| `missed_switch_rate` | 전환해야 할 때 전환하지 못한 비율 | intent shift 기준을 명시 |
| `latency_ms` | 실행 지연 시간 | 측정 위치와 source를 함께 기록 |

`Accuracy`만 단독으로 쓰지 않는다. action 기준인지 binary 기준인지 같이 적는다.

고객 신호 해석 점검에서 계산한 일치율이 생기더라도 `action_accuracy`와 섞지 않는다. 예를 들어 `event_type` 해석 일치율은 "고객 신호 해석 점검" 또는 "predicted_event_type match"처럼 별도 이름과 조건으로 기록한다.

## Failure Taxonomy

현재 평가 계약에서 쓰는 primary failure는 아래 5종이다. 공유 문서와 리포트에는 이 이름과 의미를 기준으로 쓴다.

| primary | 의미 | 예시 |
| --- | --- | --- |
| `false_stop` | 멈추지 말아야 할 때 개입으로 판단 | backchannel인데 `respond_and_continue`나 `stop_and_switch`로 판단 |
| `missed_switch` | 흐름 전환을 놓침 | intent shift인데 `continue` 또는 `respond_and_continue`로 판단 |
| `action_confusion` | 다른 valid action으로 판단 | `respond_and_continue`와 `stop_and_switch` 경계 혼동 |
| `ambiguous_intent` | 입력 자체에서 intent가 불명확 | 고객 발화가 모호해 기준 action도 흔들림 |
| `STT_uncertainty` | transcript 노이즈가 판단 오류를 유발 | 오디오/STT 결과가 불확실 |

디버깅이 필요할 때는 secondary 축으로 `transcription`, `signal`, `intent`, `policy_threshold`, `eval_criteria`, `latency_streaming`을 쓴다.

Primary와 secondary를 같은 평면에 섞지 않는다.

## 수치 인용 규칙

공유 문서, PR, 발표 자료에 수치를 쓸 때는 아래를 같이 남긴다.

- `run_id`
- dataset 또는 판단 케이스 snapshot
- policy version
- criteria snapshot
- 실행 날짜
- `evaluation.json` 경로

실험 전 수치는 확정 표현으로 쓰지 않는다.

| 쓰면 안 되는 표현 | 가능한 표현 |
| --- | --- |
| "False Stop Rate가 25%에서 8%로 줄었다" | "목표는 false stop 감소이며, 수치는 run artifact 생성 후 확정한다" |
| "Policy v2 accuracy는 85%" | "Policy v2 목표는 missed switch 감소다. 실제 accuracy는 run 기준으로 인용한다" |
| "Playground에서 90%가 나왔다" | "`results/runs/{run_id}/evaluation.json` 기준 action_accuracy는 ..." |

다른 브랜치에서 생성된 run을 인용할 때도 branch/commit/run_id를 함께 적는다. 현재 브랜치에 없는 result는 현재 기준의 확정 수치로 쓰지 않는다.

## 비교 조건

Before/After 비교는 아래 조건이 같아야 한다.

- 같은 판단 케이스 set 또는 dataset snapshot
- 같은 criteria snapshot
- 비교하려는 변경 외 다른 policy 설정이 동일
- 각 run의 `changed` 필드가 비교 의도와 일치

조건이 다르면 수치가 좋아 보여도 "비교 불가"로 표시한다.

## 문서로 옮기기 전 체크

- 수치마다 `run_id`가 있는가?
- `results/runs/{run_id}/evaluation.json`에서 같은 값을 확인했는가?
- `action_accuracy`와 binary accuracy를 섞지 않았는가?
- primary failure 5종 밖의 단어를 새로 만들지 않았는가?
- 미실측 목표 수치를 결과처럼 쓰지 않았는가?
