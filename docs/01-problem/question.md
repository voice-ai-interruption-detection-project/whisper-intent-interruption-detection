# 우리의 리서치 질문

## 핵심 질문

> **의도를 감지해 고객 상담 중 AI의 행동을 결정할 수 있는가?**

더 구체적으로:

1. 고객의 **텍스트(STT)**에서 의도를 인식할 수 있는가?
2. 현재 AI의 주제와 고객의 의도를 **비교**해 전환을 감지할 수 있는가?
3. 감지한 의도 변화에 따라 AI가 **자연스러운 행동을 선택**할 수 있는가?

---

## 구체적 검증 항목

### 1️⃣ Backchannel Detection (쉬운 단계)

**질문**: 맞장구("네", "음")를 다른 의도와 구분할 수 있는가?

```
고객: "네, 알겠어요."
AI 판단: backchannel → continue (멈추지 않음) ✅
```

**목표**: False Stop Rate를 XXX%에서 XX%로 감소

---

### 2️⃣ Intent Shift Detection (중간 단계)

**질문**: 고객의 의도 전환을 감지할 수 있는가?

```
AI 주제: "배송조회"
고객: "환불받고 싶은데요."
→ 의도 전환 감지 → stop_and_switch ✅
```

**목표**: Missed Switch Rate를 XXX%에서 XX%로 감소

---

### 3️⃣ Action Policy (전체 단계)

**질문**: 상황에 따라 6가지 행동 중 적절한 것을 선택할 수 있는가?

```
상황: backchannel → continue
상황: same_intent_question → pause
상황: intent_shift → stop_and_switch
상황: complaint → handoff
...
```

**목표**: 전체 Accuracy를 XXX%에 도달

---

## 평가 방식

우리는 단계적으로 정책을 비교한다:

| 단계 | 정책 | 주요 신호 | 평가 지표 |
|------|------|---------|----------|
| Baseline | VAD-only | 음성 신호 | baseline |
| Policy v1 | + Backchannel | 음성 + 텍스트 | False Stop ↓ |
| Policy v2 | + Intent Shift | + 의도 유사도 | Missed Switch ↓ |
| Policy v3 | Full Policy | 모든 신호 종합 | Accuracy ↑ |

각 단계가 이전 단계의 문제를 얼마나 해결했는지 본다.

---

## 1주일 MVP의 목표

**Week 1 목표:**
- Baseline~Policy v3 정책 구현 및 평가
- Text Replay 기반 검증 (정확도 포커스)
- 대표 케이스 3개 데모
- 다음 단계의 기초 다지기

**측정 방식:**
```
30개 시나리오 × 4가지 정책 (Baseline~Policy v3)
→ Confusion Matrix 생성
→ 각 정책의 강점/약점 분석
```

---

## 성공 기준

✅ **최소 기준:**
- Baseline과 Policy v1 사이에 유의미한 차이 (False Stop ↓)
- Policy v1과 Policy v2 사이에 유의미한 차이 (Missed Switch ↓)

✅ **추가 기준:**
- Policy v3 정책이 일관된 규칙으로 표현 가능한가?
- 어떤 케이스가 모든 정책을 실패하게 하는가?

---

## 다음: 어떻게 풀 것인가?

우리의 해결 접근법:

👉 **[Approach & Design](../02-design/overview.md)**
