# whisper-intent-interruption-detection

음성 AI 상담에서 고객의 끼어들기와 의도 전환에 더 자연스럽게 반응하는 경험을 실험하고 구현하는 팀 사이드 프로젝트다.

현재 MVP의 초점은 AI가 말하는 중 들어온 고객 발화를 보고 다음 행동을 고르는 판단 구조를 검증하는 데 있다. Whisper/STT/audio adapter는 이 판단 구조를 음성 입력 쪽으로 연결하기 위한 구현 요소다.

## 현재 상태

Backend 의존성(FastAPI + Whisper STT + sentence-transformers)과 dev baseline(Poetry lock, ruff, pre-commit + detect-secrets)이 들어와 있다. 현재 구현 기준으로 판단 케이스(`scenario`) loader, 공통 타입, 텍스트 LLM 기반 `baseline`/`policy_v1`, runner CLI, evaluator artifact, FastAPI API, 정적 Playground UI, 대표 오디오 파일 입력(Audio File Test) adapter가 동작한다.

## Quickstart

```bash
# 1. 의존성 설치 (Python 3.11, Poetry 2.x)
poetry install

# 2. 테스트
poetry run pytest tests/ -v

# 3. 실제 LLM 판단을 쓸 때만 설정
export OPENAI_API_KEY=...
export OPENAI_ACTION_MODEL=gpt-5.4-mini

# 4. 단일 판단 케이스(scenario) 실행
poetry run python src/runner.py --policy baseline --dataset data/scenarios.json --scenario-id commerce_no_speech_001

# 5. Test Bench run artifact 생성
poetry run python src/runner.py --policy policy_v1 --dataset data/scenarios.json --write-results

# 6. 오디오 파일 입력(Audio File Test) fixture 생성 (OpenAI TTS)
poetry run python scripts/generate_audio_fixtures.py \
  --scenario-id commerce_shipping_to_refund_001

# 또는 macOS 로컬 TTS
poetry run python scripts/generate_audio_fixtures.py \
  --provider say \
  --all-speech

# 7. 오디오 파일 입력(Audio File Test) run artifact 생성
poetry run python src/runner.py \
  --policy policy_v1 \
  --dataset data/scenarios.json \
  --audio-manifest data/audio/manifest.json \
  --audio-transcriber precomputed \
  --write-results

# 8. Backend API + Playground 실행
poetry run uvicorn backend.main:app --reload
```

Playground는 `http://127.0.0.1:8000`에서 열린다. Test Bench Report(배치 평가 화면)에서는 입력 경로(`input_mode`)를 선택해 텍스트 판단 케이스 묶음과 audio files를 같은 run artifact 계약으로 실행할 수 있다. `OPENAI_API_KEY`가 없으면 실제 LLM policy 실행과 TTS fixture 생성은 실패한다. 오디오 파일 입력(Audio File Test)은 `precomputed` transcript adapter로도 같은 runner 흐름을 검증할 수 있다. 테스트는 fake LLM client로 네트워크 없이 검증한다. 공식 수치는 화면 표시가 아니라 `results/runs/{run_id}/evaluation.json`을 기준으로 인용한다.

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
