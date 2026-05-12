# Context

## 선택지

### 1. `LLMActionPolicy` 중심 구조를 계속 확장한다

현재 구조를 유지하면서 `LLMActionPolicy` 안에 고객 신호 해석, action 선택, fallback, audio signal 처리, policy version 차이를 계속 추가한다.

장점은 파일 이동이 적고 당장 구현이 단순하다는 점이다.

단점은 빠른 검증용으로 만든 구조가 제품 판단 흐름의 중심이 되어, `Interpreter Pipeline`과 `AI Action Selector`가 이름만 분리되고 실제 component boundary로는 서지 못한다는 점이다.

### 2. 기존 LLM action judge를 폐기하고 새 pipeline으로 즉시 재작성한다

`LLMActionPolicy`를 버리고 `DecisionPipeline`, `Interpreter`, `AI Action Selector`를 새로 구현한다.

장점은 새 구조로 빠르게 정렬된다는 점이다.

단점은 기존 runner/evaluator/UI/audio 합류 검증 결과를 한 번에 흔들 수 있고, one-shot LLM structured output으로 이미 확보한 빠른 판단 경로를 불필요하게 폐기할 수 있다는 점이다.

### 3. `LLMActionPolicy`를 발판으로 보존하되 component boundary로 탈출한다

`LLMActionPolicy`는 빠른 action flow 검증용 발판 또는 legacy one-shot 경로로 낮추고, 다음 구현은 `DecisionPipeline`, `Interpreter Pipeline`, `AI Action Selector` 경계를 실제 코드 구조로 분리한다.

이 방향을 채택한다.

## 기각한 이유

`LLMActionPolicy` 중심 구조를 계속 확장하는 방식은 기존 작업을 이어가기 쉬워 보이지만, 새 개선이 계속 같은 클래스 안에 누적되는 문제가 있다. 그러면 `predicted_event_type`과 `actual_action`이 분리된 것처럼 보이더라도 실제 action 선택은 여전히 direct LLM judgment에 묶인다.

반대로 기존 LLM action judge를 즉시 폐기하는 방식은 2026-05-09 decision의 핵심을 과하게 뒤집는다. 당시 결정은 사람이 붙인 `event_type`을 실행 로직처럼 쓰지 않고, baseline부터 고객 transcript를 보고 판단하는 주체를 둬야 한다는 문제를 해결한 것이었다.

따라서 기존 결정을 history로 보존하면서, 그 의미를 "LLMActionPolicy 단일 구조 유지"가 아니라 "baseline부터 LLM-backed 판단 주체 필요"로 재해석한다.

## 판단이 바뀐 지점

처음에는 "baseline부터 LLM이 판단한다"는 말이 `baseline`, `policy_v1` 모두 LLM이 최종 `actual_action`을 직접 고르는 구조로 굳어졌다.

이후 pipeline layer 작업을 보면서 문제는 LLM 사용 여부가 아니라, 고객 신호 해석과 AI 행동 선택이 `LLMActionPolicy` 한 층으로 합쳐져 있다는 점으로 정리됐다.

이번 결정에서 확인한 재해석은 아래와 같다.

```text
기존처럼 오해될 수 있는 해석:
baseline부터 LLM action judge
-> LLMActionPolicy가 계속 최종 판단 본체여야 한다

현재 채택한 해석:
baseline부터 LLM-backed 판단 주체가 필요하다
-> 그 주체는 Interpreter / AI Action Selector component로 나뉠 수 있다
```

이 재해석은 2026-05-09 결정을 폐기하지 않고, 2026-05-11 policy signal layer realignment의 후속 구현 방향을 더 선명하게 한다.

## 연결된 파일

- `context/decisions/2026-05-09-llm-action-policy-baseline/`
- `context/decisions/2026-05-11-policy-signal-layer-realignment/`
- `src/interruption_detection/policies/llm_action.py`
- `src/interruption_detection/runner.py`
- `src/interruption_detection/audio/adapter.py`
- `context/internal/`은 코드 리팩토링 후 갱신한다.
