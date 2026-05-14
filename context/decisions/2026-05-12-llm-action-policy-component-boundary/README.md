---
date: 2026-05-12
status: active
related_pr:
related_runs:
skill_source: record-decision
tags: [policy, llm, pipeline, component-boundary, mvp]
---

# LLM Action Policy Component Boundary

## 정리

`LLMActionPolicy`는 빠르게 전체 action 판단 흐름을 검증하기 위한 발판이었다.

2026-05-09의 "baseline부터 LLM이 판단한다"는 결정은 `LLMActionPolicy` 단일 클래스 구조를 계속 유지한다는 뜻이 아니라, baseline부터 고객 transcript를 보고 판단하는 LLM-backed 판단 주체가 필요하다는 뜻으로 재해석한다.

다음 코드 작업은 `DecisionPipeline`, `Interpreter Pipeline`, `AI Action Selector` 같은 component boundary를 실제 구현 경계로 세우는 방향으로 진행한다.

## 범위

- `context/decisions/2026-05-09-llm-action-policy-baseline/`은 history로 보존
- `context/decisions/2026-05-11-policy-signal-layer-realignment/`의 후속 결정
- `src/interruption_detection/policies/`
- `src/interruption_detection/runner.py`
- `src/interruption_detection/audio/`
- 이후 코드 작업 후 갱신할 `context/internal/`

## 배경

초기 LLM action judge 전환은 `event_type -> actual_action` 하드코딩 placeholder를 벗어나고, runner/UI/evaluator/Test Bench가 실제 action 판단 결과를 끝까지 흘릴 수 있는지 빠르게 확인하기 위한 선택이었다.

하지만 이후 `LLMActionPolicy` 안에 고객 신호 해석, action 선택, prompt version, signals, latency, migration alias가 계속 쌓이면서, 개선 작업이 공통 pipeline으로 나아가기보다 단일 클래스 내부 확장으로 빨려 들어가는 우려가 생겼다.

이 사안은 LLM 사용 여부가 아니라, LLM의 역할과 코드 경계를 어디에 둘지에 대한 결정이다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: 5/9 결정을 뒤집지 않고도 `LLMActionPolicy`가 계속 커지는 흐름을 끊을 수 있다.
- 좋아진 것: Text/Audio 입력을 같은 decision pipeline으로 합류시키는 다음 구현 방향이 선명해진다.
- 좋아진 것: `Interpreter Pipeline`과 `AI Action Selector`를 실제 component로 분리할 근거가 생긴다.
- 나빠진 것: 단일 `LLMActionPolicy`보다 파일과 타입이 늘어날 수 있다.
- 감수한 부분: one-shot LLM structured output은 당장 폐기하지 않고, 필요하면 legacy baseline 또는 component 내부 구현으로 낮춰 둔다.

## 후속 점검

- [ ] 코드 리팩토링 후 `context/internal/` 문서를 실제 구현 기준으로 갱신한다.
- [ ] `LLMActionPolicy`에 새 판단 로직이 계속 쌓이지 않는지 확인한다.
- [ ] Text/Audio가 같은 `DecisionPipeline` 또는 동등한 root pipeline으로 합류하는지 확인한다.
- [ ] `baseline`과 `policy_v1`이 서로 다른 pipeline이 아니라 같은 component boundary 위의 비교 단위로 유지되는지 확인한다.
