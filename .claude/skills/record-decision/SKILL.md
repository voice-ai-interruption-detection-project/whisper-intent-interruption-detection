---
name: record-decision
description: 이 프로젝트의 context/decisions/에 결정, 고민, AI 대화 맥락을 사안별 폴더로 남긴다. 사용자가 "/record-decision", "결정 기록", "decisions에 추가", "이번 결정 남겨줘", "고민 정리해줘", "AI 대화 맥락 저장"처럼 요청할 때 사용한다.
---

# record-decision

이 skill은 이 프로젝트 안의 결정, 고민, AI 대화 맥락을 `context/decisions/YYYY-MM-DD-{topic}/` 형태로 저장한다.

## 원칙

- 사용자가 명시적으로 저장을 요청했을 때만 파일을 만든다.
- 결과물은 프로젝트 repo 안의 `context/decisions/`에 둔다.
- 결정이 끝나지 않았으면 `status: exploring`으로 남긴다.
- AI 대화 원문이나 긴 근거는 `raw.md`에 두고, 정리된 맥락은 `context.md`에 둔다.
- 개인 로컬 경로, 인증 정보, 비공개 원문은 저장하지 않는다.

## Workflow

1. 주제를 짧은 kebab-case slug로 정한다.
   - 예: `directory-boundary-restructure`, `action-label-rename`
2. 오늘 날짜로 `context/decisions/YYYY-MM-DD-{slug}/` 폴더를 만든다.
3. 아래 세 파일을 만든다.
   - `README.md`: 빠르게 훑는 결정/고민 요약
   - `context.md`: 선택지, 기각한 이유, 토론 흐름
   - `raw.md`: AI 대화 원본, 회의 녹취, 긴 근거 자료
4. `README.md` frontmatter를 채운다. 모르는 값은 빈칸으로 둔다.
5. `context/decisions/README.md` 색인 표에 한 줄을 추가한다.

## README.md Template

```markdown
---
date: 2026-MM-DD
status: active | exploring | superseded-by: 2026-MM-DD-...
related_pr:
related_runs:
skill_source:
tags: []
---

# {title}

## 정리

무엇을 정했나 / 무엇을 고민 중인가를 1-5줄로 적는다.

## 범위

영향받는 자리. 예: `context/internal/`, `.claude/rules/`, `src/`, `data/`, `docs/`, 또는 "아직 미반영".

## 배경

왜 이 사안이 열렸는지 짧게 적는다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것:
- 나빠진 것:
- 감수한 부분:

## 후속 점검

- [ ] 검증하거나 이어서 볼 항목
```

## context.md Template

```markdown
# Context

## 선택지

## 기각한 이유

## 판단이 바뀐 지점

## 연결된 파일
```

## raw.md Template

```markdown
# Raw Material

원문이 없거나 저장하지 않기로 했다면 "저장한 원문 없음"이라고 적는다.
```
