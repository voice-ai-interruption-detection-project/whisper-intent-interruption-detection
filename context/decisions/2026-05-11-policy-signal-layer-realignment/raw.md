# Raw Material

이 파일은 현재 세션에서 나온 핵심 문제의식과 작업 메모를 재진입 가능한 수준으로 보존한다.

긴 대화 전문, 개인 로컬 경로, 비공개 원문 위치는 저장하지 않는다.

## 사용자 문제의식

사용자는 현재 구현과 active context가 아래 흐름으로 기울었다고 보았다.

```text
RunnerInput 한 덩어리
-> LLMActionPolicy
-> actual_action 판단
```

사용자는 이것이 원래 목적이던 "마이크/오디오 기반 AI 상담 interruption 및 intent shift 대응"의 제품 흐름 검증과 다를 수 있다고 보았다.

특히 Text Replay는 처음부터 제품 흐름을 버리려는 것이 아니라, live mic, streaming STT, latency가 어려우니 먼저 판단 구조를 빠르게 검증하기 위한 단계였다고 이해했다.

## 확인한 구분

초기 의도에 가까운 흐름은 아래처럼 정리했다.

```text
고객 장면
-> 판단 케이스(scenario)
-> 입력 경로(Text / Audio File / Mic)
-> transcript / speech signal 구성
-> 고객 신호 해석
-> AI 행동 판단(AI Action Policy)
-> actual_action 생성
-> expected_action과 비교
-> failure 분석 / run artifact 기록
```

현재 구현에 가까운 흐름은 아래처럼 정리했다.

```text
Text scenario / direct input / audio transcript
-> RunnerInput
-> LLM action judge
-> actual_action + reason + interpreted_user_intent + is_intent_shift
-> expected_action과 비교
```

재정렬 후보는 아래처럼 정리했다.

```text
입력 경로
-> transcript / speech signal
-> Signal Analyzer
-> Action Policy
-> optional LLM fallback
-> safety guard
-> evaluation / run artifact
```

## 중요한 정정

사용자는 "단순 mapping이 싫다"는 말이 "모든 action을 LLM에게 다 던지자"는 뜻은 아니었다고 정정했다.

오히려 rule, threshold, classifier, LLM signal judge, fallback을 섞는 hybrid 구조도 고민했었다.

세션 중 사용자가 직접 짚은 요지는 아래에 가깝다.

```text
policy도 애초에 이렇게 LLM으로만 나뉠 필요가 없었던 것 같다.

내가 말한 단순 mapping 문제는
"무조건 LLM에게 다 던지자"는 의도가 아니었다.

고민 자료에도 hybrid 가능성을 생각한 흔적이 있다.
```

따라서 이번 사안의 핵심 문장은 아래다.

```text
현재 문제는 LLM을 썼다는 점이 아니라,
고객 신호 해석과 AI 행동 판단이 LLM action judge 한 층으로 합쳐져 있다는 점이다.
```

## 페어 설명용으로 정리한 최소 도식

사용자는 표보다 흐름이 보이는 도식을 원했다. 최종적으로 아래처럼 각 단계 옆에 schema/runtime 값을 짧게 붙이는 방식이 적절하다고 정리했다.

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

현재 구현과 비교하는 최소 도식은 아래다.

```text
원래/회복 후보:
transcript / speech signal
-> 고객 신호 해석(event_type 계열)
-> AI 행동 판단(action label)
-> actual_action

현재 구현:
RunnerInput
-> LLM action judge
-> actual_action
```

## 오해 방지 메모

- `event_type`, `expected_user_intent`, `expected_action`은 현재 기준으로 사람이 붙인 기준 annotation이다.
- `actual_action`, `reason`, `signals`는 policy 실행 후 생기는 결과다.
- 현재 LLM prompt에서 `event_type`, `expected_user_intent`, `expected_action`을 제외한 것은 hardcoded label mapping을 줄이기 위한 guard로 의미가 있다.
- 다만 guard가 있다는 사실과 LLM이 최종 action judge를 맡는 것이 제품적으로 최선이라는 주장은 다르다.
- 이 decision은 현재 구현을 되돌리자는 기록이 아니라, 다음 작업을 진행할 수 있다는 가정에서 signal/action 층위를 다시 나눠볼 필요를 남기는 기록이다.
- 개인 고민 자료는 공식 결정 근거가 아니라 사용자 의도와 불안의 흐름을 추적하는 보조 자료로만 본다.

## 작업 중 생성/정리한 자료

처음에는 페어 공유용 짧은 브리프를 만들었고, 이어서 다른 세션이 바로 이어받을 수 있는 working context 문서를 만들었다.

그 뒤 사용자가 "분석, 브리프 문서만 남기고 나머지는 git 작업 이전으로 되돌려달라"고 요청했다.

정리 결과, temp에는 새로 만든 두 문서만 untracked로 남기고, 기존 temp 문서 삭제 상태와 중복 이동 흔적은 되돌렸다.

## 현재 작성한 temp 문서

- `context/temp/analysis-notes/pipeline-layer-realignment-working-context.tmp.md`
- `context/temp/pair-briefs/pipeline-layer-realignment-pair-brief.tmp.md`

## 저장한 원문

저장한 긴 원문 없음.

근거가 되는 페어/기획/고민 자료는 현재 repo 밖의 팀 프로젝트 작업 자료에도 있으나, 이 decision에는 개인 로컬 경로나 긴 원문을 직접 저장하지 않는다.
