# context/internal

프로젝트의 내부 기준 자료를 정리하는 영역이다.

`docs/`가 팀 외부에도 보여줄 수 있는 공유/공개 문서라면, `context/internal/`은 그 전에 팀 안에서 기준을 맞추는 작업 자료층이다. 제품 맥락, 용어 정리, 정책 초안, 평가 기준, 설계 메모, 문서로 옮기기 전의 정리본처럼 아직 공개 문서나 active rule로 고정하기 이른 자료를 둔다.

여기서 정리한 내용이 안정되면 필요한 active 위치(`docs/`, `.claude/rules/`, 코드, 데이터)로 반영한다.

## 운영 기준

- 처음부터 현재 기준 어휘로 작성한다.
- action label은 `respond_and_continue` 같은 현재 라벨을 쓴다.
- 실패 분류는 primary 5종(`false_stop`, `missed_switch`, `action_confusion`, `ambiguous_intent`, `STT_uncertainty`)을 기준으로 한다.
- 결과 산출물은 `results/runs/{run_id}/` 계약을 기준으로 한다.
- 과거 자료를 그대로 복사하지 말고, 필요한 내용만 현재 기준으로 재정리한다.

## 들어오는 자료

- 제품 방향을 현재 기준에 맞춰 다시 정리한 메모
- action label, event type, policy version 같은 용어·정책 초안
- 평가 기준, failure taxonomy, run artifact 계약 정리
- docs에 옮길 수 있지만 아직 외부 공유 문장으로 다듬지 않은 자료
- 코드나 데이터 변경 전에 팀 안에서 맞춰야 하는 설계 메모

## 현재 기준 자료

| 문서 | 역할 |
| --- | --- |
| [Current MVP Brief](current-mvp.md) | 현재 코드 상태와 내부 기준에 맞춘 살아있는 MVP 실행 범위 |
| [Product Context](product-context.md) | 제품 문제, 현재 범위, 사용자, 비목표, 남은 결정 후보를 다시 잡기 위한 현재 기준 |
| [Project Language Map](project-language-map.md) | scenario, input mode, event type, action label, policy version의 층위 정리 |
| [Reference](reference/README.md) | schema key와 enum value를 빠르게 확인하는 하위 참조 문서 묶음 |
| [Schema Keys](reference/schema-keys.md) | scenario 원본 key와 run result key의 역할 구분 |
| [Event Types](reference/event-types.md) | `event_type` 7종의 개념, 대표 신호, 경계 기준 |
| [Action Labels](reference/action-labels.md) | action label 6종의 의미와 expected/actual 역할 구분 |
| [Scenario Worked Example](scenario-worked-example.md) | 한 scenario가 schema key/value, policy 판단, evaluation으로 이어지는 예시 |
| [Evaluation and Results Contract](evaluation-and-results-contract.md) | metric, failure taxonomy, `results/runs/{run_id}/` 계약, 수치 인용 기준 |

## docs로 반영할 때

1. `context/internal/`에서 기준과 용어를 먼저 맞춘다.
2. 반영 범위가 라벨, 정책, 평가 기준을 바꾸면 `context/decisions/`에 사안별 기록을 남긴다.
3. 공개/공유가 필요한 내용만 `docs/`에 발췌한다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
