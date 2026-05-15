# Team & Timeline

## 프로젝트 형태

Wind는 2인 페어 중심으로 진행한 팀 사이드 프로젝트입니다.

| 역할 | 주요 담당 |
| --- | --- |
| 제품/데이터 | 문제 정의, scenario bank, action label 기준, 문서 정리 |
| 구현/평가 | runner, policy, evaluator, API, Playground, run artifact |

## 진행 요약

| 날짜 | 상태 | 주요 산출물 |
| --- | --- | --- |
| 2026-05-08 | 완료 | 하네스 초기 구조, policy naming, action label 정리, `data/scenarios.json` 30개, `data/scenario_stats.json` |
| 2026-05-09 | 완료 | scenario loader, 공통 타입, CLI runner, baseline/policy_v1, evaluator, run artifact, FastAPI API, Playground/Test Bench UI |
| 2026-05-09 이후 | 완료 | LLM structured output 기반 policy 판단, Text Replay 자유 입력, Audio File Test adapter, precomputed/Whisper transcriber 분리 |
| 2026-05-12 | 완료 | 공통 `DecisionPipeline`, `Interpreter Pipeline`, `AI Action Selector` 경계 정리 |
| 2026-05-15 | 완료 | `policy_v2`, `policy_v3`, `policy_v3_1` 실험, diagnostic dataset, core/challenge run artifact, Mic Trial expected action override |

## 현재 MVP 산출물

| 영역 | 산출물 |
| --- | --- |
| 데이터 | `data/scenarios.json`, `data/datasets.json`, diagnostic datasets, audio manifest |
| 코드 | CLI runner, FastAPI API, Playground/Test Bench UI, policies, evaluation, audio adapter |
| 평가 | `results/runs/{run_id}/` artifacts |
| 문서 | README, MkDocs `docs/`, 내부 기준 `context/internal/`, 결정 기록 `context/decisions/` |

## 최종 실험 해석

현재 MVP에서 가장 높은 core 결과는 `policy_v3_1`입니다.

- run_id: `20260515_111953_policy_v3_1`
- dataset: `core`
- correct / total: `27 / 30`
- action_accuracy: `0.9000`
- 추가 확인 케이스: `false_stop=1`, `missed_switch=1`, `ambiguous_intent=1`

challenge dataset에서는 `policy_v3_1`이 return/refund 인접 workflow 경계의 `missed_switch`를 0건으로 줄였습니다.

- run_id: `20260515_111904_policy_v3_1`
- dataset: `policy_v3_challenge`
- correct / total: `17 / 18`
- action_accuracy: `0.9444`

## 향후 보완할 부분

| 항목 | 상태 |
| --- | --- |
| 반복 실행 안정성 | 같은 dataset 반복 실행 또는 fixture 전략 검토 |
| complaint 기준 | `commerce_complaint_001` 케이스를 기준으로 세부 정책 정리 |
| ambiguous 기준 | `ask_clarifying`, `brief_ack`, `continue` 경계 추가 검토 |
| selector 구조 | action selector 역할을 단계적으로 고도화 |
| 공유 문서 | MVP 기준 설명을 유지하고, 수치는 run artifact 기준으로 인용 |

## 다음

👉 [Papers & References](./papers.md)
