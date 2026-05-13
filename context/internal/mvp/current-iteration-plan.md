# Current MVP Iteration Plan

이 문서는 현재 MVP의 Step별 작업 흐름을 정리한다.

Step N은 달력 날짜가 아니라 MVP 작업 iteration이다. 완료된 일은 실제 날짜와 commit을 함께 적고, 예정 작업은 planned로만 둔다.

Step은 실행 경계가 아니라 작업 흐름을 설명하는 기록 단위다. 최신 사용자 지시를 우선하고, 필요하면 완료/진행 중인 Step을 넘나들어 작업한다.

## Step 1 - completed on 2026-05-08

### 실제 완료

- 하네스와 backend/MkDocs 초기 구조가 main에 들어왔다.
- policy naming을 `baseline`, `policy_v1`, `policy_v2`, `policy_v3`로 맞췄다.
- action label에서 `pause`를 제거하고 `respond_and_continue` 기준을 반영했다.
- intent ID를 영문 snake case로 표준화했다.
- `data/scenarios.json`에 커머스 판단 케이스 30개를 만들었다.
- `data/scenario_stats.json`에 event/action/level/intent 분포 snapshot을 남겼다.

### 증거

| commit | 의미 |
| --- | --- |
| `601ce8a`, `d5bfbea` | 하네스와 project initialization 브랜치 main 병합 |
| `9a6e019` | policy 이름을 `baseline`, `policy_v1`, `policy_v2`, `policy_v3`로 정리 |
| `640ccaf` | `pause`를 `respond_and_continue`로 변경 |
| `5fcacd2`, `d78968e` | 판단 케이스 schema와 docs 예시의 intent ID 정리 |
| `4273baa` | `data/scenarios.json`, `data/scenario_stats.json` 추가 |
| `4a47619` | scenario stats 분포 정정 |

### Step 1 종료 시점에는 아직 완료라고 보지 않았던 것

- `src/runner.py`, `src/interruption_detection/evaluation/`, `src/interruption_detection/policies/`는 현재 active code로 아직 없다.
- `results/runs/{run_id}/` artifact는 현재 active branch 기준으로 아직 없다.
- Workbench/Playground UI는 제품 완성본이 아니라 실험 surface로 다뤘다.

## Step 2 - completed on 2026-05-09

### 실제 완료

- `data/scenarios.json` loader와 schema validation을 현재 기준으로 만들었다.
- action label, event type, policy input/output 타입을 정의했다.
- `src/runner.py`를 만들고 텍스트 입력(Text Replay), CLI, Backend, Test Bench가 같은 entry를 쓰게 했다.
- `baseline`과 `policy_v1`을 최소 구현했다.
- Test Bench evaluator를 만들고 `results/runs/{run_id}/` artifact를 생성했다.
- failure를 primary 5종 기준으로 분류하고 `error_analysis.md`를 남겼다.
- FastAPI API와 정적 Playground UI를 같은 runner/evaluator entry 위에 연결했다.
- UI를 좌측 상위 sidebar, Playground, Test Bench Report(배치 평가 화면) 탭 구조로 정리했다.
- Playground에서는 `Inspect selected policy`와 `Compare all policies`를 분리해 단일 policy 상세와 전체 policy 비교를 따로 보게 했다.
- Test Bench Report(배치 평가 화면)에서는 `Run selected policy`, `Run all policies`, run card, decision log table, `run_meta.json` 뷰로 artifact를 확인하게 했다.
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
| UI live check on `http://127.0.0.1:8000` | HTML, `/runs`, 판단 케이스 predict 응답 확인 |

## Step 3 - in progress on 2026-05-09

### 작업 중인 방향

- Step 2의 `baseline`, `policy_v1` 하드코딩 placeholder를 텍스트 입력을 보고 LLM이 바로 `actual_action`을 고르는 방식으로 전환한다.
- 오디오 입력은 원래 이번 단계에서 제외했지만, 텍스트 입력 판단과 Playground 직접 입력이 예상보다 빨리 닫혀 대표 오디오 파일 입력(Audio File Test)을 같은 iteration 안에서 input adapter로 당겨 구현한다.
- `expected_actions`, `event_type`, `expected_user_intent`는 LLM prompt에 넣지 않는다. LLM은 AI intent, AI 발화, 고객 transcript, speech signal, 정책별 추가 prompt 기준으로 `actual_action`을 선택한다.
- Playground는 판단 케이스 replay뿐 아니라 자유 텍스트 입력도 같은 `/predict`와 runner 경로로 판단하게 한다.
- Test Bench는 같은 evaluator를 유지하고, LLM policy run artifact를 새로 생성해 Step 2 placeholder run과 구분한다.

### 현재 구현 메모

- `src/interruption_detection/llm.py`에 OpenAI Responses API structured output client를 둔다.
- `baseline`은 최소 텍스트 context만 쓰는 LLM 기준선이다.
- `policy_v1`은 action label 정의, few-shot 예시, tone hint를 더한 LLM 정책이다.
- 오디오 파일 입력(Audio File Test)은 `data/scenarios.json`을 수정하지 않고 별도 manifest와 TTS fixture 파일을 input adapter로 읽는다.
- 실제 Whisper STT와 precomputed transcript adapter를 분리해, STT 품질과 runner 합류 경계를 따로 검증한다.
- Test Bench Report(배치 평가 화면)는 입력 경로(`input_mode`)를 선택해 텍스트 판단 케이스 묶음과 audio manifest batch를 같은 `/runs`와 artifact 계약으로 실행한다.
- 테스트는 실제 API를 호출하지 않고 fake LLM client로 runner/API/evaluator 경계를 검증한다.
- Step 3 기준 `signals.interpreted_user_intent`, `signals.is_intent_shift`, `signals.confidence`는 LLM이 `actual_action`을 고르면서 함께 남긴 참고값이었다. 이후 공통 pipeline 작업에서는 고객 발화를 어떻게 이해했는지 더 쉽게 확인할 수 있도록, 이 값을 `predicted_event_type`, `predicted_user_intent`, `ambiguity`, `signal_source` 같은 이름으로 정리한다.

## Step 4 - in progress on 2026-05-12

### 작업 중인 방향

- Text/Audio 입력 뒤에 공통 고객 신호 해석(`Interpreter Pipeline`)과 AI 행동 선택(`AI Action Selector`) 흐름을 둔다.
- `baseline`, `policy_v1`도 같은 해석/행동 흐름을 통과한다.
- 기존 `actual_action` 생성과 `expected_actions` vs `actual_action` 평가 흐름은 유지한다.
- `predicted_event_type`, `predicted_user_intent`, `confidence`, `ambiguity`, `signal_source`, `interpreter_steps`는 대표 성능 수치가 아니라 실패 이유를 보기 위한 `signals` 점검값으로 남긴다.
- `signals.interpreted_user_intent`, `signals.is_intent_shift`는 migration 호환 alias로 한 단계 유지한다.

### 현재 구현 메모

- 첫 구현은 LLM structured output을 사용해 고객 신호 해석 결과와 `actual_action`을 함께 받는다.
- 기존에도 LLM user prompt에는 `event_type`, `expected_user_intent`, `expected_actions`을 넣지 않았다. 이번 구현은 그 guard를 유지하면서, runner가 policy 호출 시 runtime 필드만 담은 `PolicyInput`으로 변환해 policy 입력 표면을 좁힌다.
- 정책 코드는 이 결과를 `CustomerSignalInterpretation`으로 정규화한 뒤 `signals`에 표준 키와 legacy alias를 함께 남긴다.
- Text Replay와 Audio File Test는 기존처럼 같은 `runner.run_input` 경로로 합류한다.
- `event_type`, `expected_user_intent`, `expected_actions`은 evaluator/error analysis 기준값으로만 쓰며, LLM user prompt에는 넣지 않는다.
- Test Bench UI는 dataset registry를 통해 공식 core dataset과 진단용 edge slice를 구분해 실행한다.

## Step 5+ - candidate slots

아래는 확정 계획이 아니라 Step 4 결과를 보고 조정할 후보 슬롯이다.

| 후보 | 열리는 조건 |
| --- | --- |
| Policy v2 (`policy_v2`) | 공통 해석/행동 선택 흐름 위에서 backchannel/noise/no_speech의 false_stop을 먼저 안정화할 때 |
| 대표 오디오 파일 입력(Audio File Test) 확장 | 대표 케이스 수를 늘리거나 Whisper STT 결과를 수치 비교에 포함할 때 |
| Policy v3 (`policy_v3`) | same intent follow-up과 intent shift 구분 강화가 다음 병목으로 확인될 때 |
| Mic Trial 기대 action 선택 | 마이크 발화가 원래 scenario의 `expected_actions`와 다른 의도를 테스트해 Playground `match`/`mismatch`가 사용자가 기대한 행동을 기준으로 봐야 할 때 |
| `brief_ack` 유지 여부 | `continue`와 합치거나 독립 label로 유지할 필요가 실제 run에서 드러날 때 |
| STT 연결 방식 | 실제 Whisper/API, local Whisper, precomputed transcript의 책임 경계를 확정할 때 |
| 최종 발표 초점 | 제품 데모, 실험 결과, 실패 분석 중 무엇을 앞세울지 정할 때 |

### 차기 작업 메모 - Policy v3 + Mic Trial 기대 action 선택

2026-05-14 이후 후보 작업으로 둔다. 오늘 Mic Trial 구현 범위에는 넣지 않는다.

- `policy_v3`는 same intent follow-up과 intent shift 구분을 강화하는 정책 후보로 계획한다.
- Mic Trial은 기존 scenario context를 재사용하되, 개발자가 마이크로 넣은 고객 발화가 원래 scenario의 `expected_actions`와 다른 테스트 의도일 수 있음을 인정한다.
- Playground의 Mic Trial 영역에 action label select를 추가해 개발자가 이번 마이크 발화에서 기대하는 행동을 고르게 한다.
- Mic Trial 실행 결과의 `match`/`mismatch`는 원본 scenario `expected_actions`가 아니라 개발자가 선택한 기대 action을 기준으로 계산한다.
- 이 선택값은 Playground Mic Trial 평가용 override로만 쓰고, `data/scenarios.json`의 기준 `expected_actions`는 수정하지 않는다.
- LLM/policy prompt에는 기존 guard처럼 `expected_actions`나 개발자 선택 기대 action을 넣지 않는다. 선택값은 policy 실행 후 결과 판정에만 사용한다.
- 결과 UI에는 원본 scenario 기준과 Mic Trial 선택 기준을 구분해 보여준다. 예: `scenario expected_actions`와 `mic expected_action`을 별도 행으로 표시한다.
- 공식 Test Bench 수치와 run artifact에는 바로 섞지 않는다. Mic Trial 선택 기준을 공식 평가로 승격하려면 별도 input manifest나 run artifact 계약을 먼저 정한다.

## 작성 체크

- 완료된 작업과 예정 작업을 같은 문장에 섞지 않았는가?
- 다른 브랜치의 scaffold나 run artifact를 current MVP의 입력처럼 쓰지 않았는가?
- Playground 화면 수치를 외부 인용 가능한 평가 수치처럼 쓰지 않았는가?
- 미실측 목표 수치를 결과처럼 쓰지 않았는가?
- 초기 기획 문서의 표현을 현재 기준 어휘로 정규화했는가?
