# 팀 프로젝트 하네스 종합 분석

작성일: 2026-05-07

## 목적

이 문서는 `whisper-intent-interruption-detection` 팀 사이드 프로젝트에 필요한 하네스를 정리한다. 핵심은 특정 레퍼런스의 폴더명이나 agent 이름을 복사하는 것이 아니라, 여러 하네스에서 반복되는 설계 패턴을 **확정된 MVP의 구현, 검증, 문서화 흐름**에 맞게 재해석하는 것이다.

여기서 말하는 `초기`와 `확장`은 하네스 도입 단계가 아니라 **개발 진행 단계**다. 개발 초기에도 조사, 구조 검토, 수치 검증, 실패 사례 분류 같은 agent 역할은 쓸 수 있다. 다만 그 역할을 저장소 안의 영구 정의로 둘지는 반복성과 비용을 보고 결정한다.

## 확정된 MVP 맥락

2차 회의 후 MVP는 단순한 `interruption detector`가 아니라 **Interruption Detection Test Bench**, 즉 AI 엔지니어용 실험 콘솔로 정리됐다.

1주차 최소 기준은 아래다.

```text
Text Replay MVP
  + 대표 Audio File Test
  + Mic Trial은 후순위 확장 슬롯
```

핵심 제품 질문은 “사용자가 말했는가?”에서 끝나지 않는다.

```text
AI가 말하는 중 고객 신호가 들어왔을 때
AI가 계속 말할지, 짧게 반응할지, 잠깐 멈출지,
새 상담 흐름으로 전환할지, 확인 질문할지, 이관 후보로 보낼지
상황별로 판단할 수 있는가?
```

따라서 하네스가 보호해야 할 중심 흐름은 아래다.

```text
Scenario Bank
-> Input Mode
-> Signal / Transcript
-> Event Type / Intent
-> AI Action Policy
-> action label
-> Evaluation
-> Decision Log
-> Error Analysis
```

이 흐름에서는 `VAD-only baseline`도 중요하지만, 최종 중심은 `Interrupt-aware AI Action Policy`다. 즉 “소리 나면 멈춤”보다 나은 제품 행동 판단 구조를 만들고, `false stop`과 `missed switch`가 어떻게 달라지는지 보여주는 것이 MVP의 핵심이다.

## 하네스가 답해야 할 질문

이제 하네스는 실험 수치만이 아니라 구현 구조와 제품 판단 흐름까지 추적해야 한다.

- 이 파일은 원본 scenario인가, label/action 기준인가, 구현 코드인가, 설정인가, 실행 결과인가?
- 같은 고객 상황이 Text Replay와 Audio File Test에서 같은 AI Action Policy 입력으로 들어가는가?
- 이 코드는 입력 모드, 처리 흐름, 판단 로직, 평가 중 어디에 속하는가?
- P0/P1/P2/P3 policy version은 같은 evaluator로 비교되는가?
- `expected_action`과 `actual_action`은 어떤 기준으로 비교되는가?
- false stop, missed switch, action accuracy는 어떤 result artifact에서 나온 값인가?
- decision log에는 policy가 왜 그런 action label을 골랐는지 남는가?
- 실패 케이스가 다음 scenario/rule/threshold 개선으로 돌아오는가?
- agent나 자동 검사가 필요한 반복 작업은 무엇인가?

## 세 레퍼런스의 공통점

세 자료는 출처와 관심사가 다르지만, 반복해서 같은 방향을 가리킨다. 공통점은 “AI에게 더 많은 지침을 주자”가 아니라 **구현과 검증이 다시 추적 가능하도록 작업 표면을 나누자**에 가깝다.

| 공통점 | 세 자료에서 반복된 신호 | 이 MVP에서 가져올 해석 | 예시 상황 |
| --- | --- | --- | --- |
| 루트 지침은 얇아야 한다 | 매번 읽히는 지침이 길어지면 오히려 작업 판단을 흐린다 | `CLAUDE.md`는 항상 필요한 협업/경계 규칙만 둔다 | AI Action Policy 세부 규칙은 루트가 아니라 별도 문서/코드에 둔다 |
| 기준 파일과 결과 파일을 나눈다 | 원본, 결정, 실행 결과, 공유 문서를 한 표면에 섞지 않는다 | Source of Truth와 실행 결과를 분리한다 | `scenarios.json`과 `evaluation.json`을 섞지 않는다 |
| 증거 없이 완료를 말하지 않는다 | review, test, ship gate가 모두 evidence를 요구한다 | 코드 변경은 실행 결과와, 성능 주장은 metric/decision log와 연결한다 | 콘솔 변경은 sample input으로 실행하고, README 수치는 result에서 확인한다 |
| 역할을 분리한다 | 기준 문서, 실행 코드, 검증 agent, 자동 검사 장치가 서로 다른 일을 한다 | agent는 먼저 report-only 검토 역할로 쓴다 | 수치 검증은 agent가 해도 파일 수정은 메인 작업자가 한다 |
| 반복될 때 강화한다 | 처음부터 큰 framework를 들이지 않고, 확정된 반복 절차는 작게 정의한 뒤 필요할 때만 Sensor를 덧댄다 | 문서 -> agent -> hook 같은 고정 순서가 아니라, 문제 성격에 맞는 가장 가벼운 장치를 고른다 | result 덮어쓰기가 반복되면 run id/checker를 만든다 |
| 작은 완주 단위가 중요하다 | 큰 lifecycle보다 작은 단위의 완주와 검증을 강조한다 | 기능 하나를 구현, 실행, 평가, 문서화까지 닫는다 | Text Replay로 P0~P3 policy를 실행하고 expected vs actual을 확인한다 |

## 세 레퍼런스의 차이점

차이는 “무엇을 그대로 가져올까”보다 “각 자료가 어떤 판단을 도와주는가”로 보는 편이 좋다.

| 레퍼런스 | 주 관심사 | 강한 점 | 그대로 가져오면 어색한 점 | 이 MVP에서의 쓰임 |
| --- | --- | --- | --- | --- |
| 외부 하네스 조사 | 여러 AI coding harness의 공통 운영 방식 | 작업을 계획, 구현, 리뷰, 검증, 기록으로 닫는 흐름과 과한 context의 위험을 보여준다 | gstack/Superpowers/BMAD 같은 full framework는 팀 POC에 무겁다 | 기능 구현과 policy 실험을 모두 `계획 -> 구현 -> 검토 -> 검증 -> 기록`으로 닫는 감각을 가져온다 |
| 내부 구조 하네스 분석 | 지식/문서/결정/검증 표면을 나누는 방식 | Source of Truth, decision record, report-only 검토 역할이 선명하다 | 장기 지식 허브나 글쓰기 repo의 전체 폴더 지도는 현재 repo에 과하다 | scenario, label, policy decision, result, report의 위치를 나누는 기준으로 쓴다 |
| 이전 구현/실험 프로젝트 하네스 분석 | 실제 구현과 실험을 굴리는 규칙 | 3층 구조, config 규약, 코드 스타일, Guide/Sensor, Before/After 증명이 구체적이다 | RAG/QA/VLM/Supabase나 교육 sprint 규칙은 이 프로젝트와 다르다 | input adapter, policy pipeline, evaluator, config, smoke test 같은 개발 규칙으로 바꿔 적용한다 |

요약하면, 외부 조사는 **작업 단위 운영 철학**, 내부 구조 분석은 **작업 표면의 경계**, 이전 구현/실험 프로젝트 분석은 **구현과 검증을 굴리는 개발 규칙**을 준다. 이 셋을 섞되, 폴더명이나 도구 묶음은 그대로 복사하지 않는다.

## 분석에서 나온 핵심 판단

확정된 MVP를 기준으로 보면, 이 프로젝트에 필요한 하네스는 “실험 결과를 잘 보관하는 구조”보다 넓다. 필요한 것은 **AI Action Policy를 구현하고, 입력 모드가 달라도 같은 판단 흐름으로 실행하며, 그 결과를 설명 가능한 근거로 남기는 운영 구조**다.

따라서 바로 가져올 것은 특정 도구 묶음이 아니라 아래 패턴들이다.

| 패턴 | 왜 필요한가 | 이 MVP에서의 모습 | 예시 상황 |
| --- | --- | --- | --- |
| Source of Truth 정하기 | 기준 scenario, action label, 실행 결과가 섞이면 판단 기준이 흔들린다 | scenario, label 정의, policy code, result를 따로 둔다 | `scenarios.json`에 policy 예측값을 덮어쓰면 정답과 결과를 구분할 수 없다 |
| Input Adapter 분리 | Text, Audio, Mic이 모두 다른 구현을 타면 policy 비교가 어려워진다 | 입력 모드는 달라도 같은 AI Action Policy input으로 변환한다 | Audio File Test도 결국 `transcript`, `speech_event`, `current_intent`로 policy에 들어간다 |
| 실행 흐름 분리 | 빠른 POC일수록 입력, policy, 평가, 리포트가 한 파일에 뭉치기 쉽다 | entry, input adapter, policy pipeline, evaluator를 나눈다 | UI에서 바로 intent similarity를 계산하면 CLI 평가 재사용이 어렵다 |
| 설정과 실행 조건 기록 | 같은 policy라도 threshold, intent descriptions, transcript source가 다르면 결과가 달라진다 | model, threshold, input mode, dataset id, command, date를 결과와 같이 남긴다 | 발표 전날 `missed switch 감소`가 어떤 policy/version에서 나온 값인지 못 찾을 수 있다 |
| Policy version 비교 | P0~P3가 다른 평가 코드로 돌면 개선을 말하기 어렵다 | 모든 policy version을 같은 evaluator로 비교한다 | P0 VAD-only와 P3 AI Action Policy가 같은 confusion matrix 계산을 통과한다 |
| Decision Log 남기기 | action label만 있으면 왜 그런 판단을 했는지 설명할 수 없다 | `signals`, `reason`, `expected_action`, `actual_action`을 남긴다 | `stop_and_switch`가 intent shift 때문인지 complaint 때문인지 설명한다 |
| 코드 변경 단위 관리 | 구현과 리팩토링, 설정 변경이 섞이면 리뷰와 디버깅이 어려워진다 | 기능 변경, 구조 정리, config 변경을 가능한 한 분리한다 | policy rule 수정과 폴더 구조 개편을 한 번에 하면 성능 변화 원인을 찾기 어렵다 |
| 검토 역할 분리 | 팀원이 놓친 수치/근거/실패 사례를 별도 시선으로 볼 필요가 있다 | 조사, 구조 검토, 수치 검증, 실패 사례 분류는 report-only로 본다 | README의 “false stop 감소”가 실제 result와 맞는지 별도 검토한다 |
| 점진적 강제 | 처음부터 넓은 hook과 scanner를 두면 속도가 죽고, 늦으면 사고가 난다 | 확정된 반복 절차는 초기에 문서/체크리스트/skill/agent로 작게 두고, 반복 위반이 보이면 그 지점에 자동 검사를 더한다 | result 덮어쓰기가 반복되면 run id/checker를 만들고, hardcoded threshold가 반복되면 config check를 만든다 |

## 레퍼런스에서 추출한 패턴

### 1. Source of Truth와 작업 파일의 위치를 정한다

좋은 하네스는 “어디에 무엇을 써야 하는가”를 먼저 정한다. 이 MVP에서는 특히 scenario, action label, policy output, evaluation result가 섞이지 않아야 한다.

| 표면 | 역할 | 원칙 | 예시 상황 |
| --- | --- | --- | --- |
| 루트 지침 | 팀 전체에 항상 적용되는 최소 규칙 | 짧게 유지 | 매 작업마다 읽혀도 부담 없는 협업 규칙만 둔다 |
| scenario bank | 고객 상황과 기대 행동의 기준 | policy 결과를 덮어쓰지 않는다 | `expected_action`은 기준이고 `actual_action`은 결과다 |
| action label 정의 | AI가 선택할 수 있는 제품 행동 | label 이름과 의미를 안정적으로 둔다 | `brief_ack`를 독립 label로 둘지 결정하면 이유를 남긴다 |
| input mapping | text/audio/mic 입력을 policy input으로 변환 | 입력 방식별 차이를 adapter에 가둔다 | audio file은 transcript/source와 scenario id를 같이 둔다 |
| 설정 파일 | 모델, threshold, window size, intent descriptions | 코드 곳곳에 흩뿌리지 않고 한 곳에서 관리한다 | 여러 파일에 `0.7`이 박혀 있으면 threshold 변경이 누락된다 |
| policy code | P0~P3 판단 로직 | 같은 input/output contract를 따른다 | 모든 policy는 `actual_action`과 `reason`을 반환한다 |
| 실험/실행 기록 | 실행 조건과 결과 연결 | 나중에 재현 가능해야 함 | P2 결과와 P3 결과를 같은 파일명으로 덮어쓰지 않는다 |
| decision log | 각 판단의 이유 | 실패 분석과 리포트에서 재사용한다 | `signals`, `reason`, `is_correct`를 남긴다 |
| 공유 문서 | README, report, presentation | 실제 결과 파일에서 확인된 수치만 사용 | 발표 자료의 action accuracy 값은 `results/evaluation.json`에서 다시 확인한다 |

쉽게 말하면, “사람이 만든 기준”과 “코드가 만든 결과”를 한 파일에 섞지 말자는 뜻이다.

```text
data/scenarios.json         # 사람이 만든 고객 상황과 expected_action
data/audio_samples/         # 대표 음성 파일
data/audio_mapping.*        # audio file과 scenario/transcript 연결
src/policies/               # P0~P3 AI Action Policy 구현
results/evaluation.json     # policy 실행 결과와 metric
results/decision_logs.jsonl # policy가 왜 그런 행동을 골랐는지
results/error_analysis.md   # 실패 케이스와 다음 개선 포인트
```

예를 들어 `data/scenarios.json`이 정답 기준이라면, 평가 스크립트가 여기에 `actual_action`을 덮어쓰면 안 된다. 예측 결과는 `results/`에 따로 남겨야 한다. 그래야 나중에 action accuracy가 바뀌었을 때 scenario 기준이 바뀐 것인지, policy가 바뀐 것인지, threshold가 바뀐 것인지 추적할 수 있다.

### 2. 입력 모드는 분리하되 판단 구조는 하나로 둔다

MVP의 중요한 결정은 `Text Replay + 대표 Audio File Test`, 그리고 Mic Trial 후순위다. 이것은 구현상 input layer를 분리해야 한다는 뜻이다.

| 입력 모드 | 1주차 역할 | policy에 넘길 형태 | 하네스 포인트 |
| --- | --- | --- | --- |
| Text Replay | scenario와 action label을 가장 빠르게 검증 | `user_utterance`, `event_type`, `current_intent` | 기본 평가 모드 |
| Audio File Test | 음성 프로젝트라는 연결고리를 확보 | `audio_file`, `transcript`, `speech_event` | audio mapping과 mock/precomputed transcript 허용 |
| Mic Trial | 후속 live 입력 구조 확인 | `recording_state`, `transcript`, `latency_hint` | 1주차 성능 평가 대상 아님 |

중요한 것은 세 입력 모드가 서로 다른 판단 로직으로 흩어지지 않는 것이다. 입력 방식은 다르지만 최종적으로 같은 AI Action Policy input으로 변환되어야 P0~P3 비교가 가능하다.

### 3. 코드는 “입력, 처리 흐름, 정책, 평가”로 나눈다

3층 구조의 핵심은 이름 자체가 아니라 **변경 이유가 다른 코드를 분리하는 것**이다. 이 MVP에서는 기존의 entry/pipeline/domain 구분을 조금 더 제품 흐름에 맞춰 읽는 편이 좋다.

| 레이어 | 책임 | 예시 | 섞이면 생기는 문제 |
| --- | --- | --- | --- |
| Entry / Console | CLI, HTML console, demo script | `index.html`, `cli.py` | 화면 수정이 policy 로직을 건드림 |
| Input Adapter | Text/Audio/Mic 입력을 공통 input으로 변환 | scenario loader, audio mapping, transcript source | Audio File Test만 다른 판단 흐름을 타게 됨 |
| Policy Pipeline | P0~P3 policy 실행 흐름 조합 | policy runner, version selector | policy 비교가 evaluator와 뒤섞임 |
| Domain Logic | intent similarity, backchannel rule, action rule | `intent_detector.py`, `p2_intent_shift.py` | threshold/intent 변경 추적 어려움 |
| Evaluation | expected vs actual, metrics, confusion matrix | `evaluator.py` | 평가 변경과 policy 개선이 뒤섞임 |
| Reporting | README/report/demo scenario 정리 | report generator, manual summary | 검증 전 수치가 문서에 들어감 |

처음부터 모든 폴더를 만들 필요는 없다. 하지만 구현이 시작되면 “이 코드는 입력 변환인가, policy 판단인가, 평가인가, 표시인가?”를 계속 물어야 한다. 같은 파일 안에서 세 책임이 길게 섞이면 분리 신호다.

### 4. 설정과 코드 변경을 추적 가능하게 둔다

이 프로젝트는 실행 가능한 콘솔/파이프라인을 만드는 구현 프로젝트다. 그래서 threshold, model name, intent description, action label subset, transcript source 같은 설정이 코드 곳곳에 흩어지면 금방 관리가 어려워진다.

| 기준 | 이유 | 예시 상황 |
| --- | --- | --- |
| 반복되는 값은 이름 붙인다 | 의미 없는 숫자가 흩어지는 것을 막는다 | `0.7` 대신 `INTENT_SHIFT_THRESHOLD`를 둔다 |
| policy input/output contract를 고정한다 | P0~P3를 같은 evaluator로 비교하기 위해서 | 모든 policy가 `actual_action`, `reason`, `signals`를 반환한다 |
| 실행 시점 설정을 결과와 같이 남긴다 | 같은 코드라도 설정이 다르면 결과가 달라진다 | intent descriptions 변경 전후 결과를 구분한다 |
| 기능 변경과 리팩토링을 구분한다 | 리뷰와 디버깅이 쉬워진다 | P2 intent logic 수정과 파일 이동을 분리한다 |
| 외부 서비스 의존을 감춘다 | API 교체나 mock 테스트가 쉬워진다 | 실제 STT가 없어도 precomputed transcript로 policy 실행 가능 |
| I/O와 순수 계산을 분리한다 | 테스트가 쉬워진다 | audio file 읽기는 adapter에 두고 intent similarity는 pure function으로 둔다 |

이전 프로젝트의 개발 규칙에서 가져올 핵심은 “특정 폴더 구조”보다 이런 냄새 신호다.

- 같은 threshold/window/timeout이 여러 파일에 반복된다.
- 함수 인자가 너무 많아진다.
- policy runner가 세부 intent 계산까지 모두 떠안는다.
- util이 단순 1:1 wrapper만 늘어난다.
- result 파일 생성과 policy 판단이 같은 함수에 묶인다.
- 테스트나 실행 확인 없이 큰 구조 변경이 들어간다.

### 5. 검증은 metric과 decision log를 함께 본다

이 MVP의 산출물은 단순히 “정확도 향상”이 아니다. 설득력 있는 것은 **어떤 고객 상황에서 어떤 action을 골랐고, 어떤 실패가 줄었는지**다.

| 항목 | 기록 이유 | 예시 상황 |
| --- | --- | --- |
| scenario id | 어떤 고객 상황에서 나온 결과인지 확인 | `commerce_refund_001` 결과를 다시 찾는다 |
| policy version | P0~P3 개선 흐름 추적 | P1이 false stop을 줄였는지 본다 |
| expected_action | 사람이 정한 기준 | `intent_shift`의 기준 행동이 `stop_and_switch`인지 확인 |
| actual_action | policy 결과 | P3가 실제로 어떤 action label을 골랐는지 본다 |
| signals | 판단에 쓴 입력 | `speech_event`, `transcript`, `intent_shift`, `similarity` |
| reason | 설명 가능성 | “backchannel이라 계속 진행” 같은 이유를 남긴다 |
| false stop / missed switch | 고객 경험 기준 metric | 맞장구에서 멈췄는지, 환불 전환을 놓쳤는지 본다 |
| action confusion matrix | 어떤 행동을 헷갈리는지 | `pause`와 `stop_and_switch` 혼동을 확인한다 |
| error analysis | 다음 수정 지점 | 실패 케이스를 scenario bank/rule/threshold 개선으로 되돌린다 |

여기서 중요한 것은 “실험 폴더를 예쁘게 만드는 것”이 아니라, 결과 수치를 제품 행동과 실패 사례로 설명할 수 있게 만드는 것이다.

### 6. Agent는 초기에 금지할 대상이 아니라 역할로 이해한다

초기 개발 단계에도 agent 역할은 충분히 쓸 수 있다. 다만 “agent를 쓴다”와 “저장소에 local agent 정의를 만든다”는 다르다. 이미 확정된 반복 절차라면 초기에 작은 skill이나 local agent로 두어도 된다. 조심할 것은 agent/skill 자체가 아니라, 아직 생기지 않은 미래 구조까지 예상해서 넓게 만드는 것이다.

| 역할 | 개발 초기 사용 | 영구 정의 후보가 되는 시점 | 예시 상황 |
| --- | --- | --- | --- |
| Material Review | MVP 문서, 논문 가이드, 기존 결정 요약 | 같은 종류의 context 수집이 반복되거나 시작 절차로 확정될 때 | PRD와 계획서를 한 장으로 압축한다 |
| Architecture Review | 입력 모드, policy, evaluator 경계 점검 | 코드 구조 논쟁이 반복되거나 경계 점검이 MVP의 고정 관문일 때 | Audio File Test가 Text Replay와 다른 policy 흐름을 타는지 확인한다 |
| Code Review | 구현 변경의 버그, 누락 테스트, config 누락 점검 | 기능이 여러 파일로 퍼질 때 | P2 변경 후 evaluator와 console이 같은 input contract를 기대하는지 본다 |
| Evidence Check | README/report/presentation 수치 검증 | 결과 리포트가 반복 생성되거나 외부 공유 전 검증 관문으로 확정될 때 | “missed switch 감소”가 실제 result와 맞는지 확인한다 |
| Failure Review | FP/FN과 action confusion 유형화 | 실패 사례 포맷이 안정될 때 | false stop이 backchannel 때문인지 noise 때문인지 나눈다 |
| Harness Scan | hardcoded threshold, result 삭제 위험 점검 | 코드와 규칙이 충분히 쌓였을 때 | 여러 파일에 `0.7`이 흩어져 있거나 result를 덮어쓰는지 본다 |

기본 원칙은 report-only다. agent는 조사/검증/분류 결과를 반환하고, 파일 수정은 메인 작업자가 판단한다. 이렇게 해야 자동화가 팀의 책임 경계를 흐리지 않는다.

### 7. Guide와 Sensor를 분리한다

문서에 적힌 규칙은 기억을 돕는 Guide다. 하지만 정말로 깨지면 안 되는 것은 언젠가 test, lint, hook, scanner 같은 Sensor로 옮길 수 있다. 이때도 고정된 승격 순서를 따르는 것이 아니라, 문제 성격에 맞는 필요한 장치를 고른다.

초기에는 대체로 Guide와 작은 역할 정의로 충분하다. 이미 확정된 반복 절차는 checklist, skill, report-only agent로 얇게 세울 수 있다.

- root guide
- synthesis 문서
- PRD/계획서
- README의 실행 방법
- scenario schema와 action label 정의
- 실험 시작 체크리스트 또는 작은 skill
- 수치 검증/구조 검토용 report-only agent 역할

반복 위반이 보이면 새 영역을 넓히기보다, 그 문제가 실제로 생긴 지점에 둘 Sensor 후보로 본다.

- result 파일을 자주 덮어쓴다 -> result snapshot/checker
- API key가 코드에 들어갈 뻔한다 -> secret scanner
- threshold가 여러 파일에 흩어진다 -> config check
- report 수치가 result와 어긋난다 -> evidence checker
- scenario 기준 파일이 직접 수정되며 이력이 사라진다 -> data guard
- CLI/console 실행이 깨진 채 문서만 바뀐다 -> smoke test
- 타입/포맷 오류가 반복된다 -> lint/typecheck

이 기준은 “자동화가 멋져 보이는가”가 아니라 “안 하면 실제로 실수하는가”다. 확정된 반복 절차를 작게 정의하는 것은 괜찮고, 아직 실체가 없는 미래 구조를 많이 만드는 것이 두터워지는 지점이다.

## 개발 단계별 적용

### 개발 초기: Text Replay MVP

목표는 가장 작은 실행 흐름이 한 번 이어지는 것이다.

```text
scenario
  -> P0/P1/P2/P3 policy 실행
  -> expected_action vs actual_action
  -> evaluation result
  -> decision log
  -> short report
```

이때 필요한 하네스는 작다.

- 루트 지침은 최소 협업 규칙만 둔다.
- scenario schema와 action label 정의를 먼저 안정화한다.
- policy input/output contract를 맞춘다.
- 반복되는 threshold, model name, intent descriptions는 상수나 config로 이름 붙인다.
- Text Replay는 sample scenario로 실제 실행해본다.
- P0~P3 policy는 같은 evaluator를 통과한다.
- result artifact가 생기기 전에는 성능 수치를 확정 표현하지 않는다.
- 필요한 경우 material review, architecture review, evidence check agent 역할을 사용한다.

### 개발 중반: Audio File Test와 policy 비교

Text Replay가 잡힌 뒤 대표 Audio File Test를 연결하고, policy version별 비교와 실패 분석이 늘어나는 단계다.

추가 후보:

- audio mapping: audio file, scenario id, transcript source 연결.
- run artifact contract: command, config snapshot, dataset id, metrics, manual sample.
- config object 또는 named constants: threshold/window/model 설정을 한 곳에서 추적.
- code review checklist: 기능 변경, 리팩토링, config 변경이 섞였는지 확인.
- failure taxonomy: false stop, missed switch, action confusion, ambiguous intent, STT uncertainty.
- evidence check 절차: report 수치와 result artifact/decision log 대조.

agent 역할은 초기에도 쓸 수 있다. 다만 이 단계부터 architecture review, code review, evidence check, failure review를 저장소 안의 local agent 정의로 둘 근거가 더 강해진다.

### 개발 확장: Mic Trial / Console Extension

Mic Trial, simulated live chunk, dashboard성 화면처럼 사용자가 보는 표면이 생기면 하네스도 조금 더 명확해야 한다.

추가 후보:

- route/controller와 policy pipeline 분리.
- demo input과 evaluation input 구분.
- latency/cost metric 기록.
- public report와 internal note 경계.
- smoke test, lint/typecheck, secret scan 같은 기본 Sensor.
- hook/scanner 같은 Sensor.
- docs/core, docs/lenses, docs/guards 같은 기준 문서 분리.

여기서도 핵심은 구조의 크기가 아니라 책임의 분리다.

## 바로 가져올 패턴

| 패턴 | 바로 적용 방식 | 예시 상황 |
| --- | --- | --- |
| 루트 규칙 최소화 | `CLAUDE.md`에는 항상 필요한 협업/경계 규칙만 둔다 | 세부 구현/검증 규칙은 synthesis 문서나 하위 문서에 둔다 |
| Source of Truth 정하기 | scenario, action label, policy result, report 수치를 구분한다 | `expected_action`과 `actual_action`을 같은 파일에 덮어쓰지 않는다 |
| Input Adapter 분리 | Text/Audio/Mic 입력을 공통 policy input으로 변환한다 | audio file도 transcript와 speech event로 policy에 들어간다 |
| AI Action Policy contract | P0~P3가 같은 input/output 형식을 따른다 | 모든 policy가 `actual_action`, `reason`, `signals`를 반환한다 |
| 실행 흐름 분리 | entry/input adapter/policy/evaluator/report 책임을 구분한다 | console 코드는 명령만 받고, policy 판단은 별도 함수에 둔다 |
| 설정값 이름 붙이기 | 반복되는 threshold/window/model name을 상수나 config로 둔다 | `0.7`이 여러 파일에 흩어지지 않게 한다 |
| 같은 평가 코드 사용 | P0~P3 policy를 같은 evaluator로 비교한다 | 모든 버전이 같은 action confusion matrix 계산을 통과한다 |
| 실행 조건 기록 | input mode, policy version, threshold, dataset id, date, command를 결과와 연결한다 | `results` 옆에 어떤 설정으로 돌렸는지 남긴다 |
| Decision Log 남기기 | 각 판단의 signal과 reason을 저장한다 | `stop_and_switch` 이유가 intent shift인지 complaint인지 남긴다 |
| 읽고 검토만 하는 역할 | agent 역할은 조사/검증/분류부터 사용한다 | 발표 수치 검증은 맡기되 파일 수정은 메인 작업자가 한다 |
| 점진적 강제 | 확정된 반복 절차는 작게 두고, 반복 실수가 보일 때 그 지점의 Sensor를 강화한다 | 결과 덮어쓰기가 반복되면 run id/checker를 검토한다 |

## 확장 후보로 남길 패턴

| 후보 | 도입 조건 |
| --- | --- |
| 결정 기록 템플릿 | action label, metric, threshold, model 기준이 바뀔 때 |
| 실행/검증 기록 형식 | 실행 조건이나 policy 비교가 2회 이상 반복될 때 |
| 실패 사례 분류표 | false stop, missed switch, action confusion 사례가 충분히 쌓일 때 |
| 코드 리뷰 체크리스트 | 구현 변경이 여러 파일로 퍼질 때 |
| 수치 검증 agent | report 수치 검증이 반복되거나 외부 공유 전 검증 관문으로 확정될 때 |
| 실패 사례 검토 agent | 실패 사례 분류가 반복되거나 분류 기준이 안정될 때 |
| 구조 검토 agent | input adapter/policy/evaluator 경계 문제가 반복되거나 고정 리뷰 관문이 필요할 때 |
| Smoke test/lint/typecheck | CLI나 콘솔 실행이 반복해서 깨질 때 |
| Hook/scanner | 반복 위반이나 큰 실수 비용이 확인될 때 |
| Observability | latency/cost가 주요 목표가 될 때 |

## 배제할 것

| 배제 대상 | 이유 |
| --- | --- |
| 완성형 하네스 framework 전체 설치 | 짧은 팀 POC에는 운영 비용이 크다 |
| 장기 지식 허브용 폴더 지도 | 이 repo의 현재 문제는 구현 파이프라인, 실행 조건, 결과 근거를 정리하는 것이다 |
| 글쓰기 전용 다중 agent 세트 | 공유 문서 경계는 필요하지만, 현재 핵심은 구현과 검증 흐름이다 |
| RAG/QA/VLM/Supabase 전용 규칙 | 기술 표면이 다르다 |
| 완성형 상담 앱 운영 규칙 | 1주차 MVP는 상담 앱이 아니라 실험 콘솔이다 |
| Live Mic 중심 하네스 | Mic Trial은 1주차 필수 평가가 아니라 후순위 확장 슬롯이다 |
| 초기 광범위 hook/scanner 강제 | 실제 위반 패턴을 먼저 봐야 한다 |
| 검증 전 성능 수치 확정 | 실행 결과가 나오기 전에는 예시로만 둔다 |

## 레퍼런스별 역할

| 레퍼런스 묶음 | 이 문서에서의 역할 |
| --- | --- |
| 외부 하네스 조사 | 작업 단위를 계획, 구현, 리뷰, 검증, 기록으로 닫는 운영 방식의 비교군 |
| 내부 지식/글쓰기 하네스 | 원본 자료, 가공 결과, 결정 기록, 검증 표면을 나누는 구조 감각의 근거 |
| 이전 구현/실험 프로젝트 하네스 | 3층 실행 구조, config/code-style 규칙, Guide/Sensor, Before/After 검증의 근거 |
| MVP 기획 문서 | Test Bench, Text Replay, Audio File Test, AI Action Policy, decision log, error analysis라는 실제 구현 목표의 근거 |

이 표는 “어느 레퍼런스에서 무엇을 그대로 가져온다”가 아니라, 각 자료가 어떤 판단을 가능하게 했는지 정리한 것이다.

## 최종 제안

현재 시점의 최선은 다음이다.

1. 루트 지침은 최소로 유지한다.
2. 이 문서는 하네스 후보와 판단 기준을 담는 synthesis 문서로 둔다.
3. 구현이 시작되면 input adapter, AI Action Policy, evaluator, report 경계를 의식한다.
4. 첫 실행 가능한 기능부터 sample scenario, policy output, evaluation result, decision log, 문서 설명을 연결한다.
5. 설정값과 실행 조건은 코드 곳곳에 흩어지지 않게 이름 붙이고 기록한다.
6. agent는 초기에도 report-only 역할로 사용할 수 있다. 영구 정의는 반복성이나 확정된 절차가 보일 때 만든다.
7. 자동 강제 장치는 실제 반복 실수나 큰 실수 비용이 확인된 지점에 필요한 만큼 도입한다.

이렇게 하면 프로젝트는 빠르게 움직이면서도, 나중에 팀원이나 면접관이 봤을 때 “이 콘솔이 어떤 고객 상황을 검증하고, AI Action Policy가 왜 그런 행동을 골랐으며, 그 결과가 어떤 조건에서 나온 것인지”를 설명할 수 있다.
