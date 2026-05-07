# Coding Rules

이 파일은 코드 작업 시 항상 켜둘 가드다. 실험(Test Bench) 측 가드는 같은 layer의 [experiments.md](experiments.md)에 있다. 두 파일은 영역만 나누고 형식은 맞춰 둔다. Playground 작업은 이 파일만 적용된다.

이 프로젝트는 Work Bench — Playground와 Test Bench 두 surface가 같은 runner로 정책 버전을 갈아끼워 결과를 비교하는 작업대 — 라서 **변경의 단위가 곧 비교의 단위**가 된다. 한 PR 안에서 동작 변경과 파일 이동이 섞이면 "왜 결과가 바뀌었는지"가 흐려진다. 아래 항목은 그 비교 가능성이 깨지지 않게 하는 작은 약속들이다.

깊은 근거는 [docs/harness/research/sprint4-code.md](../../docs/harness/research/sprint4-code.md)에 있다 — 이 가드들은 거기서 "바로 가져올 것" + "추천 도입 순서 1번"에 해당하는 항목만 추렸다.

## Dev baseline (코드 1커밋 직전)

[plan.md](../../docs/harness/plan.md)의 0단계 항목. 아래 5개는 코드 첫 commit 전에 깔아둔다 — "Sensor는 실수가 보인 뒤"의 예외다. 이유는 늦게 깔수록 비대칭으로 비싸지기 때문(lock 없이 의존성이 굳으면 과거 run을 재현 못 살리고, secret 한 번 새면 회수 불가).

| 항목 | 도구 | 깔아두는 이유 |
| --- | --- | --- |
| 의존성 핀 + lock | `pyproject.toml` + uv (또는 poetry, pip-tools) | 정책 비교 외 변동(라이브러리 버전) 차단 |
| python 버전 핀 | `pyproject.toml`의 `requires-python` | 환경 차이 차단 |
| format/lint | ruff | reformat diff가 정책 변경 commit에 섞이지 않게 |
| pre-commit + secret scan | `pre-commit` + `detect-secrets` 또는 `gitleaks` | API key·HF token 새는 사고 차단 |
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

## Magic number 금지

- threshold, debounce, window 같은 숫자는 코드 안에 흩어두지 않는다. `src/policies/`의 생성자 인자나 named constant로 둔다.
- 그 값은 `policy.snapshot()`이 반환하는 dict에 들어가야 한다 — `run_meta.json`의 `policy_snapshot`으로 자동 노출된다.
- snapshot에 안 잡히는 숫자는 결과를 바꿀 수 없다는 게 invariant다.

## 의존성과 외부 서비스

- 새 라이브러리, 외부 API, 모델 provider 도입 시 PR 본문 또는 commit message에 "왜 필요한가" + "어디까지 쓰이는가"를 같이 남긴다.
- 한 줄짜리 추가도 마찬가지다. 도입 시점에 범위를 못 박지 않으면 나중에 사용처를 코드에서 거꾸로 찾아야 한다.
- API key, credential, `.env`, 로컬 전용 파일은 커밋하지 않는다 (루트 [CLAUDE.md](../../CLAUDE.md) "작업 기준" 참조).

## 검증된 수치만 외부로

- README, report, presentation, slack에 수치를 인용할 때는 `results/runs/{run_id}` 가 존재하고 같은 값을 가져야 한다.
- **Playground 화면에서 본 수치는 외부 인용 금지** — Test Bench batch로 한 번 돌려서 run artifact를 만든 다음에만 인용한다.
- 외부 공유 전에는 `result-evidence-checker` agent로 한 번 더 본다. (이 항목은 [experiments.md](experiments.md)와 일부러 겹친다 — 인용 직전에 둘 다 켜진다.)

## Sensor는 실수가 보인 뒤

- Guide(이 파일·`CLAUDE.md`·`docs/harness/`)는 행동 전 방향, Sensor(hook, scanner, lint, smoke test)는 행동 후 교정 장치다.
- 새 차단 장치는 같은 실수가 반복되거나 한 번의 비용이 큰 지점이 보였을 때만 추가한다. 처음부터 두껍게 깔지 않는다.
- 코드에서 막을 수 있는 실수는 작성 시점에 막는다 — 예: runner는 같은 `run_id` 폴더가 이미 있으면 두 번째 실행을 거부하도록 작성한다.
- 새 Sensor를 추가할 때는 어느 실수 패턴이 트리거였는지 commit message에 짧게 남긴다.

## 빼면 실수하는가

이 파일에 추가할 새 규칙은 [experiments.md](experiments.md)와 같은 기준 — "빼면 실수하는가" — 을 통과해야 한다. 두 파일이 같이 길어지면 작업자가 어느 쪽을 봐야 할지 헤맨다.
