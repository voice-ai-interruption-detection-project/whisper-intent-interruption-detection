# internal

프로젝트의 내부 기준 자료를 정리하는 영역이다.

`docs/`가 팀 외부에도 보여줄 수 있는 공유/공개 문서라면, `internal/`은 그 전에 팀 안에서 기준을 맞추는 작업 자료층이다. 기획 보강, 용어 정리, 정책 초안, 평가 기준, 설계 메모, 문서로 옮기기 전의 정리본처럼 아직 공개 문서나 active rule로 고정하기 이른 자료를 둔다.

여기서 정리한 내용이 안정되면 필요한 active 위치(`docs/`, `.claude/rules/`, 코드, 데이터)로 반영한다.

## 운영 기준

- 처음부터 현재 기준 어휘로 작성한다.
- action label은 `respond_and_continue` 같은 현재 라벨을 쓴다.
- 실패 분류는 primary 5종(`false_stop`, `missed_switch`, `action_confusion`, `ambiguous_intent`, `STT_uncertainty`)을 기준으로 한다.
- 결과 산출물은 `results/runs/{run_id}/` 계약을 기준으로 한다.
- `기획/`의 과거 자료를 그대로 복사하지 말고, 필요한 내용만 현재 기준으로 재정리한다.

## 들어오는 자료

- 기획·제품 방향을 현재 기준에 맞춰 다시 정리한 메모
- action label, event type, policy version 같은 용어·정책 초안
- 평가 기준, failure taxonomy, run artifact 계약 정리
- docs에 옮길 수 있지만 아직 외부 공유 문장으로 다듬지 않은 자료
- 코드나 데이터 변경 전에 팀 안에서 맞춰야 하는 설계 메모

## 현재 기준 자료

- [Project Language Map](project-language-map.md): scenario, input mode, event type, action label, policy version의 층위 정리
- [Evaluation and Results Contract](evaluation-and-results-contract.md): metric, failure taxonomy, `results/runs/{run_id}/` 계약, 수치 인용 기준

## docs로 반영할 때

1. `internal/`에서 기준과 용어를 먼저 맞춘다.
2. 반영 범위가 라벨, 정책, 평가 기준을 바꾸면 `decisions/`에 사안별 기록을 남긴다.
3. 공개/공유가 필요한 내용만 `docs/`에 발췌한다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
