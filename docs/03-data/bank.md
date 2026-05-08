# Scenario Bank: 시나리오 현황

## 목표

1주차 MVP를 위해 **30개의 text scenario**를 구축한다.

| 단계 | 목표 규모 | 목적 | 진행 |
|------|---------|------|------|
| **v1** | 30개 | AI Action Policy skeleton 검증 | 📋 진행 중 |
| v2 | 50개 | action label별 coverage 확보 | 🔮 이후 |

---

## Scenario v1: 30개 목표 (현재)

### 구성 전략

**Event Type별 균등 분포:**

```
Event Type분포 (목표)
├─ backchannel     × 6 (20%)   → 맞장구 이해
├─ same_intent_q   × 6 (20%)   → 같은 주제 확인
├─ intent_shift    × 6 (20%)   → 의도 전환
├─ no_speech       × 4 (13%)   → 침묵
├─ noise           × 4 (13%)   → 배경음
├─ complaint       × 2 (7%)    → 불만
└─ ambiguous       × 2 (7%)    → 불명확
   = 30 총계
```

**Difficulty별 분포:**

```
Level 1-2: 8개  (쉬움 - backchannel, noise)
Level 3:   8개  (중간 - same_intent, ambiguous)
Level 4-5: 14개 (어려움 - intent_shift, complaint, 경계 케이스)
```

**Intent별 분포:**

```
배송조회(shipping)     × 8
환불요청(refund)      × 8
반품요청(return)       × 5
결제문제(payment)      × 5
상품문의(product)      × 3
상담사연결(agent)      × 1
```

---

## 생성 프로세스

### Step 1: Intent별 기본 발화 설계

각 intent마다 "AI 기본 발화"를 정의

```
배송조회:
├─ "현재 배송 중이며 내일 오후 도착 예정입니다."
├─ "배송비는 [금액]입니다."
└─ "수거는 [방법]입니다."

환불요청:
├─ "환불은 [조건]에서 가능합니다."
└─ "환불 방법을 설명드리겠습니다."
```

### Step 2: Event Type별 사용자 발화 생성

각 event_type마다 적절한 사용자 발화 생성

```
backchannel → "네", "음", "알겠어요"
same_intent → "배송비는?", "수거는?"
intent_shift → "환불받고 싶어요" (배송 중일 때)
complaint → "뭐 이딴 배송이야!"
```

### Step 3: 어노테이션

- event_type 라벨링
- expected_action 결정 (두 명 이상)
- level 책정
- notes 작성 (모호한 경우)

### Step 4: QA

- 분포 확인
- 라벨 일관성 확인
- edge case 추가

---

## 현재 진행 상황

### 완료
- [ ] 커머스 intent 범위 확정
- [ ] AI 기본 발화 작성
- [ ] scenario template 설계

### 진행 중
- [ ] 30개 scenario 생성
- [ ] Event type별 균등 분포 확인
- [ ] 어노테이션 (두 명 라벨링)

### 예정
- [ ] QA 및 최종 검증
- [ ] scenario_stats.json 생성

---

## 대표 케이스 5개

최종 완성 후, 가장 대표적인 케이스 5개를 선정:

1. **False Stop 케이스** - Baseline 실패, Policy v1 성공
   - Event: backchannel
   - Expected: continue
   - 예시: "네, 알겠어요"

2. **Missed Intent Switch 케이스** - Policy v1 실패, Policy v2 성공
   - Event: intent_shift
   - Expected: stop_and_switch
   - 예시: "환불받고 싶어요"

3. **경계 케이스** - 모호함
   - Event: ambiguous
   - Expected: ask_clarifying
   - 예시: "음... 잠깐요"

4. **Easy Case** - 모두 성공
   - Event: noise
   - Expected: continue

5. **Complex Case** - 모든 정책이 다른 판단
   - Event: complaint
   - Expected: handoff

---

## 다음

👉 **[Input Modes](./input-modes.md)** — 이 데이터를 어떻게 입력받을 건가?
