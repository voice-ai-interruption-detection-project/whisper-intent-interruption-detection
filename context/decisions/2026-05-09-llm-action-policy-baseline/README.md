---
date: 2026-05-09
status: active
related_pr:
related_runs:
skill_source:
tags: [policy, llm, mvp]
---

# LLM Action Policy Baseline

## 정리

Day 2의 `baseline`, `policy_v1`은 runner/UI/evaluator 하네스를 확인하기 위한 하드코딩 placeholder로 본다. MVP의 실제 action 판단은 baseline부터 텍스트 transcript를 입력으로 받는 LLM action judge가 맡는다.

## 범위

`src/interruption_detection/llm.py`, `src/interruption_detection/policies/`, `src/backend/static/`, `context/internal/mvp/`, `README.md`

## 배경

프로젝트 목표는 시나리오의 `event_type`을 action으로 강제 매핑하는 것이 아니라, AI가 말하는 중 들어온 고객 transcript를 보고 AI Action Policy가 자연스러운 `actual_action`을 판단하는 것이다.

## 상세 맥락

자세한 토론과 대안은 `context.md`, 원문과 긴 근거는 `raw.md`에 둔다.

## 결과 / 트레이드오프

- 좋아진 것: Playground와 Test Bench가 실제 LLM 판단 경로를 검증할 수 있다.
- 나빠진 것: 실제 run은 `OPENAI_API_KEY`와 모델 호출 비용/지연 시간에 의존한다.
- 감수한 부분: 오디오는 이번 단계에서 제외하고 텍스트 transcript 기준으로 먼저 닫는다.

## 후속 점검

- [ ] 실제 OpenAI API key로 `baseline`, `policy_v1` run artifact를 새로 생성한다.
- [ ] LLM prompt에 `event_type`, `expected_action`, `expected_user_intent`가 들어가지 않는지 계속 테스트한다.
