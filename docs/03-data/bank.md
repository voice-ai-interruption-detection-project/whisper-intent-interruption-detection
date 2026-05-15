# Scenario Bank: 현재 데이터셋

## Core Dataset

현재 공식 Test Bench 기준 원본은 `data/scenarios.json`입니다.

| 항목 | 값 |
| --- | --- |
| dataset_id | `core` |
| path | `data/scenarios.json` |
| scope | `official` |
| scenario 수 | 30 |
| 지원 입력 경로 | `text`, `audio_file` |

## Event Type 분포

| event_type | 개수 |
| --- | ---: |
| `no_speech` | 4 |
| `noise` | 4 |
| `backchannel` | 6 |
| `same_intent_question` | 6 |
| `intent_shift` | 6 |
| `complaint` | 2 |
| `ambiguous` | 2 |
| **합계** | **30** |

## Action 기준 분포

`expected_actions`는 복수 정답을 허용합니다. 특히 `backchannel` 일부 케이스는 `continue`와 `brief_ack`를 모두 자연스러운 행동으로 봅니다.

| expected_actions set | 개수 |
| --- | ---: |
| `continue` | 8 |
| `continue|brief_ack` | 6 |
| `brief_ack` | 1 |
| `respond_and_continue` | 6 |
| `stop_and_switch` | 6 |
| `ask_clarifying` | 1 |
| `handoff` | 2 |

전체 30개 케이스의 상세 분포는 `data/scenario_stats.json`과 `data/scenarios.json`을 함께 봅니다.

## Diagnostic Datasets

정책별 경계를 더 잘 보기 위해 공식 core와 별도의 diagnostic slice를 둡니다.

| dataset_id | path | 목적 |
| --- | --- | --- |
| `policy_v2_edge` | `data/scenarios_policy_v2_edge.json` | backchannel, noise, no-speech false_stop 안정화와 짧은 명확 요청 회귀 확인 |
| `policy_v3_edge` | `data/scenarios_policy_v3_edge.json` | same-intent question과 intent shift minimal pair 1차 진단 |
| `policy_v3_challenge` | `data/scenarios_policy_v3_challenge.json` | return/refund, payment/cancel, shipping/address처럼 가까운 업무 경계 진단 |

diagnostic run은 core accuracy와 섞지 않습니다. run metadata의 `dataset_id`, `dataset_scope`, `dataset_snapshot`으로 범위를 구분합니다.

## 대표 케이스

| 케이스 | scenario_id | 핵심 행동 |
| --- | --- | --- |
| 맞장구 | `commerce_backchannel_001` | `continue` 또는 `brief_ack` |
| 배송 안의 보충 질문 | `commerce_shipping_follow_001` | `respond_and_continue` |
| 배송에서 환불로 전환 | `commerce_shipping_to_refund_001` | `stop_and_switch` |
| 강한 불만 | `commerce_complaint_002` | `handoff` |
| 모호한 발화 | `commerce_ambiguous_002` | `ask_clarifying` |

## 기준 데이터

`data/scenarios.json`에는 기준 원본만 둡니다.

넣는 것:

- `event_type`
- `expected_user_intent`
- `expected_actions`
- 라벨링 근거인 `notes`

넣지 않는 것:

- `actual_action`
- metric
- decision log
- run 결과

결과는 항상 `results/runs/{run_id}/` 아래에 남깁니다.

## 다음

[Input Modes](./input-modes.md)
