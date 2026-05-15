# Context

## 선택지

- `policy_v3`를 prompt guidance와 few-shot만 바꾸는 정책 버전으로 둔다.
- selector를 실제 action 선택 주체로 독립화한다.
- complaint, severity, handoff 세부 기준까지 함께 정책화한다.

## 기각한 이유

selector 독립화는 `DecisionPipeline`, `ActionSelector`, latency, schema, 테스트 범위가 함께 바뀐다. prompt 변경과 같은 실험으로 묶으면 결과 차이의 원인을 분리하기 어렵다.

complaint, severity, handoff 기준은 더 많은 케이스와 합의가 필요하다. 이번 slice는 결제, 배송, 반품, 환불 맥락에서 같은 업무 안의 보충 질문과 업무 전환만 겨냥한다.

## 판단이 바뀐 지점

core dataset은 `policy_v3`의 목표 경계를 강하게 검증하기보다 정책 등록, prompt snapshot, artifact 계약 유지 여부를 보는 용도로 둔다. 경계 개선 여부는 `policy_v3_edge` diagnostic dataset에서 본다.

## 연결된 파일

- `policyV3_quide.md`
- `data/scenarios_policy_v3_edge.json`
- `data/scenarios_policy_v3_challenge.json`
- `data/datasets.json`
- `src/interruption_detection/policies/policy_v3.py`
- `results/runs/{run_id}/run_meta.json`
