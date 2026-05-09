# Current MVP Iteration Plan

이 문서는 현재 MVP의 Day별 작업 흐름을 정리한다.

Day N은 달력 날짜가 아니라 MVP 작업 iteration이다. 완료된 일은 실제 날짜와 commit을 함께 적고, 예정 작업은 planned로만 둔다.

## Day 1 - completed on 2026-05-08

### 실제 완료

- 하네스와 backend/MkDocs 초기 구조가 main에 들어왔다.
- policy naming을 `baseline`, `policy_v1`, `policy_v2`, `policy_v3`로 맞췄다.
- action label에서 `pause`를 제거하고 `respond_and_continue` 기준을 반영했다.
- intent ID를 영문 snake case로 표준화했다.
- `data/scenarios.json`에 커머스 scenario 30개를 만들었다.
- `data/scenario_stats.json`에 event/action/level/intent 분포 snapshot을 남겼다.

### 증거

| commit | 의미 |
| --- | --- |
| `601ce8a`, `d5bfbea` | 하네스와 project initialization 브랜치 main 병합 |
| `9a6e019` | policy 이름을 `baseline`, `policy_v1`, `policy_v2`, `policy_v3`로 정리 |
| `640ccaf` | `pause`를 `respond_and_continue`로 변경 |
| `5fcacd2`, `d78968e` | scenario schema와 docs 예시의 intent ID 정리 |
| `4273baa` | `data/scenarios.json`, `data/scenario_stats.json` 추가 |
| `4a47619` | scenario stats 분포 정정 |

### 아직 완료라고 보지 않는 것

- `src/runner.py`, `src/evaluator.py` 또는 `src/evaluation/`, `src/policies/`는 현재 active code로 아직 없다.
- `results/runs/{run_id}/` artifact는 현재 active branch 기준으로 아직 없다.
- Workbench/Playground UI는 완성된 제품 표면으로 보지 않는다.

## Day 2 - planned, not started

### 목표

- `data/scenarios.json` loader와 schema validation을 현재 기준으로 만든다.
- action label, event type, policy input/output 타입을 정의한다.
- `src/runner.py`를 만들고 Text Replay, CLI, Backend, Test Bench가 같은 entry를 쓰게 한다.
- `baseline`과 `policy_v1`을 최소 구현한다.
- Test Bench evaluator를 만들고 `results/runs/{run_id}/` artifact를 생성한다.
- failure를 primary 5종 기준으로 분류하고 `error_analysis.md`를 남긴다.

### 완료 조건

- `data/scenarios.json`의 30개 scenario를 로드하고 검증할 수 있다.
- `expected_action`은 scenario 원본에만 있고, `actual_action`은 run result에만 있다.
- `baseline`과 `policy_v1`이 같은 runner/evaluator를 통과한다.
- 새 run이 `results/runs/{run_id}/run_meta.json`, `evaluation.json`, `decision_logs.jsonl`, `error_analysis.md`를 만든다.
- 수치를 말할 때 run id, dataset, policy version, criteria snapshot을 함께 확인할 수 있다.
- `pause`가 코드, run artifact, 새 문서에 현재 action label로 다시 등장하지 않는다.

## Day 3+ - candidate slots

아래는 확정 계획이 아니라 Day 2 결과를 보고 조정할 후보 슬롯이다.

| 후보 | 열리는 조건 |
| --- | --- |
| Policy v2 (`policy_v2`) | `policy_v1` run에서 intent shift의 missed switch가 다음 병목으로 확인될 때 |
| Playground | runner/evaluator가 안정되어 단일 scenario 판단을 보여줄 화면이 필요할 때 |
| Backend API | runner entry가 안정되고 UI나 외부 surface가 호출할 adapter가 필요할 때 |
| 대표 Audio File Test | transcript/signal adapter가 같은 runner input으로 합류할 수 있을 때 |
| Policy v3 (`policy_v3`) | complaint, ambiguous, tone/severity hint 기준을 decision으로 고정한 뒤 |

## 작성 체크

- 완료된 작업과 예정 작업을 같은 문장에 섞지 않았는가?
- 다른 브랜치의 scaffold나 run artifact를 current MVP의 입력처럼 쓰지 않았는가?
- Playground 화면 수치를 외부 인용 가능한 평가 수치처럼 쓰지 않았는가?
- 미실측 목표 수치를 결과처럼 쓰지 않았는가?
- 초기 기획 문서의 표현을 현재 기준 어휘로 정규화했는가?
