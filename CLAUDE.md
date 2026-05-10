# whisper-intent-interruption-detection 프로젝트 가이드

## 프로젝트 개요

음성 AI 상담에서 고객의 끼어들기와 의도 전환에 더 자연스럽게 반응하는 경험을 실험하고 구현하는 팀 사이드 프로젝트다.

현재 MVP의 초점은 AI가 말하는 중 들어온 고객 발화를 보고 다음 행동을 고르는 판단 구조를 텍스트 입력(Text Replay)과 대표 오디오 파일 입력(Audio File Test) 같은 입력 경로로 검증하는 데 있다. Whisper/STT/audio adapter는 이 판단 구조를 음성 입력 쪽으로 연결하기 위한 구현 요소다.

## 협업 원칙

- 프로젝트 문서에는 개인 컴퓨터 경로, 개인 AI 도구 설정, 로컬 하네스 운영 맥락을 넣지 않는다.
- 팀원이 같은 저장소만 보고 이해하거나 재현할 수 있는 정보만 남긴다.
- 환경 설정, 실행 방법, 데이터 준비 절차가 필요하면 개인 로컬 기준이 아니라 팀 공용 기준으로 문서화한다.
- 실험 결과를 남길 때는 입력 데이터, 모델/설정, 평가 기준, 실행 날짜를 함께 기록한다.

## 작업 라우팅

| 작업                                                                 | 먼저 보는 가드 / 도구                                                                                                |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Playground 코드 변경 (입력 처리, UI, runner 호출)                    | [.claude/rules/coding.md](.claude/rules/coding.md), [.claude/rules/workflow.md](.claude/rules/workflow.md)           |
| 배치 평가(Test Bench) 작업 (판단 케이스/policy 변경, run artifact 생성, 수치 인용) | [.claude/rules/experiments.md](.claude/rules/experiments.md), [.claude/rules/workflow.md](.claude/rules/workflow.md) |
| 내부 기준 자료·용어·정책 초안 정리                                   | [context/internal/](context/internal/), [context/decisions/](context/decisions/), [.claude/rules/workflow.md](.claude/rules/workflow.md) |
| 결정·고민·AI 대화 맥락 기록                                         | `record-decision` skill, [context/decisions/](context/decisions/)                                                    |
| commit / PR / 공유 메모 작성                                         | [.claude/rules/workflow.md](.claude/rules/workflow.md)                                                               |
| 실험 자료 수집·구조 점검·수치 검증·실패 분류                         | 아래 [Repo-local tools](#repo-local-tools) 표                                                                        |

## Workspace Map

루트 `CLAUDE.md`는 협업 경계와 작업 라우팅만 둔다. 본문 가드는 `.claude/rules/`에 두고, 각 작업 영역의 자세한 운영 기준은 해당 폴더 README를 우선한다.

| 영역                 | 역할                          | 기준 / 주의                                                                                         |
| -------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------- |
| `docs/`              | mkdocs로 외부 배포되는 공유/공개 문서 | 공개 문장으로 다듬은 내용만 둔다. 내부 기준과 어긋나면 follow-up에서 정리한다.                     |
| `data/`              | 기준 원본                      | 판단 케이스(`scenario`)와 expected_action만 둔다. actual_action, metric, decision log는 넣지 않는다.              |
| `results/`           | 배치 평가(Test Bench) run artifact | 외부 인용 수치의 출처다. `results/runs/{run_id}/` 계약을 따른다.                                    |
| `context/`           | 내부 기준·결정·archive·임시 메모 | 루트 노이즈를 줄이기 위해 운영 맥락 문서는 이 아래에 둔다. 자세한 역할은 [context/README.md](context/README.md)를 본다. |
| `context/internal/`  | 내부 기준 자료를 맞추는 작업 자료층 | 제품 맥락, 용어 정리, 정책 초안, 평가 기준, 설계 메모를 현재 어휘로 정리한다. 제품 맥락은 `context/internal/product-context.md`에 둔다. |
| `context/decisions/` | 결정·고민·AI 대화 맥락 보관소 | 라벨·정책·평가 기준이 바뀌거나 탐색 중일 때 사안별 폴더로 남긴다.                                  |
| `context/archive/`   | 현재 기준에서 물러난 자료      | history/evidence로만 본다. active 가드와 충돌하면 active 쪽을 우선한다.                            |
| `context/temp/`      | 임시 작업·짧은 공유 자료      | `.tmp.md` suffix를 권장한다. 오래 남으면 `context/internal/`이나 `context/decisions/`로 승격할지 본다. |
| `.claude/rules/`     | active 작업 가드               | coding, experiments, workflow처럼 실제 작업 기준을 작게 나눠 둔다.                                  |
| `.claude/agents/`    | Claude repo-local agents       | report-only 조사·검증 도구의 원천이다.                                                              |
| `.codex/agents/`     | Codex agent bridge             | `.claude/agents/`와 같은 역할이지만 포맷이 달라 자동 symlink가 아니다.                              |
| `.claude/skills/`    | Claude repo-local skills       | 반복 절차를 실행 지향으로 묶는다.                                                                   |
| `.codex/skills/`     | Codex skill bridge             | Codex에서도 안전한 repo-local skill을 연결한다.                                                     |

## Repo-local tools

### Agents

- 모두 report-only다. agent는 조사·검증·분류 결과만 반환하고, 파일 수정은 메인 작업자가 판단한다.
- Claude 원천: `.claude/agents/*.md`, Codex 브릿지: `.codex/agents/*.toml`. 포맷이 달라 자동 symlink가 아니므로 한쪽 수정 후에는 전역 `tooling-map-auditor` agent로 양쪽 drift를 점검한다.
- Codex 브릿지는 `name`, `description`, `developer_instructions`를 기본 필드로 쓰고, `read_only`, `system_prompt`, `tools` 같은 Claude 전용/비지원 필드를 넣지 않는다. report-only 성격은 본문 지시로 남긴다.

| agent                           | 사용 시점                                                                        |
| ------------------------------- | -------------------------------------------------------------------------------- |
| `experiment-material-collector` | 새 실험 시작, 두 run 비교, Before/After 리포트 작성, 실험 슬라이스 onboarding 전 |
| `harness-structure-reviewer`    | 새 policy 추가, runner 리팩토링, 새 입력 경로(input adapter/input_mode) 추가, 구조 변경 commit 직전 |
| `result-evidence-checker`       | README/report/presentation에 수치 인용 직전, 외부 공유 PR 머지 직전              |
| `failure-classifier`            | run 실패 케이스가 생긴 직후, issue 작성·다음 실험 계획 직전                      |
| `decision-record-advisor`       | 라벨·정책·평가 기준, 문서 경계 변경처럼 decisions 기록 여부가 애매할 때 |

### Skills

| skill             | 사용 시점                                                                 |
| ----------------- | ------------------------------------------------------------------------- |
| `record-decision` | 결정·고민·AI 대화 맥락을 `context/decisions/`에 사안별 폴더로 남길 때 사용한다. |

## 운영 흐름

- 새 내부 기준 자료는 `context/internal/`에서 먼저 정리한다.
- 라벨·정책·평가 기준이 바뀌거나 탐색 중이면 `context/decisions/`에 사안별 기록을 남긴다.
- decisions 기록 여부가 애매하면 `decision-record-advisor`로 기록 후보인지 먼저 본다.
- 외부 공유가 필요한 내용만 `docs/`로 발췌한다.
- 현재 기준에서 물러난 자료는 `context/archive/`로 보낸다.
- 앞으로 갖출 개발 하네스 항목은 [.claude/harness-candidates.md](.claude/harness-candidates.md)에 backlog로 둔다. 이 파일은 active rule이나 gate가 아니며, 개발하면서 구체화한다.
- 새 작업 영역이 생기면 `.claude/rules/` 안에서 필요한 만큼 작게 나눈다.
- repo-local skill/agent/rule은 작업 속도나 정확도를 바로 올리면 가볍게 추가한다. hook/scanner 같은 자동 체크는 작업 흐름에 영향을 줄 수 있으니 목적과 적용 범위만 짧게 남긴다.
- 새 규칙은 작업 보조 문장이다 — 읽는 사람이 다음 행동을 덜 헷갈리게 하면 충분하다.

## 작업 기준

- 코드와 문서는 작고 검증 가능한 단위로 변경한다.
- 새 의존성이나 외부 서비스가 필요하면 이유와 사용 범위를 명확히 남긴다.
- 민감한 데이터, 개인 인증 정보, 로컬 전용 파일은 커밋하지 않는다.
