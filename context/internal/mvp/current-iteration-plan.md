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

### Day 1 종료 시점에는 아직 완료라고 보지 않았던 것

- `src/runner.py`, `src/evaluator.py` 또는 `src/evaluation/`, `src/policies/`는 현재 active code로 아직 없다.
- `results/runs/{run_id}/` artifact는 현재 active branch 기준으로 아직 없다.
- Workbench/Playground UI는 완성된 제품 표면으로 보지 않는다.

## Day 2 - completed on 2026-05-09

### 실제 완료

- `data/scenarios.json` loader와 schema validation을 현재 기준으로 만들었다.
- action label, event type, policy input/output 타입을 정의했다.
- `src/runner.py`를 만들고 Text Replay, CLI, Backend, Test Bench가 같은 entry를 쓰게 했다.
- `baseline`과 `policy_v1`을 최소 구현했다.
- Test Bench evaluator를 만들고 `results/runs/{run_id}/` artifact를 생성했다.
- failure를 primary 5종 기준으로 분류하고 `error_analysis.md`를 남겼다.
- FastAPI API와 정적 Playground UI를 같은 runner/evaluator entry 위에 연결했다.
- UI를 좌측 Work Bench sidebar, Playground, Test Bench Report 탭 구조로 정리했다.
- Playground에서는 `Inspect selected policy`와 `Compare all policies`를 분리해 단일 policy 상세와 전체 policy 비교를 따로 보게 했다.
- Test Bench Report에서는 `Run selected policy`, `Run all policies`, run card, decision log table, `run_meta.json` 뷰로 artifact를 확인하게 했다.
- 현재 focus policy에 해당하는 run card를 강조하고, 페이지별로 실제 사용하는 sidebar 영역만 활성 표시되게 했다.
- `/runs` 목록 API를 추가해 UI가 기존 run artifact를 읽어 recent runs와 report card를 렌더링하게 했다.

### 증거

| evidence | 의미 |
| --- | --- |
| `poetry run pytest tests/ -v` | loader, policy, runner, evaluator, API, static UI 테스트 통과 |
| `poetry run ruff check src tests` | 새 Python 코드 lint 통과 |
| `results/runs/20260509_124609_baseline/` | `baseline` CLI run artifact 생성 |
| `results/runs/20260509_124609_policy_v1/` | `policy_v1` CLI run artifact 생성 |
| `src/backend/main.py`, `src/backend/static/` | FastAPI API와 Playground UI 추가 |
| `GET /runs` | 저장된 run artifact 목록을 UI에 제공 |
| UI live check on `http://127.0.0.1:8000` | HTML, `/runs`, scenario predict 응답 확인 |

## Day 3 - in progress on 2026-05-09

### 작업 중인 방향

- Day 2의 `baseline`, `policy_v1` 하드코딩 placeholder를 텍스트 기반 LLM action judge로 전환한다.
- 오디오 입력은 원래 이번 단계에서 제외했지만, 텍스트 기반 LLM action judge와 Playground 직접 입력이 예상보다 빨리 닫혀 대표 Audio File Test를 같은 iteration 안에서 input adapter로 당겨 구현한다.
- `expected_action`, `event_type`, `expected_user_intent`는 LLM prompt에 넣지 않는다. LLM은 AI intent, AI 발화, 고객 transcript, speech signal, 정책별 추가 prompt 기준으로 `actual_action`을 선택한다.
- Playground는 scenario replay뿐 아니라 자유 텍스트 입력도 같은 `/predict`와 runner 경로로 판단하게 한다.
- Test Bench는 같은 evaluator를 유지하고, LLM policy run artifact를 새로 생성해 Day 2 placeholder run과 구분한다.

### 현재 구현 메모

- `src/interruption_detection/llm.py`에 OpenAI Responses API structured output client를 둔다.
- `baseline`은 최소 텍스트 context만 쓰는 LLM 기준선이다.
- `policy_v1`은 action label 정의, few-shot 예시, tone hint를 더한 LLM 정책이다.
- Audio File Test는 `data/scenarios.json`을 수정하지 않고 별도 manifest와 TTS fixture 파일을 input adapter로 읽는다.
- 실제 Whisper STT와 precomputed transcript adapter를 분리해, STT 품질과 runner 합류 경계를 따로 검증한다.
- Test Bench Report는 input mode를 선택해 text scenario set과 audio manifest batch를 같은 `/runs`와 artifact 계약으로 실행한다.
- 테스트는 실제 API를 호출하지 않고 fake LLM client로 runner/API/evaluator 경계를 검증한다.

## Day 4+ - candidate slots

아래는 확정 계획이 아니라 Day 3 결과를 보고 조정할 후보 슬롯이다.

| 후보 | 열리는 조건 |
| --- | --- |
| Policy v2 (`policy_v2`) | `policy_v1` run에서 intent shift의 missed switch가 다음 병목으로 확인될 때 |
| 대표 Audio File Test 확장 | 대표 케이스 수를 늘리거나 Whisper STT 결과를 수치 비교에 포함할 때 |
| Policy v3 (`policy_v3`) | complaint, ambiguous, tone/severity hint 기준을 decision으로 고정한 뒤 |

## 작성 체크

- 완료된 작업과 예정 작업을 같은 문장에 섞지 않았는가?
- 다른 브랜치의 scaffold나 run artifact를 current MVP의 입력처럼 쓰지 않았는가?
- Playground 화면 수치를 외부 인용 가능한 평가 수치처럼 쓰지 않았는가?
- 미실측 목표 수치를 결과처럼 쓰지 않았는가?
- 초기 기획 문서의 표현을 현재 기준 어휘로 정규화했는가?
