# Demo 3: Ambiguous Case (의도가 불명확한 경우)

## 상황

```
AI: "어떤 상품을 찾으세요?"

고객: "음... 잠깐요."  (의도 불명확)
```

---

## 모든 정책이 고민하는 상황

### 분석

| 신호 | 값 |
|------|-----|
| 음성 감지 | ✅ 있음 |
| Backchannel? | ❌ 아님 (단순 생각 신호) |
| Intent Shift? | ❓ 모름 (뭘 말하려는지 모름) |
| 의도 유사도 | ❌ 계산 불가 (발화가 너무 짧음) |

### Baseline (VAD-only)
```
음성 감지 → "stop_and_switch"
(의도를 모르니까 일단 멈춤)
```

### Policy v1 (Backchannel Rule)
```
"음"은... backchannel일까?
아니다, 이건 생각하는 신호다.
→ "stop_and_switch"
```

### Policy v2 (Intent Shift Detection)
```
의도를 파악할 수 없음.
→ "stop_and_switch"? "pause"?
```

---

## Policy v3의 판단

### Policy v3 (Full AI Action Policy)

```python
if ambiguous_utterance:
    return "ask_clarifying"  # 확인 질문하기
```

### 결과

```
AI: "어떤 상품을 찾으세요?"
고객: "음... 잠깐요."
AI: "혹시 어떤 종류의 상품을 찾으세요?"  ← 확인 질문

고객 입장: "좋아, 다시 생각해서 말해야겠다"
→ 자연스러운 대화 흐름 복구
```

### 평가

- **Expected Action**: `ask_clarifying`
- **Actual Action (Policy v3)**: `ask_clarifying`
- **결과**: ✅ 상황에 맞는 판단

---

## 이 케이스의 의미

### 왜 어려운가?

1. **발화가 짧음** — 의도 분류 불가
2. **비언어 신호** — "음"은 생각 신호일 수도, 불만일 수도
3. **문맥 부족** — 이전 대화 맥락이 필요할 수도

### 올바른 대응

Baseline~Policy v2는 "멈추거나 전환"하는 방식만 아는데,
Policy v3은 "오해를 풀고 다시 물어보기"라는 새로운 선택지를 제시

### 배우는 점

**항상 명확한 답이 있는 건 아니다.**
- 의도가 불명확하면 물어봐야 한다
- 이것도 중요한 AI 행동이다

---

## 다른 경계 케이스들

### 케이스 1: 짧은 불만 신호

```
AI: "배송은 내일 도착 예정입니다."
고객: "에이..."  (약한 불만 신호)

분석:
- Backchannel 아님
- 명확한 의도 전환 아님
- 하지만 불만은 있음

Policy v3 판단: 상황에 따라 "ask_clarifying" 또는 "stop_and_switch"
(tone hint를 고려해 결정)
```

### 케이스 2: 부정확한 STT 결과

```
AI: "배송은 내일 도착 예정입니다."
고객: (발화: "환불받고 싶어요")
STT 결과: "황룰 받고 싶어"  (STT 오류)

Policy v2 분석:
- "황룰" → 인식 불가
- 의도 분류 실패
- 유사도 계산 실패

Policy v3 판단: STT 신뢰도 낮음 → "ask_clarifying"
```

### 케이스 3: 다중 의도

```
AI: "배송 상황을 알려드릴까요?"
고객: "네, 그런데 배송비는 따로 드나요?"

분석:
- 기본: 배송 확인 (backchannel)
- 추가: 배송비 질문 (same_intent_question)

Policy v3 판단: 복합 신호 → "pause" (일단 멈추고 답하기)
```

---

## 평가상의 의미

### Accuracy 개선 폭

```
Baseline→Policy v1: ↑13%  (False Stop 제거)
Policy v1→Policy v2: ↑7%   (Intent Shift 감지)
Policy v2→Policy v3: ↑4%   (경계 케이스 처리)
```

Policy v3의 개선 폭이 작은 이유:
- 경계 케이스는 적음 (7%)
- 하지만 사용자 경험 관점에서는 중요

### Confusion Matrix에서 보이는 것

```
Policy v2에서:
- same_intent_question을 stop_and_switch로 헷갈림
- ambiguous를 stop_and_switch로 잘못 판단

Policy v3에서:
- ambiguous가 제대로 분류됨
- 경계가 명확해짐
```

---

## 핵심 학습

### 이 데모 3가지가 보여주는 것

1. **Demo 1**: 간단한 규칙이 큰 효과 (Backchannel)
2. **Demo 2**: 의미 분석의 중요성 (Intent Similarity)
3. **Demo 3**: 항상 명확한 답은 없다 (Ambiguity 처리)

### 리서치 임플리케이션

```
AI가 "멈춘다"만 아는 것 → "언제 멈추고 뭘 할지" 판단
```

이것이 자연스러운 음성 상담의 핵심.

---

## 마치며

이 3가지 데모는:
- ✅ **간단한 개선**으로 얻는 효과
- ✅ **기술적 깊이**로 가능해지는 것들
- ✅ **근본적인 한계**와 그 대응

을 보여준다.

---

## 다음

👉 **[Resources](../05-resources/team.md)** — 팀, 타임라인, 논문
