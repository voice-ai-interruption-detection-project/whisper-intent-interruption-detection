# Evaluation Approach: 정책들을 어떻게 평가하는가?

## 평가의 기본 원칙

```
각 정책(Baseline~Policy v3)을 같은 30개 시나리오에 적용
  ↓
actual_action이 expected_actions에 포함되는지 비교
  ↓
어떤 정책이 어떤 상황을 더 잘 다루는가 분석
```

---

## 평가 대상 3가지

### 1️⃣ Binary Interruption (개입 필요 여부)

**정의:**
```
Intervention Required: pause, stop_and_switch, ask_clarifying, handoff
No Intervention:      continue, brief_ack
```

**의미:**
- AI가 "멈춰야 하는가" vs "계속 말해야 하는가"

---

### 2️⃣ Action Classification (행동 분류)

**정의:** 6가지 action label 중 정확히 어떤 것을 선택했는가?

**의미:**
- 단순히 멈추는지 계속하는지만이 아니라
- **어떤 식으로 멈추고 어떻게 대응할 것인가**

---

### 3️⃣ Policy Version Comparison (정책 간 비교)

**정의:** Baseline, Policy v1, Policy v2, Policy v3의 성능을 단계별로 비교

**의미:**
- 각 단계에서 "새로 추가한 신호"가 실제로 개선을 가져왔는가?
- 언제 어떤 문제가 해결되는가?

---

## 평가 지표 (Metrics)

### 📊 분류 정확도

| 지표 | 정의 | 의미 |
|------|------|------|
| **Accuracy** | (TP + TN) / 전체 | 전체 예측이 얼마나 맞았는가? |
| **Precision** | TP / (TP + FP) | "멈춰야 한다"고 했을 때, 실제로 맞을 확률? |
| **Recall** | TP / (TP + FN) | 실제로 멈춰야 하는 경우를 놓치지 않았는가? |
| **F1 Score** | 2 × (P × R) / (P + R) | Precision과 Recall의 균형 |

### 🎯 도메인 특화 지표

| 지표 | 정의 | 고객 입장 |
|------|------|---------|
| **False Stop Rate** | 멈추지 말아야 할 때 멈춘 비율 | "왜 내 맞장구에 반응을 안 하지?" |
| **Missed Switch Rate** | 전환해야 할 때 못한 비율 | "내 의도를 못 알아듣나?" |
| **Mismatch Matrix** | 복수 정답 set별 오답 actual_action 패턴 | 어떤 허용 행동 묶음에서 무엇으로 틀리는가? |

---

## 단계별 평가 전략

### Baseline vs Policy v1 비교

```
목표: False Stop Rate 감소

측정:
├─ Baseline (VAD-only)
│  └─ backchannel 시나리오를 모두 "interrupt"로 판단
│     → False Stop Rate = 25%
│
└─ Policy v1 (+ Backchannel Rule)
   └─ backchannel을 "continue"로 판단
      → False Stop Rate = 8%
      ✅ 개선: 25% → 8% (↓17%)
```

---

### Policy v1 vs Policy v2 비교

```
목표: Missed Switch Rate 감소

측정:
├─ Policy v1 (Backchannel만 봄)
│  └─ intent_shift 시나리오도 "continue"로 남김
│     → Missed Switch Rate = 40%
│
└─ Policy v2 (+ Intent Shift Detection)
   └─ intent_shift를 "stop_and_switch"로 판단
      → Missed Switch Rate = 12%
      ✅ 개선: 40% → 12% (↓28%)
```

---

### Policy v2 vs Policy v3 비교

```
목표: 종합 정확도(Accuracy) 향상

측정:
├─ Policy v2 (Intent Similarity만 봄)
│  └─ Accuracy = 85%
│     하지만 complaint나 ambiguous를 다루지 못함
│
└─ Policy v3 (Full Policy)
   └─ 모든 event_type 고려
      → Accuracy = 89%
      ✅ 개선: 85% → 89% (↑4%)
```

---

## Mismatch Matrix 예시

```
Policy v2 정책의 Mismatch Matrix (예시):

Expected actions set                Actual action
brief_ack|continue                  stop_and_switch: 2
respond_and_continue                ask_clarifying: 1
stop_and_switch                     continue: 3

해석:
- backchannel 허용 set(continue/brief_ack)에서 멈춤 판단이 난 케이스가 있음
- "same_intent_question"과 "intent_shift" 경계에서 실수 많음
- 정답 action이 여러 개인 케이스는 primary label로 접지 않고 set membership으로 평가함
```

---

## Decision Log 기록

각 시나리오에 대해 다음을 기록:

```json
{
  "scenario_id": "commerce_refund_001",
  "policy_version": "Policy v2",
  
  "expected_actions": ["stop_and_switch"],
  "actual_action": "stop_and_switch",
  "action_match": true,
  
  "signals": {
    "has_user_speech": true,
    "stt_text": "아 그게 아니라 환불받고 싶은데요.",
    "predicted_user_intent": "환불요청",
    "current_intent": "배송조회",
    "intent_similarity": 0.22
  },
  
  "reason": "사용자 발화가 기존 배송조회 intent와 낮은 유사도를 보이고 환불요청 intent로 분류되어 전환 판단"
}
```

---

## 1주차 MVP 평가 계획

### 데이터셋
- **Scenario Bank**: 30개 (level 1~5 고르게 분포)
- **Test Set**: 모든 30개 (작은 규모라 train/test split 하지 않고 전체 평가)

### 평가 흐름

```
Step 1: Scenario 로드 (30개)
Step 2: 각 정책 실행 (Baseline, Policy v1, Policy v2, Policy v3)
Step 3: 결과 기록 (decision_logs.jsonl)
Step 4: 지표 계산 (accuracy, precision, recall, F1, domain metrics)
Step 5: 비교 분석 (Baseline vs Policy v1, Policy v1 vs Policy v2, Policy v2 vs Policy v3)
Step 6: 실패 케이스 분석
```

### 산출물

```
results/
├─ evaluation.json          # 정책별 지표 종합
├─ decision_logs.jsonl      # 각 시나리오별 판단 로그
├─ evaluation.json          # action_accuracy, failures, mismatch_matrix, latency
├─ run_meta.json            # 실행 설정과 기준 snapshot
├─ metrics_comparison.png   # Accuracy/Precision/Recall 비교
└─ error_analysis.md        # 실패 케이스 분석
```

---

## 평가의 한계

### 1️⃣ Text-only 평가
- 실제 음성의 prosody, tone, speed를 반영하지 않음
- 향후 audio sample로 확장 계획

### 2️⃣ Intent Shift Threshold 고정
- 현재: 0.6으로 고정
- 실제로는 domain/task별로 조정 필요

### 3️⃣ 라벨링 편향
- expected_actions는 우리가 "허용 가능한 행동"으로 정한 것
- 실제 고객 반응과 다를 수 있음

### 4️⃣ 샘플 크기 작음
- 30개 시나리오는 통계적으로 유의미하지 않을 수 있음
- 하지만 MVP 단계에선 경향성을 보는 것이 목표

---

## 성공 기준

✅ **최소 기준:**
- Baseline과 Policy v1 사이에 유의미한 차이 (False Stop ↓)
- Policy v1과 Policy v2 사이에 유의미한 차이 (Missed Switch ↓)
- 각 정책의 강점과 약점이 명확히 드러남

✅ **추가 기준:**
- Policy v3가 "해석 가능한 규칙"으로 표현 가능한가?
- 어떤 케이스가 모든 정책을 실패하게 하는가?
- threshold 조정의 여지가 있는가?

---

## 다음 섹션

👉 **[Data & Scenarios](../03-data/schema.md)** — 평가 데이터를 어떻게 설계했는가?
