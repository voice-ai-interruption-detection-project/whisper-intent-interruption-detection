---
date: 2026-05-11
status: active
related_pr: docs/context-intent-alignment
related_runs:
skill_source: record-decision
tags: [docs, product-context, terminology, harness, ai-collaboration]
---

# Context Intent Alignment

## 정리

`context/internal/` 문서가 제품 의도보다 하네스 용어와 방어적 가드를 앞세우는 문제를 줄이기 위해, 제품 의도와 테스트/개발 편의 구조의 층위를 다시 맞춘다.

핵심 기준은 "삭제"가 아니라 "층위 낮추기"다. `input_mode`, Text Replay, Audio File Test, Test Bench, Playground 같은 용어는 필요한 자리에 남기되, 제품의 본질적 개념처럼 앞세우지 않는다.

## 범위

- `CLAUDE.md`, `README.md`
- `context/README.md`
- `context/internal/product-context.md`
- `context/internal/project-language-map.md`
- `context/internal/mvp/`
- `context/internal/reference/`
- `context/internal/scenario-worked-example.md`
- `.claude/rules/`, `.claude/agents/`
- `.codex/agents/`
- 일부 코드 주석과 docstring

`docs/` 공개 문서는 이번 정리 범위에서 제외했다.

## 배경

원래 프로젝트 의도는 음성 AI 상담 서비스 전체를 완성하는 것이 아니라, AI가 말하는 중 고객이 끼어들거나 의도를 바꾸는 순간에 AI가 다음 행동을 어떻게 고를지 검증하는 사이드 프로젝트였다.

문서 정비 과정에서 이 의도는 어느 정도 보존됐지만, `scenario`, `input_mode`, Text Replay, AI Action Policy, Test Bench 같은 하네스 용어가 앞쪽으로 올라오며 "제품 문제"보다 "평가 장치"가 프로젝트의 본체처럼 보이는 왜곡이 생겼다.

또한 과거 AI 작업자가 rule/embedding 기반 해석으로 기운 일을 막기 위해 넣은 강한 부정문과 negative-list가 매 세션 AI 해석을 지나치게 좁히는 부작용을 만들었다.

## 상세 맥락

자세한 토론 흐름, 선택지, 커밋 대조는 `context.md`를 본다.

사용자가 제공한 대화 원문은 `raw.md`에 발췌 형태로 보존한다. 개인 로컬 경로와 긴 원문 전체는 저장하지 않고, decision을 재검토하는 데 필요한 주장과 작업 로그만 남긴다.

## 결과 / 트레이드오프

- 좋아진 것: `product-context`가 세션 시작 때 제품 의도를 짧게 회복하는 문서로 바뀌었다.
- 좋아진 것: 입력 방식은 제품 개념이 아니라 "입력 경로 / input adapter" 층위로 낮아졌다.
- 좋아진 것: 문서 감사나 원래 의도 복원 작업에서는 `internal`도 검토 대상이 될 수 있다는 예외가 생겼다.
- 좋아진 것: `Workbench`는 제품 컨셉으로 앞세우지 않고, `Playground`와 배치 평가(Test Bench)를 실제 표면 이름으로 구분한다.
- 나빠진 것: 일부 문서에서 한국어 설명과 코드 식별자가 병기되어 문장이 조금 길어졌다.
- 감수한 부분: `input_mode`, `expected_action`, `actual_action` 같은 필드명은 코드/API/run artifact 계약이므로 rename하지 않는다.

## 후속 점검

- [ ] UI 화면 워딩도 같은 기준을 따른다. 첫 노출은 쉽게 쓰되, 코드/API 계약이나 실험 표면명은 필요할 때 병기한다.
- [ ] 공개 `docs/`를 정리할 때는 이번 decision을 기준으로 삼되, 외부 독자용 문장으로 다시 다듬는다.
- [ ] action label 축소, event type 축소, `expected_action`/`actual_action` rename 같은 schema 변경은 별도 decision 없이는 적용하지 않는다.
