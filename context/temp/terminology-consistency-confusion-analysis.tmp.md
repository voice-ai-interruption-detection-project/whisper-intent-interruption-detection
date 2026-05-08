# Terminology Consistency Branch Context Brief

이 문서는 `docs/internal-terminology-sync` 브랜치에서 왜 internal 기준 자료를 보강했는지, 어떤 혼선 패턴을 확인했는지, 지금까지 무엇을 정리했는지 남기는 임시 context brief다.

`docs/` 본문을 바로 고치기 위한 문서가 아니라, 이후 공개 문서를 정리할 때 기준이 흐트러지지 않게 하기 위한 작업 메모다.

## 왜 이 문서를 만들었나

이 브랜치의 출발점은 이전 구조 정리 PR에서 남긴 follow-up이었다.

- `docs/` 본문에는 오래된 label, 미실측 수치, flat result tree 설명이 남아 있었다.
- 초기 `기획/` 자료에는 좋은 설명 흐름과 용어 결정의 흔적이 있지만, 현재 기준과 섞어 쓰기에는 낡은 표현도 있었다. 해당 원문은 `context/archive/product-planning/`으로 이동했고, 제품 방향의 현재 기준은 `context/internal/product-context.md`로 재정리했다.
- 페어 대화에서는 용어 자체보다 `층위`, `schema key/value`, `policy input/output`, `evaluation`이 한 화면에 겹칠 때 이해가 어려워지는 패턴이 반복됐다.

따라서 이번 브랜치는 공개 문서 본문을 바로 고치는 대신, 먼저 `context/internal/`에 현재 기준을 맞추는 작업으로 진행했다.

## 이번 브랜치에서 확인한 핵심 혼선

### 1. Key와 value가 같은 개념처럼 보임

예를 들어 아래 표현은 두 층위를 동시에 담고 있다.

```text
event_type = intent_shift
```

`event_type`은 schema key이고, `intent_shift`는 그 key에 들어가는 enum value다. 이 구분이 흐려지면 `backchannel`이 event type인지 action label인지, `expected_action`이 key인지 label인지 계속 다시 확인하게 된다.

이번 브랜치에서는 이 문제를 [context/internal/reference/schema-keys.md](../internal/reference/schema-keys.md)로 분리했다.

### 2. Event Type과 Action Label이 같은 층위처럼 보임

현재 기준은 아래처럼 분리된다.

| 층위 | 예시 | 의미 |
| --- | --- | --- |
| `event_type` | `backchannel`, `intent_shift`, `same_intent_question` | 고객 신호의 종류 |
| action label | `continue`, `respond_and_continue`, `stop_and_switch` | AI가 선택할 행동 |

`event_type`은 고객 쪽 신호이고, action label은 AI 쪽 행동이다.

이번 브랜치에서는 [context/internal/reference/event-types.md](../internal/reference/event-types.md)와 [context/internal/reference/action-labels.md](../internal/reference/action-labels.md)를 나눠 이 구분을 고정했다.

### 3. Expected와 Actual은 다른 값 체계가 아니라 다른 역할임

`expected_action`과 `actual_action`은 같은 action label vocabulary를 쓴다.

| 이름 | 값 집합 | 역할 | 위치 |
| --- | --- | --- | --- |
| `expected_action` | action label vocabulary | 사람이 정한 기준/정답 | `data/scenarios.json` |
| `actual_action` | action label vocabulary | policy 실행 결과/예측 | `results/runs/{run_id}/decision_logs.jsonl` |

따라서 `expected_action = stop_and_switch`, `actual_action = respond_and_continue`는 “두 용어가 다른 체계”라는 뜻이 아니다. 같은 선택지 집합 안에서 기준과 policy 결과가 달랐다는 뜻이다.

### 4. Schema와 pipeline이 섞임

schema는 한 scenario에 필요한 정보를 담는 key/value 목록이다. pipeline은 그 값들이 실행 중 어떤 순서로 쓰이는지 나타내는 흐름이다.

```text
scenario card
-> input mode
-> event / intent 해석
-> AI Action Policy 실행
-> actual_action 생성
-> expected_action과 비교
-> failure 분류
```

이 구분은 [context/internal/scenario-worked-example.md](../internal/scenario-worked-example.md)에 예시로 정리했다.

### 5. docs와 기획 문서에는 좋은 형식과 낡은 기준이 같이 있음

`docs/`와 초기 기획 자료에서 가져올 만한 좋은 패턴은 긴 고객 장면 설명이 아니라, enum 값을 간결하게 정리하는 형식이었다.

예:

- event type 7종을 개념, 대표 워딩/신호, 기본 expected action으로 나열
- action label 6종을 의미와 경계로 정리
- Text/Audio/Mic이 뒤쪽에서 같은 AI Action Policy로 연결된다는 도식

하지만 그대로 가져오면 안 되는 것도 있었다.

- `pause`가 현재 action label처럼 남아 있음
- `25% -> 8%`, `40% -> 12%` 같은 미실측 수치가 결과처럼 쓰임
- `results/evaluation.json`, `results/decision_logs.jsonl` 같은 flat result tree 설명이 남아 있음
- `30개 목표`, `30개 진행 중`, `30개 완료`가 문서별로 섞임

그래서 이번 브랜치에서는 문장 자체를 옮기기보다, 형식만 참고해 현재 기준 reference를 새로 만들었다.

### 6. 제품 방향과 용어 reference가 같은 문서에 섞임

초기 기획 문서에는 제품 문제, 범위, 입력 모드, action label, 실행 일정, 폴더 구조가 한꺼번에 들어 있었다. 페어 중에는 이 때문에 "무엇이 현재 제품 기준이고, 무엇이 용어 reference이며, 무엇이 날짜별 계획인지"를 다시 확인하는 일이 반복됐다.

이번 브랜치에서는 제품 방향과 실행 범위는 [context/internal/product-context.md](../internal/product-context.md)에 두고, 용어 층위와 enum 값은 [context/internal/project-language-map.md](../internal/project-language-map.md)와 [context/internal/reference/](../internal/reference/) 아래로 분리했다.

추가로 Workbench / Playground / Test Bench가 섞이지 않도록 제품 표면 기준을 product context와 language map에 나눠 적었다.

### 7. `tone hint`와 audio prosody가 같은 말처럼 보일 수 있음

`user_tone_hint`는 scenario에 사람이 붙여 둔 metadata 수준의 힌트다. Text Replay에서도 사용할 수 있다.

반면 audio prosody는 pitch, RMS, speaking rate 같은 실제 음성 feature를 뽑아 감정/긴급도를 추론하는 구현이다. 이건 1주차 핵심 구현에서 제외한다.

따라서 현재 기준은 아래처럼 분리한다.

- Policy v3는 scenario metadata 수준의 `tone/severity hint`를 참고할 수 있다.
- audio prosody 기반 감정 인식은 후순위 확장이다.

## 이번 브랜치에서 정리한 기준

### Internal 기준 자료 추가

| 파일 | 역할 |
| --- | --- |
| [context/internal/project-language-map.md](../internal/project-language-map.md) | 전체 층위와 읽는 순서 |
| [context/internal/product-context.md](../internal/product-context.md) | 제품 문제, 현재 범위, 제품 표면, 비목표, 남은 결정 후보 |
| [context/internal/evaluation-and-results-contract.md](../internal/evaluation-and-results-contract.md) | expected/actual, metric, run artifact 계약 |
| [context/internal/scenario-worked-example.md](../internal/scenario-worked-example.md) | 한 scenario가 schema, policy, evaluation으로 이어지는 예시 |
| [context/internal/reference/schema-keys.md](../internal/reference/schema-keys.md) | schema key와 result key의 역할 구분 |
| [context/internal/reference/event-types.md](../internal/reference/event-types.md) | `event_type` 7종 reference |
| [context/internal/reference/action-labels.md](../internal/reference/action-labels.md) | action label 6종 reference |

### Current 기준으로 고정한 것

- `pause`는 현재 action label로 쓰지 않는다.
- 같은 주제 질문에 답하고 이어가는 행동은 `respond_and_continue`로 쓴다.
- `expected_action`은 기준/정답이고, `actual_action`은 policy 실행 결과다.
- `data/scenarios.json`에는 기준 원본만 둔다. `actual_action`, metric, decision log는 넣지 않는다.
- 새 result는 `results/runs/{run_id}/` 구조를 기준으로 둔다.
- 미실측 수치는 결과처럼 쓰지 않는다.
- `data/scenarios.json`의 30개 scenario는 현재 시작점이다. golden set으로 고정하지 않고 evaluation/error analysis를 보며 조정할 수 있다.
- Workbench는 완성형 상담 앱이 아니라 Playground와 Test Bench를 묶는 상위 실험 콘솔 후보로 본다.
- `user_tone_hint`는 metadata 수준의 힌트이고, audio prosody 기반 감정 인식은 후순위 확장이다.
- `docs/` 본문은 아직 고치지 않는다. internal 기준이 안정된 뒤 공개 문장으로 발췌한다.

### 구조 정리

- reference 성격의 문서 3개를 `context/internal/reference/` 아래로 묶었다.
- `docs/archive/` 자료는 `context/archive/`로 이전했다.
- archive는 history/evidence로만 보고, active 기준과 충돌하면 `context/internal/`, `.claude/rules/`, 코드/데이터 쪽을 우선한다.
- 초기 `기획/` 원문은 `context/archive/product-planning/`으로 이동했다.
- 루트 가이드, repo-local agents, Codex agent bridge도 `context/internal/product-context.md`와 archive 경계에 맞춰 갱신했다.
- 운영/맥락 문서 루트 노출을 줄이기 위해 `internal/`, `decisions/`, `archive/`, `temp/`는 `context/` 아래로 접었다.

## 작업 이력

이번 브랜치에서 관련된 주요 commit은 아래 흐름이다.

| commit | 내용 |
| --- | --- |
| `3e5bf39` | `internal/` 용어 지도와 평가 계약 추가 |
| `4a47619` | `data/scenario_stats.json` 분포 정정 |
| `377f207` | failure classifier 예시 label을 현재 기준으로 갱신 |
| `6fcb92b` | 이 temp 혼선 분석 메모 최초 추가 |
| `15d0ce4` | scenario worked example 추가 |
| `8523aa3` | expected/actual action 역할 구분 보강 |
| `b4964ae` | schema key, event type, action label reference 추가 |
| `e6f4106` | reference 문서를 `internal/reference/`로 묶음 |
| `27558c1` | `docs/archive` 자료를 루트 `archive`로 이동 |
| `9cfe23f` | 초기 product planning 원문을 archive로 이동하고 `internal/product-context.md`를 현재 제품 기준으로 추가 |
| `uncommitted` | `internal/`, `decisions/`, `archive/`, `temp/`를 `context/` 아래로 이동하고 하네스 경로 갱신 |

## docs 본문을 나중에 정리할 때 볼 것

아직 `docs/` 본문은 고치지 않는다. 나중에 공개 문서를 정리할 때는 아래 순서로 본다.

1. 제품 방향, 범위, 비목표는 `context/internal/product-context.md`를 먼저 본다.
2. `context/internal/project-language-map.md`에서 전체 층위를 확인한다.
3. key/value 혼선은 `context/internal/reference/schema-keys.md`를 기준으로 정리한다.
4. enum 설명은 `context/internal/reference/event-types.md`, `context/internal/reference/action-labels.md`의 표 형식을 참고한다.
5. 수치와 result tree는 `context/internal/evaluation-and-results-contract.md`를 기준으로 고친다.
6. 흐름 설명이 필요하면 `context/internal/scenario-worked-example.md`의 순서를 따른다.

체크리스트:

- `pause`가 현재 action label처럼 쓰이는가?
- `event_type`과 action label이 같은 층위로 보이는가?
- schema key와 enum value를 같은 말처럼 설명하는가?
- `expected_action`과 `actual_action`을 다른 값 체계처럼 설명하는가?
- `scenario`가 전체 상담 플로우처럼 설명되는가?
- `input_mode`가 AI 발화 방식처럼 읽히는가?
- 목표 수치가 실측 결과처럼 쓰이는가?
- flat `results/evaluation.json` 구조가 남아 있는가?
- Text Replay가 음성 프로젝트의 대체물처럼 설명되는가?
- Workbench를 완성형 상담 앱처럼 설명하는가?
- `user_tone_hint`와 audio prosody feature extraction을 같은 범위로 설명하는가?
- failure taxonomy가 고객 경험/실패 유형과 연결되지 않고 metric 이름만 나열되는가?

## 남은 follow-up

- `docs/` 본문에서 `pause` 잔재를 `respond_and_continue` 기준으로 정리
- `docs/` 본문에서 미실측 개선 수치를 목표/가설 표현으로 낮추거나 run artifact 기반 수치로 교체
- `docs/02-design/evaluation.md`의 result tree 설명을 `results/runs/{run_id}/` 기준으로 정리
- `docs/03-data/bank.md`처럼 현재 상태와 목표 상태가 섞인 문서 정리
- 완료: 초기 `기획/` 원문은 `context/archive/product-planning/`으로 이동하고, 필요한 내용은 `context/internal/` 기준 자료로 재정리

## 유지할 경계

- 이 문서는 공개 문서가 아니라 `context/temp/` 작업 메모다.
- 페어 원본과 과거 docs는 evidence로만 보고, 프로젝트 문서에는 개인 로컬 절대경로를 넣지 않는다.
- archive의 초기 기획 자료를 그대로 복사하지 않고, 현재 기준 어휘로 재정리한다.
- 수치 인용은 run artifact가 생긴 뒤에 한다.
