# Backend 패키지 가이드

> `src/backend/`에서 쓰는 Python dependency의 용도와 하네스 경계를 맞추기 위한 문서다.
> 정확한 버전 범위는 [pyproject.toml](../../pyproject.toml), 재현 가능한 해석 결과는 [poetry.lock](../../poetry.lock)을 기준으로 본다.

이 문서는 API 계약서나 PRD가 아니다. Backend 구현자가 패키지를 추가하거나 사용할 때, 현재 하네스의 책임 경계를 잃지 않기 위한 dependency guide다.

## 하네스 경계

`src/backend/`는 FastAPI 기반 API 표면이다. 정책 판정, 평가 기준, run artifact 생성 규칙을 backend 안에 다시 구현하지 않는다.

| 영역 | 맡는 것 | 맡지 않는 것 |
| --- | --- | --- |
| `src/backend/` | HTTP 요청/응답, 파일 업로드, input adapter, runner 호출 | policy 판정 로직, evaluator 재구현, result 직접 누적 |
| `src/runner.py` | Text/Audio/CLI/Test Bench가 공유하는 policy 실행 entry | HTTP 세부 구현 |
| `data/scenarios.json` | 기준 scenario와 `expected_action` | `actual_action`, metric, decision log |
| `results/runs/{run_id}/` | Test Bench run artifact, metric, decision log | 기준 scenario 원본 |

입력 방식이 Text Replay든 Audio File Test든 최종 판단은 같은 runner entry를 통과해야 한다. Backend endpoint는 그 entry를 감싸는 adapter로 둔다.

## 용어 기준

현재 action label vocabulary는 아래 6개다.

```text
continue
brief_ack
respond_and_continue
stop_and_switch
ask_clarifying
handoff
```

`pause`는 현재 action label로 쓰지 않는다. 같은 주제 질문에 답하고 이어가는 행동은 `respond_and_continue`로 쓴다.

`expected_action`은 사람이 정한 기준값이고, `actual_action`은 policy 실행 후 나온 결과값이다. 두 값은 같은 action label vocabulary를 쓰지만 저장 위치와 생성 시점이 다르다.

## API와 서버

### FastAPI (`>=0.136.1,<0.137.0`)

REST API 표면을 만든다.

- scenario 조회 또는 선택 요청 처리
- Text Replay 입력을 runner input으로 변환
- Audio File Test 파일 업로드와 transcript/signal adapter 연결
- runner 결과를 API response로 반환

Backend가 `evaluation.json`이나 `decision_logs.jsonl`을 직접 산출하는 구조로 만들지 않는다. 평가 결과가 필요하면 Test Bench run artifact를 읽거나, 별도 eval runner를 호출하는 방향을 먼저 검토한다.

`POST /runs`는 `input_mode`로 text scenario batch와 audio manifest batch를 선택한다. 두 경로 모두 evaluator가 `results/runs/{run_id}/` 계약을 만들고, Backend는 요청 모델을 검증한 뒤 evaluator를 호출한다.

현재 구현된 endpoint와 후보는 아래처럼 본다.

```text
GET  /scenarios
POST /scenarios/{scenario_id}/predict
POST /predict
POST /audio/transcribe
POST /audio/predict
GET  /runs/{run_id}
```

### Uvicorn (`>=0.46.0,<0.47.0`)

FastAPI 앱을 로컬 개발 서버로 실행한다.

```bash
poetry run uvicorn backend.main:app --reload
```

`src/backend/main.py`가 생긴 뒤 위 명령을 기준으로 README quickstart와 맞춘다.

### python-multipart (`>=0.0.27,<0.0.28`)

Audio File Test에서 브라우저가 업로드한 오디오 파일을 받기 위해 쓴다.

```python
from fastapi import UploadFile


async def read_audio_upload(file: UploadFile) -> bytes:
    return await file.read()
```

파일 업로드는 backend의 책임이지만, 업로드 이후 policy 판단은 runner input으로 변환해서 공통 흐름에 합류시킨다.

## 데이터 검증과 설정

### Pydantic (`>=2.13.4,<3.0.0`)

API 요청/응답 스키마와 runner adapter의 boundary type을 정의한다.

```python
from pydantic import BaseModel


class ScenarioCard(BaseModel):
    scenario_id: str
    level: int
    domain: str
    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    event_type: str
    expected_action: str
    expected_user_intent: str | None
    user_tone_hint: str
    has_user_speech: bool
    notes: str | None = None


class PolicyDecision(BaseModel):
    policy_version: str
    actual_action: str
    signals: dict
    reason: str
    confidence: float | None = None
```

`ScenarioCard`는 `data/scenarios.json`의 기준 원본을 읽는 타입이고, `PolicyDecision`은 실행 뒤 결과 타입이다. 둘을 같은 저장소 파일에 섞지 않는다.

### Pydantic Settings (`>=2.14.0,<3.0.0`)

환경 기반 설정을 typed config로 관리한다.

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    whisper_model: str = "base"
    sbert_model: str = "distiluse-base-multilingual-cased-v2"
    vad_threshold: float = 0.5
    intent_similarity_threshold: float = 0.7
```

threshold 같은 값이 policy 결과를 바꾼다면, 코드 안의 magic number로 흩어두지 않고 policy snapshot에 드러나야 한다.

### python-dotenv (`>=1.2.2,<2.0.0`)

로컬 개발용 `.env`를 읽을 때 쓴다.

```bash
WHISPER_MODEL=base
SBERT_MODEL=distiluse-base-multilingual-cased-v2
VAD_THRESHOLD=0.5
```

`.env`와 credential은 커밋하지 않는다.

### PyYAML (`>=6.0.3,<7.0.0`)

정책 표시명, intent description, 실험 설정 같은 사람이 읽는 설정 파일이 필요할 때 쓴다. 현재 기준 scenario 원본은 `data/scenarios.json`이다.

```yaml
policy_versions:
  baseline:
    display_name: Baseline
    goal: VAD-only 기준선 확인
  policy_v1:
    display_name: Policy v1
    goal: backchannel/noise의 false stop 감소
  policy_v2:
    display_name: Policy v2
    goal: intent shift의 missed switch 감소
  policy_v3:
    display_name: Policy v3
    goal: complaint/ambiguous까지 포함한 action 선택
```

YAML 설정이 policy 결과를 바꾸면 해당 값도 run metadata나 policy snapshot에서 추적 가능해야 한다.

## 음성 입력과 신호 처리

### openai-whisper (`>=20250625,<20250626`)

Audio File Test에서 오디오를 transcript로 바꾸는 STT 후보다.

- 대표 오디오 파일을 transcript로 변환
- STT 결과와 사람이 보정한 transcript를 비교
- `STT_uncertainty` 분석 후보를 남김

초기 하네스에서는 실제 Whisper 연결이 필수 전제가 아니다. 대표 Audio File Test는 mock/precomputed transcript로도 같은 runner 흐름에 합류할 수 있어야 한다.

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.wav", language="ko")
transcript = result["text"]
```

### OpenAI Speech API

`scripts/generate_audio_fixtures.py`에서 scenario의 `user_utterance`를 대표 오디오 fixture로 만들 때 쓴다. SDK 의존성을 추가하지 않고 HTTP API를 직접 호출한다.

- 기본 모델: `OPENAI_TTS_MODEL=gpt-4o-mini-tts`
- 기본 voice: `OPENAI_TTS_VOICE=coral`
- 기본 출력: WAV

TTS fixture는 입력 자료이며, 생성된 manifest에도 `actual_action`이나 metric을 넣지 않는다. 실제 정책 실행 결과는 `results/runs/{run_id}/`로만 남긴다.

### macOS `say`

OpenAI key 없이 로컬 개발용 TTS fixture를 만들 때 쓴다.

```bash
poetry run python scripts/generate_audio_fixtures.py --provider say --all-speech
```

기본 voice는 `Yuna`이며, `--voice` 또는 `LOCAL_TTS_VOICE`로 바꿀 수 있다. 이 경로는 개발 fixture용이고, 외부 공유 수치의 근거는 여전히 run artifact다.

### webrtcvad (`>=2.0.10,<3.0.0`)

Voice Activity Detection으로 사용자의 음성 신호 여부를 추정한다.

- baseline에서 "사용자가 말했는가" 신호 확인
- noise/no_speech/backchannel 경계의 입력 feature 후보
- Audio File Test에서 speech segment 추출

VAD-only는 "말했는가"는 볼 수 있지만 "무슨 의도인가"는 보지 못한다. 이 한계가 false stop과 missed switch를 줄이는 policy 비교의 출발점이다.

### soundfile (`>=0.13.1,<0.14.0`)

WAV/FLAC 등 오디오 파일 I/O에 쓴다.

```python
import soundfile as sf

samples, sample_rate = sf.read("audio.wav")
```

### librosa (`>=0.11.0,<0.12.0`)

오디오 로드, resampling, feature extraction에 쓴다.

- sample rate 정규화
- waveform feature 추출
- 대표 Audio File Test의 전처리

pitch, MFCC, prosody 기반 감정 인식은 현재 1차 하네스의 핵심 구현이 아니다. 필요한 feature만 adapter 안에 가둔다.

## Intent와 수치 계산

### sentence-transformers (`>=5.4.1,<6.0.0`)

문장 embedding으로 intent shift 후보를 계산한다.

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
current_emb = model.encode(["shipping_inquiry"])
user_emb = model.encode(["환불받고 싶은데요"])
similarity = cosine_similarity(current_emb, user_emb)[0][0]
```

intent similarity 기준은 policy 결과를 바꾸는 값이다. 기준을 바꾸면 policy snapshot이나 run metadata에서 추적되게 한다.

### NumPy (`>=2.4.4,<3.0.0`)

오디오 sample 배열, embedding vector, similarity 계산의 기초 연산에 쓴다.

### Pandas (`>=3.0.2,<4.0.0`)

scenario와 run 결과를 표 형태로 다룰 때 쓴다.

```python
import json
from pathlib import Path

import pandas as pd

payload = json.loads(Path("data/scenarios.json").read_text(encoding="utf-8"))
scenarios = pd.DataFrame(payload["scenarios"])
```

`data/scenarios.json`에는 `actual_action`, metric, decision log를 쓰지 않는다. 평가 결과를 DataFrame으로 만들더라도 저장 위치는 `results/runs/{run_id}/` 계약을 따른다.

### scikit-learn (`>=1.8.0,<2.0.0`)

embedding similarity, confusion matrix, accuracy 같은 평가 보조 계산에 쓴다.

```python
from sklearn.metrics import accuracy_score, confusion_matrix

accuracy = accuracy_score(expected_actions, actual_actions)
matrix = confusion_matrix(expected_actions, actual_actions, labels=action_labels)
```

수치를 공유 문서나 PR에 쓸 때는 `results/runs/{run_id}/evaluation.json`에서 확인한 값만 인용한다.

## 출력과 개발 도구

### Rich (`>=15.0.0,<16.0.0`)

CLI나 Test Bench 결과를 사람이 읽기 좋은 표로 보여줄 때 쓴다. API response의 canonical format을 Rich 출력에 맞추지 않는다.

### pytest (`>=9.0.3,<10.0.0`)

단위 테스트와 통합 테스트에 쓴다.

```bash
poetry run pytest tests/ -v
```

### pytest-asyncio (`>=1.3.0,<2.0.0`)

비동기 함수나 async route 테스트에 쓴다.

### pytest-cov (`>=7.1.0,<8.0.0`)

필요할 때 coverage를 확인한다. 현재 하네스의 초기 gate는 아니며, 반복 리스크가 보이면 강화한다.

### httpx (`>=0.28.1,<0.29.0`)

FastAPI endpoint 테스트 클라이언트로 쓴다.

```python
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/predict", json={...})
```

### black (`>=24.4.2,<25.0.0`)

코드 포맷팅에 쓴다. pre-commit 설정과 함께 맞춘다.

```bash
poetry run black src tests
```

### ruff (`>=0.4.4,<0.5.0`)

lint와 import 정렬에 쓴다.

```bash
poetry run ruff check src tests
```

### mypy (`>=2.0.0,<3.0.0`)

정적 타입 체크에 쓴다. strict type gate는 아직 현재 하네스의 필수 조건이 아니다.

```bash
poetry run mypy src
```

## 목표 구조 후보

아래 구조는 구현 후보이며, 현재 파일 존재 여부를 나타내는 inventory가 아니다.

```text
src/backend/
├── main.py                  # FastAPI app entry
├── config.py                # Settings
└── app/
    ├── models.py            # API/request/response schema
    ├── api/
    │   ├── scenarios.py     # scenario 조회
    │   ├── predict.py       # runner 호출 endpoint
    │   └── runs.py          # run artifact 조회가 필요할 때
    └── services/
        ├── audio.py         # upload/audio adapter
        ├── stt.py           # Whisper 또는 precomputed transcript adapter
        └── runner_client.py # policy 로직이 아니라 src/runner.py 호출 adapter
```

구조를 추가할 때는 `services/` 안에 policy 판정 로직이 자라지 않게 본다. 새 backend entry를 만들면 Playground, CLI, Test Bench와 같은 runner를 쓰는지 먼저 확인한다.

## 구현 전 체크

- Backend endpoint가 `src/runner.py`를 우회해 policy를 직접 판단하지 않는가?
- `data/scenarios.json`에 `actual_action`, metric, decision log를 쓰지 않았는가?
- 수치나 failure를 말할 때 `results/runs/{run_id}/` 출처가 있는가?
- `pause` 같은 과거 action label을 새 API schema에 되살리지 않았는가?
- STT가 불안정해도 precomputed transcript로 같은 runner 흐름을 검증할 수 있는가?
- 새 dependency를 추가했다면 왜 필요한지와 어디까지 쓰는지 PR/작업 메모에 남겼는가?

## 관련 기준 문서

- [Product Context](../../context/internal/product-context.md)
- [Project Language Map](../../context/internal/project-language-map.md)
- [Schema Key Reference](../../context/internal/reference/schema-keys.md)
- [Action Label Reference](../../context/internal/reference/action-labels.md)
- [Evaluation and Results Contract](../../context/internal/evaluation-and-results-contract.md)
- [Experiment Rules](../../.claude/rules/experiments.md)
