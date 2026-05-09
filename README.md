# whisper-intent-interruption-detection

Whisper 기반 intent/interruption detection 실험과 구현을 위한 팀 사이드 프로젝트다.

## 현재 상태

Backend 의존성(FastAPI + Whisper STT + sentence-transformers)과 dev baseline(Poetry lock, ruff, pre-commit + detect-secrets)이 들어와 있다. Day 2 기준으로 scenario loader, 공통 타입, `baseline`/`policy_v1`, runner CLI, evaluator artifact, FastAPI API, 정적 Playground UI가 동작한다.

## Quickstart

```bash
# 1. 의존성 설치 (Python 3.11, Poetry 2.x)
poetry install

# 2. 테스트
poetry run pytest tests/ -v

# 3. 단일 scenario 실행
poetry run python src/runner.py --policy baseline --dataset data/scenarios.json --scenario-id commerce_no_speech_001

# 4. Test Bench run artifact 생성
poetry run python src/runner.py --policy policy_v1 --dataset data/scenarios.json --write-results

# 5. Backend API + Playground 실행
poetry run uvicorn backend.main:app --reload
```

Playground는 `http://127.0.0.1:8000`에서 열린다. 공식 수치는 화면 표시가 아니라 `results/runs/{run_id}/evaluation.json`을 기준으로 인용한다.

자세한 패키지 설명은 [src/backend/PACKAGES.md](src/backend/PACKAGES.md).

## 협업과 작업 가이드

- 협업 경계와 작업 라우팅: [CLAUDE.md](CLAUDE.md)
- 외부 공개 문서(mkdocs): [docs/](docs/)
- 내부 기준·결정·archive·임시 메모: [context/](context/)
- 현재 내부 기준 자료: [context/internal/](context/internal/)
- 결정·맥락 기록: [context/decisions/](context/decisions/)
- 작업 시 참고하는 가드: [.claude/rules/](.claude/rules/)
- 검증·분류용 report-only agent: [.claude/agents/](.claude/agents/)
- repo-local skill: [.claude/skills/](.claude/skills/)
