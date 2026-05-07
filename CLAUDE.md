# whisper-intent-interruption-detection 프로젝트 가이드

## 프로젝트 개요

Whisper 기반 intent/interruption detection 실험과 구현을 위한 팀 사이드 프로젝트다.

## 협업 원칙

- 프로젝트 문서에는 개인 컴퓨터 경로, 개인 AI 도구 설정, 로컬 하네스 운영 맥락을 넣지 않는다.
- 팀원이 같은 저장소만 보고 이해하거나 재현할 수 있는 정보만 남긴다.
- 환경 설정, 실행 방법, 데이터 준비 절차가 필요하면 개인 로컬 기준이 아니라 팀 공용 기준으로 문서화한다.
- 실험 결과를 남길 때는 입력 데이터, 모델/설정, 평가 기준, 실행 날짜를 함께 기록한다.

## 하네스 반영 기준

- 루트 지침은 항상 적용되는 최소 협업/경계 규칙만 둔다.
- `docs/harness/`는 **페어 onboarding과 처음 합의용 레퍼런스 layer**다. 잘 안 바뀌는 원칙(`concept.md`), 단계별 적용(`plan.md`), 분석 근거 archive(`research/synthesis.md`, `external-references.md`, `devhub-blog.md`, `sprint4-code.md`)만 둔다. 작업 시 가드는 여기 쌓지 않는다.
- `.claude/rules/`는 **작업 시 항상 켜둘 가드 layer**다. 실험 측은 `experiments.md`, 개발 측은 `coding.md`. 영역만 나누고 폴더는 늘리지 않는다.
- 3층 구조, 실험 프로토콜, agent 후보, hook/scanner 같은 세부 항목은 실제 개발 표면이 생기거나 반복 패턴이 보일 때 하위 문서나 별도 정의로 승격한다.
- repo-local skill/agent/rule/hook은 같은 작업이 반복되거나 실수 비용이 커졌을 때 추가한다.
- 새 규칙은 "빼면 실수하는가?"를 통과해야 한다.

## Repo-local agents

- 모두 report-only다. agent는 조사·검증·분류 결과만 반환하고, 파일 수정은 메인 작업자가 판단한다.
- Claude 원천: `.claude/agents/*.md`, Codex 브릿지: `.codex/agents/*.toml`. 포맷이 달라 자동 symlink가 아니므로 한쪽 수정 시 다른 쪽 드리프트를 점검한다.

| agent | 사용 시점 |
| --- | --- |
| `experiment-material-collector` | 새 실험 시작, 두 run 비교, Before/After 리포트 작성, 실험 슬라이스 onboarding 전 |
| `harness-structure-reviewer` | 새 policy 추가, runner 리팩토링, 새 input mode 추가, 구조 변경 commit 직전 |
| `result-evidence-checker` | README/report/presentation에 수치 인용 직전, 외부 공유 PR 머지 직전 |
| `failure-classifier` | run 실패 케이스가 생긴 직후, issue 작성·다음 실험 계획 직전 |

## 작업 기준

- 코드와 문서는 작고 검증 가능한 단위로 변경한다.
- 새 의존성이나 외부 서비스가 필요하면 이유와 사용 범위를 명확히 남긴다.
- 민감한 데이터, 개인 인증 정보, 로컬 전용 파일은 커밋하지 않는다.
