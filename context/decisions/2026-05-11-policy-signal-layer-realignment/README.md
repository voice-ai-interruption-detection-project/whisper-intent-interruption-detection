---
date: 2026-05-11
status: exploring
related_pr:
related_runs:
skill_source: record-decision
tags: [policy, llm, mvp, product-flow, context]
---

# Policy Signal Layer Realignment

## 정리

현재 진행할 수 있다는 가정 아래, `LLM action judge` 중심으로 합쳐진 고객 신호 해석과 AI 행동 판단 층을 다시 분리할지 검토한다.

핵심은 LLM 사용 여부가 아니라, LLM을 최종 action judge로 둘지, `Interpreter Pipeline` 안의 보조 판단/fallback/debug 기능으로 둘지 정렬하는 것이다.

아직 코드나 active context를 바꾸는 결정은 아니다. 기존 LLM action judge 구현은 보존하고, 다음 작업 전에 문서/정책/구현 흐름을 덜 꼬이게 하는 기준을 세운다.

## 범위

- 아직 미반영
- `context/internal/`
- `context/decisions/2026-05-09-llm-action-policy-baseline/`
- `src/interruption_detection/policies/`
- `src/interruption_detection/runner.py`
- `src/interruption_detection/audio/`
- `results/runs/{run_id}/` artifact 의미

## 배경

5차 페어에서 Day 2 placeholder가 사람이 붙인 `event_type`을 action으로 매핑하는 구조처럼 보였고, "고객 발화를 보고 신호를 판단하는 주체가 없다"는 문제가 열렸다.

이를 빠르게 해결하기 위해 `baseline`, `policy_v1`부터 LLM이 transcript와 AI context를 보고 `actual_action`을 직접 고르는 경로를 붙였다.

이 선택은 hardcoded mapping 문제를 줄였지만, 이후 current MVP와 active context에서 `LLM action judge`가 제품 기본 판단 구조처럼 굳어지며 고객 신호 해석과 AI 행동 판단이 한 층으로 합쳐진 상태가 되었다.

이번 기록은 그 흐름을 바로 뒤집기 위한 것이 아니라, 다음 작업을 진행할 수 있다는 가정에서 어떤 층위를 다시 나눠야 하는지 남기기 위한 것이다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

현재 작업 메모는 `context/temp/pipeline-layer-realignment-working-context.tmp.md`와 `context/temp/pipeline-layer-realignment-pair-brief.tmp.md`에 있다.

## 결과 / 트레이드오프

- 좋아진 것: LLM을 버릴지 쓸지의 이분법이 아니라, LLM 역할의 층위를 분리해 다음 작업을 논의할 수 있다.
- 좋아진 것: 기존 `LLMActionPolicy`를 즉시 폐기하지 않고 one-shot LLM judge baseline으로 보존할 수 있다.
- 좋아진 것: active context를 바로 고치기 전에 decision과 작업 순서를 먼저 남긴다.
- 나빠진 것: `Interpreter Pipeline`, `Thin Action Policy`, fallback 같은 층을 나누면 구조가 조금 복잡해질 수 있다.
- 감수한 부분: 기존 `LLM Action Policy Baseline` decision은 아직 active로 남아 있으며, supersede 또는 재해석 여부는 후속 논의가 필요하다.

## 후속 점검

- [ ] 페어와 현재 이슈가 "LLM 사용 여부"가 아니라 "LLM 역할 층위" 문제인지 먼저 공유한다.
- [ ] `LLM Action Policy Baseline` decision을 유지, 격하, supersede 중 어떻게 다룰지 정한다.
- [ ] `context/internal/` 수정 대상과 문장 기준을 확정한다.
- [ ] 코드 변경 전 `Interpreter Pipeline` / `Thin Action Policy` / `LLM fallback` 경계를 설계한다.
- [ ] `Interpreter Pipeline`만 만들고 `actual_action` 생성을 뒤로 미뤄 기존 Test Bench 비교 흐름을 끊지 않도록 한다.
- [ ] run artifact에 `signal_source`, `confidence`, `interpreter_steps` 같은 필드를 남길 필요가 있는지 검토한다.
