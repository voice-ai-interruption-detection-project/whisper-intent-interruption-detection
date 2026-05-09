# Coding Rules

이 파일은 Playground 코드 작업 시 참고하는 개발 가이드다. 작업 라우팅은 루트 [CLAUDE.md](../../CLAUDE.md)를 본다.

이 프로젝트는 Work Bench — Playground와 Test Bench 두 surface가 같은 runner로 정책 버전을 갈아끼워 결과를 비교하는 작업대 — 라서 **변경의 단위가 곧 비교의 단위**가 된다. 한 PR 안에서 동작 변경과 파일 이동이 섞이면 "왜 결과가 바뀌었는지"가 흐려진다. 아래 항목은 그 비교 가능성이 깨지지 않게 하는 작은 약속들이다.

## Dev baseline (코드 1커밋 직전)

아래 5개는 코드 첫 commit 전에 깔아둔다 — "Sensor는 실수가 보인 뒤"의 예외다. 이유는 늦게 깔수록 비대칭으로 비싸지기 때문(lock 없이 의존성이 굳으면 과거 run을 재현 못 살리고, secret 한 번 새면 회수 불가).

| 항목 | 도구 | 깔아두는 이유 |
| --- | --- | --- |
| 의존성 핀 + lock | `pyproject.toml` + uv (또는 poetry, pip-tools) | 정책 비교 외 변동(라이브러리 버전) 줄이기 |
| python 버전 핀 | `pyproject.toml`의 `requires-python` | 환경 차이 줄이기 |
| format/lint | ruff | reformat diff가 정책 변경 commit에 섞이지 않게 |
| pre-commit + secret scan | `pre-commit` + `detect-secrets` 또는 `gitleaks` | API key·HF token 노출 방지 |
| README quickstart | 3-5줄 (설치, 실행, 테스트) | 페어가 같은 환경 재현 가능 |

CI workflow, mypy strict, coverage threshold, devcontainer는 여기 안 넣는다 — 1단계 진행하면서 필요해지면 그때.

## 한 번에 하나의 변수

- 한 PR/실행에서 동시에 바뀐 변수가 늘어날수록 결과 차이의 원인이 흐려진다. policy 로직, threshold, dataset, evaluator 기준은 가능한 한 따로 바꾼다.
- 같이 바꿔야 하면 PR 본문에 어느 것이 주요 변경인지 명시한다.
- 정책 비교 run을 만들 때, `run_meta.json`의 `changed` 필드가 한 항목이면 가장 깔끔하다. 두 개 이상이면 "왜 같이 바뀌었는지"를 적는다.

## 리팩토링과 동작 변경 분리

- 파일 이동, 이름 변경, 함수 분리는 정책/평가 동작을 바꾸지 않는다는 게 전제다. 동작 변경(threshold 수정, 새 분기 추가)과 같은 commit에 섞지 않는다.
- 가능하면 두 commit으로 나눈다. 한 commit에 가야 하면 commit 본문에서 어느 hunk가 동작 변경인지 짚는다.
- 리팩 commit 직후에는 evaluator가 같은 결과를 내는지 (`action_accuracy`, `confusion_matrix`가 같은지) 확인한다.
- runner / policy / adapter 같은 구조 변경 commit 직전에는 `harness-structure-reviewer` agent로 boundary leak을 한 번 본다.

## Magic number 줄이기

- threshold, debounce, window 같은 숫자는 코드 안에 흩어두지 않는다. `src/policies/`의 생성자 인자나 named constant로 둔다.
- 그 값은 `policy.snapshot()`이 반환하는 dict에 들어가야 한다 — `run_meta.json`의 `policy_snapshot`으로 자동 노출된다.
- snapshot에 안 잡히는 숫자는 결과를 바꿀 수 없다는 게 invariant다.

## 주석은 경계 표식으로 쓴다

- public 함수, 모델, adapter, endpoint에는 "무엇을 책임지는가"를 한 문장 docstring이나 짧은 블록 주석으로 남긴다.
- 인라인 주석은 구현 순서 설명이 아니라 why, contract, invariant, boundary를 설명할 때만 단다.
- `runner`, `policy_snapshot`, `run artifact`, `input adapter`처럼 코드 식별자나 하네스 용어는 영어 그대로 써도 된다.
- 다만 설명 문장 전체를 전문 영어 문장으로 쓰지 않는다. "Validate request payload and return normalized response"보다 "요청 payload를 검증하고 정규화한 응답을 반환한다"처럼 쓴다.
- 외부 API 문구, 원문 인용, 에러 메시지처럼 영어가 기준인 경우에는 영어를 유지하되, 필요한 맥락은 한국어로 덧붙인다.

## Placeholder는 진짜 구현처럼 보이지 않게 한다

- 다음 구현을 위해 껍데기만 둔 코드에는 grep 가능한 `TO_DO:` 표식을 남긴다. 형식은 `TO_DO: 아직 {무엇}이 비어 있다. 다음: {구체적으로 구현할 것}`처럼 짧게 쓴다.
- `pass`, 빈 함수, 의미 없는 `return None`만 남겨두지 않는다. 호출될 수 있는 production 경로라면 `NotImplementedError("TO_DO: ...")`처럼 명시적으로 실패하게 둔다.
- API/UI 경계에서 아직 구현되지 않은 기능을 노출해야 하면 정상 결과처럼 보이는 mock payload를 반환하지 않는다. 가능하면 501/400 계열 오류나 `status: "not_implemented"`, `message: "TO_DO: ..."`처럼 미구현 상태가 응답에 드러나게 한다.
- 테스트 double이나 precomputed transcript처럼 실제 구현을 대체한 값은 허용한다. 대신 run artifact나 응답을 봤을 때 `fake`, `mock`, `precomputed` 같은 대체 출처가 snapshot, signals, metadata 중 하나에 드러나야 한다.
- 이런 대체값으로 만든 결과를 외부에 인용할 때는 실제 모델/STT 성능처럼 말하지 않는다. 예: "STT+policy 정확도"가 아니라 "precomputed transcript 기준 policy `action_accuracy`"처럼 조건을 함께 적는다.
- placeholder를 추가한 작업 메모에는 왜 지금 껍데기만 두는지와 다음 작업 단위를 적는다.

## 의존성과 외부 서비스

- 새 라이브러리, 외부 API, 모델 provider 도입 시 PR 본문 또는 commit message에 "왜 필요한가" + "어디까지 쓰이는가"를 같이 남긴다.
- 한 줄짜리 추가도 마찬가지다. 도입 시점에 범위를 못 박지 않으면 나중에 사용처를 코드에서 거꾸로 찾아야 한다.
- API key, credential, `.env`, 로컬 전용 파일은 커밋하지 않는다 (루트 [CLAUDE.md](../../CLAUDE.md) "작업 기준" 참조).

## 검증된 수치만 외부로

수치 인용 직전 가드는 [experiments.md "검증된 수치만 공유한다"](experiments.md#검증된-수치만-공유한다)를 따른다 — Playground 화면 수치를 외부에 옮기지 않는다는 invariant는 양쪽 surface 모두에 적용된다.

## 자동 체크는 작고 투명하게

- Guide(이 파일·`CLAUDE.md`)는 행동 전 방향, Sensor(hook, scanner, lint, smoke test)는 행동 후 교정 장치다.
- 문서 규칙, 체크리스트, 작은 helper는 작업을 빠르게 만들면 먼저 추가해도 된다.
- hook/scanner처럼 자동으로 확인하는 장치는 작업 흐름에 영향을 줄 수 있으니, 왜 필요한지와 어디에 적용되는지만 짧게 남긴다.
- 코드에서 자연스럽게 방지할 수 있는 실수는 구현에 녹인다. 예: runner는 같은 `run_id` 폴더가 이미 있으면 새 결과를 덮어쓰지 않는다.
- 새 Sensor를 추가할 때는 목적을 commit/PR 메모에 짧게 남긴다.

## 규칙 추가 기준

이 파일에 추가할 새 규칙은 "작업자가 다음 행동을 덜 헷갈리게 하는가"를 기준으로 본다. 길어지면 추가를 막기보다 파일을 나누거나 표현을 줄여서 찾기 쉽게 만든다.
