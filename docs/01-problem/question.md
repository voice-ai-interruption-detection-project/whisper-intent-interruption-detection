# 우리의 질문

## 핵심 질문

> AI가 말하는 중 들어온 고객 신호를 보고, AI의 다음 행동을 자연스럽게 고를 수 있는가?

이 프로젝트가 확인한 것은 단순히 "고객이 말했는가?"가 아닙니다.

```text
고객 발화가 맞장구인가?
같은 업무 안의 보충 질문인가?
다른 업무로 바뀐 요청인가?

그렇다면 AI는 계속 말할까,
짧게 인정할까,
답하고 이어갈까,
멈추고 전환할까?
```

## 검증 항목

### 1. Backchannel / Noise 안정화

**질문:** 짧은 맞장구, 침묵, 의미 없는 소리 때문에 AI가 불필요하게 멈추지 않는가?

```text
고객: 네, 알겠어요.
자연스러운 행동: continue 또는 brief_ack
```

이 축은 `policy_v2`에서 주로 봅니다. 목표 실패 유형은 `false_stop`입니다.

### 2. Same Intent Follow-up vs Intent Shift

**질문:** 고객이 같은 업무 안에서 더 묻는 것과, 다른 업무로 바꾸는 것을 구분하는가?

```text
AI current intent: shipping_inquiry
고객: 배송비는 얼마예요?
자연스러운 행동: respond_and_continue

AI current intent: shipping_inquiry
고객: 환불받고 싶어요.
자연스러운 행동: stop_and_switch
```

이 축은 `policy_v3`와 `policy_v3_1`에서 집중적으로 봅니다. 특히 `policy_v3_1`은 return/refund처럼 가까워 보이지만 별도 workflow인 경계를 다룹니다.

## 현재 결론

`policy_v3_1`은 core dataset에서 `action_accuracy=0.9000`을 기록했습니다.

- run_id: `20260515_111953_policy_v3_1`
- dataset: `data/scenarios.json`
- correct / total: `27 / 30`
- 추가 확인 케이스: `false_stop=1`, `missed_switch=1`, `ambiguous_intent=1`

즉, MVP는 판단 구조가 작동한다는 신호를 보여줬습니다. 이 결과는 다음 개선 지점을 정리하기 위한 실험 결과로 읽습니다.

## 다음

👉 [Solution Overview](../02-design/overview.md)
