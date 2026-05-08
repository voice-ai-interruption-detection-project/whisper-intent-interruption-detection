# Experiment Rules

이 파일은 Test Bench(scenario set batch eval) 작업 시 참고하는 가이드다. Playground는 expected_action·run artifact 계약이 없어서 이 파일을 거치지 않는다. 작업 라우팅은 루트 [CLAUDE.md](../../CLAUDE.md)를 본다.

## Source of Truth 분리

- `data/scenarios.json` 안에 `actual_action`, `policy_*` 같은 결과 필드를 쓰지 않는다. 기준 원본만 둔다.
- `actual_action`, metric, decision log는 `results/runs/{run_id}/`에만 쓴다.
- `data/` 안 파일을 수정해야 할 때는 의도가 "기준 원본 변경"인지 "결과 기록"인지 먼저 명시한다.

## Run artifact 최소 계약

새 result를 만들 때 `results/runs/{run_id}/`에 다음 4개를 같이 만든다.

- `run_meta.json` — 필수 필드: `run_id`, `timestamp`, `source` (`cli`/`eval`/`demo`/`manual-review`), `mode`, `target`, `changed`, `dataset`, `policy_version`, `policy_snapshot`, `criteria_snapshot`, `latency_ms`, `command`
- `evaluation.json` — `action_accuracy`, `failures` (primary frame), `confusion_matrix`, `latency_ms`
- `decision_logs.jsonl` — case별 `reason`, `signals`, `stage_latencies_ms`
- `error_analysis.md` — 실패 케이스 (없으면 비어있어도 됨)

`run_id`는 `{YYYYMMDD_HHMMSS}_{policy_name}` 패턴을 유지한다. 같은 `run_id` 폴더가 이미 있으면 두 번째 실행은 거부한다.

## 코드 변경 단위 (실험 측)

- 새 action label 추가: label 이름, 의미, 어떤 expected_action 예시가 있는지 같이 기록한다.
- 새 policy version 추가: 기존 evaluator를 그대로 통과하는 형태를 기준으로 둔다 (eval 코드 변경 없음).
- threshold 변경: 상수/생성자 인자로 바꾸고 `policy_snapshot`에 노출시킨다. magic number는 줄인다.

리팩토링·의존성·한 번에 한 변수 같은 일반 개발 가드는 [coding.md](coding.md)에 둔다.

## eval과 Playground는 같은 runner를 호출한다

- `src/evaluation/*`은 detection 판정 로직을 다시 구현하지 않는다.
- `src/app.py`(Playground)도 정책 판정을 직접 구현하지 않는다 — 같은 `src/runner.py`를 호출한다.
- `src/backend/`(FastAPI API 진입)도 정책 판정을 직접 구현하지 않는다 — 같은 `src/runner.py`를 호출한다.
- demo, CLI, eval, Playground, Backend API가 같은 runner entry를 통과한다. 새 entry를 만들면 기존 runner를 재사용하는지 먼저 확인한다.

## 검증된 수치만 공유한다

- README, report, presentation, slack 등에 수치를 인용할 때는 `results/runs/{run_id}` 가 존재하고 같은 값을 가져야 한다.
- Playground 화면에서 본 수치는 외부 인용 출처로 쓰지 않는다. 같은 정책으로 Test Bench batch를 한 번 돌려서 run artifact를 만든 다음 인용한다.
- 외부 공유 전에는 `result-evidence-checker` agent로 한 번 더 본다.
- 외부 docs 어휘는 primary 5종(`false_stop`, `missed_switch`, `action_confusion`, `ambiguous_intent`, `STT_uncertainty`) 중 정의된 것만 사용한다.

## 실패는 두 축으로 본다

- Primary (사용자 시점): `false_stop`, `missed_switch`, `action_confusion`, `ambiguous_intent`, `STT_uncertainty`. 보고서·README가 쓰는 단어.
- Secondary (디버깅 시점): `transcription`, `signal`, `intent`, `policy_threshold`, `eval_criteria`, `latency_streaming`. 디버깅할 때만 켠다.
- 두 축을 평면에 섞어 나열하지 않는다.
- 실패 케이스가 쌓인 직후 `failure-classifier` agent로 두 축 분류 결과를 받는다 (issue·다음 실험 계획 직전).

## 규칙 추가 기준

이 파일에 추가할 새 규칙은 실험 재현성, 비교 가능성, 수치 인용 정확도를 높이는지 기준으로 본다. 가벼운 체크리스트는 먼저 추가해도 되고, hook/scanner 같은 자동 체크는 목적과 범위만 짧게 남긴다.
