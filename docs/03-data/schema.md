# Scenario Schema: 데이터 구조

## 개요

모든 시나리오는 다음 JSON 구조를 따른다.

```json
{
  "scenario_id": "commerce_refund_001",
  "level": 4,
  "domain": "commerce",
  "ai_current_intent": "배송조회",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "아 그게 아니라 환불받고 싶은데요.",
  "event_type": "intent_shift",
  "expected_action": "stop_and_switch",
  "expected_user_intent": "환불요청",
  "user_tone_hint": "neutral",
  "has_user_speech": true,
  "notes": "AI 발화 중 사용자가 다른 업무 의도를 제시한 케이스"
}
```

---

## 필드 설명

### 📌 식별 정보

#### `scenario_id` (string, required)
- **의미**: 시나리오의 고유 식별자
- **형식**: `{domain}_{intent/type}_{number}`
- **예시**: `commerce_refund_001`

#### `level` (integer 1~5, required)
- **의미**: 판단 난이도
- **기준**:
  - 1~2: 쉬움 (noise, backchannel)
  - 3: 중간 (같은 주제 질문)
  - 4~5: 어려움 (의도 경계가 모호)

#### `domain` (string, required)
- **의미**: 업무 도메인
- **현재**: `commerce`만 사용 (1주차 범위)

---

### 🤖 AI 상황 정보

#### `ai_current_intent` (string, required)
- **의미**: AI가 진행 중이던 비즈니스 의도
- **가능한 값**: `shipping_inquiry`, `refund_request`, `return_request`, `payment_issue`, `product_inquiry`, `agent_connection`
- **예시**: `배송조회`

#### `ai_utterance` (string, required)
- **의미**: AI가 말하던 발화
- **길이**: 20~100글자 (자연스러운 길이)
- **예시**: `현재 상품은 배송 중이며 내일 오후 도착 예정입니다.`

---

### 👤 사용자 신호 정보

#### `user_utterance` (string, required)
- **의미**: 사용자의 개입 발화
- **길이**: 3~50글자
- **예시**: `아 그게 아니라 환불받고 싶은데요.`

#### `has_user_speech` (boolean, required)
- **의미**: 사용자가 실제로 음성을 냈는가?
- **값**:
  - `true`: 사용자 음성 있음
  - `false`: 사용자 음성 없음 (no_speech, noise)
- **참고**: `false`인 경우 `user_utterance`는 empty string

#### `user_tone_hint` (string: neutral / frustrated / urgent, required)
- **의미**: 사용자의 감정/톤 힌트 (향후 확장용)
- **값**:
  - `neutral`: 중립적 톤
  - `frustrated`: 답답함/불만
  - `urgent`: 긴급/급함

---

### 🏷️ 분류 정보

#### `event_type` (enum, required)
- **의미**: 사용자 신호의 종류
- **가능한 값**:
  - `no_speech`: 사용자 발화 없음
  - `noise`: 배경음/비언어 소리
  - `backchannel`: 맞장구 ("네", "음")
  - `same_intent_question`: 같은 업무 내 보충 질문
  - `intent_shift`: 다른 업무 의도로 전환
  - `complaint`: 불만/긴급 발화
  - `ambiguous`: 의도 불명확
- **예시**: `intent_shift`

#### `expected_user_intent` (string or null, required)
- **의미**: 사용자 발화에서 추출되는 비즈니스 의도
- **값**: 위의 intent 목록 또는 `null` (의도 없음)
- **예시**: `환불요청`

#### `expected_action` (enum, required)
- **의미**: 이 상황에서 AI가 해야 할 행동
- **가능한 값**:
  - `continue`: 계속 말하기
  - `brief_ack`: 짧게 반응하고 계속
  - `respond_and_continue`: 고객 질문에 답하고 계속
  - `stop_and_switch`: 주제 바꾸기
  - `ask_clarifying`: 확인 질문
  - `handoff`: 상담사 연결
- **예시**: `stop_and_switch`

#### `notes` (string, optional)
- **의미**: 어노테이션 근거 또는 특이사항
- **용도**: 라벨링이 모호한 경우 필수 기록
- **예시**: `AI 발화 중 사용자가 다른 업무 의도를 제시한 케이스`

---

## 시나리오 분포

### Event Type별 분포 (목표)

| Event Type | 샘플 수 | 비율 |
|-----------|--------|------|
| `no_speech` | 4 | 13% |
| `noise` | 4 | 13% |
| `backchannel` | 6 | 20% |
| `same_intent_question` | 6 | 20% |
| `intent_shift` | 6 | 20% |
| `complaint` | 2 | 7% |
| `ambiguous` | 2 | 7% |
| **합계** | **30** | **100%** |

### Level별 분포 (목표)

| Level | 의미 | 샘플 수 |
|-------|------|--------|
| 1~2 | 쉬움 | 8 |
| 3 | 중간 | 8 |
| 4~5 | 어려움 | 14 |

### Intent별 분포 (목표)

| Intent | 샘플 수 |
|--------|--------|
| `shipping_inquiry` | 8 |
| `refund_request` | 8 |
| `return_request` | 5 |
| `payment_issue` | 5 |
| `product_inquiry` | 3 |
| `agent_connection` | 1 |

---

## 어노테이션 기준

### 1️⃣ `event_type` 라벨링

**기준:**
1. `user_utterance`의 텍스트 내용을 먼저 봄
2. 맞장구 keyword 확인 → `backchannel`
3. intent shift 확인 → `intent_shift`
4. 같은 주제 내 질문 → `same_intent_question`

**특별한 경우:**
- 방언/구어체 → 의도 기준으로 분류
- "음... 잠깐요" → `ambiguous`

### 2️⃣ `expected_action` 라벨링

**기준:** 고객 입장에서 "자연스러운 AI 행동"을 기준으로 함

- 라벨링 전에 두 명 이상 독립적으로 판단
- 불일치 시 협의

### 3️⃣ `level` 책정

**기준:** Policy가 판단하기 어려운 정도

- Level 1~2: 명확한 케이스 (noise, 뚜렷한 맞장구)
- Level 3: 중간 (같은 주제 질문, 경계가 조금 모호)
- Level 4~5: 어려운 케이스 (intent shift 경계 모호, 복합 상황)

### 4️⃣ `notes` 작성

**규칙:** 라벨링 근거가 불명확하면 반드시 작성

예시:
```
"맞장구와 긍정 응답의 경계가 있지만, 
문맥상 동의 신호로 봄"
```

---

## 예시 시나리오 5개

### 예1: Backchannel (쉬움)
```json
{
  "scenario_id": "commerce_backchannel_001",
  "level": 1,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "네, 알겠어요.",
  "event_type": "backchannel",
  "expected_action": "continue",
  "expected_user_intent": null,
  "user_tone_hint": "neutral",
  "has_user_speech": true,
  "notes": ""
}
```

### 예2: Intent Shift (중간)
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
  "notes": "배송조회와 환불요청 intent 경계"
}
```

### 예3: Same Intent Question (중간)
```json
{
  "scenario_id": "commerce_shipping_follow_001",
  "level": 3,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "현재 상품은 배송 중이며 내일 오후 도착 예정입니다.",
  "user_utterance": "배송비는 따로 드나요?",
  "event_type": "same_intent_question",
  "expected_action": "respond_and_continue",
  "expected_user_intent": "shipping_inquiry",
  "user_tone_hint": "neutral",
  "has_user_speech": true,
  "notes": "같은 배송 주제 내 추가 질문"
}
```

### 예4: Noise (쉬움)
```json
{
  "scenario_id": "commerce_noise_001",
  "level": 1,
  "domain": "commerce",
  "ai_current_intent": "product_inquiry",
  "ai_utterance": "사이즈는 M, L, XL 세 가지가 있습니다.",
  "user_utterance": "",
  "event_type": "noise",
  "expected_action": "continue",
  "expected_user_intent": null,
  "user_tone_hint": "neutral",
  "has_user_speech": false,
  "notes": "기침 소리"
}
```

### 예5: Complaint (어려움)
```json
{
  "scenario_id": "commerce_complaint_001",
  "level": 5,
  "domain": "commerce",
  "ai_current_intent": "shipping_inquiry",
  "ai_utterance": "배송은 정상 진행 중입니다.",
  "user_utterance": "뭐 이딴 배송이야! 지금 당장 와야 돼!",
  "event_type": "complaint",
  "expected_action": "handoff",
  "expected_user_intent": null,
  "user_tone_hint": "urgent",
  "has_user_speech": true,
  "notes": "긴급성 높은 불만 - 상담사 연결 필요"
}
```

---

## 파일 형식

### Single File (`data/scenarios.json`)
```json
{
  "scenarios": [
    { scenario 1 },
    { scenario 2 },
    ...
  ],
  "metadata": {
    "total": 30,
    "version": "1.0",
    "created_date": "2026-05-07"
  }
}
```

---

## 다음

👉 **[Scenario Bank](./bank.md)** — 시나리오 수집 진행 상황
