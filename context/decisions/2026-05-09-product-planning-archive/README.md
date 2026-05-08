---
date: 2026-05-09
status: active
related_pr:
related_runs:
skill_source: record-decision
tags: [docs, source-of-truth, archive, product-context]
---

# Product Planning Archive Boundary

## 정리

초기 `기획/` 원문을 `context/archive/product-planning/`으로 이동하고, 현재 제품 방향의 active 기준은 `context/internal/product-context.md`로 둔다.

용어 층위와 enum 기준은 `context/internal/project-language-map.md`와 `context/internal/reference/`를 우선한다. archive 문서는 더 자세해 보여도 history/evidence로만 본다.

## 범위

- `context/archive/product-planning/`
- `context/internal/product-context.md`
- `context/internal/project-language-map.md`
- `context/internal/reference/`
- `src/backend/PACKAGES.md`
- `context/archive/README.md`

## 배경

초기 PRD, 계획서, 방향성 문서는 MVP 방향을 빠르게 합의하는 데 유용했지만, 이후 `pause`/`respond_and_continue`, flat result tree, 목표 수치, scenario 단위 설명처럼 현재 기준과 어긋나는 표현이 함께 남았다.

페어 중에도 `scenario`, `input_mode`, `event_type`, action label, evaluation 층위가 섞일 때 이해가 어려워지는 문제가 반복됐다. 그래서 원문은 보존하되, active 작업 기준은 현재 어휘로 다시 정리한 `context/internal/` 문서로 분리한다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: AI 작업자와 팀원이 현재 제품 기준을 `context/internal/product-context.md`에서 바로 찾을 수 있다.
- 좋아진 것: 초반 기획 원문을 잃지 않으면서도 active 기준과 archive evidence의 역할이 분리된다.
- 나빠진 것: 예전 링크를 따라가던 사람은 archive 위치를 한 번 더 확인해야 한다.
- 감수한 부분: archive 원문 안의 낡은 표현은 고치지 않고, README에서 읽는 경계를 명시한다.

## 후속 점검

- [ ] 공개 `docs/` 본문을 정리할 때 `context/internal/product-context.md`와 `context/internal/project-language-map.md` 기준으로 발췌한다.
- [ ] archive 원문을 직접 인용해야 할 때는 history/evidence임을 명시한다.
