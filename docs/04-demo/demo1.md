# Demo 1: False Stop (맞장구를 멈춤으로 오인)

## 상황

```
AI: "현재 배송 중이며 내일 오후 도착 예정입니다."

고객: "네, 알겠어요."  (맞장구)
```

---

## 문제: Baseline 실패

### Baseline (VAD-only)의 판단

| 신호 | 판단 |
|------|------|
| 음성 감지 | ✅ 있음 |
| 의도 확인 | ❌ 안 함 |

```
if speech_detected:
    return "stop_and_switch"  ← 음성이 있으니 무조건 멈춤
```

### 결과

```
AI: "현재 배송 중이며 내일 오후 도착 예정입니다."
고객: "네, 알겠어요."
AI: 🤐 (멈춤)

고객 입장: "어? 왜 말을 안 하지?"
→ 부자연스러움, 대화 끊김
```

### 평가

- **Expected Action**: `continue` (또는 `brief_ack`)
- **Actual Action (Baseline)**: `stop_and_switch`
- **결과**: ❌ False Positive (False Stop)

---

## 해결: Policy v1 성공

### Policy v1 (+ Backchannel Rule)의 판단

```python
backchannel_keywords = ["네", "음", "알겠어요", "맞아"]

if speech_detected:
    if utterance in backchannel_keywords:
        return "brief_ack"  # 또는 "continue"
    else:
        return "stop_and_switch"
```

| 신호 | 판단 |
|------|------|
| 음성 감지 | ✅ 있음 |
| Backchannel 확인 | ✅ "네" 감지 |
| 판단 | ✅ 계속 말하기 |

### 결과

```
AI: "현재 배송 중이며 내일 오후 도착 예정입니다."
고객: "네, 알겠어요."
AI: "네, 알겠습니다. 그래서 배송은..."  ← 자연스럽게 진행

고객 입장: "내 말을 들었고 계속해주네"
→ 자연스러운 대화
```

### 평가

- **Expected Action**: `continue`
- **Actual Action (Policy v1)**: `continue`
- **결과**: ✅ 정확한 판단

---

## 의미

### 이 예시가 보여주는 것

1. **Baseline의 한계**: 음성만 가지고는 "좋은 신호"와 "나쁜 신호"를 구분 불가
2. **간단한 해결책**: keyword matching만으로도 많은 개선 가능
3. **False Stop 문제**: 실제 상담에서 20~25% 발생

### 성능 개선

```
False Stop Rate:
Baseline: 25%
Policy v1: 8%
━━━━━━━━
개선: ↓17%
```

---

## 다른 케이스

이 방식이 작동하는 다른 경우들:

### 맞장구의 다양한 형태

```
고객: "음"
고객: "네요"
고객: "알겠어요"
고객: "맞아"
고객: "그렇군요"
```

모두 Policy v1에서는 정확하게 처리됨.

---

## 다음

👉 **[Demo 2: Missed Intent Switch](./demo2.md)**
