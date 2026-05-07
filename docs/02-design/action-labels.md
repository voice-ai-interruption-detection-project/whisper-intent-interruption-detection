# Action Labels: AI가 선택할 수 있는 6가지 행동

## 개요

AI가 사용자 개입 신호를 감지한 후 선택할 수 있는 제품 행동(action)의 정의 목록.

각 action label은:
- **AI가 실제로 취할 수 있는 행동**
- **평가할 때 예상 행동과 비교되는 기준**
- **정책(Baseline~Policy v3)이 반환하는 결과값**

---

## 6가지 Action Label

### 1️⃣ `continue` — 계속 말하기

**정의:** AI가 현재 발화를 그대로 계속 진행

**발동 조건:**
- 사용자 발화 없음 (no_speech)
- 배경음 또는 짧은 비언어 소리 (noise)
- 맞장구 (backchannel) - Policy v1 이상에서

**고객 입장:**
- "상담원이 자연스럽게 이어 나간다"

**예시:**
```
AI: "배송은 3일 이내에 도착하고..."
고객: (침묵)
→ AI는 계속 설명
```

---

### 2️⃣ `brief_ack` — 짧게 반응하고 계속

**정의:** AI가 고객의 맞장구를 인정하고 바로 이어 나감

**발동 조건:**
- backchannel ("네", "음", "알겠어요")

**고객 입장:**
- "내 의견이 들렸으니까 계속해"

**예시:**
```
AI: "배송 상황을 말씀드리겠습니다."
고객: "네."
→ AI: "네, 알겠습니다. 지금 배송 중이고..."
```

**`continue`와의 차이:**
- `continue`: AI가 신경 쓰지 않고 진행
- `brief_ack`: AI가 명시적으로 인정하고 진행 ("네, 맞습니다. 그래서...")

---

### 3️⃣ `pause` — 잠깐 멈추고 답하기

**정의:** AI가 잠깐 멈춰서 고객의 질문에 답한 후 이전 주제로 돌아감

**발동 조건:**
- 같은 업무 내 보충 질문 (same_intent_question)

**고객 입장:**
- "같은 주제인데 내 질문에 답해줘"

**예시:**
```
AI: "배송은 내일 도착 예정입니다."
고객: "배송비는 따로 드나요?"  ← 같은 주제(배송)의 질문
→ AI: "네, 배송비는 [답변]. 그래서 배송은..."
```

---

### 4️⃣ `stop_and_switch` — 멈추고 주제 바꾸기

**정의:** AI가 현재 주제를 멈추고 고객의 새로운 의도로 주제를 전환

**발동 조건:**
- 다른 업무 의도로의 전환 (intent_shift)
- 불만 또는 긴급 발화 (complaint) - severity 낮음

**고객 입장:**
- "내가 다른 것을 원해, 주제를 바꿔"

**예시:**
```
AI: "배송은 내일 도착 예정입니다."
고객: "아, 그게 아니라 환불받고 싶은데요."  ← 새로운 의도(환불)
→ AI: "환불을 원하시는군요. 환불 방법은..."
```

---

### 5️⃣ `ask_clarifying` — 확인 질문하기

**정의:** AI가 고객의 의도가 명확하지 않아서 확인 질문을 던짐

**발동 조건:**
- 의도가 불명확한 발화 (ambiguous)

**고객 입장:**
- "내 의도를 이해 못 했으면 물어봐"

**예시:**
```
AI: "어떤 상품을 찾으세요?"
고객: "음... 잠깐요."  ← 의도 불명확
→ AI: "혹시 어떤 상품을 찾으시나요?"
```

---

### 6️⃣ `handoff` — 상담사 연결

**정의:** AI가 처리 불가능한 상황이라고 판단해 상담사에게 연결

**발동 조건:**
- 불만/긴급 발화 (complaint) - severity 높음

**고객 입장:**
- "이건 상담사와 이야기하고 싶어"

**예시:**
```
AI: "배송 상황은 정상입니다."
고객: "뭐 이딴 배송이야! 지금 당장 와야 된다고!"  ← 긴급
→ AI: "상담사께 연결해 드리겠습니다."
```

---

## Event Type과의 매핑

각 event_type이 발생했을 때 기대되는 action:

| Event Type | 기본 Expected Action | 설명 |
|-----------|-------------------|------|
| `no_speech` | `continue` | 사용자 발화 없음 |
| `noise` | `continue` | 배경음 또는 비언어 소리 |
| `backchannel` | `continue` / `brief_ack` | "네", "음" 등 맞장구 |
| `same_intent_question` | `pause` | 같은 주제 내 보충 질문 |
| `intent_shift` | `stop_and_switch` | 다른 의도로 전환 |
| `complaint` | `stop_and_switch` / `handoff` | 불만/긴급 발화 |
| `ambiguous` | `ask_clarifying` | 의도 불명확 |

---

## 평가 기준

### 1️⃣ 이진 분류 (Binary Classification)

```
실제 행동이 "개입 필요"한가? (interrupt vs continue)

continue, brief_ack
  ↓
불필요한 개입 (No Intervention)

pause, stop_and_switch, ask_clarifying, handoff
  ↓
개입 필요 (Intervention Required)
```

### 2️⃣ 다중 분류 (Multi-class Classification)

6가지 action label 중 정확히 어떤 것을 선택했는가?

```
- 맞게 선택: True Positive
- 틀리게 선택: False Positive / False Negative
```

---

## 다음

👉 **[Event Types & Intents](./event-types.md)** — 사용자 신호를 어떻게 분류하는가?
