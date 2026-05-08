# Interruption Detection MVP PRD

> 작성일: 2026-05-06
> 상태: 2차 회의 후 PRD v1
> 관련 문서: `MVP-방향성-초안.md`, `MVP-계획서.md`
> 용어 기준: [용어-결정-노트.md](용어-결정-노트.md)

## 1. 제품 요약

### 제품명

상담 끼어들기 판단 실험 콘솔

영문 작업명은 `Interruption Detection Test Bench`로 둔다.

### 한 줄 설명

음성 AI 상담 중 사용자의 끼어들기와 맥락 전환을 감지하고, AI가 **계속 말할지, 잠깐 멈출지, 다른 상담 흐름으로 바꿀지** 판단하는 과정을 텍스트와 오디오 파일로 검증하고, 이후 마이크 입력까지 확장할 수 있게 하는 실험 콘솔이다.

### 먼저 보는 고객 장면

```txt
AI: 고객님의 상품은 현재 배송 중이며...
고객: 아 그게 아니라 환불받고 싶은데요.

문제:
AI가 이 말을 놓치고 배송 안내를 계속하면 고객은 "내 말을 안 듣는다"고 느낀다.

목표:
AI가 고객의 새 요청을 알아차리고, 하던 말을 멈춘 뒤 환불 흐름으로 바꾸게 한다.
```

이 PRD의 기술 용어는 이 장면을 구현하고 검증하기 위한 도구다. `action label`은 고객에게 보이는 말이 아니라, AI Action Policy가 내놓은 행동 결과에 붙이는 평가용 이름이다.

### 핵심 가치

이 MVP는 완성형 상담 AI 앱보다 먼저, 음성 상담에서 AI가 사용자의 개입 신호를 어떻게 해석하고 어떤 제품 행동을 선택해야 하는지 검증한다.

핵심은 **고객이 말했을 때 AI가 적절히 반응하는가**다. 구현에서는 이 문제를 `input mode`, `speech event`, `STT/transcript`, `intent shift`, `AI Action Policy`, `evaluation`으로 나누어 확인한다.

```txt
VAD-only:
사용자 음성 감지 => interruption

Interrupt-aware AI Action Policy:
입력 방식 선택: text / audio file / mic
-> 사용자 음성 또는 텍스트 신호 확보
-> 사용자 발화 해석
-> 기존 intent와 비교
-> 상황에 맞는 제품 행동 선택
-> expected_action과 비교
```

### 제품-기술 용어 매핑

| 제품/기획 표현 | 기술/구현 표현 | 이 MVP에서 보는 것 |
| --- | --- | --- |
| 테스트 상황 | scenario | AI 발화, 사용자 발화, 기대 행동을 묶은 케이스 |
| 입력 방식 | input mode | Text Replay, Audio File Test, Mic Trial 확장 슬롯 |
| 전사 출처 | transcript source | 직접 입력, precomputed transcript, mock STT |
| 고객 개입 신호 | speech event, user utterance | 사용자가 실제로 말했는지와 무엇을 말했는지 |
| 상담 주제 | intent | 배송조회, 환불요청, 결제문제 등 |
| 주제 전환 | intent shift | 현재 상담 의도와 사용자 발화 의도가 달라졌는지 |
| AI의 다음 행동 | action label / expected_action | 계속, 짧게 반응, 멈춤, 전환, 확인 질문, 이관 중 무엇이 맞는지 비교 |
| 상황별 결정표 | AI Action Policy | 어떤 신호 조합에서 어떤 행동을 고를지 |
| 괜히 말 끊기 | false stop | 맞장구/소음인데 멈춘 비율 |
| 고객 요청 놓침 | missed switch | 주제가 바뀌었는데 계속 말한 비율 |

## 2. 배경과 문제

음성 AI 상담에서 사용자가 중간에 말을 끊거나 맥락을 바꿨는데도 AI가 기존 답변을 계속하면, 사용자는 AI가 자신의 말을 듣지 않는다고 느낀다.

반대로 사용자가 "네", "음", "알겠어요"처럼 짧게 반응했을 뿐인데 AI가 매번 멈추면 대화 흐름이 깨진다.

기존의 단순 VAD 기반 접근은 `사용자가 말했는가`에는 답할 수 있지만, 아래 질문에는 답하기 어렵다.

- 사용자의 발화가 단순 반응인가?
- 기존 상담 의도와 같은 질문인가?
- 새로운 의도로 전환한 것인가?
- 불만이나 긴급 상황인가?
- AI는 계속 말해야 하는가, 멈춰야 하는가, 전환해야 하는가?

따라서 이 MVP의 문제는 음성 감지 자체가 아니라 **사용자 개입 신호를 제품 행동으로 바꾸는 판단 구조**를 만드는 것이다.

## 3. 목표

### 2차 회의 후 기준

2차 회의에서 PRD의 1주차 기준은 아래처럼 정리됐다.

| 항목 | 기준 |
| --- | --- |
| 제품 형태 | 완성형 상담 앱보다 AI 엔지니어용 실험 콘솔 |
| 최소 완료 | Text Replay MVP + 대표 Audio File Test |
| 후순위 | Live Mic, streaming, prosody risk, 완성형 상담 서비스 |
| 차별점 | 새 모델보다 문제 해결 과정, AI Action Policy 비교, 실패 분석 |
| 논문 활용 | 3일차쯤 구현 중 생긴 질문을 기준으로 목적형 리뷰 |

### Product Goal

AI 엔지니어와 리뷰어가 고객 개입 상황별로 AI의 다음 행동이 자연스러운지 확인하고, 단순 "소리 나면 멈춤" 방식 대비 어떤 고객 경험 문제가 줄어드는지 검증할 수 있게 한다.

### Technical Goal

VAD-only baseline과 STT/intent 기반 개선 AI Action Policy를 비교하고, `false stop`과 `missed switch`를 포함한 평가 결과를 산출한다.

### Portfolio Goal

1주일 안에 문제 정의, 데이터셋, baseline, 개선 AI Action Policy, 평가 지표, 실패 사례 분석을 갖춘 재현 가능한 MVP를 만든다.

## 4. 비목표

1주차 MVP에서는 아래를 목표로 하지 않는다.

| 비목표 | 이유 |
| --- | --- |
| 완성형 실시간 음성 상담 서비스 | 실시간 STT, TTS 재생, 상태 관리까지 포함하면 범위가 커진다. |
| 실제 콜센터 데이터 수집 | 개인정보와 데이터 확보 문제가 크다. |
| 고품질 STT/TTS 자체 최적화 | 이 프로젝트의 핵심은 음성 모델 성능이 아니라 상황별 제품 판단이다. |
| 상담 운영 대시보드 | QA 점수, 통화 요약, RAG 검색은 별도 제품 범위다. |
| Prosody 기반 감정 인식 | 불만/긴급도 보조 신호로는 유용하지만 1주차 핵심 구현은 아니다. |
| 모델 학습/fine-tuning | 1차 MVP는 rule과 pretrained embedding 기반 검증으로 충분하다. |

## 5. 사용자

### Primary User: AI Engineer

AI 엔지니어는 각 고객 상황에서 AI가 왜 특정 행동을 선택했는지 보고 싶다.

필요한 정보:

- 입력 발화
- 입력 방식
- VAD/speech event 결과
- STT transcript
- intent shift 여부
- 기대 행동
- 실제 행동
- 판단 이유
- 실패 케이스와 개선 포인트

### Secondary User: Interviewer / Reviewer

면접관 또는 리뷰어는 이 프로젝트가 단순 데모가 아니라 문제를 쪼개고 검증한 결과인지 보고 싶다.

필요한 정보:

- 왜 VAD-only가 부족한지
- 어떤 데이터셋으로 검증했는지
- 개선 AI Action Policy가 어떤 실패를 줄였는지
- synthetic 데이터의 한계와 다음 개선 방향

### Future User: Voice AI Product Operator

향후 확장 시 상담 운영자는 위험 발화, 전환 실패, 상담사 이관 후보를 보고 싶을 수 있다. 다만 1주차 MVP에서는 직접 대상 사용자가 아니다.

## 6. 핵심 사용 시나리오

### Scenario 1. 맞장구를 끼어들기로 오해하지 않기

```txt
AI: 고객님의 상품은 현재 배송 중이며...
User: 네.
Expected: 짧게 반응하고 계속
```

성공 조건:

- VAD-only는 speech event 때문에 interruption으로 볼 수 있다.
- 개선 AI Action Policy는 맞장구로 판단하고 흐름을 유지한다.

### Scenario 2. 같은 상담 주제 안의 보충 질문 처리

```txt
AI: 상품은 내일 오후 도착 예정입니다...
User: 그래서 정확히 몇 시쯤 와요?
Expected: 잠깐 멈추고 답하기
```

성공 조건:

- 사용자 발화가 기존 배송 상담 안의 질문임을 판단한다.
- 기존 긴 설명을 계속하기보다 잠깐 멈추고 짧게 답하는 행동을 낸다.

### Scenario 3. 상담 주제 전환 감지

```txt
AI: 현재 주문은 배송 중이며 내일 오후...
User: 아 그게 아니라 환불받고 싶은데요.
Expected: 멈추고 환불 상담으로 바꾸기
```

성공 조건:

- 사용자 발화가 기존 배송조회에서 환불요청으로 바뀐 것을 감지한다.
- 기존 발화를 멈추고 환불 플로우로 전환하는 행동을 낸다.

### Scenario 4. 불만/긴급 발화 처리

```txt
AI: 배송은 순차적으로 진행되고 있습니다...
User: 아니 벌써 일주일째인데 너무 늦잖아요.
Expected: 우선 대응 또는 상담사 연결 후보
```

성공 조건:

- 단순 주제 전환뿐 아니라 불만 상황으로 분류한다.
- 사과/전환/이관 후보 행동을 낸다.

### Scenario 5. 애매한 발화 처리

```txt
AI: 환불 절차를 안내드리겠습니다...
User: 잠깐만요, 아니...
Expected: 확인 질문하기
```

성공 조건:

- 확신 없이 잘못된 상담 흐름으로 전환하지 않는다.
- 확인 질문 행동을 낸다.

## 7. 기능 요구사항

### FR0. Input Mode Console

시스템은 같은 상담 상황을 Text Replay와 Audio File Test로 확인하고, 이후 Mic Trial로 확장할 수 있어야 한다.

입력 모드:

| 입력 모드 | 사용자 행동 | 시스템 처리 |
| --- | --- | --- |
| Text Replay | scenario를 선택하거나 고객 발화를 직접 입력한다. | 텍스트를 바로 AI Action Policy 판단에 사용한다. |
| Audio File Test | 음성 파일을 업로드하고 전사 텍스트를 확인/수정한다. | 오디오 파일과 transcript를 묶어 AI Action Policy 판단에 사용한다. |
| Mic Trial | 마이크 입력 확장 가능성을 확인한다. | 1주차 필수 평가가 아니라 후순위 슬롯으로 둔다. |

Acceptance Criteria:

- 콘솔에서 Text Replay와 Audio File Test를 명확히 선택할 수 있다.
- Mic Trial은 1주차 필수 기능이 아니라 후속 확장 슬롯으로 표시할 수 있다.
- 세 모드는 최종적으로 같은 `AI Action Policy input` 구조로 변환된다.
- AI 모델 또는 STT가 없어도 precomputed/mock transcript로 판단을 실행할 수 있다.
- 입력 방식은 decision log 또는 화면의 signal panel에서 확인할 수 있다.

### FR1. Scenario Bank

시스템은 고객 개입 상황별 text scenario를 관리해야 한다.

필수 필드:

- `scenario_id`
- `level`
- `domain`
- `ai_current_intent`
- `ai_utterance`
- `user_utterance`
- `event_type`
- `expected_action`
- `expected_user_intent`
- `has_user_speech`
- `user_tone_hint`
- `notes`

Acceptance Criteria:

- 목표는 30개 이상 text scenario를 로드하는 것이다.
- 첫 skeleton 단계에서는 더 적은 수로 시작해도 schema와 action label 분포를 확인할 수 있어야 한다.
- event type별 시나리오 수를 확인할 수 있다.
- expected_action 분포를 확인할 수 있다.

### FR2. AI Action Policy Version 실행

시스템은 같은 고객 상황에 대해 여러 판단 규칙 버전을 실행할 수 있어야 한다.

필수 AI Action Policy version:

- P0 VAD-only
- P1 VAD + Backchannel Rule
- P2 STT + Intent Shift
- P3 행동 결정표(AI Action Policy)

Acceptance Criteria:

- 각 scenario에 대해 AI Action Policy별 실제 행동을 출력한다.
- AI Action Policy별 결과를 같은 evaluation format으로 저장한다.
- AI Action Policy가 선택한 reason을 기록한다.

### FR3. Intent Shift Detection

시스템은 사용자 발화가 기존 상담 주제와 같은지 다른지 판단해야 한다.

입력:

- current intent
- user utterance
- candidate intent descriptions

출력:

- predicted user intent
- similarity score
- intent shift 여부

Acceptance Criteria:

- intent shift scenario에서 `stop_and_switch` 후보 판단에 필요한 신호를 제공한다.
- same intent question과 intent shift를 구분할 수 있다.

### FR4. Text Replay Evaluation

시스템은 text scenario만으로 기대 행동과 실제 행동을 비교할 수 있어야 한다.

Acceptance Criteria:

- 전체 accuracy를 계산한다.
- action confusion matrix를 생성한다.
- false stop과 missed switch를 계산한다.
- 실패 scenario 목록을 저장한다.

### FR5. Audio File Test

시스템은 대표 scenario를 audio sample로 변환하거나 연결해 VAD/STT 흐름을 확인할 수 있어야 한다.

Acceptance Criteria:

- 목표는 10개 이상 대표 audio sample을 준비하는 것이다.
- 첫 연결 단계에서는 더 적은 대표 케이스로도 audio mapping과 AI Action Policy 연결을 검증할 수 있어야 한다.
- audio sample과 원본 scenario를 매핑한다.
- 콘솔에서 audio file을 업로드하거나 선택해 재생할 수 있다.
- STT가 없을 때는 precomputed/mock transcript를 사용해 판단한다.
- VAD/STT 결과를 decision log에 남길 수 있다.

### FR5-1. Mic Trial Extension

시스템은 실제 마이크 입력 확장 가능성을 보여주는 얇은 녹음 흐름을 이후 확장할 수 있어야 한다.

Acceptance Criteria:

- 1주차에는 필수 구현이 아니다.
- 구현한다면 브라우저 권한이 허용될 때 녹음 시작/정지/재생을 할 수 있다.
- 녹음 데이터는 서버 저장을 요구하지 않는다.
- 판단은 녹음 자체가 아니라 사용자가 확인한 transcript로 실행한다.
- 브라우저 권한이 거부되어도 Text Replay와 Audio File Test는 계속 사용할 수 있어야 한다.

### FR6. Decision Log

시스템은 각 판단의 근거를 로그로 저장해야 한다.

필수 필드:

- `scenario_id`
- `policy_version`
- `expected_action`
- `actual_action`
- `signals`
- `reason`
- `is_correct`

Acceptance Criteria:

- 실패 케이스 분석에 필요한 signal이 남는다.
- 리포트에서 대표 성공/실패 사례를 재사용할 수 있다.
- 제품 관점에서 "왜 계속 말했는지", "왜 멈췄는지", "왜 전환했는지"를 설명할 수 있다.

### FR7. Result Report

시스템은 실험 결과를 README/report에 정리할 수 있는 형태로 산출해야 한다.

Acceptance Criteria:

- baseline과 개선 AI Action Policy의 metric 비교가 있다.
- false stop과 missed switch 사례가 있다.
- synthetic 데이터의 한계가 명시된다.
- 다음 확장 방향이 정리된다.

## 8. 비기능 요구사항

| 항목 | 요구사항 |
| --- | --- |
| 재현성 | 같은 scenario와 AI Action Policy를 실행하면 같은 결과가 나와야 한다. |
| 설명 가능성 | 각 action에는 reason이 있어야 한다. |
| 확장성 | text input을 audio file과 mic trial로 확장할 수 있어야 한다. |
| 단순성 | 1주차 구현은 rule 기반 AI Action Policy와 pretrained model 중심으로 유지한다. |
| 독립성 | 외부 API 연결 실패 시 precomputed transcript 또는 mock STT로 대체 가능해야 한다. |
| 문서화 | 데이터 schema, AI Action Policy rule, 평가 지표가 README/report에 설명되어야 한다. |

## 9. 데이터 요구사항

### Dataset v1

| 항목 | 기준 |
| --- | --- |
| 도메인 | 커머스 상담 |
| text scenario | 30~50개 |
| audio sample | 10~20개 |
| event type | 7종 |
| action label | 6종 |
| intent | 배송조회, 환불요청, 반품요청, 결제문제, 상품문의, 상담사연결 |

### Label Distribution 목표

| event_type | 권장 개수 |
| --- | --- |
| no_speech | 3~5 |
| noise | 3~5 |
| backchannel | 5~8 |
| same_intent_question | 5~8 |
| intent_shift | 8~12 |
| complaint | 4~6 |
| ambiguous | 3~5 |

정확한 분포보다 중요한 것은 action label별 대표 케이스가 빠지지 않는 것이다.

## 10. 성공 지표

### MVP 완료 지표

- text scenario 30개 이상
- VAD-only baseline 구현
- 개선 AI Action Policy 구현
- AI Action Policy version별 evaluation 결과
- representative audio sample 10개 이상
- Text Replay와 Audio File Test 입력 모드가 보이는 콘솔
- error analysis 문서
- README/report 초안

### 성능 지표

| 지표 | 고객 경험에서 보는 목표 | 구현상 목표 방향 |
| --- | --- | --- |
| False Stop Rate | 맞장구/소음에서 괜히 말 끊지 않기 | P0 대비 감소 |
| Missed Switch Rate | 고객이 주제를 바꿨는데 놓치지 않기 | P0/P1 대비 감소 |
| Action Accuracy | 상황별 기대 행동을 맞히기 | P0 대비 개선 |
| Intent Shift Recall | 환불/반품/결제 전환 요청을 놓치지 않기 | intent shift 케이스 recall 확보 |
| Backchannel Precision | "네", "음"을 과도하게 끼어들기로 보지 않기 | backchannel 오탐 감소 |

정량 목표 수치는 실험 결과가 나온 뒤 확정한다. 실험 전에는 임의의 개선율을 확정하지 않는다.

### 설명 가능성 지표

- 대표 성공 사례 3개를 설명할 수 있다.
- 대표 실패 사례 3개와 개선 방향을 설명할 수 있다.
- VAD-only가 왜 부족한지 데이터로 보여줄 수 있다.
- synthetic 데이터의 한계를 명시할 수 있다.

## 11. 화면 요구사항

1주차 콘솔은 최소 기능 중심으로 구성한다.

### 필수 화면

| 영역 | 제품 관점 | 기술 관점 |
| --- | --- | --- |
| Scenario Selector | 어떤 고객 상황인지 선택 | scenario 선택, level/event type 표시 |
| Input Mode Panel | 고객 개입을 어떤 방식으로 넣을지 선택 | text replay, audio file, mic trial 확장 슬롯 |
| Input Panel | AI가 하던 말과 사용자의 개입 | AI 발화, 사용자 발화, audio sample, recorded audio |
| Signal Panel | 사용자가 실제로 말했는지 | speech event, STT result, uncertainty |
| Intent Panel | 같은 상담 주제인지, 다른 요청인지 | current intent, predicted intent, similarity |
| AI Action Policy Panel | AI가 고른 다음 행동과 이유 | expected_action, actual_action, reason |
| Evaluation Panel | 괜히 멈춤/놓친 전환이 줄었는지 | AI Action Policy별 metric, confusion matrix |
| Error List | 다음에 고칠 판단 기준 | 실패 케이스 목록 |

### 화면 원칙

- 상담 앱처럼 보이기보다 실험 콘솔처럼 보인다.
- 판단 근거가 한 화면에서 보인다.
- 같은 scenario를 text/audio file 입력 방식으로 비교할 수 있게 한다.
- Mic Trial은 1주차 필수 성능 데모가 아니라 후속 live 입력 구조로 둔다.
- UI 구현이 늦어지면 notebook 또는 CLI report로 대체 가능하다.

## 12. 릴리즈 범위

### v0.1: Text Replay MVP

- scenario bank
- Text Replay input
- P0/P1/P2/P3 AI Action Policy 실행
- expected vs actual 평가
- decision log
- error analysis

### v0.2: Audio File Test

- representative audio sample
- audio file input panel
- VAD/STT 연결
- audio scenario mapping
- audio decision log

### v0.3: Mic Trial / Console Extension

- scenario selector
- mic record/playback
- mock transcript input
- AI Action Policy result panel
- evaluation summary
- representative demo scenarios

### Future

- simulated live chunk
- live mic STT
- prosody risk
- commerce voice service
- operator dashboard

## 13. 주요 리스크

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| audio 생성이 오래 걸림 | 일정 지연 | text replay를 먼저 완성하고 대표 케이스만 audio화 |
| STT 연결이 불안정함 | audio test 실패 | precomputed transcript와 mock STT 허용 |
| 브라우저 마이크 권한 문제 | mic trial 실패 | mic은 후순위 선택 기능으로 두고 transcript 직접 입력으로 대체 |
| action label이 복잡함 | 평가가 어려움 | binary 평가와 action-level 평가를 함께 제공 |
| threshold가 임의적임 | 결과 신뢰도 저하 | validation set과 실패 분석으로 조정 |
| 정량 개선이 작음 | 성과 설명 약화 | 어떤 실패가 줄었는지 error analysis 중심으로 설명 |
| UI 구현 시간이 부족함 | 데모 약화 | CLI/notebook/report를 우선 산출물로 둔다 |

## 14. 오픈 질문

### 닫힌 질문

1. 1주차 최소 완료 기준은 `Text Replay MVP + 대표 Audio File Test`로 둔다.
2. Mic Trial은 1주차 필수 구현이 아니라 후속 확장 슬롯으로 둔다.

### 남은 질문

1. audio sample 목표 개수를 10개로 둘지 20개 이상으로 둘지
2. action label에서 `brief_ack`를 독립 label로 둘지 `continue`에 포함할지
3. complaint를 `stop_and_switch`로 볼지 `handoff` 후보로 분리할지
4. STT는 실제 Whisper/API를 사용할지, 초기에는 precomputed/mock transcript로 둘지
5. SBERT 비교 기준을 intent label로 할지, intent description으로 할지
6. 최종 발표에서 제품 데모와 실험 결과 중 무엇을 더 앞세울지

## 15. 최종 요약

```txt
이 MVP는 상담 AI 전체를 만드는 프로젝트가 아니다.

사용자 음성이 들어왔을 때 무조건 멈추는 VAD-only 방식에서 출발해,
사용자 발화의 의미와 기존 intent와의 차이를 보고
AI가 어떤 행동을 선택해야 하는지 검증하는 프로젝트다.

1주차 목표는 Text Replay를 기본 평가 모드로 만들고,
대표 Audio File Test까지 붙여
VAD-only 대비 false stop과 missed switch를 줄이는
상황별 결정 구조(Interrupt-aware AI Action Policy)의 가능성을 보여주는 것이다.
```

## 변경 이력

- 2026-05-06: 2차 회의 정리를 반영해 PRD 상태를 회의 후 v1로 갱신하고, 닫힌/남은 오픈 질문을 분리
- 2026-05-06: 실험 콘솔 입력 모드를 Text Replay, Audio File Test 중심으로 정리하고 Mic Trial은 후순위 확장으로 조정
- 2026-05-06: 제품명, 제품-기술 용어 매핑, 사용 시나리오, 성공 지표, 화면 요구사항을 제품 언어 중심으로 보강
- 2026-05-06: MVP 방향성 초안과 계획서를 바탕으로 PRD 초안 작성
- 2026-05-07: 고객 장면을 도입부에 추가하고, action label이 무엇을 뜻하는지 설명 추가
- 2026-05-07: 용어 결정 노트를 반영해 `policy` 계열 표현을 `AI Action Policy` 중심으로 정리
