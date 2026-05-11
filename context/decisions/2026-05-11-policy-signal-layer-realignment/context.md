# Context

## 선택지

### 1. 현재 `LLMActionPolicy` 중심 흐름을 그대로 유지한다

```text
RunnerInput
-> LLM action judge
-> actual_action
```

장점은 구현이 단순하고 Text Replay, Audio File Test, Playground/Test Bench가 이미 같은 runner 경로를 탄다는 점이다.

단점은 고객 신호 해석과 AI 행동 판단이 한 번에 합쳐져, 실제 제품 흐름이나 Mic Trial 확장 때 어떤 판단이 어디서 일어났는지 설명하기 어렵다는 점이다.

### 2. 초기 P0/P1/P2/P3 단계형 rule 정책으로 되돌린다

```text
VAD-only
-> Backchannel Rule
-> Intent Shift
-> Full Action Policy
```

장점은 초기 기획의 단계별 signal 비교와 잘 맞는다.

단점은 5차 페어에서 발견한 "그 event_type을 누가 판단했는가" 문제가 다시 열릴 수 있다. 사람이 붙인 annotation을 그대로 쓰면 hardcoded mapping처럼 보일 수 있다.

### 3. 현재 LLM action judge를 보존하되 signal/action 층을 분리한다

```text
transcript / speech signal
-> Signal Analyzer
-> Action Policy
-> actual_action
```

LLM은 one-shot action judge baseline, signal interpreter, ambiguous fallback, evaluator/debugger 중 하나 이상의 역할을 맡을 수 있다.

현재 가장 유력한 회복 후보로 본다.

### 4. Hybrid policy를 실험한다

```text
clear case
-> rule / threshold

ambiguous case
-> LLM fallback

risky case
-> safety guard / handoff
```

장점은 제품 감각과 디버깅 가능성의 균형이 좋다.

단점은 threshold, confidence, signal conflict, fallback 조건을 별도로 설계해야 한다.

## 기각한 이유

아직 최종 기각은 없다.

다만 현재 판단은 아래에 가깝다.

- 현재 direct LLM action judge만 유지하면 빠르지만 제품 흐름 설명력이 약하다.
- 초기 rule mapping만으로 돌아가면 5차에서 발견한 hardcoding 우려가 되살아난다.
- 따라서 기존 LLM 구현을 보존하면서, 고객 신호 해석과 AI 행동 판단을 다시 나누는 방향을 먼저 검토한다.

## 판단이 바뀐 지점

처음에는 "baseline부터 LLM이 개입해야 한다"는 말이 `baseline`, `policy_v1` 모두 LLM이 최종 `actual_action`을 직접 판단해야 한다는 의미로 굳어졌다.

이번 재검토에서는 그 말을 다르게 해석한다.

```text
기존 해석:
baseline부터 LLM action judge가 최종 action label을 고른다.

재해석:
baseline부터 고객 발화를 보고 판단하는 주체가 필요하다.
그 주체는 direct LLM action judge일 수도 있지만,
Signal Analyzer, classifier, rule/threshold, LLM fallback, hybrid 구조일 수도 있다.
```

즉, 문제는 LLM을 붙였다는 점이 아니라 LLM이 고객 신호 해석과 AI 행동 판단을 한 번에 맡게 된 점이다.

## 연결된 파일

- `context/temp/analysis-notes/pipeline-layer-realignment-working-context.tmp.md`
- `context/temp/pair-briefs/pipeline-layer-realignment-pair-brief.tmp.md`
- `context/decisions/2026-05-09-llm-action-policy-baseline/README.md`
- `context/internal/product-context.md`
- `context/internal/mvp/current.md`
- `context/internal/mvp/current-iteration-plan.md`
- `context/internal/project-language-map.md`
- `context/internal/scenario-worked-example.md`
- `src/interruption_detection/policies/llm_action.py`
- `src/interruption_detection/policies/baseline.py`
- `src/interruption_detection/policies/policy_v1.py`
- `src/interruption_detection/runner.py`
- `src/interruption_detection/audio/adapter.py`
