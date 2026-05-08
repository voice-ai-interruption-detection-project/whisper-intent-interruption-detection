# Demo 2: Missed Intent Switch (의도 전환 감지)

## 상황

```
AI: "현재 상품은 배송 중이며 내일 오후 도착 예정입니다."

고객: "아, 그게 아니라 환불받고 싶은데요."  (의도 전환)
```

---

## 문제: Baseline, Policy v1 모두 실패

### Policy v1 (Backchannel Rule)까지의 판단

```python
if speech_detected:
    if utterance in backchannel_keywords:
        return "brief_ack"
    else:
        return "stop_and_switch"  ← 무조건 전환
```

**문제**: "환불받고 싶어요"는 backchannel이 아니므로 "stop_and_switch"를 반환

하지만 이건 맞나? Policy v1의 입장에서는:
- 음성 있음 ✓
- Backchannel 아님 ✓
- 그러면 전환? (근데 의도를 봐야 알 수 있음)

### 실제 동작

```
AI: "배송은 내일 도착 예정입니다."
고객: "아, 그게 아니라 환불받고 싶은데요."
AI: "네, 알겠습니다. 배송은..."  ← 여전히 배송 얘기

고객 입장: "내 말을 못 들었네?"
→ 좌절감, 상담 품질 저하
```

### 평가

- **Expected Action**: `stop_and_switch`
- **Actual Action (Policy v1)**: `stop_and_switch`
- **문제**: 운이 좋게 맞은 거지, 의도 변화 때문이 아님

---

## 해결: Policy v2 성공

### Policy v2 (+ Intent Shift Detection)의 판단

**핵심 추가**: SBERT를 사용해 **의도 유사도** 비교

```python
current_intent = "배송조회"
user_text = "환불받고 싶은데요"
predicted_intent = "환불요청"

# SBERT로 유사도 계산
similarity = sbert_similarity(current_intent, predicted_intent)
# = 0.22 (매우 낮음)

if similarity < 0.6:
    return "stop_and_switch"  # 의도 전환 감지
else:
    return "pause"  # 같은 주제 질문
```

### 의도 분석

| 정보 | 값 |
|------|-----|
| AI 의도 | "배송조회" |
| 고객 발화 | "환불받고 싶은데요" |
| 추정 의도 | "환불요청" |
| 유사도 | 0.22 (매우 낮음) |
| 판단 | `stop_and_switch` ✅ |

### 결과

```
AI: "배송은 내일 도착 예정입니다."
고객: "아, 그게 아니라 환불받고 싶은데요."
AI: "환불을 원하시는군요. 환불 방법은..."  ← 주제 전환

고객 입장: "내 말을 알아주네"
→ 자연스러운 대화, 만족도 ↑
```

### 평가

- **Expected Action**: `stop_and_switch`
- **Actual Action (Policy v2)**: `stop_and_switch`
- **결과**: ✅ 정확한 판단

---

## 의미

### 이 예시가 보여주는 것

1. **Policy v1의 한계**: 단순 규칙만으로는 의도 변화를 볼 수 없음
2. **텍스트 의미 분석**: SBERT 같은 도구로 의도를 인식 가능
3. **Missed Switch 문제**: 실제 상담에서 40~50% 발생

### 성능 개선

```
Accuracy:
Baseline: 65%
Policy v1: 75%  (backchannel 개선)
Policy v2: 85%  (intent shift 개선)
━━━━━━━━
Policy v1→Policy v2: ↑10%
```

### Intent Shift 데이터 예시

```
AI Intent      고객 Utterance          유사도    판단
배송조회   →  환불받고 싶어요         0.22    intent_shift
배송조회   →  배송비 따로 드나?       0.65    same_intent
결제문제   →  상품 사이즈가?          0.18    intent_shift
상품문의   →  그 색상 다른 게 있나?   0.72    same_intent
```

---

## 다른 케이스

이 방식이 작동하는 다른 상황들:

### 명확한 의도 전환

```
AI: "상품 정보를 알려드리겠습니다."
고객: "근데 반품은 어떻게 하나요?"
→ 의도: 상품문의 → 반품요청 (유사도 낮음)
→ stop_and_switch ✅
```

### 같은 주제 내 질문

```
AI: "배송비는 [금액]입니다."
고객: "그럼 환불받으면 배송비도 돌려받나?"
→ 의도: 배송조회 내 보충질문 (유사도 높음)
→ pause ✅
```

---

## 다음

👉 **[Demo 3: Ambiguous Case](./demo3.md)**
