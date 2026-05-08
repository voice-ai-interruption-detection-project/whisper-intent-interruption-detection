# Product Context

이 문서는 프로젝트의 제품 방향과 실행 기준을 다시 잡을 수 있게 남기는 내부 기준 자료다.

현재 action label, 평가 계약, run artifact 기준에 맞춰 제품 맥락을 정리한다. 세부 용어는 [Project Language Map](project-language-map.md)과 [reference](reference/README.md)를 우선한다.

## 한 줄 기준

이 프로젝트는 전체 상담 AI 앱을 바로 만드는 프로젝트가 아니다.

AI가 말하는 중 고객 신호가 들어온 한 순간을 scenario로 잘라 보고, AI Action Policy가 어떤 action label을 선택해야 자연스러운지 Text Replay와 대표 Audio File Test로 검증하는 실험 콘솔이다.

```text
AI speaking
-> customer signal
-> transcript / event / intent 해석
-> AI Action Policy
-> expected_action과 actual_action 비교
-> failure와 다음 수정점 기록
```

## Active 기준 위치

과거 배경 자료가 archive로 이동해도 작업 기준은 아래 위치를 우선한다.

| 기준 | 위치 |
| --- | --- |
| 제품 문제, 현재 범위, 비목표, 남은 결정 후보 | 이 문서 |
| 용어 층위와 읽는 순서 | [Project Language Map](project-language-map.md) |
| schema key와 enum value | [Schema Keys](reference/schema-keys.md) |
| event type과 action label | [Event Types](reference/event-types.md), [Action Labels](reference/action-labels.md) |
| expected/actual, metric, failure, run artifact | [Evaluation and Results Contract](evaluation-and-results-contract.md) |
| 한 scenario의 끝까지 흐름 | [Scenario Worked Example](scenario-worked-example.md) |
| 결정 이유와 대안 | [decisions](../decisions/) |

## 먼저 보는 고객 장면

```text
AI: 고객님의 상품은 현재 배송 중이며, 내일 오후 도착 예정입니다.
고객: 아 그게 아니라 환불받고 싶은데요.
```

나쁜 경험은 AI가 고객의 새 요청을 듣지 못하고 배송 안내를 계속하는 것이다.

좋은 경험은 AI가 하던 말을 멈추고, 고객의 환불 요청으로 상담 흐름을 바꾸는 것이다.

이 프로젝트에서 중요한 질문은 "사용자가 말했는가"에서 끝나지 않는다. 고객 발화가 맞장구인지, 같은 업무 안의 질문인지, 다른 업무로의 전환인지, 불만/긴급 상황인지 구분한 뒤 AI의 다음 행동을 골라야 한다.

## 대상 사용자

| 사용자 | 이 프로젝트에서 필요한 것 |
| --- | --- |
| AI Engineer | scenario별 입력, event type, intent 해석, expected/actual action, policy reason, failure를 확인한다 |
| Reviewer / Interviewer | VAD-only보다 무엇이 나아졌는지, 어떤 데이터와 평가 기준으로 확인했는지 본다 |
| Future Operator | 전환 실패, 불만/긴급 발화, 상담사 연결 후보를 나중에 운영 관점으로 볼 수 있다 |

현재 구현 단위의 직접 사용자는 AI Engineer와 Reviewer다. Future Operator는 후속 확장 관점으로만 둔다.

## 범위

### 포함

| 범위 | 기준 |
| --- | --- |
| Scenario Bank | 커머스 상담 상황을 작게 자른 테스트 카드. 현재 `data/scenarios.json`이 기준 원본이다 |
| Text Replay | scenario 또는 직접 입력한 텍스트로 policy 판단을 빠르게 검증한다 |
| 대표 Audio File Test | 음성 프로젝트라는 연결고리를 확인한다. STT가 불안정하면 mock/precomputed transcript를 허용한다 |
| AI Action Policy 비교 | VAD-only baseline에서 시작해 신호를 추가했을 때 어떤 실패가 줄어드는지 본다 |
| Evaluation | `expected_action`과 `actual_action`을 비교하고 failure를 분류한다 |
| Error Analysis | 실패 케이스를 다음 scenario, threshold, rule 조정 후보로 돌린다 |

### 제외

| 비목표 | 이유 |
| --- | --- |
| 완성형 실시간 음성 상담 서비스 | 실시간 STT, TTS, 상태 관리까지 포함하면 현재 범위가 커진다 |
| 실제 콜센터 데이터 수집 | 개인정보와 데이터 확보 문제가 크다 |
| STT/TTS 자체 최적화 | 핵심은 음성 모델 성능보다 고객 신호를 AI 행동으로 바꾸는 판단 구조다 |
| 상담 운영 대시보드 | QA 점수, 통화 요약, RAG 검색은 별도 제품 범위다 |
| audio prosody 기반 감정 인식 | pitch, RMS, speaking rate 같은 음성 feature extraction/modeling은 1주차 핵심 구현이 아니다 |
| fine-tuning | 초기 구현은 rule과 pretrained embedding 기반 검증으로 충분하다 |

## 입력 모드 기준

| input_mode | 역할 | 현재 단계 기준 |
| --- | --- | --- |
| Text Replay | 텍스트 scenario로 AI Action Policy를 빠르게 검증한다 | 필수 |
| Audio File Test | 대표 음성 파일과 transcript를 policy input으로 연결한다 | 대표 케이스만 연결 |
| Mic Trial | live 입력, latency, browser permission 리스크를 확인한다 | 후순위 확장 슬롯 |

입력 방식이 달라도 뒤쪽 판단 구조는 같아야 한다. Audio File Test나 Mic Trial이 Text Replay와 다른 policy 판단 흐름을 타면 policy version 비교가 흔들린다.

## 제품 표면 기준

페어 중 Workbench, Playground, Test Bench가 섞여 이해가 어려웠기 때문에 현재 제품 표면은 아래처럼 나눠 읽는다.

| 표면 | 역할 | 현재 단계 기준 |
| --- | --- | --- |
| Playground | 단일 scenario를 고르고 입력을 바꿔 policy 판단과 reason을 확인하는 조작 화면 | Text Replay와 대표 Audio File Test 진입점 후보 |
| Test Bench | scenario set에 policy version을 batch로 돌리고 run artifact를 남기는 평가 표면 | 수치 인용과 비교의 기준 |
| Workbench | Playground와 Test Bench를 함께 묶는 상위 실험 콘솔 이름 | UI/문서에서 쓸 수 있는 제품 표면 후보 |

현재 구현 판단에서는 Test Bench run artifact가 수치의 기준이고, Playground/Workbench는 사용자가 판단 흐름을 볼 수 있게 만드는 표면이다. Workbench가 있다고 해서 완성형 상담 앱을 만든다는 뜻은 아니다.

## Policy 비교 기준

| 표시 라벨 | 코드 식별자 | 개선 목표 |
| --- | --- | --- |
| Baseline | `baseline` | VAD-only 기준선. 고객 음성 신호만 보고 개입 판단을 하는 한계를 본다 |
| Policy v1 | `policy_v1` | backchannel/noise에서 false stop을 줄인다 |
| Policy v2 | `policy_v2` | intent shift에서 missed switch를 줄인다 |
| Policy v3 | `policy_v3` | complaint, ambiguous, scenario metadata 수준의 tone/severity hint까지 포함해 action label을 고른다 |

최종 메시지는 "좋은 interruption detector를 만들었다"보다 "고객 개입 상황을 AI의 다음 행동으로 바꾸는 판단 구조를 만들고 비교했다"에 가깝다.

## 성공 기준

현재 구현 단위가 제품/실험 단위로 닫히려면 아래를 확인한다.

- 상황 난이도별 scenario bank가 있다.
- `data/scenarios.json`에는 기준 원본과 `expected_action`만 있다.
- baseline과 policy version을 같은 runner/evaluator로 비교한다.
- Text Replay에서 expected/actual action 비교가 가능하다.
- 대표 Audio File Test가 같은 AI Action Policy input으로 합류한다.
- result는 `results/runs/{run_id}/` 계약으로 남긴다.
- false stop, missed switch, action confusion 같은 failure가 error analysis로 이어진다.
- README/report에는 run artifact에서 확인한 수치만 인용한다.

## 현재 기준으로 닫힌 것

- 초기 완료 방향은 Text Replay와 대표 Audio File Test다.
- Mic Trial은 현재 필수 평가가 아니라 후순위 확장 슬롯이다.
- `pause`는 현재 action label로 쓰지 않는다.
- 같은 주제 질문에 답하고 이어가는 행동은 `respond_and_continue`로 쓴다.
- `brief_ack`는 현재 action label vocabulary에 포함한다. 나중에 `continue`로 합치려면 별도 결정을 남긴다.
- `data/scenarios.json`에는 `actual_action`, metric, decision log를 넣지 않는다.
- `data/scenarios.json`의 30개 scenario는 현재 시작점이다. event/action 분류는 evaluation과 error analysis를 보며 조정할 수 있다.
- 실험 결과는 `results/runs/{run_id}/` 아래에 저장한다.

## 남은 결정 후보

아래는 실제 변경이 일어나면 `decisions/`에 사안별로 기록한다.

| 사안 | 결정이 필요한 순간 |
| --- | --- |
| audio sample 목표 수 | Audio File Test 범위를 10개, 20개 이상, 대표 케이스 중심 중 하나로 고정할 때 |
| `brief_ack` 유지 여부 | `continue`와 합치거나 독립 label로 계속 유지할 때 |
| complaint와 `handoff` 기준 | 불만/긴급 발화를 `stop_and_switch`와 `handoff` 중 어디로 보낼지 severity 기준을 세울 때 |
| STT 연결 방식 | 실제 Whisper/API, local Whisper, mock/precomputed transcript의 책임 경계를 정할 때 |
| intent similarity 기준 | SBERT 비교 대상을 intent label, intent description, 예시 발화 중 무엇으로 둘지 정할 때 |
| 최종 발표 초점 | 제품 데모, 실험 결과, 실패 분석 중 무엇을 앞세울지 정할 때 |

## Archive로 보내는 내용

초기 기획 원문은 [archive/product-planning](../archive/product-planning/)에 보관한다. 아래 내용은 active 기준으로 쓰지 않고, 필요하면 archive의 history/evidence로만 본다.

- `pause`를 현재 action label처럼 설명하는 문장
- 실험 전 목표 수치를 실제 결과처럼 보이게 쓰는 문장
- flat `results/evaluation.json`, `results/decision_logs.jsonl` 구조
- Text Replay를 음성 프로젝트의 대체물처럼 설명하는 문장
- 날짜별 실행 계획을 현재 완료 상태처럼 보이게 쓰는 문장
