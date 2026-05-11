---
date: 2026-05-11
status: active
related_pr: docs/context-intent-alignment
related_runs:
skill_source: record-decision
tags: [ui, wording, terminology, schema, agent, rules]
---

# UI Wording Layer Balance

## 정리

문서에서 정리한 제품 의도와 용어 기준을 UI에 반영할 때, 내부 문서 용어를 많이 노출하는 것이 곧 정합성은 아니다.

이번 결정의 핵심은 "무조건 병기"나 "무조건 한국어화"가 아니라, UI surface마다 사용자가 읽는 목적과 계약 민감도를 나눠 보는 것이다. 좌측 내비, 필터, 첫 안내처럼 개념의 기준점을 잡는 곳에서는 `판단 케이스(Scenario)` 같은 병기를 허용한다. 반대로 큰 제목, 버튼, metric, table header는 화면의 사용 맥락이나 schema/API/run artifact 계약 이름을 우선한다.

## 범위

- Playground UI wording
- Test Bench UI wording
- `src/backend/static/`의 화면 텍스트와 스타일
- UI 텍스트를 검증하는 정적 테스트
- `.claude/rules/coding.md`의 UI wording 참고 관점
- `context-language-balancer` agent의 UI wording 점검 관점

이번 decision은 schema key rename, run artifact 구조 변경, policy 행동 라벨 변경을 포함하지 않는다.

## 배경

`Context Intent Alignment` 작업 이후 UI에도 같은 기준을 적용하면서, 처음에는 문서 용어를 화면에 직접 옮기는 쪽으로 기울었다.

그 결과 `행동 판단 Workbench`, `단일 판단 케이스(Scenario) 확인`, `아직 실행 전`, `텍스트 입력 판단`, `행동 정확도`처럼 화면에서 어색하거나 과하게 설명적인 문구가 생겼다. 이는 문서 기준 자체가 틀렸다기보다, 문서 용어와 UI 표면의 역할을 충분히 나누지 못한 적용 문제였다.

사용자는 현재 브랜치 서버와 작업 전 기준 서버를 나란히 비교했고, 최종적으로 UI에는 선택적 병기와 계약 이름 보존을 함께 적용하는 방향이 더 낫다고 판단했다.

## 상세 맥락

자세한 선택지와 기각 이유는 `context.md`에 둔다.

이번 대화에서 나온 사용자 피드백과 작업 로그 발췌는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: 좌측 내비와 필터에는 `판단 케이스(Scenario)`를 남겨 개념 기준점을 제공한다.
- 좋아진 것: 큰 제목은 `단일 케이스 확인`, 상단은 `Whisper Intent Workbench`처럼 화면의 자연스러운 목적을 우선한다.
- 좋아진 것: 버튼은 `Text Replay 실행`, `선택한 policy 실행`처럼 사용자가 누르는 동작으로 읽히게 했다.
- 좋아진 것: `action_accuracy`, `expected_action`, `actual_action`, `policy`, `run_id` 같은 metric/schema/API 표면은 억지 번역하지 않는 쪽을 기본 관점으로 삼았다.
- 좋아진 것: agent와 coding rule에는 정답 예시 대신 "주의할 신호"와 "참고할 관점"으로 얇게 남겼다.
- 감수한 부분: UI 안에 한국어와 영어가 함께 남는다. 단, 이는 병기를 반복하기 위한 것이 아니라 표면별 역할 차이를 드러내기 위한 절충이다.

## 후속 점검

- [ ] 새 UI wording을 추가할 때, 화면 목적과 계약 이름 중 무엇을 우선해야 하는지 먼저 본다.
- [ ] 병기가 화면 전체에 반복되면 용어집처럼 보이지 않는지 점검한다.
- [ ] metric/schema/API 이름을 바꾸고 싶을 때는 단순 번역이 아니라 계약 변경인지 먼저 확인한다.
- [ ] 필요하면 `context-language-balancer`로 UI wording의 층위 균형을 점검한다.
