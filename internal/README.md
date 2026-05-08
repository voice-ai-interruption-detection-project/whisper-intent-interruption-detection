# internal

프로젝트의 내부 기준 자료와 작업 메모를 정리하는 영역이다.

`docs/`는 공유/공개 문서이고, `internal/`은 그 전에 개념, 용어, 평가 기준, 설계 메모를 맞추는 작업층이다. 새 자료는 여기서 먼저 정리하고, 안정되면 필요한 active 위치(`docs/`, `.claude/rules/`, 코드, 데이터)로 반영한다.

## 운영 기준

- 처음부터 현재 기준 어휘로 작성한다.
- action label은 `respond_and_continue` 같은 현재 라벨을 쓴다.
- 실패 분류는 primary 5종(`false_stop`, `missed_switch`, `action_confusion`, `ambiguous_intent`, `STT_uncertainty`)을 기준으로 한다.
- 결과 산출물은 `results/runs/{run_id}/` 계약을 기준으로 한다.
- `기획/`의 과거 자료를 그대로 복사하지 말고, 필요한 내용만 현재 기준으로 재정리한다.

## docs로 반영할 때

1. `internal/`에서 기준과 용어를 먼저 맞춘다.
2. 반영 범위가 라벨, 정책, 평가 기준을 바꾸면 `decisions/`에 사안별 기록을 남긴다.
3. 공개/공유가 필요한 내용만 `docs/`에 발췌한다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
