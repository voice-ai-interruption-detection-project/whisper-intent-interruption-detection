# Pipeline Layer Realignment Pair Brief

## 한 줄 요약

현재 이슈는 LLM을 썼다는 점이 아니라, 고객 신호 해석과 AI 행동 판단이 `LLM action judge` 한 층으로 합쳐져 있다는 점이다.

이 문서는 예전 자료로 되돌아가자는 제안이 아니라, 현재 구현에서 흐려진 파이프라인 층위를 다시 보려는 페어 논의용 메모다.

## 원래 의도한 판단 흐름

```text
고객 장면
-> 판단 케이스(scenario)             # scenario_id, domain, level, notes
-> 입력 경로(Text / Audio File / Mic) # input_mode, audio_path, transcript_source
-> transcript / speech signal 구성    # user_utterance 또는 transcript.text, has_user_speech, audio.signal
-> 고객 신호 해석                    # event_type, expected_user_intent
                                     # runtime 후보: predicted_event_type, predicted_user_intent, confidence
-> AI 행동 판단(AI Action Policy)     # ai_current_intent, ai_utterance, transcript, signal을 보고 판단
-> actual_action 생성                # actual_action, reason, signals
-> expected_action과 비교             # expected_action vs actual_action
-> failure 분석 / run artifact 기록   # primary_failure, decision_logs.jsonl, evaluation.json
```

핵심은 아래 두 층을 나눠 보는 것이다.

```text
고객 신호 해석
-> 이 발화가 맞장구인지, 같은 주제 질문인지, 의도 전환인지, 불만/긴급인지 판단

AI 행동 판단
-> 그 신호를 바탕으로 continue, brief_ack, respond_and_continue, stop_and_switch 등을 선택
```

초기 기획에서 중요했던 것은 Text/Audio/Mic 중 어느 입력을 쓰든, 뒤쪽에서는 같은 판단 흐름을 타야 한다는 점이었다.
다만 이때의 `event_type`은 사람이 붙인 기준 annotation이었고, runtime 판단 결과는 아직 따로 없었다.

## 5차 전 placeholder 흐름

```text
판단 케이스(scenario)
-> 사람이 붙인 event_type              # backchannel, intent_shift, ambiguous 등
-> rule mapping
-> actual_action
-> expected_action과 비교
```

이 흐름은 runner, evaluator, UI, Test Bench를 확인하는 데는 유용했다.
당시 목적은 고객 신호 해석기를 완성하는 것보다, action label이 runner/evaluator/UI에서 끝까지 흐르는지 먼저 보는 데 가까웠다.

다만 고객 발화 자체를 보고 신호를 판단하는 층이 빠져 있었다.

```text
"네, 알겠어요"
-> 왜 backchannel로 봤는가?

"그게 아니라 환불받고 싶은데요"
-> 왜 intent_shift로 봤는가?
```

여기서 생긴 문제는 `event_type -> action` 매핑이 임시 발판을 넘어 실제 판단 로직처럼 읽히기 시작했다는 점이다.

## 현재 구현 흐름

```text
판단 케이스 또는 직접 입력
-> RunnerInput                         # ai_current_intent, ai_utterance, user_utterance, has_user_speech
-> LLM action judge
-> PolicyDecision                      # actual_action, reason, signals
-> expected_action과 비교
-> failure 분석 / run artifact 기록
```

현재 LLM prompt에는 아래 기준 annotation을 넣지 않는다.

```text
excluded:
- expected_action
- event_type
- expected_user_intent
```

그래서 현재 구조는 label mapping 문제를 줄인다.
이 전환은 "사람이 붙인 event_type을 보지 말고, transcript를 보고 실제 판단하게 하자"는 문제의식에서 나왔다.

하지만 LLM이 아래 두 질문을 한 번에 처리한다.

```text
1. 이 고객 발화는 어떤 신호인가?
2. 그래서 AI는 어떤 action을 선택해야 하는가?
```

최근 정리한 해석은 아래에 가깝다.

- Day 2의 단순 mapping은 처음부터 틀린 설계라기보다, Text Replay에서 action 흐름과 evaluator/run artifact를 먼저 보려는 placeholder였다.
- 문제는 mapping 자체가 아니라, 사람이 붙인 기준 annotation인 `event_type`이 runtime 판단 로직처럼 쓰였다는 점이다.
- 현재 LLM action judge는 이 문제를 빠르게 푼 direct baseline이다. 다만 신호 해석과 action 선택이 한 번에 합쳐져 있다.
- 다음 단계는 너무 잘게 쪼개는 것이 아니라, `Interpreter Pipeline`과 얇은 `Action Policy`를 한 run 안에서 같이 굴리되 역할을 기록으로 나누는 것이다.

## 다시 나눠볼 후보 흐름

```text
입력 경로(Text / Audio File / Mic)
-> transcript / speech signal
-> Interpreter Pipeline                # 고객 발화를 해석해 predicted_event_type, predicted_user_intent, confidence, ambiguity를 만든다
   # 내부 기능 후보: rule/threshold, LLM 보조 판단, ambiguous fallback, debug helper
-> Thin Action Policy                  # 고객 신호 해석 결과를 보고 actual_action 선택
-> safety guard                        # 위험/이관 케이스 강제 처리 후보
-> evaluation / run artifact
```

핵심은 고객 발화를 해석하는 `Interpreter Pipeline`을 먼저 잡는 것이다.
그 안에는 필요에 따라 rule, LLM, fallback, debug 보조 기능이 붙을 수 있다.
다만 action 생성을 뒤로 미루지는 않는다. 기존 Test Bench 흐름을 살리기 위해 첫 실험부터 얇은 `Action Policy`가 `actual_action`까지 만든다.
즉 다시 단순 mapping으로 돌아가자는 것이 아니라, 해석 결과와 action 선택을 한 run 안에서 같이 남기자는 방향이다.

```text
직접 action 판단 baseline
-> 현재 구현처럼 transcript와 맥락을 보고 action label까지 직접 고른다.
-> 제품 기본 구조라기보다 비교용 baseline으로 보존할 수 있다.

해석 단계
-> 고객 발화를 보고 predicted_event_type, predicted_user_intent, confidence를 만든다.
-> 내부 구현은 rule일 수도 있고 LLM일 수도 있고 둘을 섞을 수도 있다.

fallback 단계
-> rule/threshold로 명확하지 않은 케이스만 추가 판단한다.

debug/evaluation 보조
-> failure reason, expected_action 보정 후보, error analysis를 돕는다.
```

## mapping을 보는 기준

피해야 할 mapping은 아래다.

```text
scenario.event_type       # 사람이 붙인 기준 annotation
-> actual_action
```

허용 가능한 action 결정은 아래다.

```text
predicted_event_type      # runtime에 transcript/context를 보고 만든 해석 결과
+ predicted_user_intent
+ confidence
+ ambiguity
-> actual_action
```

겉으로는 둘 다 event type 비슷한 값에서 action으로 가는 것처럼 보인다.
하지만 앞쪽은 정답지를 실행 로직으로 쓰는 것이고, 뒤쪽은 runtime 해석 결과를 행동으로 바꾸는 것이다.

`predicted_event_type`이라는 이름은 새 제품 개념을 늘리려는 것이 아니라, 기존 `event_type`이 맡던 기준값 역할과 runtime 해석 결과 역할을 분리하기 위한 이름이다.
문서 본문에서는 "해석된 고객 신호(predicted_event_type)"처럼 풀어 쓴다.

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

## 논의할 질문

1. 현재 `LLMActionPolicy`는 제품 기본 policy로 둘지, one-shot LLM judge baseline으로 이름/역할을 낮출지?
2. `event_type`, `expected_user_intent`는 계속 기준 annotation으로 둘지, runtime에는 `predicted_*` 계열을 별도로 둘지?
3. 다음 실험은 LLM prompt 개선이 아니라 Interpreter Pipeline + Thin Action Policy 실험으로 잡을지?
4. action 생성을 나중으로 미루지 않고, 해석 진단(interpreter diagnostic)과 action evaluation을 한 run artifact 안에 같이 남길지?
5. active context 문서에는 현재 direct LLM action judge 흐름과 다음 후보 흐름을 같이 남길지?
