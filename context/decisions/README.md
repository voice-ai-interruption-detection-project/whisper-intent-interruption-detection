# context/decisions

결정, 고민, AI 대화 맥락을 사안별로 보관하는 영역이다.

라벨, 정책, 평가 기준, 문서 기준 흐름처럼 나중에 "왜 이렇게 됐지?"를 다시 확인해야 하는 내용을 남긴다. 결정이 끝난 것뿐 아니라 아직 탐색 중인 사안도 `status: exploring`으로 남길 수 있다.

## 형식

기본 단위는 폴더다.

```text
context/decisions/YYYY-MM-DD-{kebab-topic}/
├── README.md
├── context.md
└── raw.md
```

- `README.md`: 결정/고민 요약, 상태, 범위, 결과/트레이드오프, 후속 점검
- `context.md`: 선택지, 기각한 이유, 토론 흐름, 판단이 바뀐 지점
- `raw.md`: AI 대화 원본, 회의 녹취, 긴 근거 자료

## README.md 기본 골격

```markdown
---
date: 2026-MM-DD
status: active | exploring | superseded-by: 2026-MM-DD-...
related_pr:
related_runs:
skill_source:
tags: []
---

## 정리

## 범위

## 배경

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

## 후속 점검
```

## 색인

| 날짜 | 제목 | status | 관련 PR / run |
| --- | --- | --- | --- |
| 2026-05-09 | LLM Action Policy Baseline | active |  |
| 2026-05-09 | Context Directory Boundary | active |  |
| 2026-05-09 | Product Planning Archive Boundary | active |  |
| 2026-05-11 | Context Intent Alignment | active | docs/context-intent-alignment |
| 2026-05-11 | UI Wording Layer Balance | active | docs/context-intent-alignment |
| 2026-05-11 | Policy Signal Layer Realignment | exploring |  |
| 2026-05-12 | LLM Action Policy Component Boundary | active |  |
| 2026-05-15 | Policy v3 Scope | active |  |

## 다른 기록과의 경계

여기는 이 프로젝트 안의 결정과 맥락을 보관한다. 여러 프로젝트를 가로지르는 얇은 재진입 기록은 전역 session bridge 성격의 기록으로 다룬다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
