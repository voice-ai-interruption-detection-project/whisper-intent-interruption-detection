# Pipeline Layer Realignment Working Context

> 상태: 임시 작업 문서.
> 목적: 다음 AI 세션이나 페어 작업에서 현재 문제의식, 근거, 작업 순서를 바로 이어받게 한다.
> 주의: 이 문서는 active decision이 아니다. 수정 전 계획을 세우기 위한 재진입 문서다.

## 핵심 결론

현재 문제는 LLM을 썼다는 점이 아니다.

문제는 원래 나눠 보려던 두 층이 현재 구현과 active context에서 `LLM action judge` 한 층으로 합쳐져 있다는 점이다.

```text
고객 신호 해석
-> 이 발화가 backchannel인지, same_intent_question인지, intent_shift인지, ambiguous인지 판단

AI 행동 판단
-> 해석된 신호를 바탕으로 continue, brief_ack, respond_and_continue, stop_and_switch 등을 선택
```

현재 구현은 이 두 질문을 LLM이 한 번에 처리한다.

```text
RunnerInput
-> LLM action judge
-> actual_action
```

이 흐름은 5차 페어에서 발견한 hardcoded label mapping 문제를 빠르게 푸는 데는 유효했다.

다만 Mic Trial, audio signal, 실제 제품 흐름으로 확장하려면 고객 신호 해석 결과와 AI 행동 판단 결과를 다시 나눠 기록하는 편이 더 설명 가능하다.

최근 논의에서 추가로 정리한 보정은 아래다.

- 너무 잘게 나누지 않는다. `Interpreter Pipeline`만 만들고 `actual_action`을 뒤로 미루면 기존 Test Bench의 핵심인 expected/actual 비교가 끊긴다.
- 개념적으로는 고객 신호 해석과 AI 행동 판단을 나누되, 첫 실험에서는 `Interpreter Pipeline + Thin Action Policy`를 한 파이프라인으로 같이 굴린다.
- LLM은 버릴 대상이 아니라, 현재는 direct action judge baseline이고, 다음 구조에서는 interpreter 내부 구현 또는 fallback/helper로 붙을 수 있다.

## 원래 의도한 판단 흐름

```text
고객 장면
-> 판단 케이스(scenario)              # scenario_id, domain, level, notes
-> 입력 경로(Text / Audio File / Mic) # input_mode, audio_path, transcript_source
-> transcript / speech signal 구성    # user_utterance 또는 transcript.text, has_user_speech, audio.signal
-> 고객 신호 해석                     # event_type, expected_user_intent
                                      # runtime 후보: predicted_event_type, predicted_user_intent, confidence
-> AI 행동 판단(AI Action Policy)      # ai_current_intent, ai_utterance, transcript, signal을 보고 판단
-> actual_action 생성                 # actual_action, reason, signals
-> expected_action과 비교             # expected_action vs actual_action
-> failure 분석 / run artifact 기록   # primary_failure, decision_logs.jsonl, evaluation.json
```

이 구조에서 `scenario`는 전체 상담 플로우가 아니라 판단 케이스 카드다.

`expected_action`, `event_type`, `expected_user_intent`는 사람이 붙인 기준 annotation이다.

`actual_action`, `reason`, `signals`, `primary_failure`는 policy 실행 후 결과 artifact에 남는 값이다.

## 5차 전 placeholder 흐름

```text
판단 케이스(scenario)
-> 사람이 붙인 event_type
-> rule mapping
-> actual_action
-> expected_action과 비교
```

이 단계의 가치는 있었다.

- loader, schema, runner, evaluator, API, UI, Test Bench를 연결했다.
- `expected_action`과 `actual_action`을 비교하는 run artifact 계약을 만들었다.
- policy별 결과를 눈으로 확인하는 Playground/Test Bench surface가 생겼다.

하지만 고객 발화 자체를 보고 신호를 판단하는 층이 빠져 있었다.

```text
"네, 알겠어요"
-> 왜 backchannel로 봤는가?

"그게 아니라 환불받고 싶은데요"
-> 왜 intent_shift로 봤는가?
```

그래서 당시 문제의식은 "단순 mapping이 싫으니 모든 action을 LLM에게 맡기자"가 아니라, "중간 판단을 누가 어떤 로직으로 하느냐"에 가까웠다.

### 단순 mapping의 재해석

Day 2의 단순 mapping은 처음부터 틀린 설계라기보다, Text Replay에서 action 흐름을 먼저 확인하기 위한 placeholder였다.

당시 실제 흐름은 아래에 가까웠다.

```text
baseline:
has_user_speech = true
-> stop_and_switch

policy_v1:
scenario.event_type = backchannel
-> brief_ack

scenario.event_type = intent_shift
-> stop_and_switch
```

이 흐름은 아래를 빠르게 연결하는 데 유용했다.

```text
scenario loader
-> runner
-> policy output
-> expected_action vs actual_action
-> evaluation / decision log
-> Playground / Test Bench UI
```

문제는 mapping 자체가 아니라, `scenario.event_type`이 사람이 붙인 기준 annotation인데도 runtime 판단 로직처럼 쓰였다는 점이다.
즉 "고객 발화를 보고 왜 intent_shift라고 봤는가?"라는 해석 단계가 비어 있었다.

앞으로 피해야 할 것은 아래다.

```text
scenario.event_type
-> actual_action
```

앞으로 허용할 수 있는 것은 아래다.

```text
predicted_event_type
+ predicted_user_intent
+ confidence
+ ambiguity
-> actual_action
```

`predicted_event_type`은 runtime에 transcript/context를 보고 만든 해석 결과다.
따라서 Thin Action Policy가 이 값을 쓰는 것은 기준 annotation을 베끼는 것이 아니라, 해석 결과를 행동으로 바꾸는 단계다.

## 현재 구현 흐름

현재 코드 기준 흐름은 아래에 가깝다.

```text
Text scenario / direct input / audio transcript
-> RunnerInput
   # ai_current_intent
   # ai_utterance
   # user_utterance
   # has_user_speech
   # user_tone_hint 일부
-> LLMActionPolicy
-> LLMActionClient.judge_action()
-> PolicyDecision
   # actual_action
   # reason
   # signals.confidence
   # signals.interpreted_user_intent
   # signals.is_intent_shift
-> expected_action과 비교
-> run artifact 기록
```

현재 LLM prompt에는 아래 기준 annotation을 넣지 않는다.

```text
excluded:
- expected_action
- event_type
- expected_user_intent
```

이 덕분에 사람이 붙인 `event_type`을 그대로 action으로 매핑하는 문제는 줄었다.

하지만 LLM이 아래를 한 번에 처리한다.

```text
1. 고객 발화가 어떤 신호인지 해석
2. 고객 의도가 바뀌었는지 판단
3. 최종 actual_action 선택
```

따라서 지금 `baseline`, `policy_v1`은 제품 관점의 단계별 signal/policy 버전이라기보다 LLM prompt 차이에 가까워졌다.

## 회복 후보 흐름

다음 단계의 회복 후보는 현재 LLM 구현을 버리는 것이 아니라, 역할을 낮추고 분리하는 것이다.

```text
입력 경로(Text / Audio File / Mic)
-> transcript / speech signal
-> Interpreter Pipeline
   # predicted_event_type
   # predicted_user_intent
   # is_intent_shift
   # confidence
   # ambiguity
   # signal_source
   # 내부 기능 후보: rule/threshold, LLM 보조 판단, ambiguous fallback, debug helper
-> Thin Action Policy
   # 고객 신호 해석 결과를 보고 actual_action 선택
   # deterministic / hybrid / LLM-assisted 가능
-> safety guard
   # handoff, escalation, risky complaint 후보 강제 처리
-> evaluation / run artifact
```

핵심은 고객 발화를 해석하는 `Interpreter Pipeline`을 먼저 잡는 것이다.
그 안에는 필요에 따라 rule, LLM, fallback, debug 보조 기능이 붙을 수 있다.
다만 action 생성을 추후로 미루지 않는다. 첫 구조 재정렬 실험부터 얇은 Action Policy가 `actual_action`을 만들어 기존 action evaluation을 유지한다.

```text
직접 action 판단 baseline
-> 현재 구현처럼 transcript와 맥락을 보고 action label까지 직접 고른다.
-> 비교용 one-shot semantic baseline으로 보존 가능.

해석 단계
-> 고객 발화를 보고 predicted_event_type, predicted_user_intent, confidence를 만든다.
-> 내부 구현은 rule일 수도 있고 LLM일 수도 있고 둘을 섞을 수도 있다.

fallback 단계
-> clear case는 rule/threshold로 처리하고, ambiguous case만 LLM에게 보낸다.

debug/evaluation 보조
-> failure reason, expected_action 보정 후보, error analysis를 돕는다.
```

## 용어 기준

이번 재정렬에서 헷갈리기 쉬운 값은 기준 annotation과 runtime result로 나눠 읽는다.

| 값 | 쉬운 설명 | 생성 시점 | 사용 위치 |
| --- | --- | --- | --- |
| `event_type` | 기준 고객 신호 | 사람이 scenario를 만들 때 | evaluation / error analysis |
| `expected_user_intent` | 기준 고객 의도 | 사람이 scenario를 만들 때 | evaluation / error analysis |
| `expected_action` | 기준 AI 행동 | 사람이 scenario를 만들 때 | action evaluation |
| `predicted_event_type` | 해석된 고객 신호 | runtime Interpreter Pipeline | Thin Action Policy 입력 / interpreter diagnostic |
| `predicted_user_intent` | 해석된 고객 의도 | runtime Interpreter Pipeline | Thin Action Policy 입력 / interpreter diagnostic |
| `actual_action` | policy가 고른 실제 AI 행동 | runtime Thin Action Policy 또는 direct baseline | `expected_action`과 비교 |
| `confidence` | 해석 확신도 | runtime Interpreter Pipeline | threshold / fallback / reason |
| `ambiguity` | 발화 애매함 | runtime Interpreter Pipeline | `ask_clarifying` 또는 fallback 후보 |
| `signal_source` | 해석 출처 | runtime Interpreter Pipeline | 디버깅 / run artifact |
| `interpreter_steps` | 어떤 해석 단계를 거쳤는지 | runtime Interpreter Pipeline | 디버깅 / run artifact |

`predicted_event_type`이라는 이름은 파이프라인을 나누기 때문에 필요하다.
기존 `event_type` 하나가 기준값과 runtime 해석 결과처럼 동시에 읽히던 문제를 막기 위한 이름이다.
문서 본문에서는 "해석된 고객 신호(predicted_event_type)"처럼 풀어 쓴다.

## Text / Audio 적용 방향

Text와 Audio를 따로 판단하지 않는다.
두 입력 경로는 앞단 adapter만 다르고, transcript/signal 이후에는 같은 interpreter/action 흐름을 탄다.

```text
Text input
-> user_utterance를 transcript처럼 사용
-> Interpreter Pipeline
-> Thin Action Policy
-> Evaluation

Audio input
-> STT/precomputed transcript
-> audio signal summary
-> Interpreter Pipeline
-> Thin Action Policy
-> Evaluation
```

Audio는 판단 로직을 새로 갖는 것이 아니라 아래 신호를 더 보탠다.

```text
transcript_source
audio.signal
stt metadata
transcript similarity / uncertainty
```

첫 분리 실험에서 action을 나중으로 미루지는 않는다.
대신 evaluation을 두 갈래로 남긴다.

```text
action evaluation:
expected_action vs actual_action

interpreter diagnostic:
event_type vs predicted_event_type
expected_user_intent vs predicted_user_intent
```

여기서 `event_type`과 `expected_user_intent`는 runtime 입력이 아니라, interpreter가 잘 해석했는지 보는 기준값으로만 사용한다.

## 예시

```text
user_utterance = "그게 아니라 환불받고 싶은데요."
ai_current_intent = "shipping_inquiry"

Interpreter Pipeline:
predicted_event_type = "intent_shift"
predicted_user_intent = "refund_request"
confidence = 0.91

Thin Action Policy:
actual_action = "stop_and_switch"
reason = "배송조회 흐름에서 환불요청으로 의도가 바뀌었기 때문"
```

```text
user_utterance = "네, 알겠어요."
ai_current_intent = "shipping_inquiry"

Interpreter Pipeline:
predicted_event_type = "backchannel"
predicted_user_intent = null
confidence = 0.88

Thin Action Policy:
actual_action = "continue"
reason = "새 요청이 아니라 짧은 맞장구이기 때문"
```

## 근거 요약

### 초기 기획과 4차 페어에서 확인되는 방향

- Text Replay는 음성을 포기하는 경로가 아니라, audio/STT 앞단을 잠시 고정하고 뒤쪽 판단 구조를 빠르게 검증하는 입력 경로였다.
- Audio File Test와 Mic Trial은 같은 판단 구조로 이어지는 입력 경로였다.
- 초기 계획에는 `VAD-only`, `Backchannel Rule`, `Intent Shift`, `AI Action Policy`, `Prosody Risk`처럼 신호가 단계적으로 추가되는 구조가 있었다.
- 이 구조에서 policy version은 LLM prompt version이 아니라 "어떤 신호를 추가했을 때 어떤 실패가 줄어드는지" 비교하는 단위였다.

### 5차 페어에서 바뀐 방향

- Day 2 placeholder는 사람이 붙인 `event_type`을 action으로 매핑하는 구조에 가까웠다.
- 사용자는 "그 event_type을 누가 판단했는가"를 문제로 보았다.
- 그 문제를 빠르게 해결하기 위해 baseline/policy_v1부터 LLM action judgment를 붙였다.
- 이때 `expected_action`, `event_type`, `expected_user_intent`를 LLM prompt에서 제외한 것은 적절한 guard였다.
- 다만 이 선택이 active 문서에 반영되며, LLM action judge가 제품 기본 판단 구조처럼 굳어졌다.

### 개인 고민 자료에서 확인되는 보조 맥락

- 개인 고민 자료에는 고정형/rule, 순수 LLM, 혼합형을 비교한 흔적이 있다.
- 그 자료는 공식 결정이나 architecture decision이 아니다.
- 하지만 사용자의 의도는 "모든 action을 LLM에게 맡기자"가 아니라 hybrid 가능성을 열어둔 쪽이었다는 보조 근거로 볼 수 있다.

## 현재 봐야 할 repo 파일

현재 구현 흐름:

- `src/interruption_detection/runner.py`
- `src/interruption_detection/models.py`
- `src/interruption_detection/policies/llm_action.py`
- `src/interruption_detection/policies/baseline.py`
- `src/interruption_detection/policies/policy_v1.py`
- `src/interruption_detection/llm.py`
- `src/interruption_detection/audio/adapter.py`
- `src/interruption_detection/audio/stt.py`
- `src/interruption_detection/audio/signals.py`

현재 active 문서:

- `context/internal/product-context.md`
- `context/internal/mvp/current.md`
- `context/internal/mvp/current-iteration-plan.md`
- `context/internal/project-language-map.md`
- `context/internal/scenario-worked-example.md`
- `context/decisions/2026-05-09-llm-action-policy-baseline/`
- `context/decisions/2026-05-11-context-intent-alignment/`

페어 공유용 짧은 문서:

- `context/temp/pipeline-layer-realignment-pair-brief.tmp.md`

## 작업 순서 제안

### 1. 먼저 decision을 새로 남긴다

새 decision 후보:

```text
context/decisions/2026-05-11-policy-signal-layer-realignment/
```

상태 후보:

```text
status: exploring
```

이 decision은 기존 `LLM Action Policy Baseline`을 즉시 폐기하기보다, 아래처럼 재해석하는 방향이 안전하다.

```text
기존 decision:
baseline/policy_v1부터 LLM action judge를 붙인다.

재정렬:
이 선택은 hardcoded mapping 문제를 푼 Step 3 실험 경로다.
제품/확장 구조에서는 Interpreter Pipeline과 Thin Action Policy를 다시 나눠 기록할 수 있다.
```

### 2. active context를 바로 덮어쓰지 않는다

먼저 변경 계획과 대상 파일을 정리한다.

후보 조치:

- `product-context.md`: LLM action judge를 현재 유일한 기준처럼 쓰지 않고, Interpreter Pipeline 안에 붙을 수 있는 구현 후보 중 하나로 낮춘다.
- `mvp/current.md`: 현재 구현 상태(direct LLM action judge)와 다음 구조 재정렬 후보(Interpreter Pipeline + Thin Action Policy)를 나눈다.
- `current-iteration-plan.md`: Step 3 LLM 전환은 완료/현재 구현으로 두고, Step 4 후보에 Interpreter Pipeline + Thin Action Policy 실험을 둔다.
- `project-language-map.md`: policy version, interpreter pipeline, action policy, LLM 사용 위치의 층위를 추가한다.
- `scenario-worked-example.md`: 현재 one-shot LLM path와 회복 후보 path를 구분한다.
- `evaluation-and-results-contract.md`: 기존 action evaluation은 유지하되 interpreter diagnostic 필드가 추가될 수 있음을 후보로 둔다.

### 3. 코드는 decision 이후에 설계한다

바로 리팩터링하지 않는다.

먼저 이름과 역할을 결정한다.

후보:

```text
LLMActionPolicy
-> direct_llm_action_judge 또는 llm_action_baseline으로 성격 낮추기

InterpreterPipeline
-> transcript와 context를 보고 고객 신호 해석 결과를 만든다

ThinActionPolicy
-> 고객 신호 해석 결과를 보고 actual_action 생성

HybridPolicy
-> clear case는 rule/threshold, ambiguous case는 LLM 보조 fallback
```

run artifact에는 아래 구분이 남아야 한다.

```text
signals.signal_source
signals.predicted_event_type
signals.predicted_user_intent
signals.confidence
signals.ambiguity
signals.interpreter_steps
policy_source
stage_latencies_ms
```

evaluation에는 아래 비교가 추가될 수 있다.

```text
action_evaluation:
expected_action vs actual_action

interpreter_diagnostic(해석 진단):
event_type vs predicted_event_type
expected_user_intent vs predicted_user_intent
```

## 작업 경계

이번 작업은 현재 구조를 부정하거나 과거 구조로 되돌리는 일이 아니다.
지금까지 만든 흐름을 보존하면서, 어느 층이 합쳐져 있는지 다시 정리하는 작업이다.

| 항목 | 뜻 | 이번 작업에서의 기준 |
| --- | --- | --- |
| `LLMActionPolicy` | 지금 코드에 있는 LLM 기반 action 판단 정책 | 바로 삭제하지 않는다. hardcoded mapping 문제를 피한 direct LLM action judge baseline으로 보존한다. |
| `results/runs/*` | 과거 Test Bench 실행 결과 폴더 | 과거 실험 기록이므로 덮어쓰거나 의미를 바꾸지 않는다. 새 실험은 새 run artifact로 남긴다. |
| `context/internal/` | 현재 active 기준 문서 모음 | 현재 문서를 그대로 정답으로 두지 않는다. 이번 작업은 active 기준 자체를 다시 점검하는 작업이다. |
| 개인 고민 자료 | repo 밖 또는 임시 대화에서 나온 보조 생각 | 참고만 한다. 공식 결정 근거는 repo 안의 decision/context/code/data/run artifact로 남긴다. |
| 공개 `docs/` | 외부 공유용 문서 | 지금 바로 고치지 않는다. 먼저 내부 기준(`context/decisions/`, `context/internal/`)을 맞춘 뒤 옮긴다. |
| `event_type`, `expected_user_intent`, `expected_action` | 사람이 scenario에 붙인 기준 annotation | runtime 예측값처럼 설명하지 않는다. interpreter 진단이나 action 평가 기준으로만 쓴다. |
| `Interpreter Pipeline` | 고객 발화를 보고 신호를 해석하는 단계 | 이것만 만들고 멈추지 않는다. 첫 실험은 `Thin Action Policy`까지 붙여 `actual_action`을 만든다. |
| `Thin Action Policy` | 해석 결과를 AI 행동으로 바꾸는 얇은 판단 단계 | 기존 Test Bench 비교 흐름을 유지하기 위해 `actual_action`을 생성한다. |

## 다음 작업 순서

1. 이 문서와 `pipeline-layer-realignment-pair-brief.tmp.md`를 읽는다.
   현재 문제가 "direct LLM action judge 한 층에 신호 해석과 행동 선택이 합쳐진 상태"라는 점을 맞춘다.
2. 기존 `LLM Action Policy Baseline` decision을 어떻게 다룰지 정한다.
   폐기보다는 "hardcoded event_type mapping을 피하기 위해 붙인 direct baseline"으로 재해석하는 쪽이 자연스럽다.
3. 새 decision을 남긴다.
   후보 위치는 `context/decisions/2026-05-11-policy-signal-layer-realignment/`이고, 상태는 `exploring`이 자연스럽다.
4. active context에서 바꿀 파일과 문구 방향을 먼저 정한다.
   대상 후보는 `product-context.md`, `mvp/current.md`, `current-iteration-plan.md`, `project-language-map.md`, `scenario-worked-example.md`, `evaluation-and-results-contract.md`다.
5. 문서 변경 계획을 사용자/페어에게 먼저 보여준다.
   이 작업은 코드보다 context 기준이 먼저 흔들리는 작업이기 때문이다.
6. 코드 리팩터링은 그 다음 작업으로 분리한다.
   첫 코드 후보는 `InterpreterPipeline` contract와 `ThinActionPolicy`를 얇게 세우는 것이다.
