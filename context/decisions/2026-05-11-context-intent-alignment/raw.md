# Raw Material

이 파일은 2026-05-11 대화에서 나온 핵심 원문과 작업 로그를 발췌해 저장한다.

사용자가 제공한 원문에는 개인 로컬 경로와 긴 대화 전문이 포함되어 있었으므로, 여기에는 decision 재검토에 필요한 부분만 요약/발췌한다.

## 사용자 문제 제기 요지

사용자는 음성 AI 서비스 사이드 프로젝트의 `context/internal` 문서들이 원래 의도와 다르게 해석되거나, 지나치게 강한 표현과 어려운 용어 때문에 맥락이 왜곡된다고 느꼈다.

주요 의심은 아래와 같았다.

- 프로젝트는 음성 AI 서비스 전체 구현이 아니라, interruption 경험을 개선하는 컨셉을 중심으로 실험하고 구현해보는 것이었다.
- `input`, `audio`, `mic`를 나눈 것은 제품 개념이라기보다 테스트와 구현 편의를 위한 입력 방식 분리였다.
- 현재 문서에서는 `input_mode`가 제품 시나리오의 중요한 개념처럼 보인다.
- `product-context` 문서의 톤이 너무 단정적이고 강제적이다.
- Input Mode, Text Replay 같은 용어들이 프로젝트 이해를 돕기보다 방해한다.
- 실제 대화에서 합의된 내용과 AI가 문서화 과정에서 과도하게 일반화한 내용을 구분해야 한다.

## 초기 분석 결론 발췌

초기 분석에서는 아래 결론을 냈다.

```text
현재 문서의 문제는 방향이 틀린 것이 아니라,
맥락 보호를 위해 만든 하네스 언어가 제품 의도보다 앞에 서 있다는 점이다.

복원해야 할 핵심은 이것이다.

이 프로젝트는 음성 AI 상담 서비스 전체 구현이 아니라,
그 서비스에서 가장 어색하고 중요한 순간인
"고객이 끼어들거나 의도를 바꿀 때 AI가 다음 행동을 어떻게 고를까"를
검증하는 프로젝트다.

Text Replay, Audio File Test, Mic Trial은 그 판단 구조를 만들고 검증하기 위한
입력 경로일 뿐, 제품의 본질적 개념은 아니다.
```

## 하네스 영향 점검 발췌

추가 점검에서는 아래처럼 판단했다.

```text
현재 하네스가 이전 분석을 완전히 왜곡할 정도는 아니지만,
AI가 기본값으로 읽으면 제품 의도보다 실험 하네스/현재 기준/context-internal을
더 강하게 신뢰하게 만드는 압력은 분명히 있다.
```

구체적 보정 후보:

- 프로젝트 개요를 "Whisper 기반 탐지 실험"보다 넓게 바꾼다.
- 문서 정합성 감사나 원래 의도 복원 작업에서는 archive와 회의 원문을 evidence로 확인할 수 있게 한다.
- Project Language Map 설명에서 `input_mode`를 제품 개념처럼 나열하지 않는다.

## 작업 진행 발췌

브랜치를 만들고 아래 작업을 진행했다.

```text
브랜치 docs/context-intent-alignment를 새로 파서 작업까지 진행했습니다.

CLAUDE.md 프로젝트 개요를 "Whisper 기반 detection" 중심에서
"음성 AI 상담의 끼어들기/의도 전환 경험" 중심으로 조정했습니다.

product-context.md 첫 기준을 다시 써서 제품 의도와 현재 MVP 범위를 분리했고,
Text Replay/Audio File Test는 제품 개념이 아니라 현재 입력 경로라고 명시했습니다.

project-language-map.md 최상단 흐름에서 input_mode를 빼고,
입력 경로를 adapter 층위로 낮췄습니다.

context/README.md, context/internal/README.md에
"의도 복원 / 문서 감사" 예외와 읽기 우선순위를 추가했습니다.
```

이후 사용자가 "수정 자체는 잘 된 것 같은데 전반적으로 수정한 부분이 별로 없어 보인다"고 피드백했고, `product-context.md`를 더 과감하게 줄여 세션 시작 때 제품 의도를 회복하는 문서로 바꿨다.

또 사용자가 "그냥 분석한 결과를 바탕으로 적용할만한 부분은 다 작업해놔줘 다만 docs는 냅두고"라고 지시해, `docs/`는 제외하고 `README.md`, `CLAUDE.md`, `context/README.md`, `context/internal/**`, repo-local rule/agent 설명을 정리했다.

## 용어 관련 판단 발췌

사용자는 아래 예시를 들어, 어떤 변경은 바로 적용하지 않아야 하지 않냐고 물었다.

```text
input_mode를 코드에서 input_adapter로 rename
expected_action, actual_action을 다른 key로 변경
event_type 7종을 4종으로 축소
primary failure 5종을 3종으로 축소
brief_ack를 continue에 병합
Workbench UI title을 코드에서 전부 제거
```

이에 대해 아래처럼 판단했다.

- 위 항목들은 대부분 schema/API/evaluation 계약 변경이므로 바로 적용하지 않는다.
- 지금 안전하게 할 수 있는 것은 문서와 사람이 읽는 주석/라벨의 층위 조정이다.
- 코드 식별자는 유지하고 설명 문장을 낮춘다.
- `Workbench`는 제품 컨셉으로 앞세우지 않되, 코드 전체 제거는 별도 판단으로 둔다.

## 반영 커밋

```text
d466dbd docs(context): 제품 의도와 하네스 읽기 기준 정리
0d624f3 docs(context): 하네스 용어의 제품 맥락 압박 완화
a318f81 docs(context): 쉬운 용어 우선으로 내부 표현 정리
9e4476b docs(code): 행동 판단 맥락에 맞게 주석 표현 정리
```

## 이 decision을 남기게 된 이유

사용자가 이후 "지금 코드 작업말고 이전작업들있지? 이거 과거 커밋 작업 대화인데 decisions에 반영되어 있나?"라고 확인했다.

확인 결과 기존 `context/decisions/`에는 2026-05-09 결정 3개만 있었고, 이번 브랜치에서 수행한 context intent alignment 작업의 이유와 대화 맥락은 별도 decision으로 남아 있지 않았다.

따라서 이 사안을 `2026-05-11-context-intent-alignment`로 기록한다.
