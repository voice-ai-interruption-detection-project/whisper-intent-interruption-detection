---
date: 2026-05-11
status: active
related_pr:
related_runs:
skill_source: record-decision
tags: [policy, llm, mvp, product-flow, context]
---

# Policy Signal Layer Realignment

## 정리

`LLM action judge` 중심으로 합쳐진 고객 신호 해석과 AI 행동 판단 층을 분리해, Text/Audio 입력 뒤에 공통 고객 신호 해석(`Interpreter Pipeline`)과 AI 행동 선택(`AI Action Selector`) 흐름을 둔다.

핵심은 LLM 사용 여부가 아니라, 고객 신호 해석과 `actual_action` 선택의 층위를 나누는 것이다.

기존 LLM action judge 구현은 버리지 않고, 첫 구현에서는 LLM structured output을 공통 runtime 해석 결과와 AI 행동 선택 결과로 나눠 기록한다. `expected_action`, `event_type`, `expected_user_intent`는 계속 기준값으로만 쓰고 runtime action 결정 입력으로 직접 쓰지 않는다.

## 범위

- 구현 반영 진행 중
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

- 좋아진 것: LLM을 버릴지 쓸지의 이분법이 아니라, LLM 역할의 층위를 분리해 구현할 수 있다.
- 좋아진 것: 기존 `LLMActionPolicy`를 즉시 폐기하지 않고 one-shot LLM judge baseline으로 보존할 수 있다.
- 좋아진 것: Text Replay와 Audio File Test가 같은 고객 신호 해석/AI 행동 선택 흐름으로 합류한다.
- 나빠진 것: `Interpreter Pipeline`, `AI Action Selector`, fallback 같은 층을 나누면 구조가 조금 복잡해질 수 있다.
- 감수한 부분: 기존 `LLM Action Policy Baseline` decision은 active로 유지하되, "LLM이 고객 발화를 보고 판단한다"는 결정으로 재해석한다.

## 후속 점검

- [x] 페어와 현재 이슈가 "LLM 사용 여부"가 아니라 "LLM 역할 층위" 문제인지 먼저 공유한다.
- [x] `LLM Action Policy Baseline` decision은 유지하되, 공통 해석/행동 선택 흐름의 선행 결정으로 재해석한다.
- [x] `context/internal/` 수정 대상과 문장 기준을 확정한다.
- [x] `Interpreter Pipeline` / `AI Action Selector` 경계를 구현 전제에 맞게 정한다.
- [x] `Interpreter Pipeline`만 만들고 `actual_action` 생성을 뒤로 미루지 않는다.
- [x] run artifact의 `signals`에 `predicted_event_type`, `predicted_user_intent`, `confidence`, `ambiguity`, `signal_source`, `interpreter_steps`를 남긴다.
