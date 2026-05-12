# Raw Material

이번 기록은 대화 원문 전체를 저장하지 않고, 결정에 직접 필요한 핵심 발화와 상황 맥락을 남긴다.

## 대화가 열린 상황

사용자는 현재 `refactor/pipeline-layer` 계열 작업을 보면서, 최근 브랜치 작업이 계속 "파이프라인을 개선해 나가는" 느낌보다 특정 구현체 안에서 보수적으로 누적되는 느낌이 든다고 했다.

처음 요청은 현재 브랜치 작업 현황을 보고, `Audio File Test` 적용 선에서 `pilab-2026-feb-sprint-4-optimization` 레포처럼 pipeline 구성요소를 고려해 더 적극적으로 개발할 수 있는지 분석해 달라는 것이었다.

이 과정에서 확인한 현재 구현은 아래에 가까웠다.

```text
Text/Audio input
-> RunnerInput
-> LLMActionPolicy.predict()
   -> LLM structured output 한 번 호출
   -> predicted_event_type / predicted_user_intent / actual_action을 함께 받음
   -> signals에 고객 신호 해석 점검값을 기록
-> PolicyDecision
```

즉 문서와 signals에는 `Interpreter Pipeline`, `AI Action Selector`라는 층위가 생겼지만, 실제 코드 경계는 여전히 `LLMActionPolicy` 한 클래스 안에 남아 있었다.

비교 대상으로 본 `pilab` 레포는 route / pipeline / util 3층을 두고, `run_ingest`, `run_qa`, `_trace_transcribe`, `_trace_vision`, `_trace_embed`, `run_retrieve`처럼 흐름과 구성요소 경계를 코드 구조로 드러내고 있었다. 사용자가 원하는 방향은 이처럼 다음 구현 단위가 보이는 pipeline component 경계에 가까웠다.

## 핵심 사용자 문제 제기

사용자는 다음 취지로 문제를 제기했다.

```text
지금 작업들이 계속 개선해나가는 느낌이 아니라
기존에 LLMActionPolicy 여기서 벗어나지 못하고 계속 커지는 것 같아.
```

이어 사용자는 처음 의도를 아래처럼 설명했다.

```text
처음에 원래 의도는 빠른 개발을 위해 전체 action 흐름만 검증하고
계속 진행될 거라 생각했는데,
전체 action LLMAction이 구현되고 거기서 못 벗어나고
오히려 작업이 비효율적인 것 같은데 우려가 맞아?
```

이 문제 제기는 단순한 파일명 취향이 아니라, 빠른 검증용 구현이 다음 구조를 여는 발판이 되지 못하고 중심 구조로 굳어지는 것에 대한 우려였다.

정리하면 사용자가 걱정한 것은 아래 흐름이다.

```text
원래 의도:
빠른 LLM action judge로 runner / evaluator / UI / audio 합류를 검증한다
-> 이후 interpreter / selector / audio pipeline으로 분화한다

현재 위험:
LLMActionPolicy 안에 interpreter 흉내, selector 흉내, prompt version,
signals, latency, migration alias가 계속 쌓인다
-> pipeline이라고 부르지만 교체 가능한 component는 없다
```

## 대화 중 정리된 재해석

기존 2026-05-09 결정의 요지는 "baseline부터 LLM이 고객 transcript를 보고 판단해야 한다"는 것이었다.

당시 이 결정은 필요했다. Day 2의 하드코딩 placeholder는 runner, evaluator, UI, Test Bench 흐름을 빠르게 확인하는 데는 유효했지만, 사람이 붙인 `event_type`을 runtime 판단처럼 써서 `actual_action`으로 매핑하는 문제가 있었다. 그래서 baseline부터 LLM이 고객 transcript를 보고 action을 판단하게 하는 방향이 열렸다.

이번 대화에서는 그 결정을 아래처럼 다시 읽었다.

```text
오해될 수 있는 해석:
"baseline부터 LLM action judge"
= LLMActionPolicy가 계속 최종 판단 본체여야 한다

채택한 해석:
"baseline부터 LLM action judge"
= 사람이 붙인 event_type을 베끼지 말고,
  고객 발화를 보고 판단하는 주체가 baseline부터 있어야 한다
```

이 결정은 `LLMActionPolicy` 단일 클래스 구조를 계속 유지하라는 뜻이 아니라, 사람이 붙인 `event_type`을 베끼지 않고 고객 발화를 보고 판단하는 LLM-backed 판단 주체가 baseline부터 있어야 한다는 뜻으로 재해석한다.

따라서 LLM 사용은 유지할 수 있지만, `LLMActionPolicy` 한 클래스가 고객 신호 해석, action 선택, signals, latency, migration alias를 계속 떠안는 구조는 다음 작업의 기준으로 삼지 않는다.

새 기준에서 LLM은 아래 중 하나로 남을 수 있다.

- one-shot 판단을 제공하는 legacy baseline
- `Interpreter Pipeline` 내부 구현
- ambiguous case fallback/helper
- `AI Action Selector` 내부 구현

핵심은 LLM을 버리는 것이 아니라, LLM의 역할을 component boundary 안에 넣는 것이다.

## 사용자 확인

사용자는 이 재해석에 대해 아래처럼 확인했다.

```text
이 재해석이 맞아
```

또한 기존 decision은 history로 남기고, 새로운 decision에 이 재해석을 남긴 뒤 `context/internal/` 문서는 코드 작업 후에 갱신하는 편이 낫다고 결정했다.

```text
기존에는 히스토리로 남기고 새로운 decisions에 남겨놔줘
```

```text
일단 decisions에는 남겨주고 context 문서는 코드 작업후에 작업하는게 나을 것 같아
```

따라서 이 decision은 기존 2026-05-09 decision을 수정하거나 폐기하지 않는다. 기존 기록은 당시의 빠른 구현 판단으로 보존하고, 이 문서가 그 결정을 현재 pipeline component 방향으로 재해석한 후속 기록이 된다.

## 다음 구현 방향 요약

```text
Text / Audio input
-> DecisionPipeline
-> Interpreter Pipeline
-> AI Action Selector
-> PolicyDecision / actual_action / signals
```

one-shot LLM structured output은 당장 폐기하지 않는다. 다만 필요하면 legacy baseline 또는 component 내부 구현으로 낮춰 두고, 새 판단 로직이 `LLMActionPolicy`에 계속 쌓이지 않도록 한다.

다음 코드 작업에서 중요한 기준은 아래다.

- `LLMActionPolicy`에 새 판단 로직을 계속 추가하지 않는다.
- `baseline`, `policy_v1`은 서로 다른 pipeline이 아니라 같은 pipeline component boundary 위의 비교 단위로 둔다.
- Text input과 Audio File input은 같은 root decision pipeline으로 합류한다.
- `predicted_event_type`, `predicted_user_intent`는 계속 runtime 해석 점검값으로 남기되, `actual_action` 생성과 기존 `expected_action` 비교는 유지한다.
- `context/internal/` active 문서는 코드 리팩토링 후 실제 구현 기준에 맞춰 갱신한다.
