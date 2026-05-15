# Wind Docs: Whisper Intent Interruption Detection

## What Is Wind?

Wind는 음성 AI 상담에서 AI가 말하는 중 고객이 끼어들거나 요청을 바꾸는 순간을 다루는 MVP입니다.

목표는 완성형 상담 앱을 한 번에 만드는 것이 아니라, **고객 발화를 보고 AI가 계속 말할지, 짧게 인정할지, 답하고 이어갈지, 멈추고 전환할지, 확인 질문을 할지** 판단하는 구조를 검증하는 것입니다.

## 핵심 장면

```text
AI: 고객님의 상품은 현재 배송 중이며, 내일 오후 도착 예정입니다.
고객: 아 그게 아니라 환불받고 싶은데요.
```

좋은 응답은 AI가 배송 안내를 계속 밀어붙이지 않고, 고객의 환불 요청으로 상담 흐름을 전환하는 것입니다.

## 현재 MVP 범위

| 항목 | 현재 상태 |
| --- | --- |
| 판단 케이스 | `data/scenarios.json` 기준 커머스 상담 30개 |
| 입력 경로 | Text Replay, Audio File Test, Mic Trial 보조 흐름 |
| 정책 실행 | `baseline`, `policy_v1`, `policy_v2`, `policy_v3`, `policy_v3_1` |
| 공통 흐름 | CLI, Backend API, Playground, Test Bench가 같은 runner 사용 |
| 평가 산출물 | `results/runs/{run_id}/`에 `run_meta.json`, `evaluation.json`, `decision_logs.jsonl`, `error_analysis.md` 저장 |
| 최종 후보 | `policy_v3_1` prompt-only 후보. 확정 운영 정책은 아님 |

## 최신 실험 요약

수치는 Playground 화면이 아니라 run artifact 기준입니다.

| dataset | policy | run_id | correct / total | action_accuracy | 주요 해석 |
| --- | --- | --- | ---: | ---: | --- |
| core | `policy_v2` | `20260515_112306_policy_v2` | 26 / 30 | 0.8667 | false stop은 안정적이나 일부 intent shift를 놓침 |
| core | `policy_v3_1` | `20260515_111953_policy_v3_1` | 27 / 30 | 0.9000 | return/refund 경계는 개선됐지만 payment follow-up, complaint 회귀가 남음 |
| challenge | `policy_v2` | `20260515_110153_policy_v2` | 14 / 18 | 0.7778 | 인접 업무 경계를 같은 흐름으로 묶는 실패가 드러남 |
| challenge | `policy_v3_1` | `20260515_111904_policy_v3_1` | 17 / 18 | 0.9444 | return/refund 인접 업무 `missed_switch`가 0건으로 줄어듦 |

## 읽는 순서

1. [왜 이 문제인가](01-problem/why.md)
2. [우리의 질문](01-problem/question.md)
3. [Solution Overview](02-design/overview.md)
4. [Evaluation Approach](02-design/evaluation.md)
5. [Input Modes](03-data/input-modes.md)
6. [Repository & Code Structure](05-resources/repo.md)
