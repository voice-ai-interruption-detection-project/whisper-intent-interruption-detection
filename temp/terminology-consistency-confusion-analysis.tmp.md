# Terminology Consistency and Confusion Analysis

이 문서는 `docs/` 본문을 바로 고치기 전에, 현재 프로젝트에서 어떤 정합성 문제가 있고 왜 팀원이 헷갈렸는지 정리한 임시 분석 메모다.

목적은 두 가지다.

- `internal/` 기준 자료를 보강할 때 무엇을 설명해야 하는지 정한다.
- 나중에 `docs/` 본문을 고칠 때 단순 search-replace가 아니라, 헷갈림의 원인을 기준으로 고친다.

이 문서는 공개 문서가 아니라 `temp/` 작업 메모다. 안정되면 필요한 내용만 `internal/`로 승격한다.

## 결론

현재 혼선의 핵심은 단어 하나가 어려운 것이 아니라, 같은 대상이 여러 층위에서 동시에 등장한다는 점이다.

```text
제품 장면
-> 개념 용어
-> schema key/value
-> 실행 pipeline
-> 평가 결과 / failure taxonomy
```

대화에서는 추상 용어만 볼 때 헷갈림이 생겼고, 구체 장면을 schema key/value와 pipeline에 연결했을 때 이해가 풀렸다.

따라서 지금 필요한 내부 자료는 단순 용어 사전보다 **한 scenario가 schema와 pipeline을 어떻게 통과하는지 보여주는 worked example**에 가깝다.

## 정합성 문제

### 1. 현재 action label과 과거 label이 섞임

현재 기준 action label은 `respond_and_continue`다. 하지만 과거 문서와 예시에는 `pause`가 남아 있다.

이 문제는 단순 이름 잔재처럼 보이지만, 실제로는 의미도 흔든다.

- `pause`: 잠깐 멈춘다는 동작만 강조한다.
- `respond_and_continue`: 같은 주제 질문에 답하고 원래 흐름으로 돌아간다는 제품 행동을 설명한다.

따라서 `same_intent_question`과 연결되는 action은 `pause`가 아니라 `respond_and_continue`로 설명해야 한다.

### 2. Event Type과 Action Label이 같은 층위처럼 보임

원본 대화에서 `backchannel`이 action label인지 event type인지 헷갈리는 장면이 있었다.

현재 기준은 아래처럼 분리된다.

| 층위 | 예시 | 의미 |
| --- | --- | --- |
| `event_type` | `backchannel`, `intent_shift`, `same_intent_question` | 고객이 보낸 신호의 종류 |
| `expected_action` | `continue`, `respond_and_continue`, `stop_and_switch` | AI가 해야 하는 행동 |

문서가 이 둘을 한 표면에 나열하면 “고객 신호”와 “AI 행동”이 뒤섞여 보인다.

### 3. Scenario의 크기가 불명확함

대화에서는 scenario를 전체 상담 흐름으로 볼지, AI 발화 중 고객이 끼어드는 한 순간으로 볼지 혼선이 있었다.

현재 기준은 후자다.

```text
scenario = AI가 말하는 중 고객 신호가 들어오는 한 순간의 테스트 카드
```

전체 ARS 메뉴나 상담 여정은 제품 맥락이다. scenario는 그중 policy 판단을 평가할 수 있는 작은 단위다.

### 4. Input Mode가 AI 발화로 오해됨

`input_mode`가 `ai_utterance`와 가까이 보이거나, schema key 순서와 pipeline 순서가 섞이면 “input mode가 AI가 말하는 방식인가?”처럼 읽힐 수 있다.

현재 기준은 아래와 같다.

| input mode | 의미 |
| --- | --- |
| Text Replay | 텍스트로 고객 신호를 넣어 policy 판단을 검증 |
| Audio File Test | 음성 파일을 넣어 STT/signal 흐름까지 확인 |
| Mic Trial | live mic 입력과 latency 확인 |

즉 input mode는 AI 발화가 아니라 **같은 scenario를 어떤 입력 방식으로 주입할지**다.

### 5. 목표 수치와 실측 수치가 섞일 위험

`25% -> 8%`, `40% -> 12%` 같은 수치는 run artifact가 없으면 확정 결과처럼 쓰면 안 된다.

현재 기준은 다음과 같다.

- 실측 수치는 `results/runs/{run_id}/evaluation.json`에서 확인될 때만 인용한다.
- 실험 전 수치는 목표, 예시, 가설로만 쓴다.
- Playground 화면 수치는 외부 인용 출처로 쓰지 않는다.

### 6. Results tree 설명이 두 갈래임

active rule은 `results/runs/{run_id}/` 계약을 기준으로 한다. 과거 docs 일부는 flat `results/evaluation.json`, `results/decision_logs.jsonl`처럼 설명되어 있다.

현재 기준은 다음 구조다.

```text
results/runs/{run_id}/
├── run_meta.json
├── evaluation.json
├── decision_logs.jsonl
└── error_analysis.md
```

## 헷갈리게 하는 포인트

### 1. 용어가 사전식으로만 나열됨

`scenario`, `policy`, `decision`, `action label`, `event type`이 한 화면에 병렬로 보이면, 어떤 것이 상위 개념이고 어떤 것이 결과인지 알기 어렵다.

대화에서는 “프론트/백엔드처럼 머릿속에 매핑되는 구조가 없다”는 취지의 표현이 나왔다. 익숙한 개발 층위가 없으니 단어들이 모두 같은 높이에 놓인 것처럼 보인 것이다.

### 2. Schema key 순서와 실제 pipeline 순서가 섞임

schema 예시는 필드 목록이다. 하지만 사람이 읽을 때는 그 순서를 실행 순서처럼 오해하기 쉽다.

예를 들어 `ai_utterance`, `user_utterance`, `event_type`, `expected_action`이 나열되면 다음처럼 헷갈릴 수 있다.

- AI 발화가 input mode인가?
- 고객 발화가 signal/transcript인가?
- event type은 policy가 내는 값인가, 사람이 붙인 기준인가?
- expected action은 action label과 같은가?

이 혼선은 key/value를 실제 장면에 매핑하면서 풀렸다.

### 3. 현재 상태와 목표 상태가 같은 문장에 들어감

“샘플 수 6개”, “30개 scenario” 같은 표현은 현재 가진 데이터인지 목표인지 분리해서 쓰지 않으면 오해를 만든다.

실제로 대화에서는 30개 scenario가 이미 있는 것으로 이해했다가, 오늘 만들어야 하는 목표임을 확인하면서 정정됐다.

### 4. Text Replay가 음성 프로젝트와 분리된 것처럼 보임

Text Replay만 보면 “음성 프로젝트인데 텍스트로 평가하면 목적에서 벗어나는 것 아닌가?”라는 질문이 자연스럽게 생긴다.

이 혼선은 아래 연결 설명으로 풀렸다.

```text
audio/mic
-> STT/signal
-> intent/event key
-> AI Action Policy
-> action
```

Text Replay는 앞단의 audio/STT를 잠시 고정하고, 뒤쪽 policy 판단을 먼저 검증하는 단계다.

### 5. Failure 이름이 고객 경험과 연결되지 않으면 외워야 하는 단어가 됨

`false_stop`, `missed_switch`는 그냥 metric 이름으로 보면 어렵다.

대화에서는 backchannel 예시와 연결하면서 이해가 풀렸다.

- `false_stop`: 멈추지 않아도 되는 맞장구에서 AI가 멈춤
- `missed_switch`: 멈추고 전환해야 하는데 기존 흐름을 계속함

즉 failure taxonomy도 abstract label보다 고객 장면과 같이 설명해야 한다.

## 이해가 풀리는 패턴

원본 대화에서 반복된 이해 전환은 아래 순서였다.

1. 추상 용어만 보고 헷갈림
2. 하나의 구체 장면을 잡음
3. 장면을 schema key/value에 매핑함
4. 그 key/value가 policy input과 action output으로 이어지는 것을 봄
5. expected와 actual 비교로 evaluation까지 연결함

예시는 다음처럼 써야 한다.

```text
제품 장면:
AI가 배송 상태를 설명하는 중 고객이 "그게 아니라 환불받고 싶은데요"라고 말함

schema:
ai_current_intent = shipping_inquiry
ai_utterance = 현재 상품은 배송 중이며 내일 오후 도착 예정입니다.
user_utterance = 그게 아니라 환불받고 싶은데요
event_type = intent_shift
expected_user_intent = refund_request
expected_action = stop_and_switch

pipeline:
Text Replay input
-> user_utterance를 transcript처럼 사용
-> event_type / expected_user_intent 해석
-> AI Action Policy 실행
-> actual_action 생성
-> expected_action과 비교

failure:
actual_action이 respond_and_continue면 missed_switch
actual_action이 stop_and_switch면 expected와 일치
```

## Internal 자료 보강 방향

이미 추가한 내부 기준 자료는 다음 두 축이다.

- `internal/project-language-map.md`: 용어와 층위 지도
- `internal/evaluation-and-results-contract.md`: 평가와 result 계약

다음 보강 후보는 아래 중 하나다.

### 후보 A. Project Language Map에 Worked Example 추가

가장 가볍다. 한 scenario를 제품 장면, schema, pipeline, failure까지 연결한다.

장점:
- 현재 헷갈림 패턴에 직접 대응한다.
- 새 문서를 늘리지 않는다.

단점:
- 문서가 길어질 수 있다.

### 후보 B. `internal/scenario-worked-example.md` 추가

한 파일을 온전히 예시 중심으로 둔다.

장점:
- 페어 중 막혔던 지점에 가장 친절하다.
- docs 본문 정리 전 기준 fixture로 쓰기 쉽다.

단점:
- internal 문서가 하나 더 늘어난다.

### 후보 C. `internal/current-state-vs-target.md` 추가

현재 있는 것과 앞으로 만들 것을 분리한다.

장점:
- “30개가 이미 있는가, 오늘 만들어야 하는가” 같은 상태 혼선을 줄인다.

단점:
- 계속 갱신하지 않으면 금방 낡는다.

## 추천

우선 후보 A를 한다.

`internal/project-language-map.md`에 `Worked Example: intent_shift` 섹션을 추가하고, 필요하면 이후 `internal/scenario-worked-example.md`로 분리한다.

이유:

- 지금 혼선은 용어 사전보다 연결 예시 부족에서 왔다.
- docs 본문을 아직 건드리지 않기로 했으므로, internal에서 기준 예시를 먼저 안정화하는 것이 안전하다.
- 나중에 docs 정리 시 이 예시를 공개 문장으로 발췌할 수 있다.

## Docs 본문 정리 시 체크리스트

아직 `docs/` 본문은 고치지 않는다. 나중에 정리할 때는 아래를 본다.

- `pause`가 현재 action label처럼 쓰이는가?
- `event_type`과 action label이 같은 층위로 보이는가?
- `scenario`가 전체 상담 플로우처럼 설명되는가?
- `input_mode`가 AI 발화처럼 읽히는가?
- 목표 수치가 실측 결과처럼 쓰이는가?
- flat `results/evaluation.json` 구조가 남아 있는가?
- Text Replay가 음성 프로젝트의 대체물처럼 설명되는가?
- failure taxonomy가 고객 장면 없이 metric 이름만 나열되는가?

## 이번 분석에서 유지할 경계

- `docs/` 본문은 아직 수정하지 않는다.
- 페어 원본은 evidence로만 보고, 프로젝트 문서에는 개인 로컬 절대경로를 넣지 않는다.
- `기획/` 자료를 그대로 복사하지 않고, 현재 기준 어휘로 재정리한다.
- 수치 인용은 run artifact가 생긴 뒤에 한다.
