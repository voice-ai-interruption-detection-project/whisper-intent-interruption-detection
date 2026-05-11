# Raw Material

이 파일은 2026-05-11 대화에서 나온 핵심 원문과 작업 로그를 재진입 가능한 수준으로 보존한다.

원문에는 로컬 경로와 긴 대화 전문이 포함되어 있었으므로, 여기에는 decision 재검토에 필요한 부분을 시간순으로 발췌/요약한다. 경로는 구체 절대경로 대신 자료 유형으로 일반화한다.

## 0. 저장 정책

- 원문 전체를 통째로 붙이지 않는다.
- 로컬 절대경로와 비공개 원문 위치는 저장하지 않는다.
- 사용자의 문제 제기, 분석 결론, 작업 판단, 커밋 대조, 나중에 헷갈릴 수 있는 기준은 충분히 자세히 남긴다.
- 결론만 남기지 않고, 사용자가 중간에 어떤 불만/피드백을 줬는지도 남긴다.

## 1. 사용자 최초 요청의 핵심 구조

사용자는 음성 AI 서비스 사이드 프로젝트의 `context/internal` 문서들이 원래 의도와 다르게 해석되거나, 지나치게 강한 표현과 어려운 용어 때문에 맥락이 왜곡된다고 느꼈다.

사용자가 복원하고 싶어 한 실제 배경:

- 프로젝트는 본래 "음성 AI 서비스"를 목표로 한 사이드 프로젝트다.
- 다만 전체 서비스를 완성하는 것이 목적은 아니었다.
- 핵심은 음성 AI 서비스 중에서도 interruption / interrupt 경험을 개선하는 컨셉을 작게 실험하고 구현해보는 것이었다.
- 초반에는 AI를 바로 적용하기보다, AI 없이도 동작 가능한 기본 흐름과 인터랙션 구조를 먼저 개발하려는 의도가 있었다고 사용자는 회상했다.
- 현재 문서에서는 이 의도가 "1주차에는 개발하지 않는다"처럼 너무 강한 규칙이나 제한으로 표현된 것처럼 느껴졌다.

사용자가 의심한 문제:

1. `input mode`의 위치와 의미가 이상하다.
   - `input`, `audio`, `mic`를 나눈 것은 제품 본질이라기보다 테스트와 구현 편의를 위한 입력 방식 분리였다.
   - 그런데 현재 문서에서는 이 구분이 제품 시나리오의 중요한 개념처럼 보인다.

2. `product-context`의 톤이 너무 강제적이다.
   - AI가 매 세션 프로젝트 맥락을 읽을 때 뉘앙스가 과하게 고정될 수 있다.
   - "완성형 상담 앱을 바로 만들지 않는다"가 "하면 안 된다"류의 제한으로 읽힐 위험이 있다.

3. 용어가 어렵고 해석 비용이 높다.
   - Input Mode, Text Replay, Audio File Test 같은 용어가 프로젝트 이해를 돕기보다 방해하는 느낌이 있다.
   - 어떤 용어는 유지하고, 어떤 용어는 쉬운 표현으로 바꾸고, 어떤 용어는 내부 구현 용어로 제한해야 할지 검토해달라고 요청했다.

사용자는 자료를 시간순으로 보라고 했다.

- 프로젝트 발단 자료
- 1차 페어에서 공유된 초기 방향성 자료
- 1차 회의 전후의 기획 폴더 자료
- 개발 중 만들어진 팀 repo와 하네스 구조
- 페어 회의 자료
- 프로젝트 진행 중의 대화 기록과 합의 맥락

특히 아래 구분을 요구했다.

- 실제 대화에서 명확히 합의된 내용
- 합의는 있었지만 문서화 과정에서 표현이 강해지거나 의미가 바뀐 내용
- AI가 대화 맥락을 잘못 해석해 반영했을 가능성이 있는 내용
- 임시 논의나 실험적 아이디어였는데 고정된 원칙처럼 문서화된 내용
- 특정 시점의 작업 편의를 위해 나온 내용

## 2. 초기 분석 결론 발췌

초기 분석에서는 아래처럼 정리했다.

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

초기 분석에서 본 시간순 의도 변화:

| 시점 | 원래 의미 | 이후 변형 |
| --- | --- | --- |
| 발단 | 상담/CX 운영 문제, 긴 상담과 의도/감정/해결 여부/위험도 분석의 큰 아이디어 | 팀 프로젝트로 오면서 전체 CX 대시보드는 후순위 배경으로 내려감 |
| 1차 페어 | 음성 AI 상담에서 말 끊기, 맥락 전환, 침묵 같은 대화 흐름 문제가 핵심 | 1주일 MVP 일정으로 축소 |
| 2차 페어 | 완성형 음성 상담 앱보다 interruption 판단 구조를 먼저 검증하기로 합의 | Text Replay, Audio File Test, Mic Trial이 명명되며 구조화됨 |
| 3차 페어 | policy가 추상적이라 AI Action Policy로 구체화. 문서/하네스가 너무 강하면 AI가 갇힌다는 우려 등장 | 용어 체계가 본격적으로 커짐 |
| 4차 페어 | scenario는 전체 상담 플로우가 아니라 AI 발화 중 고객 신호가 들어온 순간으로 합의. input mode는 테스트 입력 방식으로 정리 | 이 구분은 맞지만 이후 문서에서는 너무 상위 흐름에 배치됨 |
| 5차 페어 | rule mapping과 실제 AI 판단의 차이를 발견. baseline/policy v1도 LLM action judgment를 타야 한다고 재정의 | 현재 문서에는 반영됐지만 일부 오래된 rule/pretrained embedding 표현과 충돌 |

초기 분석에서 "대화상 합의로 보이는 내용"으로 본 것:

- 완성형 상담 앱을 바로 만들지 않는다.
- 코어는 단순 감지보다 AI가 다음 행동을 어떻게 고를지다.
- Text Replay는 음성을 포기하는 게 아니라 policy 판단을 빠르게 검증하는 단계다.
- Audio File Test는 최소 대표 케이스로 연결한다.
- Mic/실시간 입력은 같은 입력 경로 계열이지만, 현재 구현 성숙도상 확장 예정이다.
- `input_mode`는 테스트 입력 방식이다.
- `context/internal`은 현재 개발 기준 원천에 가깝게 쓰되, 파생물이 무분별하게 들어오면 안 된다.

초기 분석에서 "문서화 과정에서 강해진 내용"으로 본 것:

- "완성형 상담 앱을 바로 만들지 않는다"가 "이 프로젝트는 상담 AI 앱이 아니다"처럼 읽힐 수 있다.
- "1주차 핵심이 아니다"가 "하지 않는다/하면 안 된다"처럼 AI에게 해석될 위험이 있다.
- "Text Replay 중심"이 제품 구조의 중심처럼 보일 수 있다.

초기 분석에서 "AI가 과잉 해석해 문서화했을 가능성이 있는 내용"으로 본 것:

- `input_mode`가 top-level pipeline에 들어간 것
- rule과 pretrained embedding 기반 검증으로 충분하다는 문장이 LLM action policy 의도와 충돌한 것
- `baseline`, `policy_v1` 이름이 LLM 기반 판단 정책인지 VAD/rule placeholder인지 혼선을 만든 것

## 3. 하네스 영향 점검

사용자는 초기 분석 이후 "지금 분석에 영향을 끼칠 지금 하네스의 rule이나 agent나 원칙도 점검해달라"고 요청했다.

점검 결론:

```text
현재 하네스가 이전 분석을 완전히 왜곡할 정도는 아니지만,
AI가 기본값으로 읽으면 제품 의도보다 실험 하네스/현재 기준/context-internal을
더 강하게 신뢰하게 만드는 압력은 분명히 있다.
```

영향을 주는 지점:

- 프로젝트 개요가 "Whisper 기반 intent/interruption detection 실험"으로 되어 있어 원래 배경인 음성 AI 서비스의 interruption 경험 개선보다 구현/탐지 쪽으로 좁게 읽힐 수 있었다.
- `context/README.md`가 일반 개발 작업에서는 `internal`을 먼저 보게 하고 archive를 active 기준으로 직접 쓰지 말라고 한다. 일반 구현에는 좋지만, 이번처럼 원래 의도 복원/문서 감사 작업에서는 현재 문서의 왜곡을 현재 문서로 정당화할 위험이 있다.
- `context/internal/README.md`가 Product Context, Project Language Map, Scenario Worked Example을 모두 현재 기준 자료로 등록하고, Project Language Map 설명에서 scenario, input mode, event type, action label, policy version을 나란히 나열해 `input_mode`를 제품/기획 핵심 층위처럼 보이게 할 수 있었다.
- `harness-structure-reviewer` agent는 input adapter / policy / evaluator / runner / results 경계를 보호하므로 코드 구조 점검에는 적합하지만, 제품 의도 분석에서는 하네스 언어를 더 전면화할 수 있다.

그래도 완충 장치도 있었다.

- workflow rule은 "가벼운 가이드"이고 "강한 gate가 아니라 기본값"이라고 명시되어 있었다.
- harness candidates는 backlog일 뿐 active rule이 아니라고 되어 있었다.

즉, 하네스는 잘못된 것이 아니라 기본 렌즈가 실험 산출물 쪽으로 기울어져 있었고, 제품 의도 복원 작업에는 예외 원칙이 필요하다고 판단했다.

## 4. 1차 작업 진행

사용자가 종합 분석 결과를 실행해보자고 했고, 브랜치를 따로 파서 작업하라고 요청했다.

작업 브랜치:

```text
docs/context-intent-alignment
```

1차 적용 내용:

- 프로젝트 개요를 "Whisper 기반 detection" 중심에서 "음성 AI 상담의 끼어들기/의도 전환 경험" 중심으로 조정했다.
- `product-context.md` 첫 기준을 다시 써서 제품 의도와 현재 MVP 범위를 분리했다.
- Text Replay / Audio File Test는 제품 개념이 아니라 현재 입력 경로라고 명시했다.
- `mvp/current.md`에서도 같은 톤으로 MVP 한 줄 정의를 정리하고, rule/pretrained embedding 표현을 제거했다.
- `project-language-map.md` 최상단 흐름에서 `input_mode`를 빼고, 입력 경로를 adapter 층위로 낮췄다.
- `scenario-worked-example.md`에는 `event_type`, `expected_user_intent`, `expected_action`이 LLM prompt에 들어가지 않는 기준 annotation이라고 명시했다.
- `context/README.md`, `context/internal/README.md`에 "의도 복원 / 문서 감사" 예외와 읽기 우선순위를 추가했다.
- repo-local harness reviewer 설명도 "새 input mode" 대신 "새 입력 경로(input adapter/input_mode)"로 맞췄다.

검증:

- `git diff --check` 통과
- 문제 표현 검색에서 `rule과 pretrained`, `scenario -> input_mode`, `event_type / expected_user_intent를 기준으로 policy input` 같은 충돌 표현이 남지 않음을 확인

## 5. 사용자 피드백: 수정량이 적어 보임

사용자는 1차 작업 후 이렇게 피드백했다.

```text
근데 뭐랄까 뭐 수정자체는 잘 된것 같은데
전반적으로 수정한부분이 별로 없어보이는? 그런느낌이네
```

이 피드백은 중요한 방향 전환이었다.

처음 작업은 기존 문서 위에 조심스럽게 표현을 고치는 쪽이었지만, 사용자는 문서의 구조/첫인상 자체가 바뀌길 기대하고 있었다.

이에 따라 `product-context.md`를 더 과감하게 다시 정리했다.

- 기존 표 중심 문서를 "세션 시작 때 제품 의도를 회복하는 문서"로 접었다.
- Active 기준 위치, 제품 표면 기준, Policy 비교 기준 같은 하네스성 표를 덜어냈다.
- 첫 화면에서 바로 "음성 AI 상담의 끼어들기/의도 전환 경험"과 "현재 MVP는 판단 구조 검증"이 보이게 했다.
- `project-language-map.md`는 세션 시작 문서가 아니라 용어가 헷갈릴 때 보는 작업용 사전이라고 명시했다.
- `mvp/current.md`도 제품 의도를 새로 정의하는 문서가 아니라 실행 기준 문서라고 선을 그었다.

이후 사용자가 "다른데는 더 없어?"라고 물었고, 이어서 "그냥 분석한 결과를 바탕으로 적용할만한 부분은 다 작업해놔줘 다만 docs는 냅두고"라고 했다.

그 결과 `docs/`는 건드리지 않고 아래 범위까지 정리했다.

- `README.md`
- `CLAUDE.md`
- `context/README.md`
- `context/internal/**`
- `.claude/.codex`의 repo-local harness reviewer 설명

## 6. 다른 분석 자료와 용어 정리 논의

사용자는 다른 Claude의 분석도 제공했다.

그 분석의 요지는 더 강했다.

- 5월 9일 5차 페어가 왜곡의 분기점이었다.
- 하네스 폴더 구조 재편, baseline부터 LLM 판단으로 전환, 기획 원문 archive 이동, negative-list 추가가 한꺼번에 일어나면서 문서 톤이 강해졌다.
- `Input Mode`가 입력 adapter였는데 시나리오 중간의 동등 층위처럼 등장했다.
- product-context의 negative-list가 너무 많았다.
- "1주차에는 앱을 만들지 않는다"는 정확한 문장은 없지만 등가 표현이 반복되어 강하게 느껴졌다.
- 60개 이상의 도메인 용어가 active로 잡혀 있어 1주일 사이드 프로젝트 규모에 과하다.

사용자는 "그것밖에 없어 할게?", "용어 정리 뭐 이런 분석은 참고하면 안 되는 거야?"라고 물었다.

이에 대해 바로 적용할 것과 보류할 것을 나누었다.

바로 적용해도 되는 것:

- 문서 설명에서 `Input Mode`를 "입력 경로 / 테스트 입력 방식"으로 낮춘다.
- `Text Replay`, `Audio File Test`, `Mic Trial`은 제품 개념이 아니라 입력 경로로 설명한다.
- `AI Action Policy`는 설명문에서 "AI 행동 판단"으로 풀어 쓴다.
- `scenario`는 "판단 케이스"로 처음 등장시 설명한다.
- `Workbench`는 제품 컨셉으로 앞세우지 않는다.

바로 적용하지 않는 것:

```text
input_mode를 코드에서 input_adapter로 rename
expected_action, actual_action을 다른 key로 변경
event_type 7종을 4종으로 축소
primary failure 5종을 3종으로 축소
brief_ack를 continue에 병합
Workbench UI title을 코드에서 전부 제거
```

보류 이유:

- 대부분 schema/API/evaluation 계약 변경이다.
- 데이터, 테스트, evaluator, run artifact와 연결되어 있어 문서 톤 정리와 같은 PR에 섞으면 안 된다.
- 실제로 줄일지는 run 결과와 팀 합의가 더 필요하다.
- 현재 문제는 식별자 자체보다 문서와 UI에서 제품 개념처럼 앞세워지는 층위 문제다.

## 7. 확정한 용어 기준

대화 중 최종적으로 아래 기준이 생겼다.

| 현재 용어 | 정리 방향 |
| --- | --- |
| Input Mode | 문서 본문에서는 "입력 경로" 또는 "테스트 입력 방식"으로 풀어 쓴다. 코드/API/run artifact에서는 `input_mode` 유지 |
| Text Replay | "텍스트 입력(Text Replay)"처럼 병기 가능. 제품 컨셉이 아니라 판단 구조를 빠르게 검증하는 입력 경로 |
| Audio File Test | "오디오 파일 입력(Audio File Test)"처럼 병기 가능. prosody 검증 전체가 아니라 대표 음성 파일을 runner에 연결하는 경로 |
| Mic Trial | "마이크 입력(Mic Trial)"처럼 병기 가능. 같은 입력 경로 계열이지만 현재 구현에서는 확장 예정 상태로 둔다 |
| AI Action Policy | 설명문에서는 "AI 행동 판단" 또는 "AI 행동 기준"으로 풀어 쓴다. 코드/정식 명칭은 유지 가능 |
| scenario | "판단 케이스(`scenario`)"로 설명. 전체 상담 플로우가 아니라 한 순간 |
| Test Bench | `Playground`처럼 표면 이름으로 유지한다. 설명할 때는 "Test Bench(배치 평가)"처럼 병기하고, 수치와 run artifact를 남기는 평가 표면으로 설명한다 |
| Playground | 단일 판단 케이스를 조작하며 reason을 보는 표면. 유지 |
| Workbench | 상위 UI 이름 후보로만 두고 제품 컨셉으로 앞세우지 않는다 |
| expected_action | "사람이 정한 기준 행동"으로 설명. key는 유지 |
| actual_action | "policy가 낸 판단 행동"으로 설명. key는 유지 |

핵심 원칙:

```text
제품 의도와 처음 읽는 표면은 쉽게 설명한다.
그러나 구현/평가 재현에 필요한 코드값과 표면 이름은 숨기지 않고 병기한다.
```

## 8. 코드 주석 작업

사용자는 "코드 베이스에 반영할 게 있을까?", "그럼 코드에 주석쪽은?"이라고 물었다.

판단:

- schema/API 계약은 건드리지 않는다.
- LLM prompt는 policy behavior에 영향을 주므로 건드리지 않는다.
- 안전한 범위는 docstring/comment/argparse description처럼 사람이 읽는 프레이밍뿐이다.

적용한 파일:

- `src/backend/main.py`
- `src/backend/__init__.py`
- `src/interruption_detection/__init__.py`
- `scripts/generate_audio_fixtures.py`
- `src/interruption_detection/audio/manifest.py`
- `src/runner.py`

변경 방향:

- Work Bench / interruption detection 중심 표현을 행동 판단 맥락으로 조정
- Audio File Test를 "오디오 파일 입력"으로 풀어 설명
- runner 설명을 "끼어들기/의도 전환 행동 판단 policy"로 조정

커밋:

```text
9e4476b docs(code): 행동 판단 맥락에 맞게 주석 표현 정리
```

## 9. UI 워딩 후속 논의

decision 기록을 만든 뒤, 사용자는 프로젝트를 띄웠을 때 보이는 UI 워딩도 기존 단어 때문에 이해하기 어렵다고 했다.

초기 UI 수정은 아래처럼 꽤 많이 쉬운 말로 바꾸는 방향이었다.

- `Work Bench` -> `행동 판단 실험`
- `Scenario` -> `판단 케이스`
- `Input mode` -> `입력 경로`
- `Test Bench Report` -> `Test Bench Report(배치 평가 화면)`처럼 표면 이름을 유지하며 설명 병기
- `expected / actual` -> `기준 행동 / 판단 행동`
- `event type` -> `고객 신호`

그러나 사용자는 다시 중요한 피드백을 줬다.

```text
근데 무조건 용어를 수정하는것보다 어느정도 감안해서 수정해야하지 않을까?
다시 문서 작업사항들을 면밀히 살펴보고 수정해보는건 어때?
정말 구체적으로 디테일하게 어떤기준으로 수정햇다 생각해보는거지
```

이 피드백으로 UI 기준도 다시 정교해졌다.

최종 UI 워딩 기준:

1. `Workbench`처럼 제품 컨셉처럼 오해될 수 있는 상위 이름은 낮춘다.
2. `Playground`, `Test Bench`처럼 현재 문서에서 실제 표면 이름으로 남긴 용어는 유지하고, 필요한 설명만 한국어로 병기한다.
3. `input_mode`, `expected_action`, `actual_action`처럼 코드/API 계약인 말은 화면에서 완전히 숨기지 않고, 필요하면 괄호로 남긴다.
4. 사용자가 처음 보는 제목/버튼/빈 상태 문구는 한국어로 쉽게 읽히게 한다.
5. action/event/failure 값은 `답하고 계속 (respond_and_continue)`처럼 의미와 코드값을 함께 보여준다.

이후 사용자는 코드 작업 부분은 되돌리고 decision만 커밋하라고 했다. 따라서 UI 워딩 변경은 되돌렸고, 이 decision에는 후속 기준으로만 남긴다.

## 10. 반영 커밋 대조

이 decision이 설명하는 이미 반영된 커밋:

```text
d466dbd docs(context): 제품 의도와 하네스 읽기 기준 정리
0d624f3 docs(context): 하네스 용어의 제품 맥락 압박 완화
a318f81 docs(context): 쉬운 용어 우선으로 내부 표현 정리
9e4476b docs(code): 행동 판단 맥락에 맞게 주석 표현 정리
1ae6b7b docs(decision): context intent alignment 결정 기록
abf4493 docs(decision): context alignment raw 맥락 보강
10cc5e8 docs(context): Mic Trial과 Test Bench 표현 기준 정리
```

커밋별 의미:

| 커밋 | 의미 |
| --- | --- |
| `d466dbd` | 제품 의도와 하네스 읽기 기준을 active 문서에 반영한 1차 정리 |
| `0d624f3` | 하네스 용어가 제품 맥락을 압박하지 않도록 rules/agents/internal 문서 표현을 낮춤 |
| `a318f81` | 내부 문서 전반에서 쉬운 한국어 설명을 먼저 두고 코드 식별자는 필요한 자리에 병기 |
| `9e4476b` | 코드 주석/docstring에서 Workbench/detection 중심 프레이밍을 행동 판단 맥락으로 조정 |
| `1ae6b7b` | 위 작업의 대화 맥락과 적용/보류 기준을 decision으로 기록 |
| `abf4493` | decision raw를 풍부하게 보강하되, 공유 문서 경계에 맞게 직접 회사명/개인 경로성 표현은 낮춤 |
| `10cc5e8` | Mic Trial은 같은 입력 경로 계열로, Test Bench는 실제 surface 이름으로 유지하도록 용어 기준 보정 |

## 11. 이 decision을 남기게 된 이유

사용자는 이후 이렇게 확인했다.

```text
지금 코드 작업말고 이전작업들있지?
이거 과거 커밋 작업 대화인데 decisions에 반영되어 있나?
```

확인 결과 기존 `context/decisions/`에는 2026-05-09 결정 3개만 있었다.

- Context Directory Boundary
- Product Planning Archive Boundary
- LLM Action Policy Baseline

하지만 이번 브랜치에서 수행한 context intent alignment 작업의 이유와 대화 맥락은 별도 decision으로 남아 있지 않았다.

따라서 `2026-05-11-context-intent-alignment`를 만들었다.

이후 사용자가 raw가 너무 얕아 맥락을 놓칠 수 있다고 지적해, 이 파일을 더 풍부하게 보강했다.

## 12. 다음에 다시 볼 때 주의할 점

- 이 decision은 "용어를 모두 한국어로 바꾸자"는 결정이 아니다.
- 이 decision은 "코드 식별자를 rename하자"는 결정도 아니다.
- 핵심은 제품 의도, 문서 톤, 하네스 용어의 층위를 분리하는 것이다.
- schema/API/evaluation 계약 변경은 별도 decision과 테스트 계획이 필요하다.
- UI 워딩을 다시 만질 때는 쉬운 말과 코드값 병기의 균형을 잡아야 한다.
- 원래 의도 복원 작업에서는 현재 `context/internal/`도 정답이 아니라 검토 대상이 될 수 있다.

## 13. context-language-balancer agent 추가 맥락

사용자는 이번 브랜치 작업에서 문서 단어와 맥락을 계속 직접 점검해야 했고, 이 패턴을 agent로 추출할 수 있겠다고 말했다.

초기 아이디어:

- 단순 개발 지식만 있는 reviewer는 기술 용어를 너무 앞세울 수 있다.
- 반대로 "가독성"만 보는 reviewer는 문서를 과하게 친절하게 만들고 기준을 흐릴 수 있다.
- 필요한 것은 제품을 보는 태도와 개발 하네스 이해를 함께 가진 문서/용어 균형 reviewer다.

정리한 agent 역할:

- 이름은 `context-language-balancer`로 둔다.
- report-only agent다. 파일을 직접 수정하지 않는다.
- 문서를 더 쉽게 만드는 것이 목적이 아니고, 현재 용어를 무조건 보존하는 것도 목적이 아니다.
- 각 표현이 제품 개념, 입력 경로, UI surface, schema/API 계약, run artifact 중 어느 층위인지 판정한다.
- "구현 계약 보존"이라는 표현은 agent가 현재 식별자를 무조건 고정하게 만들 수 있어, "구현 계약 민감도 판단"으로 바꿨다.
- 공유 문서 경계는 얇은 quick check로만 둔다. 로컬 절대경로와 비공개 원문 위치가 직접 들어갔는지만 본다.
- repo-local agent 안에는 프로젝트 밖 개인 도구 이름이나 비공개 자료 관리 책임을 넣지 않는다.

추가한 파일:

- `.claude/agents/context-language-balancer.md`
- `.codex/agents/context-language-balancer.toml`
- `CLAUDE.md` Repo-local tools 색인
