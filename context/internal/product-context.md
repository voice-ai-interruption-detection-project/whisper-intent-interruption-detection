# Product Context

이 문서는 세션을 시작할 때 프로젝트의 제품 의도를 짧게 되찾기 위한 내부 기준 자료다.

세부 schema, action label, run artifact, policy version 설명은 이 문서에 모두 넣지 않는다. 자세한 실행 기준은 [Current MVP](mvp/current.md), 용어 기준은 [Project Language Map](project-language-map.md), 평가 계약은 [Evaluation and Results Contract](evaluation-and-results-contract.md)를 본다.

## 핵심 의도

이 프로젝트의 장기 방향은 음성 AI 상담에서 고객의 끼어들기와 의도 전환에 더 자연스럽게 반응하는 경험을 실험하는 것이다.

현재 MVP의 초점은 AI가 말하는 중 들어온 고객 발화를 보고, AI가 다음 행동을 어떻게 고를지 검증하는 작은 실험에 있다.

중심 질문은 단순히 "고객이 말했는가?"가 아니다.

```text
고객 발화가 맞장구인가?
같은 주제 안의 질문인가?
다른 업무로 바뀐 요청인가?
불만이나 긴급 상황인가?

그렇다면 AI는 계속 말할까, 짧게 인정할까,
답하고 이어갈까, 멈추고 전환할까, 확인 질문을 할까?
```

## 먼저 보는 장면

```text
AI: 고객님의 상품은 현재 배송 중이며, 내일 오후 도착 예정입니다.
고객: 아 그게 아니라 환불받고 싶은데요.
```

나쁜 경험은 AI가 고객의 새 요청을 듣지 못하고 배송 안내를 계속하는 것이다.

좋은 경험은 AI가 하던 말을 멈추고, 고객의 환불 요청으로 상담 흐름을 바꾸는 것이다.

이 프로젝트는 이런 순간을 작게 잘라 판단 케이스로 만들고, AI 행동 판단이 더 자연스러운 선택을 하는지 비교한다.

## 현재 MVP의 현실적인 범위

현재 MVP는 제품 전체가 아니라 판단 구조를 검증한다.

포함하는 것:

- 커머스 상담 중 AI 발화에 고객 신호가 끼어드는 판단 케이스
- 고객 transcript와 speech signal을 바탕으로 한 AI 행동 판단
- baseline과 policy version의 판단 차이 비교
- expected_action과 actual_action 비교
- false stop, missed switch, action confusion 같은 실패 분석
- 대표 오디오 파일이 같은 판단 구조로 들어오는지 확인

후순위로 두는 것:

- 완성형 실시간 음성 상담 서비스
- 실제 콜센터 데이터 수집
- STT/TTS 자체 성능 최적화
- 운영 대시보드, QA 점수, 통화 요약, RAG 검색
- prosody 기반 감정 인식
- fine-tuning

fine-tuning을 하지 않는다는 뜻은 AI를 쓰지 않는다는 뜻이 아니다. 현재 기준은 학습보다 LLM action judge, prompt/criteria 비교, run artifact 검증을 우선한다.

## 입력 경로는 제품 개념이 아니다

Text Replay, Audio File Test, Mic Trial은 제품의 본질적 개념이 아니라 같은 판단 구조를 어떤 입력으로 실행해 볼지 나타내는 개발/테스트 경로다.

현재 읽는 법:

- Text Replay: 텍스트로 먼저 판단 구조를 빠르게 검증한다.
- Audio File Test: 대표 음성 파일을 transcript/signal adapter로 연결해 음성 프로젝트와의 접점을 확인한다.
- Mic Trial: live 입력, latency, browser permission 리스크를 나중에 확인하는 확장 슬롯이다.

코드와 run artifact에서는 `input_mode` 필드를 유지한다. 제품 설명에서는 "입력 경로" 또는 "테스트 입력 방식"으로 풀어쓴다.

입력 경로가 달라도 뒤쪽 판단 구조는 같아야 한다. Text Replay와 Audio File Test가 서로 다른 policy 판단 흐름을 타면 비교가 흔들린다.

## 하네스 용어를 읽는 기준

이 프로젝트에는 실험을 재현하기 위한 하네스 용어가 많다. 이 용어들은 필요하지만, 제품 의도보다 앞서면 문서가 왜곡된다.

| 하네스 용어 | 제품 맥락에서 읽는 법 |
| --- | --- |
| `scenario` | 전체 상담 여정이 아니라 AI 발화 중 고객 신호가 들어온 한 판단 케이스 |
| `AI Action Policy` | 고객 개입 상황에서 AI의 다음 행동을 고르는 판단 기준 |
| `expected_action` | 사람이 붙인 자연스러운 행동 기준 |
| `actual_action` | policy가 실행 후 고른 행동 |
| `Test Bench` | 여러 판단 케이스를 batch로 돌려 수치를 남기는 평가 표면 |
| `Playground` | 한 케이스를 보며 판단과 reason을 확인하는 조작 표면 |

세부 용어는 [Project Language Map](project-language-map.md)을 기준으로 한다.

## 성공 기준

현재 MVP가 닫혔다고 보려면 아래를 확인한다.

- 판단 케이스가 `data/scenarios.json`에 기준 원본으로 정리되어 있다.
- baseline과 하나 이상의 policy version이 같은 runner/evaluator로 비교된다.
- LLM prompt에 `expected_action`, `event_type`, `expected_user_intent`가 들어가지 않는다.
- Text Replay와 대표 Audio File Test가 같은 AI 행동 판단 입력으로 합류한다.
- 결과는 `results/runs/{run_id}/` 계약으로 남는다.
- 공유 문서의 수치는 run artifact에서 확인할 수 있다.

## 읽기 경계

일반 구현 작업에서는 현재 `context/internal/`과 코드 상태를 기준으로 한다.

하지만 제품 의도 복원, 문서 왜곡 점검, 과거 합의 검증을 할 때는 이 문서도 검토 대상이다. 그때는 회의 원문, `context/decisions/`, `context/archive/`를 evidence로 함께 본다.

초기 기획 원문은 [context/archive/product-planning](../archive/product-planning/)에 보관한다. archive는 현재 기준과 충돌할 수 있지만, 원래 의도를 복원할 때는 중요한 근거가 될 수 있다.

열린 선택지는 [Current MVP Iteration Plan](mvp/current-iteration-plan.md)의 candidate slots나 `context/decisions/`에서 다룬다. Product Context에는 세션 시작에 필요한 제품 의도와 범위만 남긴다.
