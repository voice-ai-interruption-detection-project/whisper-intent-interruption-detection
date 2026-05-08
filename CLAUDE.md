# whisper-intent-interruption-detection 프로젝트 가이드

## 프로젝트 개요

Whisper 기반 intent/interruption detection 실험과 구현을 위한 팀 사이드 프로젝트다.

## 협업 원칙

- 프로젝트 문서에는 개인 컴퓨터 경로, 개인 AI 도구 설정, 로컬 하네스 운영 맥락을 넣지 않는다.
- 팀원이 같은 저장소만 보고 이해하거나 재현할 수 있는 정보만 남긴다.
- 환경 설정, 실행 방법, 데이터 준비 절차가 필요하면 개인 로컬 기준이 아니라 팀 공용 기준으로 문서화한다.
- 실험 결과를 남길 때는 입력 데이터, 모델/설정, 평가 기준, 실행 날짜를 함께 기록한다.

## 작업 라우팅

| 작업                                                                 | 먼저 보는 가드                                                                                                       |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Playground 코드 변경 (입력 처리, UI, runner 호출)                    | [.claude/rules/coding.md](.claude/rules/coding.md), [.claude/rules/workflow.md](.claude/rules/workflow.md)           |
| Test Bench 작업 (scenario/policy 변경, run artifact 생성, 수치 인용) | [.claude/rules/experiments.md](.claude/rules/experiments.md), [.claude/rules/workflow.md](.claude/rules/workflow.md) |
| commit / PR / 공유 메모 작성                                         | [.claude/rules/workflow.md](.claude/rules/workflow.md)                                                               |
| 실험 자료 수집·구조 점검·수치 검증·실패 분류                         | 아래 [Repo-local agents](#repo-local-agents) 표                                                                      |

## Repo-local agents

- 모두 report-only다. agent는 조사·검증·분류 결과만 반환하고, 파일 수정은 메인 작업자가 판단한다.
- Claude 원천: `.claude/agents/*.md`, Codex 브릿지: `.codex/agents/*.toml`. 포맷이 달라 자동 symlink가 아니므로 한쪽 수정 후에는 전역 `tooling-map-auditor` agent로 양쪽 drift를 점검한다.

| agent                           | 사용 시점                                                                        |
| ------------------------------- | -------------------------------------------------------------------------------- |
| `experiment-material-collector` | 새 실험 시작, 두 run 비교, Before/After 리포트 작성, 실험 슬라이스 onboarding 전 |
| `harness-structure-reviewer`    | 새 policy 추가, runner 리팩토링, 새 input mode 추가, 구조 변경 commit 직전       |
| `result-evidence-checker`       | README/report/presentation에 수치 인용 직전, 외부 공유 PR 머지 직전              |
| `failure-classifier`            | run 실패 케이스가 생긴 직후, issue 작성·다음 실험 계획 직전                      |

## 문서 / 하네스 운영 메타

- 루트는 협업 경계와 작업 라우팅만 둔다. 본문 가드는 `.claude/rules/`에 있다.
- `docs/`는 공유/공개 문서 영역이다.
- `docs/archive/`는 과거 조사·설계 후보를 보관하는 영역이다. AI 작업자는 사용자가 명시적으로 요청한 경우를 제외하고 archive 문서를 작업 가드, 인용 출처, 구현 근거로 직접 참조하거나 활용하지 않는다.
- 앞으로 갖출 개발 하네스 항목은 [.claude/harness-candidates.md](.claude/harness-candidates.md)에 backlog로 둔다. 이 파일은 active rule이나 gate가 아니며, 개발하면서 구체화한다.
- 새 작업 영역이 생기면 `.claude/rules/` 안에서 필요한 만큼 작게 나눈다.
- repo-local skill/agent/rule은 작업 속도나 정확도를 바로 올리면 가볍게 추가한다. hook/scanner 같은 자동 체크는 작업 흐름에 영향을 줄 수 있으니 목적과 적용 범위만 짧게 남긴다.
- 새 규칙은 작업 보조 문장이다 — 읽는 사람이 다음 행동을 덜 헷갈리게 하면 충분하다.

## 작업 기준

- 코드와 문서는 작고 검증 가능한 단위로 변경한다.
- 새 의존성이나 외부 서비스가 필요하면 이유와 사용 범위를 명확히 남긴다.
- 민감한 데이터, 개인 인증 정보, 로컬 전용 파일은 커밋하지 않는다.
