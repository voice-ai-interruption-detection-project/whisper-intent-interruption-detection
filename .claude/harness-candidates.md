# Development Harness Backlog

이 문서는 앞으로 갖출 개발 하네스 항목을 모아둔 backlog다. 지금 당장 구체 구현이나 강제 규칙으로 박아두기보다, 실제 코드와 실험 흐름이 생기면서 알맞은 형태로 잡아간다.

현재 루트 `CLAUDE.md`와 `.claude/rules/`가 실제 작업 가드다. 이 파일의 항목은 commit gate, PR gate, agent 호출 의무가 아니다. 개발 중 필요성이 선명해지면 작은 단위로 `.claude/rules/`, 설정 파일, hook, test에 반영한다.

## 구체화 기준

- 같은 혼선이나 실수가 두 번 이상 반복된다.
- 한 번의 실수로 credential, 실험 결과, 공개 수치 신뢰성이 크게 깨진다.
- 사람이 매번 기억해서 확인하기 어렵다.
- 팀원이 같은 저장소만 보고 재현해야 하는 절차가 생긴다.

## 예정 항목

| 항목 | 언제 구체화하나 | 가능한 형태 |
| --- | --- | --- |
| Toolchain baseline | 첫 실제 코드가 들어오거나 페어가 로컬 환경을 맞춰야 할 때 | `pyproject.toml`, Python version pin, lockfile, ruff, pytest 설정 |
| Pre-commit / secret scan | API key, 모델 token, `.env`가 필요한 순간 | `.pre-commit-config.yaml`, `detect-secrets` 또는 `gitleaks` |
| Config/runtime 규약 | threshold, model name, provider, env var가 생길 때 | `.claude/rules/config.md`, `.env.example`, snapshot 계약 |
| Architecture guide | `src/` 구조가 생기고 runner / policy / adapter / evaluator 경계가 드러날 때 | `.claude/rules/architecture.md` |
| Verification matrix | 작업 종류별 확인 명령이 반복될 때 | `.claude/rules/workflow.md`의 검증 표 |
| Harness scanner | 구조 위반이 리뷰에서 반복될 때 | repo-local agent 또는 작은 script |
| Placeholder/mock 반환 scanner | `TO_DO:` 없이 껍데기 구현이 남거나 mock 반환이 실제 구현처럼 보이는 일이 반복될 때 | `rg` 기반 scanner, lint helper, 또는 review checklist |
| Result overwrite guard | run artifact를 자동 생성하기 시작할 때 | runner 테스트 또는 파일 존재 체크 |
| Fixture/data write guard | 기준 데이터와 결과 데이터가 섞일 위험이 보일 때 | hook, test, 또는 agent scan |
| Commit/PR template | PR 설명에서 run id, dataset, 검증 명령이 자주 빠질 때 | PR template 또는 workflow 규칙 보강 |
| CI | 로컬 검증 누락이 반복되거나 팀원이 늘어날 때 | GitHub Actions 등 최소 lint/test workflow |

## 항목별 메모

### Toolchain baseline

초기에는 과하게 만들지 않는다. 실제 Python 코드가 들어오면 Python 버전, 의존성 lock, formatter/linter, pytest만 먼저 둔다. coverage threshold, mypy strict, devcontainer는 반복 필요가 보인 뒤 검토한다.

### Config/runtime 규약

실험 프로젝트에서는 기록된 값과 실제 실행값이 다르면 결과 비교가 깨진다. threshold, debounce window, model/provider, evaluation criteria는 코드에 흩뿌리지 말고 실행 시점 config와 run snapshot에 함께 드러나게 만드는 방향을 검토한다.

### Architecture guide

현재 agent 정의에는 `contracts`, `input_adapters`, `policies`, `runner`, `evaluation`, `results` 경계가 초기 구조 언어로 잡혀 있다. 실제 `src/`가 생기면 사람이 읽는 구조 가이드로 옮길지 판단한다.

### Verification matrix

작업 종류별로 "무엇을 실행해야 충분한가"가 반복되면 표로 만든다. 예: policy 변경, runner 변경, input adapter 변경, result artifact 변경, README 수치 변경.

### Sensor

Guide는 행동 전 방향을 잡고, Sensor는 행동 후 자동으로 잡는다. 처음부터 많은 hook을 두지 말고, 비용이 큰 실수부터 작고 투명한 장치로 만든다.

Placeholder scanner를 만들게 되면 `TO_DO:`, `pass`, `return None`, `NotImplementedError`, `mock`/`fake` 반환을 한 번에 훑되, 테스트 double과 production 경로를 구분하는 쪽을 우선한다.
