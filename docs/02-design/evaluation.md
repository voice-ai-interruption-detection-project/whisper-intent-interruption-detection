# Evaluation Approach: 어떻게 평가하는가?

## 기본 원칙

공식 평가는 Playground 화면 수치가 아니라 `results/runs/{run_id}/` artifact를 기준으로 합니다.

```text
dataset 로드
-> policy 실행
-> decision_logs.jsonl 생성
-> actual_action in expected_actions 비교
-> evaluation.json 생성
-> error_analysis.md 생성
```

## 평가 기준

`expected_actions`는 사람이 정한 자연스러운 행동 기준이고, `actual_action`은 policy 실행 결과입니다.

```text
action_match = actual_action in expected_actions
action_accuracy = correct / total
```

`backchannel`처럼 `continue`와 `brief_ack`가 모두 자연스러운 케이스는 복수 정답을 허용합니다.

## Run Artifact 구조

```text
results/runs/{run_id}/
├── run_meta.json
├── evaluation.json
├── decision_logs.jsonl
└── error_analysis.md
```

| 파일 | 내용 |
| --- | --- |
| `run_meta.json` | 실행 조건, dataset, policy snapshot, criteria snapshot |
| `evaluation.json` | total, correct, action_accuracy, failures, mismatch_matrix, latency |
| `decision_logs.jsonl` | 케이스별 expected/actual, reason, signals, failure |
| `error_analysis.md` | 실패 케이스 요약 |

## 실패 분류

| primary failure | 의미 |
| --- | --- |
| `false_stop` | 멈추지 않아도 될 때 개입 또는 전환으로 판단 |
| `missed_switch` | 전환해야 할 때 계속하거나 답하고 이어감 |
| `action_confusion` | 다른 valid action으로 혼동 |
| `ambiguous_intent` | 입력 자체의 의도가 불명확한 영역에서 실패 |
| `STT_uncertainty` | transcript 노이즈가 판단 실패에 영향을 줌 |

현재 공개 수치에서는 `action_accuracy`와 primary failure를 중심으로 봅니다. binary precision/recall은 계약상 확장 가능하지만, 현재 최종 공유 수치의 중심은 아닙니다.

## 최신 Core 결과

dataset: `data/scenarios.json`

| policy | run_id | correct / total | action_accuracy | failures |
| --- | --- | ---: | ---: | --- |
| `policy_v2` | `20260515_112306_policy_v2` | 26 / 30 | 0.8667 | `missed_switch=2`, `ambiguous_intent=2` |
| `policy_v3_1` | `20260515_111953_policy_v3_1` | 27 / 30 | 0.9000 | `false_stop=1`, `missed_switch=1`, `ambiguous_intent=1` |

`policy_v3_1`은 core에서 `policy_v2`보다 1건 더 맞췄습니다. 추가로 확인할 케이스도 함께 남았습니다.

| scenario_id | expected_actions | actual_action | primary_failure |
| --- | --- | --- | --- |
| `commerce_payment_follow_001` | `respond_and_continue` | `stop_and_switch` | `false_stop` |
| `commerce_complaint_001` | `stop_and_switch` | `respond_and_continue` | `missed_switch` |
| `commerce_ambiguous_002` | `ask_clarifying` | `brief_ack` | `ambiguous_intent` |

## 최신 Challenge 결과

dataset: `data/scenarios_policy_v3_challenge.json`

| policy | run_id | correct / total | action_accuracy | failures |
| --- | --- | ---: | ---: | --- |
| `policy_v2` | `20260515_110153_policy_v2` | 14 / 18 | 0.7778 | `missed_switch=3`, `ambiguous_intent=1` |
| `policy_v3` | `20260515_110243_policy_v3` | 15 / 18 | 0.8333 | `missed_switch=2`, `ambiguous_intent=1` |
| `policy_v3_1` | `20260515_111904_policy_v3_1` | 17 / 18 | 0.9444 | `ambiguous_intent=1` |

이 challenge dataset은 반품과 환불처럼 비슷해 보이지만 실제 처리 흐름이 다른 요청을 구분하는지 확인합니다. `policy_v3_1`은 이런 요청을 같은 흐름으로 오판해 전환을 놓치는 실패인 `missed_switch`를 0건으로 줄였습니다.

## 결과 해석

현재 결과에서 읽을 수 있는 내용은 다음입니다.

- 공통 runner/evaluator와 run artifact 구조는 의도한 흐름대로 동작한다.
- Text Replay와 Audio File Test는 같은 판단 구조로 합류할 수 있다.
- `policy_v3_1`은 이전 정책들이 놓치던 반품/환불 경계를 더 명확히 했다. 반품 수거 주소나 포장처럼 현재 반품 흐름 안의 질문은 답하고 이어가지만, 환불 계좌, 금액, 입금 시점처럼 환불 업무로 넘어가는 질문은 전환하도록 개선했다.
- complaint, ambiguous, 반복 실행 안정성은 후속 기준 정리와 추가 검증 대상으로 남아 있다.

## 다음

👉 [Data & Scenarios](../03-data/schema.md)
