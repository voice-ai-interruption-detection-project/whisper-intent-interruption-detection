# Context

## 문제 인식

사용자는 현재 `context/internal/` 문서가 실제 프로젝트 의도와 다르게 읽힐 수 있다고 보았다.

핵심 문제는 세 가지였다.

- `input_mode`가 제품 시나리오의 중요한 개념처럼 보인다.
- `product-context`의 톤이 강해서 "이번 1주차에는 개발하지 않는다"처럼 제한 규칙으로 오해될 수 있다.
- Input Mode, Text Replay, Audio File Test, AI Action Policy, Test Bench 같은 용어가 많아 이해 비용이 높다.

추가 점검에서 하네스 규칙과 agent 설명도 같은 편향을 만들 수 있음이 확인됐다. 특히 기존 project overview가 "Whisper 기반 detection" 쪽으로 좁게 읽히고, `context/README.md`가 archive보다 active internal을 우선하게 만들어 원래 의도 복원 작업에서는 현재 문서가 현재 문서를 정당화할 위험이 있었다.

## 복원한 의도

프로젝트의 원래 방향은 음성 AI 상담 서비스 전체 구현이 아니라, 그 서비스에서 가장 어색하고 중요한 순간인 "AI가 말하는 중 고객이 끼어들거나 의도를 바꿀 때 AI가 다음 행동을 어떻게 고를까"를 검증하는 것이었다.

따라서 Text Replay, Audio File Test, Mic Trial은 제품의 본질적 개념이 아니라, 같은 판단 구조를 빠르게 검증하기 위한 입력 경로다.

## 선택지

### 1. 용어를 대거 rename한다

예: `input_mode`를 `input_adapter`로 바꾸고, `expected_action`/`actual_action`도 다른 key로 바꾼다.

기각했다. 이 값들은 코드/API/run artifact 계약으로 이미 쓰이고 있어 변경 비용이 크다. 실제 문제는 식별자 자체보다 문서와 UI에서 어떤 층위로 설명되는지였다.

### 2. 하네스 용어를 모두 쉬운 말로 바꾼다

기각했다. Test Bench, Playground, Text Replay, Audio File Test는 팀 내부에서 이미 표면이나 입력 경로를 가리키는 이름으로 쓰인다. 완전히 숨기면 오히려 코드와 문서 사이의 연결이 끊긴다.

### 3. 제품 맥락은 쉽게 쓰고, 코드/계약 용어는 필요한 자리에 병기한다

채택했다.

예:

- `input_mode`는 코드/API/run artifact 필드로 유지한다.
- 제품 설명에서는 "입력 경로" 또는 "테스트 입력 방식"으로 풀어 쓴다.
- UI나 내부 문서에서는 필요하면 `입력 경로(input_mode)`처럼 병기한다.
- `expected_action`은 "사람이 정한 기준 행동", `actual_action`은 "policy가 낸 판단 행동"으로 설명한다.

## 실제 반영 커밋

| 커밋 | 반영 내용 | 대화에서 대응되는 판단 |
| --- | --- | --- |
| `d466dbd` docs(context): 제품 의도와 하네스 읽기 기준 정리 | `CLAUDE.md`, `README.md`, `context/README.md`, `context/internal/*`, harness reviewer 설명 수정 | "Whisper detection"보다 "음성 AI 상담의 끼어들기/의도 전환 경험"으로 넓히고, 문서 감사 때 archive/회의 원문도 evidence로 본다 |
| `0d624f3` docs(context): 하네스 용어의 제품 맥락 압박 완화 | rules, agents, mvp/current, product-context, language map의 하네스 용어 조정 | input mode와 Test Bench가 제품 본체처럼 보이는 압박을 낮춘다 |
| `a318f81` docs(context): 쉬운 용어 우선으로 내부 표현 정리 | internal 문서와 agent/rule 표현 전반을 한국어 설명 우선으로 정리 | "무조건 영어 용어"가 아니라 팀원이 바로 이해할 수 있는 설명을 먼저 둔다 |
| `9e4476b` docs(code): 행동 판단 맥락에 맞게 주석 표현 정리 | 코드 주석/docstring에서 Workbench/detection 중심 표현을 행동 판단 맥락으로 조정 | 코드 계약은 유지하되 사람이 읽는 주석의 프레이밍을 맞춘다 |
| `10cc5e8` docs(context): Mic Trial과 Test Bench 표현 기준 정리 | `Mic Trial`은 같은 입력 경로 계열로, `Test Bench`는 실제 surface 이름으로 정리 | "후순위"와 "쉬운 말"이 용어 자체의 격하로 읽히지 않게 보정한다 |
| 이번 후속 커밋: context-language-balancer agent 추가 | `.claude/agents/context-language-balancer.md`, `.codex/agents/context-language-balancer.toml`, `CLAUDE.md` 색인 | 같은 점검을 매번 수동으로 반복하지 않도록 문서/용어 균형 reviewer를 둔다 |

## 적용한 기준

### 남긴 것

- `input_mode`, `expected_action`, `actual_action`: schema/API/run artifact 계약
- `Playground`: 단일 판단 케이스를 조작하며 policy 판단과 reason을 확인하는 표면
- `Test Bench`: 판단 케이스 set을 batch로 실행하고 run artifact를 남기는 평가 표면
- Text Replay, Audio File Test: 입력 경로 이름으로 병기 가능

### 낮춘 것

- `Workbench`: 상위 UI 이름 후보로만 보고, 제품 컨셉으로 앞세우지 않는다.
- `input_mode`: 제품 시나리오 흐름의 핵심 단계가 아니라 입력 adapter 층위로 둔다.
- negative-list: "하지 말 것"보다 "현재는 이렇게 읽는다"는 positive 기준으로 바꾼다.

### 적용하지 않은 것

- `input_mode`를 코드에서 `input_adapter`로 rename하지 않는다.
- `expected_action`, `actual_action` key를 바꾸지 않는다.
- `event_type` 7종을 4종으로 줄이지 않는다.
- primary failure 5종을 3종으로 줄이지 않는다.
- `brief_ack`를 `continue`에 병합하지 않는다.
- LLM prompt와 schema 계약은 별도 decision 없이 바꾸지 않는다.

## 판단이 바뀐 지점

처음에는 "용어를 쉽게 바꾼다"가 중심처럼 보였지만, 대화가 진행되며 기준이 더 정교해졌다.

최종 기준은 "무조건 쉬운 말로 바꾸기"가 아니다.

제품 의도와 사용자가 처음 보는 표면은 쉽게 설명하고, 구현/평가 재현에 필요한 용어는 코드값과 함께 남긴다.

이 기준은 이후 UI 워딩에도 이어진다. 예를 들어 `Workbench`는 제거/격하하지만, `Playground`, `Test Bench`, Text Replay, Audio File Test는 실제 표면/입력 경로 이름으로 병기한다.

## 후속 하네스화: context-language-balancer

이 브랜치 작업 후 사용자는 같은 종류의 단어/문서 점검을 계속 직접 하는 것이 비효율적이라고 보았다.

새 agent는 "문서를 더 친절하게 만드는 agent"가 아니다. 또 "현재 구현 계약을 무조건 보존하는 agent"도 아니다. 역할은 표현별 층위를 판정하는 것이다.

판정 축:

- 제품 의도: 음성 AI 상담의 끼어들기/의도 전환 순간에서 AI 행동 판단이라는 중심 질문을 유지하는가.
- 용어 층위: 제품 개념, 입력 경로, UI surface, schema/API key, run artifact가 섞이지 않았는가.
- 구현 계약 민감도: 단순 wording 변경인지, schema/API/run artifact/test 계약 변경인지 구분하는가.
- 가독성과 기준성: 쉬워졌지만 기준이 흐려지지 않고, 정확하지만 방어적이지 않은가.
- repo 공유 경계 quick check: 로컬 절대경로와 비공개 원문 위치가 공유 repo 문서에 직접 들어가지 않았는가.

중요한 조정:

- "구현 계약 보존"이 아니라 "구현 계약 민감도 판단"으로 쓴다. 계약성 용어라고 영구 고정하지 않고, 바꾸려면 영향 범위, migration, 테스트, decision 필요성을 함께 제시한다.
- repo-local agent 안에는 프로젝트 밖 개인 도구 이름이나 비공개 자료 관리 책임을 넣지 않는다.
- `harness-structure-reviewer`가 코드/하네스 경계를 본다면, `context-language-balancer`는 문서/용어/제품 맥락 경계를 본다.

## 연결된 파일

- `context/internal/product-context.md`
- `context/internal/project-language-map.md`
- `context/internal/mvp/current.md`
- `context/internal/mvp/README.md`
- `context/internal/scenario-worked-example.md`
- `context/README.md`
- `CLAUDE.md`
- `README.md`
- `.claude/rules/`
- `.claude/agents/`
- `.codex/agents/`
- `.claude/agents/context-language-balancer.md`
- `.codex/agents/context-language-balancer.toml`
- `src/backend/static/` follow-up UI wording 작업
