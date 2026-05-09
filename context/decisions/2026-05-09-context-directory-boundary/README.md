---
date: 2026-05-09
status: active
related_pr:
related_runs:
skill_source: record-decision
tags: [docs, harness, context-boundary]
---

# Context Directory Boundary

## 정리

루트에 있던 `internal/`, `decisions/`, `archive/`, `temp/`를 `context/` 아래로 이동한다.

루트에는 실행 산출물(`src/`, `data/`, `results/`, `tests/`)과 공개 문서(`docs/`)를 두고, 내부 기준·결정·과거 자료·임시 메모는 `context/`로 접는다.

## 범위

- `context/`
- `context/internal/`
- `context/decisions/`
- `context/archive/`
- `context/temp/`
- `CLAUDE.md`
- `.claude/rules/`
- `.claude/agents/`
- `.codex/agents/`
- `.claude/skills/record-decision/`

## 배경

개발이 진행되면 루트에 코드/데이터/결과/공개 문서와 내부 운영 문서가 같은 층위로 나열되어, 무엇이 실행 표면이고 무엇이 작업 맥락인지 헷갈릴 가능성이 커졌다.

`docs/`는 공개 문서라 루트에 두되, 공개 문서가 아닌 내부 기준과 결정 맥락은 한 단계 접어 루트 노이즈를 줄인다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: 루트에서 실행 산출물과 공개 문서가 더 잘 보인다.
- 좋아진 것: AI 작업자가 내부 기준을 찾을 때 `context/internal/`을 우선 보면 된다.
- 나빠진 것: 기존 `internal/`, `decisions/`, `archive/`, `temp/` 링크를 한 번 갱신해야 한다.
- 감수한 부분: archive 내부의 오래된 예시 문서는 historical evidence이므로 일부 과거 경로 표현을 그대로 둘 수 있다.

## 후속 점검

- [ ] 공개 `docs/` 정리 시 새 기준 위치인 `context/internal/`을 기준으로 발췌한다.
- [ ] 새 decision을 남길 때 `context/decisions/` 색인에 추가한다.
