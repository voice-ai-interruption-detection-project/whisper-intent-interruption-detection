# Solution Overview: 4단계 정책 비교

## 우리의 접근: 단계적 개선

단일 모델 "완벽한 해결책"을 목표로 하지 않는다.
대신 각 단계에서 **어떤 신호를 추가했을 때 무엇이 개선되는지** 보여준다.

---

## 4가지 정책

### 📊 전체 흐름도

```
Baseline: VAD-only
├─ 입력: 음성 신호 (speech detected?)
├─ 판단: 음성이 있으면 interrupt
└─ 성과: 기준선 (baseline)

Policy v1: + Backchannel Rule
├─ 입력: 음성 신호 + 텍스트
├─ 판단: 하지만 "네/음"은 제외
└─ 성과: False Stop ↓ (괜히 멈추는 비율 감소)

Policy v2: + Intent Shift Detection
├─ 입력: 텍스트 + 의도 유사도
├─ 판단: 의도가 달라지면 switch
└─ 성과: Missed Switch ↓ (의도 전환 놓침 감소)

Policy v3: Full AI Action Policy
├─ 입력: 모든 신호 종합
├─ 판단: 6가지 action label 중 선택
└─ 성과: Accuracy ↑ (전체 성능 향상)
```

### 명칭 매핑

표시 라벨은 외부 문서·발표·README에서 쓰고, 코드 식별자는 파일명·yaml 키·run_id에서 쓴다.

| 표시 라벨 | 코드 식별자 | run_id 접미사 |
|---|---|---|
| `Baseline` | `baseline` | `..._baseline` |
| `Policy v1` | `policy_v1` | `..._policy_v1` |
| `Policy v2` | `policy_v2` | `..._policy_v2` |
| `Policy v3` | `policy_v3` | `..._policy_v3` |

---

## 정책별 상세

### **Baseline: VAD-only (기준선)**

**입력:**
```python
has_user_speech: bool  # 음성이 감지되었는가?
```

**판단 로직:**
```python
if not has_user_speech:
    return "continue"  # 계속 말하기
else:
    return "stop_and_switch"  # 무조건 멈춤
```

**특징:**
- ✅ 매우 간단하고 빠름
- ❌ 고객의 의도를 모른다
- ❌ 모든 음성을 같게 취급

**평가:**
- Baseline으로 사용
- 모든 맞장구를 "interrupt"로 인식 → False Stop 높음
- 모든 의도 전환을 못 봄 → Missed Switch 높음

---

### **Policy v1: Backchannel Rule 추가**

**입력:**
```python
has_user_speech: bool
utterance_text: str  # "네", "음" 등
```

**판단 로직:**
```python
if not has_user_speech:
    return "continue"

# 맞장구 감지
backchannel_keywords = ["네", "음", "네요", "알겠어요", "맞아", "그래"]
if utterance_text in backchannel_keywords:
    return "continue"  # 또는 "brief_ack"

else:
    return "stop_and_switch"
```

**특징:**
- ✅ Baseline의 False Stop 문제 해결
- ✅ 매우 간단한 규칙 기반
- ❌ 아직 의도 전환은 못 봄

**개선:**
- False Stop Rate: 25% → 8% (↓17%)
- Missed Switch Rate: 45% → 40% (변화 작음)

---

### **Policy v2: Intent Shift Detection 추가**

**입력:**
```python
current_intent: str  # AI가 진행 중이던 의도 ("배송조회", "환불요청" 등)
predicted_user_intent: str  # STT 텍스트로 예측한 고객 의도
intent_similarity: float  # 0~1 사이의 유사도
```

**판단 로직:**
```python
if not has_user_speech:
    return "continue"

if is_backchannel(utterance_text):
    return "continue"

# 의도 유사도로 전환 판단
if intent_similarity < THRESHOLD:  # 예: 0.5
    return "stop_and_switch"  # 의도 전환 감지
else:
    return "pause"  # 같은 주제 내 질문
```

**특징:**
- ✅ Policy v1의 Missed Switch 문제 해결
- ✅ 의도 유사도를 SBERT로 계산
- ❌ 아직 상황별 섬세한 대응은 안 함

**개선:**
- Missed Switch Rate: 40% → 12% (↓28%)
- Accuracy: 75% → 85% (↑10%)

---

### **Policy v3: Full AI Action Policy**

**입력:**
```python
# 모든 신호 종합
has_user_speech: bool
utterance_text: str
event_type: str  # backchannel, same_intent_question, intent_shift 등
predicted_user_intent: str
intent_similarity: float
tone_confidence: float  # (향후: 감정/톤 신호)
```

**판단 로직:**
```python
if not has_user_speech:
    return "continue"

# 이벤트 타입별로 행동 결정
if event_type == "backchannel":
    return "brief_ack"  # 또는 "continue"

elif event_type == "same_intent_question":
    return "pause"  # 멈추고 답하기

elif event_type == "intent_shift":
    if high_confidence(intent_similarity):
        return "stop_and_switch"
    else:
        return "ask_clarifying"

elif event_type == "complaint":
    if severity_high:
        return "handoff"  # 상담사 연결
    else:
        return "stop_and_switch"

else:
    return "continue"
```

**특징:**
- ✅ 6가지 action label을 상황별로 선택
- ✅ 각 행동이 고객 입장에서 자연스러움
- ✅ 규칙 기반이라 해석 가능
- ❌ 더 많은 신호를 필요로 함

**개선:**
- Accuracy: 85% → 89% (↑4%)
- 각 action label별로 언제 사용되는지 명확

---

## 핵심 개념: Event Type

각 정책의 기초가 되는 것은 **"사용자가 어떤 종류의 신호를 보냈는가"**를 분류하는 것.

| Event Type | 예시 | 기본 행동 |
|------------|------|---------|
| `no_speech` | - | `continue` |
| `noise` | 배경음 | `continue` |
| `backchannel` | "네", "음" | `brief_ack` |
| `same_intent_question` | 같은 주제 질문 | `pause` |
| `intent_shift` | 다른 의도 | `stop_and_switch` |
| `complaint` | 불만/긴급 | `stop_and_switch` / `handoff` |
| `ambiguous` | 의도 불명확 | `ask_clarifying` |

👉 **[Event Types 상세](./event-types.md)**

---

## 평가 전략

각 정책 간 성과를 비교하는 방식:

```
30개 시나리오 적용
  ↓
각 정책별 예측 수행 (Baseline, Policy v1, Policy v2, Policy v3)
  ↓
actual_action이 expected_actions에 포함되는지 비교
  ↓
Mismatch Matrix, Accuracy, Precision, Recall 계산
  ↓
"Baseline vs Policy v1에서 뭐가 개선됐는가?" 분석
```

👉 **[Evaluation Approach 상세](./evaluation.md)**

---

## 다음: 구체적 정의

**👉 [Action Labels](./action-labels.md)** — AI가 선택할 수 있는 6가지 행동

**👉 [Event Types & Intents](./event-types.md)** — 사용자 신호 분류 체계
