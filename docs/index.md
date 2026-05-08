# Wind Docs: Whisper Intent Interruption Detection

## What is Wind?

**고객이 중간에 끼어들 때, AI가 지능적으로 대응할 수 있을까?** 이 질문에서 시작된 음성 상담 인터럽션 감지 AI 프로젝트입니다.

---

## 한눈에 보는 Wind

### 문제

AI가 '음성만 감지해서 멈춘다'는 게 문제:

1. **맞장구도 개입으로 인식** (False Stop)
   - 고객: "네, 알겠어요" → AI가 갑자기 멈춤 → 어색함

2. **고객의 다른 요청을 못 봄** (Missed Switch)
   - 고객: "환불받고 싶어요" → AI: 계속 배송 얘기 → 고객 불만

### 접근
- **4단계 정책 비교**
  - Baseline: VAD-only (소리 나면 멈춤)
  - Policy v1: + Backchannel Detection (맞장구는 안 멈춤)
  - Policy v2: + Intent Shift Detection (의도 변화도 감지)
  - Policy v3: Full AI Action Policy (상황별 자연스러운 행동 선택)

### 결과물

| 항목 | 내용 |
|------|------|
| **Action Labels** | 6가지 AI 행동 정의 |
| **Scenarios** | 30개+ 상황별 시나리오 |
| **Evaluation** | Baseline~Policy v3 성능 비교 분석 |
| **Demo** | 실제 동작하는 3가지 예시 |

