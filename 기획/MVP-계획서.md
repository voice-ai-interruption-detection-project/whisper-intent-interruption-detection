# Interruption Detection MVP 계획서

> 작성일: 2026-05-06
> 상태: 2차 회의 후 실행 기준 v1
> 목적: `MVP-방향성-초안.md`의 방향을 1주일 실행 단위로 구체화한다.
> 용어 기준: [용어-결정-노트.md](용어-결정-노트.md)

## 목표

1주차 MVP의 목표는 커머스 음성 상담 상황에서 **고객이 중간에 개입했을 때 AI가 어떤 행동을 선택해야 하는지**를 상황별로 검증하는 것이다.

구현에서는 `VAD-only baseline`보다 나은 `Interrupt-aware AI Action Policy`를 만들고, 그 차이를 시나리오와 평가 지표로 확인한다.

읽는 순서는 아래처럼 잡는다. `action label`부터 정하지 않고, 고객 장면에서 AI가 해야 할 행동을 먼저 정한 뒤 label을 붙인다. 여기서 `action label`은 AI Action Policy가 내놓은 행동 결과에 붙인 평가용 이름이다.

```txt
고객이 어떤 말을 했는가?
-> AI가 고객 입장에서 어떻게 반응해야 자연스러운가?
-> 그 행동을 평가하려고 어떤 action label로 부를 것인가?
```

```txt
목표:
AI 발화 중 사용자 신호가 들어왔을 때
AI가 계속 말할지, 잠깐 멈출지, 새 상담 흐름으로 전환할지 판단하는 규칙을 만든다.

검증:
VAD-only baseline과 개선 AI Action Policy를 비교해
false stop과 missed switch가 어떻게 달라지는지 보여준다.
```

## 2차 회의 반영

2차 회의에서 이 계획서는 아래 기준으로 확정됐다.

| 항목 | 결정 |
| --- | --- |
| 첫 작업 | 2026-05-07 (목) 09:30~13:30 페어로 시작 |
| 첫 페어 목표 | 고객 상황, 데이터, action label, AI Action Policy skeleton을 함께 잡기 |
| 1주차 최소 기준 | Text Replay 중심 AI Action Policy 검증 + 대표 Audio File Test 연결 |
| Mic Trial | 1주차 필수 평가가 아니라 후순위 확장 슬롯 |
| 논문 운영 | 선행 필수가 아니라 3일차쯤 구현 질문을 기준으로 주제 선정 후 리뷰 |
| 코드 기준 문서 | 이 계획서와 PRD를 repo에 두고 AI 도구가 읽을 수 있게 운영 |

## 이 MVP가 판단하는 순서

이 계획서의 여러 개념은 아래 흐름 안에서 읽는다. 핵심은 "고객이 끼어들었다"를 바로 정답 처리하는 것이 아니라, 입력을 받아 신호와 의미를 확인한 뒤 AI의 다음 행동을 고르고 평가하는 것이다.

```txt
1. 고객 상황
   AI가 말하는 중 고객이 어떤 신호를 보냈는가?

2. 입력 방식
   그 상황을 Text Replay, Audio File Test, Mic Trial 중 무엇으로 넣는가?

3. 신호 확인
   사용자가 실제로 말했는가? 전사 텍스트가 있는가?

4. 의미 해석
   맞장구인가, 같은 주제 질문인가, 새 요청인가, 불만인가?

5. AI 행동 판단
   AI Action Policy가 AI의 다음 행동을 고른다.

6. 행동 결과 이름
   선택된 행동에 action label을 붙인다.

7. 평가
   expected_action과 actual_action을 비교하고 실패를 분석한다.
```

짧게 쓰면 아래 파이프라인이다.

```txt
Scenario
-> Input Mode
-> Signal / Transcript
-> Event Type / Intent
-> AI Action Policy
-> action label
-> Evaluation
-> Error Analysis
```

따라서 뒤의 `제품-기술 연결 요약`, `MVP 범위`, `데이터 설계`, `AI Action Policy 버전`, `평가 설계`는 각각 별도 개념이 아니라 이 판단 흐름의 한 층이다.

| 층 | 이 문서의 관련 섹션 | 역할 |
| --- | --- | --- |
| 고객 상황 | 데이터 설계, Event Type | 어떤 상담 상황을 테스트할지 정한다. |
| 입력 방식 | Input Mode Schema, 콘솔 구성 | 같은 상황을 텍스트/오디오/마이크 중 어떤 방식으로 넣을지 정한다. |
| 신호 확인 | VAD Baseline, transcript source | 사용자가 말했는지와 전사 텍스트가 있는지 확인한다. |
| 의미 해석 | Intent Scope, event_type | 고객 발화가 맞장구인지, 같은 질문인지, 새 요청인지 분류한다. |
| AI 행동 판단 | AI Action Policy 버전 | 어떤 신호 조합에서 AI가 어떤 행동을 고를지 정한다. |
| 행동 결과 | action label, expected_action | AI 행동 판단 결과를 평가 가능한 이름으로 남긴다. |
| 평가/개선 | 평가 설계, Decision Log, Error Analysis | 기대 행동과 실제 행동을 비교하고 다음 수정 지점을 찾는다. |

## 제품-기술 연결 요약

계획서를 읽을 때는 아래처럼 제품 언어와 기술 언어를 함께 본다.

| 제품 표현 | 기술 표현 | 이번 MVP에서의 산출물 |
| --- | --- | --- |
| 테스트 상황 | scenario | `data/scenarios.json` |
| 입력 방식 | input mode | Text Replay, Audio File Test, Mic Trial 확장 슬롯 |
| 전사 출처 | transcript source | 직접 입력, precomputed transcript, mock STT |
| 상황별 결정표 | AI Action Policy | `src/policies/*.py` |
| AI의 다음 행동 | action label / expected_action | `continue`, `pause`, `stop_and_switch` 등 |
| 괜히 말 끊기 | false stop | noise/backchannel 오탐 비율 |
| 고객 의도 놓침 | missed switch | intent shift 미탐 비율 |
| 판단 이유 설명 | decision log | `results/decision_logs.jsonl` |
| 다음 개선 포인트 | error analysis | `results/error_analysis.md` |

## MVP 범위

### 필수 범위

| 항목 | 제품 의미 | 기술 설명 | 산출물 |
| --- | --- | --- | --- |
| Scenario Bank | 어떤 고객 상황을 테스트할지 정한다. | 상황 난이도별 text scenario 생성 | `data/scenarios.json` |
| Input Mode Console | 같은 상황을 텍스트와 음성 파일로 확인하고 마이크 확장을 열어둔다. | Text Replay, Audio File Test 중심, Mic Trial은 후순위 슬롯 | `index.html` 또는 `app` |
| Action Label | AI가 선택할 수 있는 제품 행동을 정의한다. | `continue`, `brief_ack`, `pause`, `stop_and_switch`, `ask_clarifying`, `handoff` | action label 정의 문서 |
| VAD Baseline | "소리 나면 멈춤" 방식의 한계를 보여준다. | 음성이 있으면 interruption으로 보는 기준선 | `src/policies/p0_vad_only.py` |
| Improved AI Action Policy | 상황별로 더 자연스러운 행동을 선택한다. | STT text + intent shift + rule 기반 AI Action Policy | `src/policies/p3_action_policy.py` |
| Evaluation | 어떤 고객 경험 문제가 줄었는지 비교한다. | expected_action과 actual_action 비교 | `results/evaluation.json` |
| Error Analysis | 다음에 고칠 판단 기준을 찾는다. | 실패 케이스와 개선 포인트 정리 | `results/error_analysis.md` |
| Report/README | 제품 문제, 기술 접근, 한계를 설명한다. | 문제, 접근, 결과, 한계 정리 | `README.md`, `report.md` |

### 권장 범위

| 항목 | 설명 | 산출물 |
| --- | --- | --- |
| Audio Sample Mapping | 대표 시나리오와 음성 파일/전사 결과를 연결 | `data/audio_samples/`, audio mapping 문서 |
| Console UI Polish | 시나리오별 판단 결과를 더 보기 쉽게 다듬음 | `app` 또는 `demo` |
| Metrics Visualization | confusion matrix, metric comparison 시각화 | `results/*.png` |
| Decision Log | AI Action Policy가 어떤 이유로 action label을 선택했는지 기록 | `results/decision_logs.jsonl` |

### 확장 범위

| 항목 | 설명 |
| --- | --- |
| Simulated Live Chunk | audio file을 chunk로 잘라 실시간처럼 처리 |
| Live Mic STT | 실제 마이크 입력을 실시간 STT와 연결 |
| Prosody Risk | pitch/RMS 등 tone signal을 risk feature로 실험 |
| Commerce Voice Service | 실제 상담 데모 앱으로 확장 |

## 데이터 설계

### Text Scenario Schema

1차 데이터는 text replay 중심으로 만든다. 이 단계에서는 음성 품질보다 AI Action Policy 판단이 맞는지 빠르게 확인하는 것이 목적이다.

```json
{
  "scenario_id": "commerce_refund_001",
  "level": 4,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "아 그게 아니라 환불받고 싶은데요.",
  "event_type": "intent_shift",
  "expected_action": "stop_and_switch",
  "expected_user_intent": "refund_request",
  "user_tone_hint": "neutral",
  "has_user_speech": true,
  "notes": "AI 발화 중 사용자가 다른 업무 의도를 제시한 케이스"
}
```

### Input Mode Schema

콘솔의 입력은 세 모드로 나눈다. 세 모드는 화면에서는 다르게 보이지만, AI Action Policy에는 최종적으로 같은 형태의 판단 입력을 넘긴다.

| 입력 모드 | 화면에서 하는 일 | 1주차 처리 방식 | AI Action Policy 입력 |
| --- | --- | --- | --- |
| Text Replay | scenario를 고르거나 사용자 발화를 직접 입력 | 텍스트를 바로 판단 | `user_utterance`, `event_type`, `current_intent` |
| Audio File Test | 음성 파일을 업로드하고 재생 | STT는 아직 mock/precomputed transcript 사용 | `audio_file_name`, `transcript`, `speech_event` |
| Mic Trial | 마이크 입력 확장 가능성을 확인 | 1주차 필수 평가가 아니라 후순위 슬롯으로 둔다 | `recording_state`, `transcript`, `current_intent` |

1주차에는 실제 STT 모델 정확도를 평가하지 않는다. 대신 Text Replay와 Audio File Test에서 `transcript`가 준비되면 같은 `P0~P3 AI Action Policy`를 실행할 수 있는지를 본다. Mic Trial은 이후 live 입력으로 넘어가기 위한 구조만 막지 않는다.

### Event Type

| 고객 상황 | event_type | 고객 입장에서 자연스러운 AI 행동 | expected_action |
| --- | --- | --- | --- |
| 사용자 발화 없음 | `no_speech` | 계속 말하기 | `continue` |
| 배경음 또는 짧은 비언어 소리 | `noise` | 계속 말하기 | `continue` |
| "네", "음", "알겠어요" | `backchannel` | 짧게 반응하고 계속 | `continue` 또는 `brief_ack` |
| 같은 업무 안의 보충 질문 | `same_intent_question` | 잠깐 멈추고 답하기 | `pause` |
| 다른 업무 의도로 전환 | `intent_shift` | 멈추고 주제 바꾸기 | `stop_and_switch` |
| 불만 또는 긴급 발화 | `complaint` | 우선 대응 또는 상담사 연결 후보 | `stop_and_switch` 또는 `handoff` |
| 의도가 불명확한 발화 | `ambiguous` | 확인 질문하기 | `ask_clarifying` |

### Intent Scope

1주차 커머스 intent 범위는 너무 넓히지 않는다.

| intent ID | 의미 | 예시 발화 |
| --- | --- | --- |
| `shipping_inquiry` | 배송 상태 조회 | "언제 도착해요?", "배송 상태 알려주세요" |
| `refund_request` | 환불 요청 | "환불받고 싶어요", "돈 돌려받을 수 있나요?" |
| `return_request` | 반품 요청 | "반품하고 싶어요", "수거는 어떻게 하나요?" |
| `payment_issue` | 결제 문제 | "결제가 두 번 됐어요", "카드 취소됐나요?" |
| `product_inquiry` | 상품 문의 | "사이즈가 맞나요?", "색상 변경 되나요?" |
| `agent_connection` | 상담사 연결 | "사람이랑 통화하고 싶어요" |

### 데이터 규모

| 단계 | 목표 규모 | 목적 |
| --- | --- | --- |
| Text Scenario v1 | 30개 | AI Action Policy skeleton 검증 |
| Text Scenario v2 | 50개 | action label별 coverage 확보 |
| Audio Sample v1 | 10개 | VAD/STT 연결 확인 |
| Audio Sample v2 | 20~30개 | 대표 케이스 평가 |
| Mic Trial | 선택 | 후속 live 입력 구조 확인 |
| 확장 | 50~100개 | 리포트 정량 보강 |

## AI Action Policy 버전

최종 모델 하나만 보여주지 않고, 단계별로 어떤 실패가 줄어드는지 비교한다.

| 버전 | 쉬운 이름 | 입력 | 판단 방식 | 보고 싶은 변화 |
| --- | --- | --- | --- | --- |
| P0 VAD-only | 소리 나면 멈춤 | speech event | 음성이 있으면 interruption | 기준선 |
| P1 VAD + Backchannel Rule | 맞장구는 안 멈춤 | speech event + user text | "네/음"은 계속 진행 | 괜히 멈추는 비율 감소 |
| P2 STT + Intent Shift | 말 내용을 봄 | user text + current intent | 의도 변화면 전환 | 고객 의도 전환을 덜 놓침 |
| P3 AI Action Policy | 실제 행동을 고름 | intent + uncertainty + event type | action label 선택 | 실제 제품 행동으로 확장 |
| P4 Prosody Risk | 말투 위험도까지 봄 | tone feature | 불만/긴급도 우선순위 | 1주차 이후 |

## 판단 로직 초안

```txt
if not has_user_speech:
  return continue

if event_type == noise:
  return continue

if utterance_is_backchannel:
  return brief_ack or continue

if same_intent_question:
  return pause

if intent_shift and user_intent_confidence is high:
  return stop_and_switch

if complaint and severity is high:
  return handoff or stop_and_switch

if intent is unclear or stt_uncertainty is high:
  return ask_clarifying
```

1차 구현에서는 규칙 기반 AI Action Policy로 시작한다. threshold와 rule은 evaluation 결과를 보며 조정한다.

## 평가 설계

### 평가 대상

| 대상 | 고객 경험에서 보는 것 | 구현에서 보는 것 |
| --- | --- | --- |
| Binary Interruption | AI가 개입해야 하는 상황인지 아닌지 | interruption 여부만 비교 |
| Action Classification | AI가 어떤 제품 행동을 선택했는지 | action label 단위 비교 |
| AI Action Policy Version Comparison | 어떤 판단 기준이 어떤 고객 문제를 줄였는지 | P0, P1, P2, P3 단계별 개선 비교 |

### 지표

| 지표 | 고객 경험에서 읽는 의미 | 구현상 의미 |
| --- | --- | --- |
| Accuracy | 기대한 AI 행동을 얼마나 맞췄는가 | 전체 예측 정확도 |
| Precision | 멈추면 안 되는 상황에서 덜 멈췄는가 | 오탐 관리 |
| Recall | 전환해야 하는 상황을 놓치지 않았는가 | 미탐 관리 |
| F1 | 불필요한 멈춤과 놓친 전환의 균형 | precision/recall 균형 |
| False Stop Rate | 맞장구/소음인데 괜히 멈춘 비율 | backchannel/noise인데 intervention으로 본 비율 |
| Missed Switch Rate | 고객이 주제를 바꿨는데 계속 말한 비율 | intent shift인데 계속 말한 비율 |
| Confusion Matrix | 어떤 제품 행동을 자주 헷갈리는지 | action label 단위 혼동 구조 |

### Decision Log 예시

```json
{
  "scenario_id": "commerce_refund_001",
  "policy_version": "P3",
  "expected_action": "stop_and_switch",
  "actual_action": "stop_and_switch",
  "signals": {
    "has_user_speech": true,
    "stt_text": "아 그게 아니라 환불받고 싶은데요.",
    "predicted_user_intent": "refund_request",
    "intent_shift": true,
    "similarity_to_current_intent": 0.22
  },
  "reason": "사용자 발화가 기존 shipping_inquiry intent와 낮은 유사도를 보이고 refund_request intent로 분류되어 전환 판단"
}
```

## 1주일 실행 일정

### Day 1. 문제 정의와 데이터 설계

목표:

- 첫 페어에서 팀이 같은 구현 방향을 보도록 프로젝트 골격을 맞춘다.
- 고객 상황 분류 확정
- AI 제품 결정 목록 확정
- scenario schema 확정
- action label 확정
- text scenario 30개 생성
- baseline 평가를 위한 expected_action 정리
- 입력 모드별 공통 판단 입력 구조 확정

작업:

1. 커머스 intent 범위 확정
2. event_type과 expected_action 매핑 확정
3. text scenario v1 생성
4. label 분포 확인
5. 대표 케이스 5개 선정
6. Text/Audio/Mic 모드별 입력 필드 정리

산출물:

- `data/scenarios.json`
- `data/scenario_stats.json`
- action label 정의 문서
- input mode 정의 문서 또는 README 섹션

### Day 2. Baseline과 초기 AI Action Policy 구현

목표:

- "소리 나면 멈춤" 방식의 제품 한계를 확인
- 맞장구/소음에서 괜히 멈추는 문제를 줄이는 1차 규칙 구현
- P0 VAD-only 또는 speech-event baseline 구현
- P1 backchannel rule 구현
- Text Replay 평가 파이프라인 시작

작업:

1. scenario loader 작성
2. P0 baseline 작성
3. P1 rule 작성
4. expected vs actual 비교 함수 작성
5. 1차 evaluation 출력

산출물:

- `src/scenario_loader.py`
- `src/policies/p0_vad_only.py`
- `src/policies/p1_backchannel_rule.py`
- `src/evaluator.py`
- `results/baseline_text_eval.json`

### Day 3. STT/Intent Shift와 대표 Audio 연결

목표:

- 고객이 상담 주제를 바꿨는지 판단하는 흐름 구현
- 텍스트 판단이 실제 음성 입력으로 확장될 수 있는지 확인
- 구현 중 생긴 질문을 기준으로 논문 리뷰 주제 1개 선정
- P2 intent shift detector 구현
- 대표 시나리오를 audio sample로 변환
- Audio File Test의 최소 흐름 확인
- 오디오 파일 입력이 transcript를 통해 AI Action Policy 판단으로 이어지는지 확인

작업:

1. SBERT 또는 sentence-transformer 모델 선택
2. intent description 작성
3. similarity 기반 intent shift detector 작성
4. 대표 text scenario 10개를 TTS/audio로 변환
5. audio file과 scenario/transcript 매핑
6. STT 연결 방식 확인
7. 구현 중 나온 질문을 정리하고 같이 볼 논문/주제 1개 선정

산출물:

- `src/intent_detector.py`
- `src/policies/p2_intent_shift.py`
- `data/audio_samples/`
- audio mapping 문서 또는 README 섹션
- `results/intent_eval.json`
- 논문 리뷰 주제 메모

### Day 4. AI Action Policy와 평가/시각화

목표:

- 상황별 결정표를 실제 AI Action Policy로 구현
- 어떤 제품 행동을 헷갈리는지 확인
- P3 AI Action Policy 구현
- P0~P3 비교
- 실패 케이스 분석
- 시각화 생성

작업:

1. AI Action Policy rule 구현
2. decision log 저장
3. action confusion matrix 생성
4. false stop / missed switch 계산
5. 실패 케이스 표 정리

산출물:

- `src/policies/p3_action_policy.py`
- `results/evaluation.json`
- `results/decision_logs.jsonl`
- `results/confusion_matrix.png`
- `results/error_analysis.md`

### Day 5. 데모와 리포트 정리

목표:

- 제품 문제와 기술 검증 결과가 연결되도록 정리
- 결과를 GitHub/README/report로 정리
- 발표 가능한 스토리로 압축
- 대표 데모 시나리오 준비
- 콘솔에서 Text Replay와 Audio File Test를 구분해 보여주고, Mic Trial은 확장 슬롯으로 남기기

작업:

1. README 작성
2. report 작성
3. 대표 케이스 3개 정리
4. 콘솔 입력 모드 UI 정리
5. 한계와 향후 개선 정리

산출물:

- `README.md`
- `report.md`
- `demo_scenarios.md`
- 발표용 요약

## 콘솔 구성 초안

콘솔은 완성형 상담 앱이 아니라 AI 엔지니어가 판단 근거를 보는 실험 화면이다. 특히 입력 레이어를 아래처럼 분리한다.

```txt
[Text Replay] [Audio File Test] [Mic Trial]
```

1주차는 `Text Replay`를 기본 평가 모드로 두고, `Audio File Test`까지 최소 검증한다. `Mic Trial`은 같은 AI Action Policy로 확장될 수 있음을 보여주는 후순위 슬롯으로 둔다.

입력 모드별 화면:

| 입력 모드 | 제품 관점 | 기술 관점 | 1주차 완료 기준 |
| --- | --- | --- | --- |
| Text Replay | 고객 발화를 텍스트로 넣고 바로 판단한다. | scenario/user utterance를 AI Action Policy에 전달 | 직접 입력과 scenario 선택 가능 |
| Audio File Test | 대표 상담 상황을 음성 파일로 확인한다. | audio file + transcript + speech event 연결 | 파일 업로드/재생, transcript 입력 가능 |
| Mic Trial | 실제 마이크 입력 확장 가능성을 남긴다. | browser recording + mock transcript | 후순위, 시간이 남으면 녹음/재생 확인 |

필수 패널:

| 패널 | 제품 관점 | 기술 관점 |
| --- | --- | --- |
| Scenario Selector | 어떤 고객 상황인지 선택 | level, event_type, intent별 케이스 선택 |
| Input Mode | 어떤 방식으로 고객 개입을 넣는지 선택 | text replay, audio file, mic trial 확장 슬롯 |
| Input | AI가 하던 말과 고객의 끼어들기 | AI 발화, user utterance, audio file, recorded audio |
| Signal | 고객이 실제로 말했는지 | speech event, VAD segment, STT result |
| Intent | 고객이 같은 주제를 말하는지, 다른 요청인지 | current intent, predicted user intent, similarity |
| AI Action Policy | AI가 어떤 행동을 골랐는지와 이유 | expected_action, actual_action, reason |
| Evaluation | 괜히 멈춤/놓친 전환이 줄었는지 | metrics, confusion matrix |
| Error List | 다음에 고칠 제품 판단 기준 | 실패 케이스와 조정 포인트 |

## 예상 폴더 구조

구현 위치는 별도 코드 프로젝트 `~/Desktop/10_work/interrupt-aware-call-agent`를 기준으로 한다. 이 팀프로젝트 폴더에서는 `작업/interrupt-aware-call-agent/` symlink로 접근한다. 구조는 아래를 기준으로 시작하되, 실제 repo 구조에 맞게 조정한다.

```text
interrupt-aware-call-agent/
├── README.md
├── report.md
├── data/
│   ├── scenarios.json
│   ├── scenario_stats.json
│   └── audio_samples/
├── index.html
├── src/
│   ├── scenario_loader.py
│   ├── intent_detector.py
│   ├── evaluator.py
│   └── policies/
│       ├── p0_vad_only.py
│       ├── p1_backchannel_rule.py
│       ├── p2_intent_shift.py
│       └── p3_action_policy.py
├── results/
│   ├── evaluation.json
│   ├── decision_logs.jsonl
│   ├── error_analysis.md
│   └── confusion_matrix.png
└── demo/
```

## 역할 분담 초안

2차 회의 후 기준 역할 영역이다. 첫날은 페어로 시작하고, 이후 실제 분담은 각자 강점과 일정에 맞춰 조정한다.

| 영역 | 역할 A | 역할 B |
| --- | --- | --- |
| 문제 정의 | 공고/도메인 문제 정리 | MVP 범위와 산출물 정리 |
| 데이터 | scenario 생성/검수 | schema, label, stats 정리 |
| 모델/정책 | intent detector 설계 | AI Action Policy/evaluator 구현 |
| 입력 채널 | Text/Audio/Mic 콘솔 구조 정리 | audio sample과 transcript 구조 정리 |
| 결과 | metric 해석 | 시각화/README/report |
| 발표 | 문제-해결 스토리 | 기술 구조와 실패 사례 |

실제 분담은 각자 강점과 일정에 맞춰 조정한다. 중요한 것은 `데이터`, `AI Action Policy`, `평가`, `정리`가 끊기지 않게 연결하는 것이다.

## 리스크와 대응

| 리스크 | 대응 |
| --- | --- |
| audio 생성이 오래 걸림 | text replay를 먼저 완성하고 대표 케이스만 audio화 |
| Whisper/STT 연결이 불안정함 | STT 결과를 mock 또는 precomputed transcript로 대체 가능하게 설계 |
| 마이크 구현이 브라우저 권한에 막힘 | mic은 후순위 확장으로 두고, 구현하더라도 판단은 transcript 입력으로 대체 |
| action label이 너무 많아짐 | 리포트에서는 binary와 action-level 평가를 함께 사용 |
| SBERT threshold가 애매함 | threshold를 고정 주장하지 않고 validation set으로 조정 |
| 정량 결과가 기대만큼 좋지 않음 | 실패 사례 분석과 개선 loop 자체를 핵심 성과로 설명 |
| 실시간 데모 구현이 지연됨 | 1주차 목표에서 live mic를 제외하고 audio file test까지만 보장 |

## 최종 산출물 체크리스트

### Code

- [ ] scenario loader
- [ ] VAD/speech-event baseline
- [ ] backchannel rule
- [ ] intent shift detector
- [ ] AI Action Policy
- [ ] evaluator
- [ ] input mode UI
- [ ] audio file upload/playback
- [ ] mic record/playback 또는 후속 확장 슬롯

### Data

- [ ] text scenario 30~50개
- [ ] action label 정의
- [ ] audio sample 10~20개
- [ ] audio sample과 transcript 매핑
- [ ] annotation/schema 문서

### Results

- [ ] evaluation.json
- [ ] decision logs
- [ ] confusion matrix
- [ ] metric comparison
- [ ] error analysis

### Documentation

- [ ] README
- [ ] report
- [ ] demo scenarios
- [ ] 발표용 요약

## 남은 결정 항목

1. text scenario와 audio sample의 목표 개수
2. action label 최종 목록과 1차 구현 subset
3. 커머스 intent 범위
4. STT/Whisper 연결 방식과 mock transcript 허용 범위
5. SBERT 비교 기준을 intent label로 할지, intent description으로 할지
6. 최종 발표에서 제품 데모와 실험 결과 중 무엇을 더 앞세울지

## 변경 이력

- 2026-05-06: 2차 회의 정리를 반영해 상태를 회의 후 실행 기준으로 갱신하고, 첫 페어/논문 운영/구현 위치를 반영
- 2026-05-06: 실험 콘솔 입력 방식을 Text Replay, Audio File Test 중심으로 정리하고 Mic Trial은 후순위 확장 슬롯으로 조정
- 2026-05-06: 제품 언어와 기술 언어를 함께 읽을 수 있도록 범위, 데이터, AI Action Policy, 평가, 일정 설명 보강
- 2026-05-06: 방향성 종합 초안을 바탕으로 1주일 MVP 실행 계획서 작성
- 2026-05-07: 고객 장면에서 action label을 도출하는 읽는 순서를 추가하고, 표현을 더 직관적으로 정리
- 2026-05-07: 용어 결정 노트를 반영해 `policy` 계열 표현을 `AI Action Policy` 중심으로 정리
