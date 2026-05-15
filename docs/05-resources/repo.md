# Repository & Code Structure

## 저장소 구조

```text
whisper-intent-interruption-detection/
├── README.md
├── pyproject.toml
├── poetry.lock
├── mkdocs.yml
├── data/
│   ├── scenarios.json
│   ├── datasets.json
│   ├── scenario_stats.json
│   ├── scenarios_policy_v2_edge.json
│   ├── scenarios_policy_v3_edge.json
│   ├── scenarios_policy_v3_challenge.json
│   └── audio/
│       ├── manifest.json
│       └── fixtures/
├── src/
│   ├── runner.py
│   ├── backend/
│   │   ├── main.py
│   │   └── static/
│   └── interruption_detection/
│       ├── runner.py
│       ├── models.py
│       ├── policies/
│       ├── pipelines/
│       ├── interpreter/
│       ├── action_selector/
│       ├── audio/
│       └── evaluation/
├── results/
│   └── runs/{run_id}/
├── tests/
├── docs/
└── context/
```

## 핵심 코드 경계

| 경로 | 역할 |
| --- | --- |
| `src/runner.py` | CLI entry. 단일 scenario 실행, batch run, audio manifest run 지원 |
| `src/interruption_detection/runner.py` | 공통 policy runner. 모든 surface가 이 경로를 통과 |
| `src/interruption_detection/models.py` | Scenario, RunnerInput, PolicyInput, PolicyDecision, RunDecisionLog 등 공통 타입 |
| `src/interruption_detection/policies/` | `baseline`, `policy_v1`, `policy_v2`, `policy_v3`, `policy_v3_1` 등록 |
| `src/interruption_detection/pipelines/decision_pipeline.py` | judgment, interpreter, selector를 묶어 `PolicyDecision` 생성 |
| `src/interruption_detection/audio/` | Audio File Test manifest, STT/precomputed transcriber, audio adapter |
| `src/interruption_detection/evaluation/` | Test Bench evaluator, audio evaluator, run artifact reader |
| `src/backend/main.py` | FastAPI API. runner/evaluator를 직접 호출하는 얇은 adapter |
| `src/backend/static/` | 정적 Playground/Test Bench UI |

## 설치와 실행

```bash
# Python 3.11, Poetry 2.x
poetry install

# 테스트
poetry run pytest tests/ -q

# 단일 판단 케이스 실행
poetry run python src/runner.py \
  --policy policy_v3_1 \
  --dataset data/scenarios.json \
  --scenario-id commerce_shipping_to_refund_001

# Test Bench run artifact 생성
poetry run python src/runner.py \
  --policy policy_v3_1 \
  --dataset data/scenarios.json \
  --write-results

# Audio File Test run artifact 생성
poetry run python src/runner.py \
  --policy policy_v1 \
  --dataset data/scenarios.json \
  --audio-manifest data/audio/manifest.json \
  --audio-transcriber precomputed \
  --write-results

# Backend API + Playground
poetry run uvicorn backend.main:app --reload
```

Playground는 `http://127.0.0.1:8000`에서 열립니다.

실제 LLM 판단을 실행하려면 `OPENAI_API_KEY`가 필요합니다.

```bash
export OPENAI_API_KEY=...
export OPENAI_ACTION_MODEL=gpt-5.4-mini
```

테스트는 fake LLM client를 사용하므로 네트워크 없이 실행됩니다.

## 결과 파일

새 평가 결과는 아래 계약으로 남습니다.

```text
results/runs/{run_id}/
├── run_meta.json
├── evaluation.json
├── decision_logs.jsonl
└── error_analysis.md
```

공개 문서나 발표에서 수치를 말할 때는 `run_id`, dataset, policy version, `evaluation.json` 경로를 함께 남깁니다.

## 최신 주요 Run

| run_id | dataset | policy | action_accuracy |
| --- | --- | --- | ---: |
| `20260515_112306_policy_v2` | `core` | `policy_v2` | 0.8667 |
| `20260515_111953_policy_v3_1` | `core` | `policy_v3_1` | 0.9000 |
| `20260515_110153_policy_v2` | `policy_v3_challenge` | `policy_v2` | 0.7778 |
| `20260515_111904_policy_v3_1` | `policy_v3_challenge` | `policy_v3_1` | 0.9444 |

## MkDocs

```bash
poetry run mkdocs serve
poetry run mkdocs build --strict
```

현재 `pyproject.toml`에는 MkDocs 관련 패키지가 runtime dependency로 들어 있지 않을 수 있습니다. 로컬에서 빌드하려면 `mkdocs`, `mkdocs-material`, `pymdown-extensions`가 설치되어 있어야 합니다.

## 다음 후보

- `policy_v3_1` 반복 실행으로 LLM 변동성 확인
- `commerce_payment_follow_001`, `commerce_complaint_001` 회귀 분석
- ambiguous 케이스 기준 정리
- 독립적인 action selector 구조 실험
