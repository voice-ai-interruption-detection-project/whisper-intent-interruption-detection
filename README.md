# whisper-intent-interruption-detection

Whisper 기반 intent/interruption detection 실험과 구현을 위한 팀 사이드 프로젝트다.

## 현재 상태

Backend 의존성(FastAPI + Whisper STT + sentence-transformers)과 dev baseline(Poetry lock, ruff, pre-commit + detect-secrets)이 들어와 있다. 하네스 코어 코드(`src/runner.py`, `src/policies/`, `src/evaluation/` 등)는 아직 작성 전.

## Quickstart

```bash
# 1. 의존성 설치 (Python 3.11, Poetry 2.x)
poetry install

# 2. Backend API 개발 모드 실행 (src/backend/main.py 작성 후)
poetry run uvicorn backend.main:app --reload

# 3. 테스트
poetry run pytest tests/ -v
```

자세한 패키지 설명은 [src/backend/PACKAGES.md](src/backend/PACKAGES.md).

## 협업과 작업 가이드

- 협업 경계와 작업 라우팅: [CLAUDE.md](CLAUDE.md)
- 외부 공개 문서(mkdocs): [docs/](docs/)
- 내부 기준 자료: [internal/](internal/)
- 결정·맥락 기록: [decisions/](decisions/)
- 작업 시 참고하는 가드: [.claude/rules/](.claude/rules/)
- 검증·분류용 report-only agent: [.claude/agents/](.claude/agents/)
- repo-local skill: [.claude/skills/](.claude/skills/)
