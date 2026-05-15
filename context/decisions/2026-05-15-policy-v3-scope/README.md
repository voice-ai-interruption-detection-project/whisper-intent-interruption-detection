---
date: 2026-05-15
status: active
related_pr:
related_runs: 20260515_110153_policy_v2, 20260515_110243_policy_v3, 20260515_111904_policy_v3_1, 20260515_111953_policy_v3_1, 20260515_112306_policy_v2
skill_source: record-decision
tags: [policy, dataset, evaluation]
---

# Policy v3 Scope

## 정리

`policy_v3`는 `same_intent_question`과 `intent_shift` 경계를 더 잘 구분하기 위한 prompt-only 정책 후보로 둔다. 이번 범위에서는 selector 구조, evaluator 기준, action label vocabulary를 바꾸지 않는다. 효과 확인은 core dataset 수치와 별도 diagnostic dataset을 분리해서 본다.

## 범위

- `data/scenarios_policy_v3_edge.json`
- `data/scenarios_policy_v3_challenge.json`
- `data/datasets.json`
- `src/interruption_detection/policies/policy_v3.py`
- `tests/test_datasets.py`, `tests/test_policies.py`, `tests/test_api.py`
- `results/runs/{run_id}/`에 남길 core/challenge run artifact

## 배경

현재 MVP는 AI가 말하는 중 고객 발화가 들어왔을 때 다음 action을 고르는 판단 구조를 비교한다. 기존 core dataset은 same-intent follow-up과 intent shift 경계 오판을 강하게 드러내는 slice가 아니므로, policy prompt를 바꾸기 전에 경계 진단용 minimal pair dataset을 먼저 준비하기로 했다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: prompt 변경 효과를 core 안정성 확인과 challenge 경계 진단으로 분리해서 볼 수 있다.
- 나빠진 것: 공식 core 성능 수치와 별개로 diagnostic run을 추가로 해석해야 한다.
- 감수한 부분: `policy_v3`는 아직 selector 독립화나 complaint/handoff 세부 정책을 다루지 않는다.

## Run 기록

- `20260515_110153_policy_v2`: `policy_v3_challenge` diagnostic run, `action_accuracy=0.7778`.
- `20260515_110243_policy_v3`: `policy_v3_challenge` diagnostic run, `action_accuracy=0.8333`.
- challenge run에서는 `policy_v2`만 `policy_v3_challenge_shipping_to_cancel_001`을 `respond_and_continue`로 놓쳤고, `policy_v3`는 `stop_and_switch`로 맞췄다. 반면 반품/환불 인접 업무 두 건은 `policy_v3`도 여전히 `missed_switch`로 남았다.
- `20260515_111904_policy_v3_1`: `policy_v3_challenge` diagnostic run, `action_accuracy=0.9444`. 반품/환불 인접 업무 `missed_switch`는 0건으로 내려갔다.
- `20260515_112306_policy_v2`: core dataset 비교 run, `action_accuracy=0.8667`. 같은 core dataset에서 `policy_v3_1`은 `0.9`로 높고 `missed_switch`는 2건에서 1건으로 줄었다.
- `20260515_111953_policy_v3_1`: core dataset 비교 run, `action_accuracy=0.9`.
- core 비교에서 `policy_v3_1`은 `commerce_return_to_shipping_001`, `commerce_product_to_shipping_001`을 맞췄지만, `commerce_payment_follow_001`은 `false_stop`, `commerce_complaint_001`은 `missed_switch`로 새 회귀가 생겼다.

## 후속 점검

- [x] `policy_v3_challenge` diagnostic run artifact 생성
- [x] `policy_v2`와 `policy_v3_1` core 비교 run artifact 생성
- [x] Mic Trial expected action override는 공식 Test Bench 수치와 분리
- [x] 반품/환불 인접 업무 경계를 `policy_v3.1` prompt에서 다시 본다
- [ ] `policy_v3_1` 결과를 한 번 더 반복 실행하거나 고정 seed/fixture 전략을 검토해 LLM 변동성을 확인한다
- [ ] `policy_v3_1`의 core 회귀 케이스(`payment_follow`, `complaint`)를 별도 follow-up에서 점검한다
