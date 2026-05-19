# Wind Docs

## What Is Wind?

Wind는 음성 상담 중에 **AI가 말하고 있을 때** 고객이 끼어들거나, 갑자기 다른 요청을 꺼내는 순간을 다루는 MVP입니다.

처음부터 완성형 상담 앱을 만들기보다, 고객 발화를 보고

- 계속 말할지,
- 짧게만 인정하고 넘어갈지,
- 바로 대답하고 이어갈지,
- 아예 멈추고 흐름을 바꿀지,
- 아니면 한 번 더 확인 질문을 할지

이 판단 구조가 제대로 동작하는지를 검증하는 데에 초점을 두고 있습니다.

## 핵심 장면

대표적인 장면은 이런 상황입니다.

```text
AI: 고객님의 상품은 현재 배송 중이며, 내일 오후 도착 예정입니다.
고객: 아 그게 아니라 환불받고 싶은데요.
```

여기서 좋은 응답은 배송 안내를 그대로 밀어붙이는 게 아니라, 고객의 환불 요청으로 상담 흐름을 자연스럽게 전환하는 것입니다.

## 현재 MVP

<div class="grid cards" markdown>

- **판단 케이스**

    `data/scenarios.json` 기준 커머스 상담 30개를 사용합니다.

- **입력 경로**

    Text Replay, Audio File Test, Mic Trial 보조 흐름으로 같은 판단 구조를 실행합니다.

- **정책 실행**

    `baseline`, `policy_v1`, `policy_v2`, `policy_v3`, `policy_v3_1`을 비교합니다.

- **평가 산출물**

    `results/runs/{run_id}/`에 run metadata, evaluation, decision log, error analysis를 둡니다.

</div>

## 최신 실험 요약

수치는 Playground 화면이 아니라 run artifact 기준입니다. 현재 비교한 prompt-only 후보 중에서는 `policy_v3_1`이 가장 좋은 결과를 보였습니다.

| dataset | policy | run_id | correct / total | action_accuracy | 주요 해석 |
| --- | --- | --- | ---: | ---: | --- |
| core | `policy_v2` | `20260515_112306_policy_v2` | 26 / 30 | 0.8667 | false stop은 안정적이나 일부 intent shift를 놓침 |
| core | `policy_v3_1` | `20260515_111953_policy_v3_1` | 27 / 30 | 0.9000 | return/refund 경계는 개선됐지만 payment follow-up, complaint 회귀가 남음 |
| challenge | `policy_v2` | `20260515_110153_policy_v2` | 14 / 18 | 0.7778 | 인접 업무 경계를 같은 흐름으로 묶는 실패가 드러남 |
| challenge | `policy_v3_1` | `20260515_111904_policy_v3_1` | 17 / 18 | 0.9444 | return/refund 인접 업무 `missed_switch`가 0건으로 줄어듦 |

## 다음에 읽을 문서

<div class="grid cards" markdown>

- **문제 정의**

    VAD-only 접근의 한계와 이 프로젝트가 다루는 interrupt / intent switch 문제를 정리합니다.

    [왜 이 문제인가](01-problem/why.md)

- **설계**

    입력 경로, policy, runner, evaluator가 어떤 공통 흐름으로 연결되는지 설명합니다.

    [Solution Overview](02-design/overview.md)

- **평가**

    action label, expected action, run artifact 기준으로 실험 결과를 어떻게 읽는지 정리합니다.

    [Evaluation Approach](02-design/evaluation.md)

- **데이터**

    scenario bank와 입력 모드가 판단 구조 검증에 어떻게 쓰이는지 설명합니다.

    [Input Modes](03-data/input-modes.md)

</div>
