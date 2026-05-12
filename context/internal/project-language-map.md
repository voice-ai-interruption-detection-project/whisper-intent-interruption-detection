# Project Language Map

이 문서는 프로젝트 안에서 자주 섞이는 단어의 층위를 맞추기 위한 내부 기준 자료다.

세션 시작 문서는 아니다. 제품 의도를 확인할 때는 [Product Context](product-context.md)를 먼저 보고, 이 문서는 판단 케이스(`scenario`), 입력 경로(`input_mode`), `event_type`, `expected_action`, `actual_action` 같은 용어가 헷갈릴 때 꺼내 읽는다.

`docs/`에 바로 공개 문장으로 옮기기 전, 팀 안에서 먼저 같은 뜻으로 쓰기 위한 작업용 사전이다.

## 한 줄 기준

이 프로젝트는 **음성 AI 상담에서 AI가 말하는 중 고객 신호가 들어온 한 순간**을 판단 케이스로 잘라 보고, AI가 어떤 다음 행동을 선택해야 자연스러운지 평가한다.

```text
고객 장면
-> transcript / speech signal
-> 고객 신호 해석
-> AI 행동 판단 실행
-> expected_action과 actual_action 비교
-> failure 분석과 Test Bench run artifact 기록
```

지금은 `baseline`과 `policy_v1`에서 LLM structured output이 고객 발화 해석 결과와 `actual_action`을 함께 만들고, 정책 코드가 이를 고객 신호 해석(`Interpreter Pipeline`)과 AI 행동 선택(`AI Action Selector`) 흐름으로 나눠 기록한다. 이 흐름은 특정 policy 하나에만 붙이지 않고 `baseline`과 `policy_v1`이 함께 통과한다.

구체 예시는 [Scenario Worked Example](scenario-worked-example.md)을 먼저 본다. 특히 `event_type`, `expected_action`, `actual_action`이 한 화면에 같이 나와 헷갈릴 때는 예시를 따라가면 된다.

## Reference 읽는 순서

이 문서는 전체 지도다. 세부 값은 아래 reference로 내려가서 확인한다.

```text
Project Language Map
-> reference/Schema Keys
-> reference/Event Types / Action Labels
-> Scenario Worked Example
-> Evaluation and Results Contract
```

| 문서 | 볼 때 |
| --- | --- |
| [Schema Keys](reference/schema-keys.md) | `event_type = intent_shift`에서 key와 value가 헷갈릴 때 |
| [Event Types](reference/event-types.md) | `backchannel`, `intent_shift`, `ambiguous` 같은 고객 신호 값을 확인할 때 |
| [Action Labels](reference/action-labels.md) | `continue`, `respond_and_continue`, `stop_and_switch` 같은 AI 행동 값을 확인할 때 |
| [Scenario Worked Example](scenario-worked-example.md) | 한 판단 케이스(`scenario`)가 schema, policy, evaluation으로 이어지는 흐름을 볼 때 |

## 층위 구분

헷갈릴 때는 먼저 아래 네 층위를 나눈다.

| 층위 | 질문 | 예시 |
| --- | --- | --- |
| 상황 요약 | 어떤 순간을 다루나? | 배송 설명 중 고객이 환불을 요청함 |
| schema | 그 장면을 어떤 key/value로 저장하나? | `event_type = intent_shift` |
| runtime 해석 | policy 실행 중 고객 신호를 어떻게 해석했나? | `predicted_event_type = intent_shift` |
| policy | 어떤 입력을 보고 AI 행동을 고르나? | 해석 결과를 보고 `stop_and_switch` 판단 |
| evaluation | 기준과 실제 결과를 어떻게 비교하나? | expected와 actual이 다르면 failure 분류 |

## 핵심 용어

| 용어 | 현재 기준 | 헷갈리지 말 것 |
| --- | --- | --- |
| 판단 케이스(`scenario`) | AI 발화 중 고객 신호가 끼어드는 한 순간을 담은 테스트 카드 | 전체 상담 여정, ARS 메뉴 전체 흐름 |
| 입력 경로(`input_mode`) | 같은 판단 케이스를 어떤 입력 경로로 실행할지 나타내는 코드/API 보조 필드 | 제품 기능, 고객 신호의 종류 |
| `event_type` | 사람이 판단 케이스에 붙인 기준 고객 신호 | AI가 해야 하는 행동, runtime 예측 결과 |
| `expected_user_intent` | 사람이 판단 케이스에 붙인 기준 고객 의도 | AI의 현재 의도, action label, runtime 예측 결과 |
| `predicted_event_type` | runtime에 해석된 고객 신호 후보 | 기준값인 `event_type` |
| `predicted_user_intent` | runtime에 해석된 고객 의도 후보 | 기준값인 `expected_user_intent` |
| `expected_action` | action label 중 사람이 정한 자연스러운 AI 행동 기준 | policy가 실제로 낸 결과 |
| `actual_action` | action label 중 policy가 실제로 낸 실행 결과 | 새 action label, `data/scenarios.json`에 들어가는 기준 원본 |
| 고객 신호 해석(`Interpreter Pipeline`) | transcript/signal을 보고 runtime 고객 신호를 해석하는 단계 | 입력 adapter, evaluator, 제품 기능명 |
| AI 행동 판단(`AI Action Policy`) | 고객 개입 상황에서 AI의 다음 행동을 정하는 판단 기준 | 단순 interruption detector |
| AI 행동 선택(`AI Action Selector`) | 해석된 고객 신호를 바탕으로 policy가 `actual_action`을 고르는 단계 | 사람이 붙인 `event_type`을 그대로 action으로 매핑하는 로직 |
| `policy_version` | 어떤 개선 목표를 가진 policy인지 나타내는 비교 단위 | 모델 버전 전체, 배포 버전 |
| `Test Bench` | 판단 케이스 set에 policy를 batch로 돌리고 결과를 보존하는 배치 평가 표면 | Playground 화면, 임시 데모 |
| `Playground` | 단일 판단 케이스를 조작하며 policy 판단과 reason을 확인하는 표면 | batch 평가 결과, run artifact |

## Expected와 Actual은 같은 label set의 다른 역할이다

`expected_action`과 `actual_action`은 서로 다른 종류의 action을 뜻하지 않는다. 둘 다 `continue`, `respond_and_continue`, `stop_and_switch` 같은 action label vocabulary 중 하나를 값으로 갖는다.

차이는 **값의 종류**가 아니라 **누가 언제 정했는지**다.

| 항목 | 역할 | 값 집합 | 위치 |
| --- | --- | --- | --- |
| action label | AI 행동 선택지 이름 | `continue`, `brief_ack`, `respond_and_continue`, `stop_and_switch`, `ask_clarifying`, `handoff` | internal 기준, policy 코드 |
| `expected_action` | 사람이 미리 붙인 정답/기준 label | action label vocabulary | `data/scenarios.json` |
| `actual_action` | policy 실행 후 나온 예측/결과 label | action label vocabulary | `results/runs/{run_id}/decision_logs.jsonl` |

예를 들어 `expected_action = stop_and_switch`인데 `actual_action = respond_and_continue`라면, 두 값은 같은 action label 집합에 속한다. 다만 기준은 전환이어야 한다고 말하고, policy는 답하고 이어가겠다고 판단했으므로 evaluation에서 불일치로 본다.

## Schema와 Pipeline은 다르다

schema는 판단 케이스 한 장에 필요한 정보를 담는 key/value 목록이다. pipeline은 그 값을 어떤 순서로 처리하는지 나타내는 실행 흐름이다.

예를 들어 `data/scenarios.json`에서 `ai_utterance`, `user_utterance`, `event_type`, `expected_action`이 나란히 보인다고 해서 모두 같은 층위라는 뜻은 아니다.

| schema key | 읽는 법 |
| --- | --- |
| `ai_utterance` | AI가 말하던 문장 |
| `user_utterance` | 고객이 끼어든 발화 |
| `event_type` | 사람이 붙인 기준 고객 신호 |
| `expected_user_intent` | 사람이 붙인 기준 고객 의도 |
| `expected_action` | 사람이 정한 자연스러운 AI 행동 |

헷갈릴 때는 먼저 상황을 한 문장으로 요약하고, 그 상황을 key/value로 채운 뒤, policy가 실제로 낸 `actual_action`과 비교한다.

key별 세부 설명은 [Schema Keys](reference/schema-keys.md)를 본다.

## 기준값과 Runtime 해석 결과

`event_type`과 `expected_user_intent`는 현재 판단 케이스 원본에 들어 있는 기준값이다. 이 값들은 evaluation과 error analysis에서 기준으로 쓰며, runtime action 결정 로직이 그대로 베껴 쓰면 안 된다.

runtime에서 고객 신호 해석 결과를 남겨야 할 때는 별도 이름을 쓴다.

| 기준값 | runtime 결과 후보 | 비교 위치 |
| --- | --- | --- |
| `event_type` | `predicted_event_type` | 고객 신호 해석 점검 |
| `expected_user_intent` | `predicted_user_intent` | 고객 신호 해석 점검 |
| `expected_action` | `actual_action` | action evaluation |

피해야 할 흐름은 아래다.

```text
scenario.event_type
-> actual_action
```

허용하는 흐름은 아래다.

```text
transcript / speech signal
-> predicted_event_type / predicted_user_intent / confidence
-> actual_action
```

겉으로는 둘 다 고객 신호에서 action으로 가는 것처럼 보이지만, 앞쪽은 정답지를 실행 로직으로 쓰는 것이고 뒤쪽은 runtime 해석 결과를 행동 선택에 쓰는 것이다.

## 판단 케이스는 테스트 카드다

판단 케이스(`scenario`) 하나는 서비스 전체 플로우가 아니라 아래 정보를 묶은 작은 판단 단위다.

- AI가 현재 설명하던 업무 의도
- AI가 말하던 문장
- 고객이 중간에 넣은 신호
- 그 신호의 event type
- 고객 의도
- 자연스러운 expected action

이 단위가 작아야 `expected_action`과 `actual_action`을 비교할 수 있고, 실패 케이스를 다시 분류할 수 있다.

`Workbench`는 일부 UI title과 코드에 남아 있는 상위 UI 이름 후보다. 제품 컨셉이나 필수 표면으로 앞세우기보다, Playground와 Test Bench를 묶어 부를 때만 제한적으로 쓴다.

## 입력 경로와 판단 구조

입력 경로는 제품의 본질적 개념이 아니라 같은 판단 케이스를 텍스트, 대표 오디오 파일, 마이크 입력 중 어떤 방식으로 실행할지 정하는 adapter 층위다. 문서 본문에서는 "입력 경로"로 풀어 쓰고, 코드/API 필드가 필요할 때만 `input_mode`라고 쓴다.

| 입력 경로 | 코드/API에서 보이는 이름 | 역할 | 현재 MVP 위치 |
| --- | --- | --- | --- |
| 텍스트 입력 | `input_mode=text`, Text Replay | 텍스트 판단 케이스로 policy 판단을 빠르게 검증 | 필수 |
| 오디오 파일 입력 | `input_mode=audio_file`, Audio File Test | 대표 음성 파일에서 STT/signal 흐름을 연결 | 일부 연결 |
| 마이크 입력 | Mic Trial | live 입력과 latency를 확인 | 확장 예정 |

텍스트 입력은 음성 프로젝트를 포기하는 단계가 아니다. 오디오/STT 앞단을 잠시 고정하고, 뒤쪽 AI 행동 판단 구조를 먼저 검증하는 단계다.

## Event Type과 Action Label

`event_type`은 고객 신호이고, action label은 AI 행동이다.

| event_type | 고객 신호 | 기본 expected_action |
| --- | --- | --- |
| `no_speech` | 고객 발화 없음 | `continue` |
| `noise` | 배경음, 비언어 소리 | `continue` |
| `backchannel` | "네", "음", "알겠어요" 같은 맞장구 | `continue` 또는 `brief_ack` |
| `same_intent_question` | 같은 업무 안의 보충 질문 | `respond_and_continue` |
| `intent_shift` | 다른 업무 의도로 전환 | `stop_and_switch` |
| `complaint` | 불만, 긴급 발화 | `stop_and_switch` 또는 `handoff` |
| `ambiguous` | 의도가 불명확한 발화 | `ask_clarifying` |

같은 event type이라도 판단 케이스 metadata 수준의 tone/severity hint나 문맥에 따라 expected_action이 달라질 수 있다. 이때는 `notes`에 판단 근거를 남긴다.

값별 세부 설명은 [Event Types](reference/event-types.md)를 본다.

## Action Label 기준

| action label | 의미 |
| --- | --- |
| `continue` | 현재 발화를 그대로 이어간다 |
| `brief_ack` | 짧게 인정하고 이어간다 |
| `respond_and_continue` | 같은 주제 질문에 답하고 원래 설명으로 돌아간다 |
| `stop_and_switch` | 현재 발화를 멈추고 새 의도로 전환한다 |
| `ask_clarifying` | 의도가 불명확해 확인 질문을 한다 |
| `handoff` | AI가 처리하기 어렵다고 보고 상담사 연결 후보로 보낸다 |

`pause`는 현재 action label로 쓰지 않는다. 같은 주제 질문에 답하고 이어가는 행동은 `respond_and_continue`로 쓴다.

값별 세부 설명은 [Action Labels](reference/action-labels.md)를 본다.

## Policy Version 기준

policy version은 서로 다른 파이프라인을 뜻하지 않는다. 같은 판단 흐름에서 어떤 입력, 기준, 신호를 더해 비교했는지 남기는 이름이다.

| 표시 라벨 | 코드 식별자 | 읽는 법 |
| --- | --- | --- |
| Baseline | `baseline` | 최소 입력만 보고 판단하는 기준선 |
| Policy v1 | `policy_v1` | action label 설명, 예시, tone hint를 더한 현재 비교 대상 |
| Policy v2 | `policy_v2` | 필요할 때 새 신호나 기준을 추가해 비교할 다음 후보 |
| Policy v3 | `policy_v3` | complaint, ambiguous, safety guard 같은 더 넓은 기준을 볼 때의 후보 |

policy version은 "더 좋은 이름"이 아니라 **어떤 신호를 추가했을 때 어떤 실패가 줄었는지**를 비교하기 위한 단위다.

## 문서로 옮기기 전 체크

- 판단 케이스(`scenario`)를 전체 상담 플로우처럼 설명하지 않았는가?
- `event_type`과 action label을 같은 표면에 섞지 않았는가?
- `event_type`과 `predicted_event_type`을 같은 역할처럼 설명하지 않았는가?
- `pause`가 현재 label처럼 남아 있지 않은가?
- 텍스트 입력이나 Text Replay를 음성 단계의 대체물처럼 쓰지 않았는가?
- policy version마다 개선 목표가 함께 적혀 있는가?
- schema key 나열을 실행 순서처럼 설명하지 않았는가?
- 입력 경로(`input_mode`)를 제품 기능이나 AI 발화 방식처럼 설명하지 않았는가?
- `expected_action`과 `actual_action`을 서로 다른 label 체계처럼 설명하지 않았는가?
- 수치가 있으면 `results/runs/{run_id}/` 출처가 함께 있는가?
