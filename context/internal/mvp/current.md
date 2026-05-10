# Current MVP

이 문서는 현재 코드와 내부 기준 문서를 기준으로, 지금 닫으려는 MVP의 실행 범위를 맞추기 위한 작업용 문서다.

제품 의도를 새로 정의하는 문서가 아니다. 제품 맥락은 [Product Context](../product-context.md)를 먼저 보고, 이 문서는 구현자가 "지금 무엇을 만들고 무엇을 만들지 않는지" 빠르게 확인할 때 사용한다.

MVP 기준은 작업 중 계속 다듬어질 수 있다. 이 문서는 공개 문서나 확정 PRD가 아니라 현재 실행 기준이다.

세부 용어와 평가 계약은 이 문서가 다시 정의하지 않고 아래 active 자료를 우선한다.

| 기준 | 먼저 볼 문서 |
| --- | --- |
| MVP 문서 허브와 읽는 순서 | [MVP Execution Hub](README.md) |
| 제품 문제, 현재 범위, 후순위 범위 | [Product Context](../product-context.md) |
| 용어 층위와 읽는 순서 | [Project Language Map](../project-language-map.md) |
| schema key와 enum value | [Reference](../reference/README.md) |
| expected/actual, metric, run artifact | [Evaluation and Results Contract](../evaluation-and-results-contract.md) |
| 한 판단 케이스(`scenario`)의 끝까지 흐름 | [Scenario Worked Example](../scenario-worked-example.md) |
| Step별 완료/예정 작업 | [Current MVP Iteration Plan](current-iteration-plan.md) |

## 한 줄 MVP

음성 AI 상담에서 AI가 말하는 중 고객 신호가 들어온 한 순간을 작게 잘라, AI가 다음 행동을 어떻게 고를지 검증하는 실험 콘솔을 만든다.

현재 MVP의 초점은 interruption / intent shift 판단 구조 검증에 있다.

텍스트 입력(Text Replay)과 대표 오디오 파일 입력(Audio File Test)은 제품 개념이 아니라 이 판단 구조를 빠르게 확인하기 위한 현재 입력 경로다.

```text
AI speaking
-> customer signal
-> 판단 케이스(scenario) / transcript / signal input
-> AI 행동 판단
-> actual_action 생성
-> expected_action과 비교
-> failure와 다음 수정점 기록
```

## 현재 repo 상태

현재 브랜치 기준으로 확인한 구현 상태는 아래와 같다.

| 영역 | 현재 상태 | MVP에서의 의미 |
| --- | --- | --- |
| `data/scenarios.json` | 커머스 판단 케이스(`scenario`) 30개 있음 | 텍스트 입력(Text Replay)과 배치 평가(Test Bench)의 기준 원본 |
| `data/scenario_stats.json` | event/action/level/intent 분포 있음 | 판단 케이스 set snapshot 확인용 |
| `src/backend/PACKAGES.md` | backend dependency와 하네스 경계 설명 있음 | FastAPI/API 작업 시 책임 경계 가이드 |
| `pyproject.toml` | FastAPI, Whisper, sentence-transformers, VAD, audio/data/test 의존성 있음 | 구현 후보 dependency는 준비됨 |
| `src/runner.py`, `src/interruption_detection/runner.py` | CLI와 공통 policy 실행 entry가 있음 | 텍스트 입력(Text Replay), Backend, 배치 평가(Test Bench)가 같은 runner를 통과한다 |
| `src/interruption_detection/policies/` | `baseline`, `policy_v1`이 텍스트 LLM 판단 정책으로 전환됨 | Step 2 하드코딩 placeholder에서 실제 LLM action judge로 이동했다 |
| `src/interruption_detection/llm.py` | OpenAI Responses API용 structured output client가 있음 | `OPENAI_API_KEY`가 있을 때 실제 LLM 판단을 호출한다 |
| `src/interruption_detection/evaluation/` | 배치 평가(Test Bench) batch eval과 run artifact 생성이 있음 | `results/runs/{run_id}/` 계약으로 평가 결과를 남긴다 |
| `src/interruption_detection/audio/` | 오디오 파일 입력(Audio File Test) manifest, precomputed/Whisper STT adapter, audio signal 요약이 있음 | 오디오 입력도 같은 runner input으로 합류한다 |
| `src/backend/main.py`, `src/backend/static/` | FastAPI API와 Playground/Test Bench UI가 있음 | 판단 케이스 replay, 자유 텍스트 입력, audio upload, text/audio batch run이 같은 runner/evaluator 경계를 호출한다 |
| `scripts/generate_audio_fixtures.py` | 판단 케이스의 `user_utterance`로 TTS fixture와 audio manifest를 생성함 | 대표 오디오 파일을 재현 가능한 입력으로 만든다 |
| `results/runs/` | Step 2 hardcoded placeholder 기준 run artifact가 있음 | LLM 전환 후 수치는 새 run artifact를 만들어 다시 인용해야 한다 |

MVP 구현은 현재 브랜치의 파일과 현재 기준 문서를 기준으로 새로 진행한다. 다른 브랜치의 실험 scaffold나 run artifact는 현재 구현 계획의 입력으로 보지 않는다.

## MVP에 포함하는 것

| 범위 | 최소 기준 |
| --- | --- |
| 판단 케이스 목록(Scenario Bank) | `data/scenarios.json` 30개를 기준 원본으로 로드한다 |
| 텍스트 입력(Text Replay) | 판단 케이스를 선택하거나 텍스트 입력을 넣어 policy 판단을 먼저 확인한다 |
| AI 행동 판단 Runner(AI Action Policy Runner) | 텍스트 입력, 오디오 입력, CLI, Backend가 공유할 단일 runner entry를 둔다 |
| Baseline | transcript와 speech signal을 최소 입력으로 쓰는 LLM action 판단 기준선을 둔다 |
| Policy v1 | action label 정의, 예시, tone hint를 포함한 LLM 정책으로 false stop을 줄이는지 본다 |
| 배치 평가(Test Bench) | 판단 케이스 set에 policy를 batch 실행하고 `results/runs/{run_id}/` artifact를 남긴다 |
| Error Analysis | failure를 primary 5종 기준으로 분류하고 다음 수정 후보를 남긴다 |
| 대표 오디오 파일 입력(Audio File Test) | mock/precomputed transcript라도 같은 runner 흐름에 합류시킨다 |

## 후순위 범위

| 후순위 항목 | 이유 |
| --- | --- |
| 완성형 실시간 음성 상담 서비스 | STT/TTS/상태 관리/대화 운영까지 포함하면 범위가 커진다 |
| 실제 콜센터 데이터 수집 | 개인정보와 데이터 확보 문제가 크다 |
| STT/TTS 자체 최적화 | 핵심은 음성 모델 성능보다 고객 신호를 AI 행동으로 바꾸는 판단 구조다 |
| Live Mic 성능 평가 | 후순위 확장 슬롯이다 |
| audio prosody 기반 감정 인식 | pitch/RMS/speaking rate 모델링은 1차 MVP 핵심 구현이 아니다 |
| fine-tuning | 현재 MVP에서는 학습보다 LLM action judge, prompt/criteria 비교, run artifact 검증을 우선한다 |
| 출처 없는 개선 수치 | 수치는 `results/runs/{run_id}/evaluation.json` 생성 후 인용한다 |

## 제품 표면

| 표면 | MVP에서의 역할 | 현재 우선순위 |
| --- | --- | --- |
| 배치 평가(Test Bench) | 판단 케이스 set에 policy를 batch 실행하고 수치를 남기는 표면 | 1순위 |
| Playground | 단일 판단 케이스를 조작하며 판단과 reason을 확인하는 표면 | 2순위 |
| Backend API | UI나 외부 surface가 runner를 호출하는 adapter | runner 이후 |

Playground 화면에서 본 수치는 외부 인용 출처로 쓰지 않는다. 같은 정책으로 배치 평가(Test Bench) run artifact를 만든 뒤 인용한다.

`Workbench`는 일부 UI title과 코드에 남아 있는 상위 UI 이름 후보다. MVP 필수 표면은 배치 평가(Test Bench)와 Playground다.

## Policy Version 목표

| 표시 라벨 | 코드 식별자 | MVP에서의 목표 |
| --- | --- | --- |
| Baseline | `baseline` | 최소 텍스트 LLM 기준선. AI intent, AI 발화, 고객 transcript, speech signal만 보고 action label을 고른다 |
| Policy v1 | `policy_v1` | action label 정의, 예시, tone hint를 더한 텍스트 LLM 정책으로 backchannel/noise 판단을 개선한다 |
| Policy v2 | `policy_v2` | intent shift에서 missed switch를 줄인다 |
| Policy v3 | `policy_v3` | complaint, ambiguous, 판단 케이스 metadata 수준의 tone/severity hint까지 포함해 action label을 고른다 |

policy version은 "더 좋은 이름"이 아니라 어떤 신호를 추가했을 때 어떤 실패가 줄었는지 비교하기 위한 단위다.

## 구현 순서

Step별 완료/예정 작업과 현재 표현 기준은 [Current MVP Iteration Plan](current-iteration-plan.md)을 본다. 아래 순서는 현재 MVP를 닫기 위한 구현 흐름이며, 완료 여부 표시는 아니다.

1. `data/scenarios.json` loader와 schema validation을 만든다.
2. action label, event type, policy input/output 타입을 정의한다.
3. `src/runner.py`를 만들고 모든 surface가 이 entry를 통과하게 한다.
4. `baseline`과 `policy_v1`을 최소 구현한다.
5. 배치 평가(Test Bench) evaluator를 만들고 `results/runs/{run_id}/` artifact를 생성한다.
6. failure를 primary 5종 기준으로 분류하고 `error_analysis.md`를 남긴다.
7. Playground나 Backend API는 runner를 직접 호출하는 adapter로 붙인다.
8. 대표 오디오 파일 입력(Audio File Test)은 transcript/signal adapter를 통해 같은 runner input으로 합류시킨다.

## 완료 기준

MVP가 닫혔다고 보려면 아래를 확인한다.

- `data/scenarios.json`의 30개 판단 케이스를 로드하고 검증할 수 있다.
- `expected_action`은 판단 케이스 원본에만 있고, `actual_action`은 run result에만 있다.
- `baseline`과 하나 이상의 개선 policy를 같은 runner/evaluator로 비교한다.
- 배치 평가(Test Bench)가 `results/runs/{run_id}/run_meta.json`, `evaluation.json`, `decision_logs.jsonl`, `error_analysis.md`를 만든다.
- README나 공유 문서에 쓰는 수치는 run id와 함께 확인 가능하다.
- 텍스트 입력(Text Replay)에서 판단 케이스별 expected/actual/reason/failure를 볼 수 있다.
- 대표 오디오 파일 입력(Audio File Test)이 mock/precomputed transcript라도 같은 AI 행동 판단 입력으로 들어온다.
- 같은 주제 질문에 답하고 이어가는 행동은 `respond_and_continue`로 기록한다.

## 현재 표현 기준

과거 문서나 회의 기록을 현재 문서로 옮길 때는 아래처럼 현재 표현으로 정규화한다.

| 과거 표현 | 현재 표현 |
| --- | --- |
| `pause` | `respond_and_continue` |
| `P0`, `P1`, `P2`, `P3` 단독 표기 | `baseline`, `policy_v1`, `policy_v2`, `policy_v3` |
| `results/evaluation.json` flat 구조 | `results/runs/{run_id}/evaluation.json` |
| `results/decision_logs.jsonl` flat 구조 | `results/runs/{run_id}/decision_logs.jsonl` |
| 실험 전 개선율 | 목표/가설로만 표현하고, 결과는 run artifact 이후 인용 |
| Workbench | 상위 UI 이름 후보로만 쓰고, 제품 컨셉으로 앞세우지 않는다 |

## 이 문서를 고치는 기준

이 문서는 MVP 실행 범위가 바뀔 때 고친다.

- action label, policy version, 평가 기준이 바뀌면 `context/decisions/`에 먼저 결정 맥락을 남긴다.
- 코드가 실제로 추가되면 "현재 repo 상태" 표를 갱신한다.
- 새 MVP나 2주차 MVP처럼 범위가 크게 바뀌면 이 문서에 덧붙여 섞지 말고, [MVP Execution Hub](README.md)의 문서 상태 규칙에 따라 새 문서/decision/archive 경계를 먼저 잡는다.
- 공개 문서로 옮길 문장은 이 문서에서 바로 복사하지 말고 `docs/` 문맥에 맞춰 다시 다듬는다.
