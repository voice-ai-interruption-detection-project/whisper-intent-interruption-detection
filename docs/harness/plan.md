# 하네스 적용 계획

작성일: 2026-05-07 (Work Bench framing + dev baseline 반영)

## 이 문서가 답하는 것

- 코드나 실험을 시작하기 전, "지금 단계에서 어디까지 만들어야 하나"를 잡으려고 본다.
- 새 PR을 올리기 전, dev baseline·run artifact 계약·가벼운 규칙을 다시 확인하려고 본다.
- 원칙 본문은 [concept.md](concept.md)에 있다. 이 문서는 적용에만 집중한다.

## 한눈에

| 단계 | 목표 | 핵심 산출물 |
| --- | --- | --- |
| 0단계 (Dev baseline) | 코드 1커밋이 들어오기 전 dev 가드를 깐다 | `pyproject.toml` + lock, ruff, pre-commit + secret scan, README quickstart |
| 1단계 (Work Bench MVP) | Playground와 Test Bench가 같은 runner로 한 번 끝까지 이어진다 | `src/contracts.py`, `src/runner.py`, `src/app.py`, `src/eval/run_scenarios.py`, `results/runs/` |
| 2단계 | 대표 Audio File Test가 같은 정책 입력으로 합류, 정책 버전 비교가 안정화된다 | `data/audio_mapping.json`, `src/input_adapters/audio_file.py`, failure taxonomy 정착 |
| 3단계 | Mic Trial 또는 반복 실험에서 부분 재실행과 fixture 재사용이 필요해진다 | route/controller 분리, planner, override layer, fixture fingerprint |

각 단계는 다음 단계가 무엇을 추가할지 미리 알면서, **그 단계에서 필요한 것만** 만든다.

## 0단계: Dev baseline

코드 1커밋이 들어오기 직전에 깔아두면 비용이 작은 가드. "Sensor는 실수가 보인 뒤"의 예외다 — 이 항목들은 늦게 깔수록 비대칭으로 비싸진다(lock 없이 의존성이 굳으면 과거 run을 못 살리고, secret이 한 번 새면 회수 불가).

| 항목 | 도구 | 깔아두는 이유 |
| --- | --- | --- |
| 의존성 핀 + lock | `pyproject.toml` + uv (또는 poetry, pip-tools) | 재현성. 정책 비교 외부의 변동(라이브러리 버전)을 차단 |
| python 버전 핀 | `pyproject.toml`의 `requires-python` | 환경 차이로 인한 결과 변동 차단 |
| format/lint | ruff (format+lint 통합) | reformat diff가 정책 변경 commit에 섞이는 것 방지 |
| pre-commit + secret scan | `pre-commit` + `detect-secrets` 또는 `gitleaks` | API key·HF token이 새는 사고 차단 |
| README quickstart | 3-5줄 (설치, 실행, 테스트) | 페어가 같은 환경 재현 가능 |

**아직 안 한다:** mypy strict, coverage threshold, GitHub Actions CI workflow, branch/PR 템플릿, devcontainer. 1단계 진행하면서 필요해지면 그때.

## 1단계: Work Bench MVP

Playground와 Test Bench가 한 번 끝까지 이어지는 단계. 둘은 같은 runner를 호출한다.

```text
Playground 흐름 (평소 dev 표면)
  text input
  -> input_adapters.text_replay
  -> runner(policy_name, PolicyInput)
  -> 화면 결과 (action / reason / signals / latency)
  -> sessions/today.jsonl (선택)

Test Bench 흐름 (마일스톤 표면)
  data/scenarios.json
  -> input_adapters.text_replay
  -> runner(policy_name, PolicyInput) for each
  -> evaluation.evaluator
  -> results/runs/{run_id}/{run_meta, evaluation, decision_logs, error_analysis}
```

> **P0~P3**는 정책 버전 라벨이다. P0는 "신호가 있으면 무조건 멈춤"의 베이스라인, P1은 event 종류별 매핑, P2는 intent shift 추가, P3는 escalation까지 보는 풀 룰. 같은 evaluator·같은 입력으로 비교해야 P0→P3의 개선이 의미를 갖는다.

### 첫 코드 골격

폴더명은 구현 과정에서 조정할 수 있지만, 책임은 섞지 않는다.

```text
data/
  scenarios.json              # 사람이 정한 기준 (Test Bench용 expected_action)
  audio_mapping.json          # 2단계에서 추가

src/
  contracts.py                # ActionLabel, PolicyInput, PolicyOutput
  input_adapters/
    text_replay.py            # scenario / playground input -> PolicyInput
    audio_file.py             # 2단계에서 추가
  policies/
    p0_vad_only.py            # baseline
    p1_event_type.py
    p2_intent_shift.py
    p3_action_policy.py
  runner.py                   # 공유 진입점 — Playground와 Test Bench가 둘 다 호출
  evaluation/
    evaluator.py              # expected vs actual (Test Bench용)
    metrics.py                # action accuracy, false stop, missed switch, latency
  app.py                      # Playground 진입 (Streamlit / Gradio / FastAPI+HTML 중 택1)
  eval/
    run_scenarios.py          # Test Bench batch entry — runner를 호출

results/runs/{run_id}/
  run_meta.json               # 12 필드 (아래 참조)
  evaluation.json             # metric summary
  decision_logs.jsonl         # scenario별 signal/reason/action
  error_analysis.md           # 실패 유형과 다음 수정 포인트

sessions/                     # Playground 가벼운 로그 (선택)
  YYYY-MM-DD.jsonl
```

책임 분리 (한 줄 요약):

- `data/`는 사람이 정한 기준만 담는다 (Test Bench 전용).
- `src/contracts.py`는 정책들이 공유하는 입력/출력 약속.
- `src/input_adapters/`는 Text/Audio/Mic 차이를 PolicyInput으로 맞춘다.
- `src/policies/`는 판단 로직만 담는다.
- `src/runner.py`는 Playground와 Test Bench가 둘 다 호출하는 단일 진입점.
- `src/evaluation/`은 Test Bench의 결과 비교와 metric만 담는다. **detection 판정 로직을 다시 구현하지 않는다** — runner를 호출한다.
- `src/app.py`는 Playground UI — runner를 호출한다. 정책 판정 로직을 직접 구현하지 않는다.
- `src/eval/run_scenarios.py`는 Test Bench batch — runner를 호출한다.
- `results/`는 Test Bench 산출물만 담고, 기준 원본을 덮어쓰지 않는다.
- `sessions/`는 Playground의 가벼운 로그(선택). 외부 인용 금지.

### Run artifact 최소 계약 (Test Bench)

결과는 덮어쓰지 않는다. 모든 run은 `run_id` 폴더 아래 저장한다.

`run_meta.json` 필수 필드:

| 필드 | 이유 |
| --- | --- |
| `run_id` | 결과 식별과 비교 |
| `timestamp` | 시간 추적 |
| `source` | `cli` / `eval` / `demo` / `manual-review` 중 어느 경로에서 실행됐는지 |
| `mode` | `baseline` / `compare` |
| `target` | 이번 실행이 만들 산출물 (`policy` / `eval` / `report`) |
| `changed` | 직전 baseline 대비 바뀐 stage 목록 |
| `dataset` | scenario set id 또는 dataset id |
| `policy_version` | P0~P3 |
| `policy_snapshot` | threshold, intent description, action label set |
| `criteria_snapshot` | eval 기준, action label 정의 버전 |
| `latency_ms` | total 및 stage별 (transcribe / detect / intent / policy) |
| `command` | 실행에 쓴 명령 |

핵심은 **결과 수치만 저장하지 않는다**는 점이다. 어떤 입력으로 어떤 정책을 어떤 설정으로 실행했는지가 같은 위치에 있어야 한다.

Playground는 이 계약을 따르지 않는다 — 그래서 Playground 결과는 외부 인용 출처가 될 수 없다.

### 첫 실행 흐름 완료 기준

코드가 있다는 것이 아니라 아래가 모두 이어질 때 완료다.

**Playground 측:**

- `app.py`를 띄우면 정책 P0~P3 중 최소 P0/P1을 즉시 입력으로 호출 가능하다.
- 화면에 `action`, `reason`, `signals`, `latency`가 표시된다.
- 정책 드롭다운을 바꾸면 같은 입력에 다른 결과를 즉시 본다.

**Test Bench 측:**

```text
data/scenarios.json
-> text_replay adapter
-> runner를 통해 P0~P3 중 최소 P0/P1 실행
-> evaluator
-> results/runs/{run_id}/evaluation.json
-> results/runs/{run_id}/decision_logs.jsonl
-> results/runs/{run_id}/run_meta.json
```

체크리스트:

- 동일 scenario set으로 둘 이상의 정책 버전을 batch 실행할 수 있다.
- 모든 정책 output은 `actual_action`, `reason`, `signals`를 가진다.
- evaluator는 `expected_action`과 `actual_action`을 같은 기준으로 비교한다.
- evaluator는 detection 판정을 다시 구현하지 않고 runner를 호출한다.
- **Playground app.py도 detection 판정을 다시 구현하지 않고 runner를 호출한다.**
- result에는 실행 조건(`run_meta.json` 필수 필드)이 모두 남는다.
- 같은 결과 폴더가 두 번 만들어지지 않는다 (overwrite 방지).
- README/report에 쓰는 수치는 `results/runs/{run_id}`에서 다시 찾을 수 있다 (Playground 화면에서 본 수치는 인용 안 함).

### 가벼운 규칙 (Test Bench 작업 시)

| 상황 | 적용 규칙 |
| --- | --- |
| 새 action label 추가 | label 이름, 의미, expected_action 예시를 같이 남긴다 |
| 새 정책 버전 추가 | 기존 evaluator를 그대로 통과해야 한다 |
| threshold 변경 | 상수/config 이름으로 바꾸고 `run_meta`에 남긴다 |
| Playground/Test Bench 변경 | 양쪽이 여전히 같은 runner를 호출하는지 확인한다 |
| README/report 수치 작성 | result artifact와 decision log를 먼저 확인한다 (Playground 화면 수치 인용 금지) |
| 리팩토링 | 정책 동작 변경과 파일 이동을 가능한 한 분리한다 |

### 검토 역할 (report-only)

작업 흐름의 4지점에서 가벼운 검토를 거친다. 아래 역할들은 [.claude/agents/](../../.claude/agents/)에 4개 agent로 정의되어 있어서, 필요한 시점에 호출해서 report를 받을 수 있다 (파일 수정은 메인 작업자가 한다).

| 시점 | 역할 | 확인할 것 | agent |
| --- | --- | --- | --- |
| scenario/action label 초안 후 | 자료/기준 검토 | expected_action이 제품 행동으로 충분히 구분되는가 | `experiment-material-collector` |
| 첫 runner 작성 후 | 구조 검토 | adapter, policy, evaluator, runner, app(Playground) 책임이 섞이지 않았는가 | `harness-structure-reviewer` |
| 첫 result 생성 후 | 수치 검증 | README/report 수치가 result와 맞는가 | `result-evidence-checker` |
| 실패 사례가 쌓인 후 | 실패 분류 | false stop, missed switch, action confusion으로 나뉘는가 | `failure-classifier` |

## 2단계: Audio File Test와 정책 비교

Text Replay가 잡힌 뒤 대표 Audio File Test를 연결하고, 정책 버전 비교와 실패 분석이 늘어나는 단계다.

추가:

- `data/audio_mapping.json`: audio file ↔ scenario id ↔ transcript 출처 연결
- `src/input_adapters/audio_file.py`: audio/transcript를 PolicyInput으로 변환
- failure taxonomy 정착: false stop / missed switch / action confusion / ambiguous intent / STT uncertainty
- evidence check 절차 정착: report 수치 ↔ result/decision log 대조
- code review checklist: 기능 변경, 리팩토링, config 변경이 한 PR에 섞였는지

도입 후보:

- **Override layer** — 실험에서 threshold/policy/model을 반복 변경하기 시작하면 `with override_policy(threshold=..., debounce_ms=...):` 형태의 작은 helper를 만든다. block을 빠져나오면 무조건 원래 값으로 복원해서, 실험용 변경이 다음 실행을 오염시키지 않게 한다. 정상 종료/예외/중첩/모르는 field 4가지 동작을 테스트한다.
- **하네스 invariant 테스트** — 기능 테스트와 별개로 "result overwrite 금지", "snapshot 필수 key 누락 금지", "override 복원", "eval-runner 실제 호출", "Playground app도 runner 호출", "criteria version 분리" 같은 하네스 규칙 자체를 테스트.
- **CI workflow** — lint(ruff) + (선택) pytest를 PR마다. 1단계가 안정되면.

이 단계부터 일부 report-only agent를 저장소 안의 local 정의로 둘 근거가 강해진다.

## 3단계: Mic Trial / Console Extension / 반복 실험

Mic Trial, simulated live chunk, dashboard 화면 확장, 또는 같은 dataset을 반복 실험하면서 단계별 부분 실행이 필요해지면 도입한다.

추가 후보:

- route/controller와 정책 pipeline 분리
- demo 입력과 evaluation 입력 구분
- public report와 internal note 경계
- smoke test, 엄격한 typecheck(mypy strict)
- **실행 계획기 (planner)** — 변경 영향에 따라 stage 단위로 `fresh / fixture / skip`을 결정한다. baseline은 모두 fresh로 돌리고, compare는 변경된 stage와 그 downstream만 fresh, 나머지는 이전 결과 재사용. 매번 전체를 다시 돌리지 않게 해준다.
- **Fixture fingerprint** — transcript / signal / intent / 정책 결과 같은 중간 산출물을 재사용할 때, 현재 설정과 fixture 설정이 같은지 확인하는 hash 키. 다르면 재사용을 거부.
- 반복 위반이 확인된 지점의 hook/scanner

## 실패 분류 축

실패는 두 축으로 본다. 섞지 않는다.

### Primary — 결과 분류 (사용자 시점, 보고서 단어)

| 분류 | 의미 |
| --- | --- |
| false stop | 멈추지 말아야 할 때 멈춤 (예: 맞장구) |
| missed switch | 흐름 전환을 놓침 (예: 환불 의사를 무시) |
| action confusion | 다른 action label로 판단 (예: pause vs stop_and_switch) |
| ambiguous intent | intent가 모호할 때 잘못된 가정 |
| STT uncertainty | transcript 불확실성으로 인한 오판 |

### Secondary — 진단 축 (디버깅 시점)

각 결과 사례를 어디 층 문제로 귀속시킬지 본다.

- transcription 문제인가
- acoustic / silence signal 문제인가
- intent label 문제인가
- policy threshold 문제인가
- eval 기준 문제인가
- latency / streaming 문제인가

primary는 보고서·README가 쓰는 단어다. secondary는 "이 false stop은 왜 났지?"를 추적할 때만 켠다. 두 축을 한 평면에 나열하지 않는다.

## Sensor 추가 조건

자동 강제 장치는 실제 문제가 보인 뒤 추가한다 (단, 0단계 dev baseline은 예외).

| 반복되는 문제 | 추가할 Sensor 후보 |
| --- | --- |
| result가 덮어써져 이전 비교를 잃음 | run_id 생성 규칙 강제, overwrite 방지 checker |
| threshold가 여러 파일에 흩어짐 | config/named constant check |
| README 수치가 result와 불일치 | evidence check script 또는 report checker |
| Playground 화면 수치가 외부에 인용됨 | 인용 위치에 `run_id` 강제 (출처 표기 lint) |
| scenario 기준 원본에 actual 결과가 섞임 | data guard |
| Playground app이 정책 판정을 다시 구현 | 구조 review (harness-structure-reviewer) |
| runner가 자주 깨짐 | smoke test |
| API key가 코드에 들어갈 위험 | secret scanner (0단계에서 이미 깔림) |

핵심은 "처음부터 다 막기"가 아니라, 실제로 실수한 곳을 다음부터 덜 실수하게 만드는 것이다.

## 바로 적용할 원칙 (요약)

| 원칙 | 적용 방식 |
| --- | --- |
| 루트 지침은 얇게 둔다 | `CLAUDE.md`에는 항상 필요한 협업/경계 규칙만 둔다 |
| 0단계 baseline은 예외 | dev 가드는 코드 1커밋 전에 깐다 |
| 두 surface는 같은 runner 호출 | Playground app, Test Bench batch, demo 모두 runner.py를 통과 |
| 기준과 결과를 분리한다 | `expected_action`은 기준 원본에, `actual_action`은 results에 둔다 |
| 입력은 변환하고 판단은 공유한다 | Text/Audio/Mic을 같은 PolicyInput으로 맞춘다 |
| 정책 contract를 고정한다 | 모든 정책이 `actual_action`, `reason`, `signals`를 반환한다 |
| 같은 evaluator로 비교한다 | P0~P3가 같은 metric 계산을 통과한다 |
| eval은 runner를 재사용한다 | evaluator는 detection 판정을 다시 구현하지 않는다 |
| Playground도 runner를 재사용한다 | app.py는 정책 판정을 직접 구현하지 않는다 |
| 결과는 덮어쓰지 않는다 | run_id 폴더로 분리한다 |
| latency도 결과다 | run_meta에 stage별 latency_ms를 남긴다 |
| decision log를 남긴다 | action label만이 아니라 판단 이유를 남긴다 |
| 검증된 수치만 공유한다 | 외부 인용은 Test Bench artifact에서만, Playground 화면 수치 금지 |
| 반복 실수에만 강제 장치를 더한다 | hook/scanner는 실제 위반 패턴이 보일 때 만든다 |

## 아직 하지 않을 것

- 완성형 하네스 framework 전체 설치
- mypy strict, coverage threshold, devcontainer
- GitHub Actions CI workflow (1단계 진행 중 안정되면)
- 장기 지식 허브용 폴더 지도 도입
- RAG/QA/VLM/Supabase 전용 규칙 복사
- Live Mic 중심 하네스 선도입
- 광범위 hook/scanner 선도입
- 검증 전 성능 수치 확정
- planner / fixture fingerprint / override layer / harness invariant test의 1단계 도입

## 다음 작업

**0단계 (Dev baseline) — 코드 들어오기 전:**

1. `pyproject.toml` 만들고 python 버전 핀 + uv lock
2. ruff 설정 + pre-commit 훅 (ruff + detect-secrets)
3. README quickstart 3-5줄

**1단계 (Work Bench MVP):**

1. scenario schema와 action label 초안.
2. policy I/O contract (`src/contracts.py`).
3. `src/runner.py` — Playground와 Test Bench가 공유하는 단일 진입점.
4. Playground 진입 `src/app.py` — 즉시 입력 → 화면 결과.
5. Test Bench batch `src/eval/run_scenarios.py` — scenarios.json → run artifact.
6. 같은 evaluator로 `expected_action`과 `actual_action`을 비교한다.
7. `results/runs/{run_id}/`에 `run_meta.json`, `evaluation.json`, `decision_logs.jsonl`을 생성한다 (run_id 기반, overwrite 방지).
8. `run_meta.json`에 source, latency_ms, policy/criteria snapshot을 포함한다.
9. README/report에는 result에서 확인한 수치만 옮긴다 (Playground 화면 수치 금지).
