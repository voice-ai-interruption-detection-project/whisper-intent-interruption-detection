# Team & Timeline

## 프로젝트 형태

Wind는 2인 페어 중심으로 진행한 팀 사이드 프로젝트입니다.

| 이름 | 주요 담당 |
| --- | --- |
| 함명연 |  |
| 심혜진 |  |

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

추후 추가 예정입니다.

## 향후 보완할 부분

| 항목 | 상태 |
| --- | --- |
|  |  |

## 다음

👉 [Repository](./repo.md)
