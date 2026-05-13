# Input Modes: 3가지 입력 방식

## 개요

같은 상황(scenario)을 다양한 방식으로 입력할 수 있다.

```
실험 콘솔 (Console)
├─ Text Replay        (1주차 필수) ✅
├─ Audio File Test    (1주차 필수) ✅
└─ Mic Trial          (1주차 후순위) 🔮
```

---

## 1️⃣ Text Replay (텍스트 직접 입력)

### 정의
고객의 발화를 **텍스트로 직접 입력**하고 AI Action Policy를 실행

### 화면에서의 동작
```
[시나리오 선택] → [사용자 발화 텍스트 입력] → [판단 결과]
```

### AI Action Policy 입력
```python
{
  "user_utterance": "아 그게 아니라 환불받고 싶은데요.",
  "current_intent": "배송조회",
  "event_type": "intent_shift"  # 또는 사용자가 선택
}
```

### 1주차 처리 방식

| 항목 | 방식 |
|------|------|
| 시나리오 선택 | scenario.json에서 선택 또는 직접 입력 |
| 발화 텍스트 | 직접 입력 또는 시나리오에서 로드 |
| STT | 직접 입력 또는 mock (STT 모델 불필요) |
| Event Type | 텍스트 기반 자동 분류 또는 사용자 선택 |

### 장점
- ✅ 가장 빠르고 간단
- ✅ STT 오류 영향 없음
- ✅ Policy 성능에만 포커스 가능
- ✅ iteration이 빠름

### 단점
- ❌ 음성의 특성(prosody, tone) 미반영
- ❌ 실제 STT 오류 시뮬레이션 안 함

### 예시

```
AI: "현재 배송 중이며 내일 오후 도착 예정입니다."

[Text Replay 모드]

사용자 발화: "아 그게 아니라 환불받고 싶은데요."
↓
Policy 판단: intent_shift → stop_and_switch
↓
결과: "✅ 올바른 판단"
```

---

## 2️⃣ Audio File Test (음성 파일 테스트)

### 정의
**실제 음성 파일**을 업로드하고, 녹음/재생 후 판단

### 화면에서의 동작
```
[음성 파일 업로드] → [재생] → [STT 텍스트 확인] → [판단]
```

### AI Action Policy 입력
```python
{
  "audio_file_name": "refund_001.wav",
  "transcript": "아 그게 아니라 환불받고 싶은데요.",  # STT 결과 또는 라벨
  "speech_event": "speech_detected",
  "current_intent": "배송조회"
}
```

### 1주차 처리 방식

| 항목 | 방식 |
|------|------|
| 음성 파일 | 대표 10개 음성 샘플 준비 (TTS 또는 수집) |
| Transcript | 직접 라벨링 또는 mock STT 사용 |
| VAD/Speech Event | 음성 구간 라벨 또는 간단한 threshold |
| STT 모델 | 1주차에는 mock (실제 STT는 후순위) |

### 준비할 것

```
data/audio_samples/
├─ refund_001.wav       (고객 발화)
├─ refund_001.txt       (Transcript)
├─ backchannel_001.wav
├─ backchannel_001.txt
└─ ...
```

### 장점
- ✅ 텍스트와 음성의 차이 확인 가능
- ✅ 데모 영상으로 사용 가능
- ✅ Prosody/tone은 아직 아니지만, 음성의 자연성 반영

### 단점
- ❌ 음성 수집/생성에 시간 필요
- ❌ STT 정확도 평가 안 함 (1주차)

### 예시

```
[Audio File Test 모드]

파일 선택: refund_001.wav
↓ [재생 버튼]
Audio: "아 그게 아니라 환불받고 싶은데요."

Transcript 확인:
"아 그게 아니라 환불받고 싶은데요."
↓
Policy 판단: intent_shift → stop_and_switch
↓
결과: "✅ 올바른 판단"
```

---

## 3️⃣ Mic Trial (마이크 실시간 입력)

### 정의
**실시간 마이크 입력**을 녹음하고 판단

### 화면에서의 동작
```
[녹음 시작] → [고객 발화 녹음] → [STT] → [판단]
```

### 기술 요구사항
- Browser microphone access
- Web Audio API
- Real-time speech recognition (향후)

### 1주차 진행 방식

| 항목 | 1주차 처리 |
|------|-----------|
| 마이크 | 브라우저 마이크 접근 가능하게 할 준비만 |
| 녹음 | 간단한 record/playback 구현 |
| STT | mock transcript 또는 사용자 직접 입력 |
| 판단 | Text Replay와 동일한 Policy 사용 |

### 1주차 목표
- "이 방식으로 확장 가능하다"는 것만 보여주기
- 실제 live STT는 이후 구현

### 예시

```
[Mic Trial 모드]

[녹음 시작]
사용자가 마이크에 말함: "아 그게 아니라..."
[녹음 중지]
↓
Mock STT: "아 그게 아니라 환불받고 싶은데요."
(또는 사용자가 직접 입력)
↓
Policy 판단: intent_shift → stop_and_switch
```

---

## 세 모드의 비교

| 항목 | Text Replay | Audio File | Mic Trial |
|------|-------------|-----------|-----------|
| **입력** | 텍스트만 | 음성 파일 + 텍스트 | 실시간 음성 |
| **준비 시간** | 1시간 | 3시간 (샘플 생성) | 2시간 (구조만) |
| **1주차 목표** | ✅ 필수 | ✅ 필수 | 🔮 선택 |
| **Policy 테스트** | 핵심 | 추가 검증 | 구조 확인 |
| **데모 가치** | 보통 | 높음 | 최고 |
| **기술 복잡도** | 낮음 | 중간 | 높음 |

---

## 공통 데이터 흐름

세 모드 모두, 최종적으로 AI Action Policy에 전달되는 정보는 동일:

```
┌─────────────────────────────────────┐
│  입력 모드별로 다름                 │
│  (Text / Audio / Mic)               │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  공통 정규화 (Normalization)         │
│  ├─ user_utterance (STT or Text)   │
│  ├─ event_type                      │
│  ├─ current_intent                  │
│  └─ intent_similarity               │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  AI Action Policy (Baseline~Policy v3)            │
│  → action label 결정                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  결과 표시                          │
│  ├─ expected_actions               │
│  ├─ actual_action                  │
│  ├─ decision reason                │
│  └─ evaluation                      │
└─────────────────────────────────────┘
```

---

## 콘솔 UI 구성 (예상)

```
┌─────────────────────────────────────────┐
│ Wind Docs Experiment Console            │
├─────────────────────────────────────────┤
│                                         │
│ [Text Replay] [Audio File] [Mic Trial] │ ← 입력 모드 선택
│                                         │
├─────────────────────────────────────────┤
│ Scenario Selector                       │
│ ┌─────────────────────────────────────┐ │
│ │ Select or Create Scenario           │ │
│ │ - commerce_refund_001               │ │
│ │ - commerce_backchannel_001          │ │
│ └─────────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│ Input Panel                             │
│ ┌─────────────────────────────────────┐ │
│ │ AI Utterance: [배송 중이며...]      │ │
│ │ User Input: [환불받고...]          │ │
│ └─────────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│ Results                                 │
│ ┌─────────────────────────────────────┐ │
│ │ Event Type: intent_shift            │ │
│ │ Expected: stop_and_switch           │ │
│ │ Baseline: ❌ continue                     │ │
│ │ Policy v1: ❌ continue                     │ │
│ │ Policy v2: ✅ stop_and_switch              │ │
│ │ Policy v3: ✅ stop_and_switch              │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## 다음

👉 **[Demo & Examples](../04-demo/demo1.md)** — 실제 예시 3가지
