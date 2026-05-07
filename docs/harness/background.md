# 하네스 가이드 — 페어 공유용 한 장

작성일: 2026-05-07

## 이 한 장에 담은 것

페어가 깊이 들어가기 전에 **이 한 장만 읽고도** 다음 셋을 잡고 가게 만들었다.

- 이 하네스가 **어디서 왔는지** (배경과 근거)
- 하네스가 **무엇을 약속하는지** (`concept.md`의 핵심 원칙)
- 그게 **어떻게 굴러가는지** (`plan.md`의 단계별 적용)

자세한 본문은 각각 [concept.md](concept.md)와 [plan.md](plan.md)에 있다. 이 페이지는 그 둘을 묶어 보여주는 안내판이다.

## 1. 어디서 왔나

이 프로젝트는 Whisper 기반 intent/interruption detection을 다루는 팀 사이드 프로젝트다. 2차 회의에서 MVP가 단순 "interruption detector"가 아니라 **"AI가 말하는 도중 고객 신호가 들어왔을 때 어떻게 반응할지를 비교 실험하는 콘솔(Test Bench)"** 으로 잡혔다.

이 정의가 모든 결정의 anchor였다. "감지 정확도"보다 "정책 버전 비교가 다시 추적 가능한가"가 핵심이라서, 결과를 어디까지 보존할지를 먼저 정해야 했다.

근거가 된 자료는 네 묶음. 각각 다른 판단을 도와줬다.

1. **외부 AI coding harness 사례** (gstack, Superpowers, BMAD, Codex/Claude 공식 가이드) — 단계 gate 감각과 "evidence 없이 완료를 말하지 않는다"를 가져옴. framework 통째로는 안 가져옴 (1주차 POC에 무겁다).
2. **비슷한 문제를 푼 내부 사례** (장기 지식 허브, 글쓰기 운영 repo) — "원천을 보호하고 검증을 분리한다", report-only agent 패턴을 가져옴.
3. **이전 RAG/QA 파이프라인 프로젝트 (sprint-4)** — 가장 직접적인 선례. `run_id` 폴더, snapshot 함께 저장, eval=runner 재사용을 그대로 가져옴. override layer / planner / fixture fingerprint는 **지금 필요한 실체가 없어서** 2~3단계로 미룸.
4. **회의 결정 (Test Bench)** — 위 셋을 합칠 때 anchor.

자세한 분석은 [research/](research/) 아래에 archive로 남아 있다. 평소 작업엔 들어갈 일 없고 "왜 이건 안 가져왔지?" 같은 질문이 생겼을 때만 들춘다.

## 2. 무엇을 약속하나 — `concept.md`의 6 원칙

`concept.md`는 잘 안 바뀌는 원칙 layer다. 위 자료들이 공통적으로 가리키는 방향을 6개로 압축했다.

| # | 원칙 | 짧은 예시 |
| --- | --- | --- |
| 1 | 기준 원본과 실행 결과를 섞지 않는다 | `expected_action`은 [data/scenarios.json](../../data/scenarios.json), `actual_action`은 [results/runs/](../../results/) — 한 파일에 같이 못 들어감 |
| 2 | 입력 방식은 달라도 판단 구조는 하나 | Text/Audio/Mic이 달라도 정책에 들어가는 형태는 `PolicyInput` 하나 |
| 3 | 작은 완주 단위로 닫는다 | "코드 짜고 끝" X. sample run + decision log + report 검증까지 가야 완주 |
| 4 | 설정과 실행 조건을 결과 옆에 남긴다 | 결과 폴더에 수치만이 아니라 threshold·정책 버전·latency까지 같이 |
| 5 | eval은 실제 pipeline을 재사용한다 | evaluator는 정책을 다시 구현하지 않고 runner를 호출 |
| 6 | Agent와 skill은 역할로 본다 (report-only) | 검증·분류는 agent가, 파일 수정은 사람이 |

각 원칙의 본문과 표는 [concept.md](concept.md)에 있다.

## 3. 어떻게 굴러가나 — `plan.md`의 단계

`plan.md`는 위 6 원칙을 단계별 코드/문서 구조로 옮긴다. 한눈에:

| 단계 | 목표 | 핵심 산출물 |
| --- | --- | --- |
| 1단계 | Text Replay MVP가 한 번 끝까지 이어진다 | [src/contracts.py](../../src/contracts.py), [src/runners/run_text_replay.py](../../src/runners/run_text_replay.py), [results/runs/](../../results/) |
| 2단계 | Audio File Test가 같은 정책 입력으로 합류, 정책 비교 안정화 | `data/audio_mapping.json`, `src/input_adapters/audio_file.py`, failure taxonomy |
| 3단계 | Mic Trial / 반복 실험에서 부분 재실행 필요 | planner, override layer, fixture fingerprint |

1단계의 실행 흐름:

```text
data/scenarios.json
  -> text_replay adapter
  -> P0~P3 정책 (P0=베이스라인, P1=event 매핑, P2=intent shift, P3=풀 룰)
  -> evaluator
  -> results/runs/{run_id}/run_meta.json + evaluation.json + decision_logs.jsonl
```

각 run은 `run_meta.json`에 `run_id` / `source` / `policy_snapshot` / `criteria_snapshot` / `latency_ms` / `command` 등을 같이 남긴다 (전체 12 필드는 plan.md의 표 참조). 같은 `run_id` 폴더가 이미 있으면 두 번째 실행은 거부된다 — overwrite 사고가 코드로 막힌다.

검토는 4지점에 걸친다. 각 시점마다 [.claude/agents/](../../.claude/agents/)에 정의된 report-only agent를 부르면 됨.

| 시점 | agent | 보는 것 |
| --- | --- | --- |
| scenario·label 초안 후 | `experiment-material-collector` | 흩어진 자료를 한 카드로 |
| 첫 runner 작성 후 | `harness-structure-reviewer` | 8개 boundary leak 점검 |
| 첫 result 생성 후 | `result-evidence-checker` | 문서 수치 ↔ result artifact 대조 |
| 실패 사례 쌓인 후 | `failure-classifier` | primary/secondary 두 축 분류 |

## 4. 원칙이 끝까지 어떻게 떨어지는지 (예시 한 건)

원칙 1: "기준 원본과 실행 결과를 섞지 않는다"

```text
원칙       기준 원본과 실행 결과를 섞지 않는다
  -> 폴더    data/  vs  results/
  -> 코드    data/scenarios.json에는 expected_action만 / decision_logs.jsonl에는 actual_action만
  -> 검토    harness-structure-reviewer가 점검 항목 1번으로 "data/ 아래에 actual_action이 새지 않았나" 본다
```

같은 invariant가 **원칙 → 폴더 경계 → 코드 → agent 점검 항목**까지 4단계에 걸쳐 깔린다. 다른 5개 원칙도 같은 식으로 떨어져 있다.

## 더 깊이 보고 싶을 때

- 원칙만 빠르게 다시 보고 싶음 → [concept.md](concept.md)
- 지금 단계에서 무엇까지 만들어야 하는지 → [plan.md](plan.md)
- "왜 이건 안 가져왔지?" 같은 질문 → [research/](research/)
- 작업 시 항상 켜둘 가드 → [.claude/rules/experiments.md](../../.claude/rules/experiments.md)
- 검토용 4 agent → [.claude/agents/](../../.claude/agents/)
