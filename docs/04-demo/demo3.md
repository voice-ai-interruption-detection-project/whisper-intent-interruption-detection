# Demo 3: 모호한 발화 처리

## 상황

```text
AI: 현재 배송 상태를 확인해 드리겠습니다.
고객: 음... 그게 맞나?
```

고객이 새 업무를 요청한 것인지, 단순히 생각 중인지, 기존 설명에 의문을 가진 것인지 확실하지 않습니다.

## 자연스러운 행동

대표적인 기대 행동은 `ask_clarifying`입니다.

```text
AI: 어떤 부분을 다시 확인해 드릴까요?
```

의도가 불명확한 상태에서 바로 전환하거나 계속 진행하면 고객 의도를 잘못 확정할 수 있습니다.

## 현재 결과

ambiguous 케이스는 여전히 어려운 영역입니다.

`policy_v3_1` core run에서 남은 ambiguous 실패:

| scenario_id | expected_actions | actual_action | primary_failure |
| --- | --- | --- | --- |
| `commerce_ambiguous_002` | `ask_clarifying` | `brief_ack` | `ambiguous_intent` |

`policy_v3_challenge`에서도 남은 1건의 실패는 ambiguous control 케이스였습니다.

| scenario_id | expected_actions | actual_action | primary_failure |
| --- | --- | --- | --- |
| `policy_v3_challenge_ambiguous_control_001` | `ask_clarifying` | `continue` | `ambiguous_intent` |

## 해석

현재 MVP는 same-intent vs intent-shift, return/refund boundary에서는 개선 신호를 보여줬지만, 모호한 발화의 세부 기준은 아직 안정화되지 않았습니다.

후속 정책에서 봐야 할 질문은 아래입니다.

- "잠깐요"는 기다려 달라는 신호인가, 확인 질문을 유도해야 하는 신호인가?
- 짧은 되묻기와 단순 backchannel을 어떻게 나눌 것인가?
- ambiguous를 무조건 `ask_clarifying`으로 볼지, 일부는 `brief_ack`나 `continue`를 허용할지?

## 핵심 학습

MVP의 목적은 모든 케이스를 완벽히 맞추는 것이 아니라, 실패 케이스를 다음 정책 개선 단위로 분리하는 것입니다. ambiguous failure는 그 다음 실험 후보입니다.
