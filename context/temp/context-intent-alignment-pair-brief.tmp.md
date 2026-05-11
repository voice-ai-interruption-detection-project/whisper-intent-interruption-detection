# Context Intent Alignment Pair Brief

`docs/context-intent-alignment` 브랜치 전체를 페어에게 설명하기 위한 짧은 공유 메모다. 공개 `docs/` 정리는 이번 범위에서 제외한다.

## 한 줄 요약

이 브랜치는 기능을 크게 바꾼 작업이 아니라, 프로젝트를 읽는 기준을 다시 맞춘 작업이다.

핵심은 이 프로젝트를 `input_mode`, Workbench, Test Bench 자체가 아니라 아래 질문으로 읽게 하는 것이다.

```text
AI가 말하는 중 고객 신호가 들어왔을 때,
AI는 다음 행동을 어떻게 고르는가?
```

## 왜 했나

브랜치 시작 전 문서에도 제품 의도는 있었다. 다만 `scenario`, `input_mode`, Text Replay, Audio File Test, Test Bench 같은 하네스 용어가 앞쪽으로 올라오면서, 프로젝트가 "음성 AI 상담의 끼어들기/의도 전환 경험"보다 "입력 모드와 평가 장치" 중심으로 읽힐 위험이 있었다.

또 과거에는 AI가 프로젝트를 너무 좁게 해석하지 않게 하려고 강한 부정문과 제한 문장을 넣었는데, 이게 시간이 지나면서 "무엇을 검증하는가"보다 "무엇을 하면 안 되는가"를 더 크게 보이게 만들 수 있었다.

그래서 이번 작업의 기준은 **삭제가 아니라 층위 낮추기**였다. 필요한 용어는 남기되, 제품 개념 / 입력 경로 / UI surface / schema/API key / run artifact 계약을 구분했다.

## 선택한 방향

decision에서 크게 세 방향을 봤고, 세 번째를 택했다.

| 선택지 | 판단 |
| --- | --- |
| `input_mode`, `expected_action`, `actual_action` 같은 key를 대거 rename | 코드/API/run artifact 계약이라 영향이 커서 보류 |
| 하네스 용어를 모두 쉬운 한국어로 번역 | 코드와 결과 파일을 추적하기 어려워져서 보류 |
| 제품 맥락은 쉽게 쓰고, 계약 용어는 필요한 자리에 남김 | 채택 |

## 이번 브랜치에서 맞춘 기준

- `scenario`는 전체 상담 플로우가 아니라 **판단 케이스(Scenario)** 한 장이다.
- Text Replay, Audio File Test, Mic Trial은 제품 기능이 아니라 같은 판단 구조를 실행해 보는 **입력 경로**다.
- `expected_action`, `actual_action`, `action_accuracy`, `run_id`는 억지 번역하지 않는 계약 이름이다.
- `Workbench`는 제품 컨셉이 아니라 Playground와 Run artifacts/Test Bench를 담는 작업 화면 shell이다.
- UI에서는 개념 기준점이 필요한 곳에만 병기를 쓰고, 큰 제목·버튼·metric/table은 사용 맥락과 계약 이름을 우선한다.

## 주요 작업 흐름

| 커밋 | 내용 |
| --- | --- |
| `d466dbd` ~ `a318f81` | Product Context, Language Map, MVP 문서 등 내부 기준 정리 |
| `9e4476b` | 코드 주석/docstring의 표현을 행동 판단 맥락에 맞춤 |
| `1ae6b7b`, `abf4493` | Context Intent Alignment decision 기록 |
| `10cc5e8` | Mic Trial, Test Bench 표현 기준 보정 |
| `ca124da` | `context-language-balancer` agent 추가 |
| `83aa998`, `6351d9e` | UI wording 반영 후 과한 병기/번역 재조정 |

## 페어가 보면 좋은 파일

먼저 아래 4개만 보면 브랜치 의도는 대부분 잡힌다.

- [Product Context](../internal/product-context.md)
- [Project Language Map](../internal/project-language-map.md)
- [Current MVP](../internal/mvp/current.md)
- [Context Intent Alignment decision](../decisions/2026-05-11-context-intent-alignment/README.md)

UI wording까지 볼 때:

- [Workbench UI](../../src/backend/static/index.html)
- [UI JS](../../src/backend/static/js/main.js)
- [UI Wording Layer Balance decision](../decisions/2026-05-11-ui-wording-layer-balance/README.md)

반복 점검 장치:

- [context-language-balancer agent](../../.claude/agents/context-language-balancer.md)
- [UI wording rule](../../.claude/rules/coding.md)

## 리뷰할 때 볼 것

- 제품 의도가 "AI 행동 판단 구조"로 먼저 읽히는가?
- Text Replay/Audio File Test가 제품 기능이 아니라 입력 경로로 읽히는가?
- `scenario`가 전체 상담 여정이 아니라 판단 케이스로 읽히는가?
- `expected_action`, `actual_action`, `action_accuracy` 같은 계약 이름이 불필요하게 번역되지 않았는가?
- UI에서 `판단 케이스(Scenario)` 병기가 반복 설명이 아니라 개념 기준점으로만 쓰이는가?

## 하지 않은 것

- schema/API key rename은 하지 않았다.
- action label set은 바꾸지 않았다.
- policy/evaluator 판단 로직을 바꾸려는 브랜치가 아니다.
- 공개 `docs/`는 이번 범위에서 제외했다.
- archive 자료를 현재 기준으로 직접 승격하지 않았다.

## 남은 확인 포인트

- `context/internal/mvp/current-iteration-plan.md`의 Step 3 상태는 실제 구현 완료분과 새 LLM run artifact 필요분을 나눠 최신화할 수 있다.
- `Workbench` 표현은 이제 실제 UI shell에 가까워졌으므로, active context에서 "후보" 뉘앙스를 줄일 수 있다.
- 코드 온보딩용으로 따로 정리한 읽기 가이드는 이번 PR 범위에서 제외한다.
- 새 decision인 `UI Wording Layer Balance`를 최종 커밋에 포함할지 확인한다.

## 짧은 설명 스크립트

```text
이번 브랜치는 기능 추가보다 프로젝트를 읽는 기준을 맞춘 작업이에요.

핵심은 Workbench나 input mode 자체가 아니라,
AI가 말하는 중 고객 신호가 들어왔을 때 다음 행동을 어떻게 고르는지입니다.

그래서 scenario는 판단 케이스로,
Text Replay와 Audio File Test는 입력 경로로,
expected_action/actual_action/action_accuracy는 계약 이름으로 정리했습니다.

같은 기준을 내부 문서, 코드 주석, 작업 가드, agent, UI wording에 반영했습니다.
```
