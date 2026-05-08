# Backend 패키지 도구 설명

> 상담 AI 끼어들기 감지 실험 콘솔의 백엔드 dependencies 가이드
> 작업 배경(contract 아님): [context/internal/product-context.md](../../context/internal/product-context.md)

## 📋 개요

이 프로젝트는 음성 AI 상담 중 사용자의 끼어들기와 맥락 전환을 감지하는 실험 콘솔입니다.
backend 패키지들은 다음 세 가지 핵심 기능을 지원합니다:

1. **REST API 서버**: 프론트엔드와의 통신
2. **음성 신호 처리**: VAD(Voice Activity Detection), STT(Speech-to-Text), 오디오 파일 분석
3. **Intent 분석**: 사용자 발화의 의도 변화 감지 및 AI Action Policy 판단

> **하네스 invariant**: `src/backend/`는 API 표면이다. 정책 판정·평가 로직을 직접 구현하지 않고 `src/runner.py`를 호출한다. 다른 surface(Playground, demo, CLI, Test Bench eval)와 동등하게 단일 runner를 통과한다 (`.claude/rules/experiments.md` 참조).

---

## 🔌 API & 서버 (FastAPI 스택)

### FastAPI (>=0.136.1)
**용도**: REST API 서버 구축

- Scenario 관리 API
- 입력 모드별 처리 (Text Replay, Audio File Test)
- AI Action Policy 실행 및 결과 반환
- Decision Log 저장
- Evaluation 결과 산출

**주요 엔드포인트**:
- `POST /scenario/<id>` - 시나리오 선택 후 판단 실행
- `POST /predict` - 텍스트 또는 오디오 입력으로 action 예측
- `GET /results` - evaluation 결과 조회

### Uvicorn (>=0.46.0)
**용도**: FastAPI 앱 실행 (ASGI 서버)

```bash
uvicorn main:app --reload
```

---

## 📊 데이터 검증 & 설정 (Pydantic 스택)

### Pydantic (>=2.13.4)
**용도**: API 요청/응답 스키마 정의 및 검증

**주요 모델**:
```python
# Scenario 데이터 구조
class Scenario(BaseModel):
    scenario_id: str
    level: str  # difficulty
    domain: str  # e.g., "commerce"
    ai_current_intent: str
    ai_utterance: str
    user_utterance: str
    event_type: str
    expected_action: str
    has_user_speech: bool
    # ... etc

# AI Action Policy 결과
class PolicyDecision(BaseModel):
    policy_version: str
    actual_action: str
    signals: dict
    reason: str
    confidence: float
```

### Pydantic Settings (>=2.14.0)
**용도**: 환경 기반 설정 관리

```python
# .env 파일로부터 로드
class Settings(BaseSettings):
    whisper_model: str = "base"  # STT 모델 선택
    sbert_model: str = "sentence-transformers/..."  # Intent embedding
    vad_threshold: float = 0.5
    intent_similarity_threshold: float = 0.7
```

### python-dotenv (>=1.2.2)
**용도**: `.env` 파일에서 환경 변수 로드

```bash
WHISPER_MODEL=base
SBERT_MODEL=distiluse-base-multilingual-cased-v2
VAD_THRESHOLD=0.5
```

---

## 🎵 음성 신호 처리

### openai-whisper (>=20250625)
**용도**: Speech-to-Text (STT) - 오디오 파일을 텍스트로 변환

**역할**:
- Audio File Test 입력 모드의 STT 처리
- 음성 파일 → 텍스트 전사(transcript)
- 불확실성 점수 제공 (confidence level)

**사용 예**:
```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.wav", language="ko")
transcript = result["text"]
confidence = result.get("confidence", 0.5)
```

### WebRTC VAD (>=2.0.10)
**용도**: Voice Activity Detection - 음성 감지

**역할**:
- P0 baseline의 기본 신호: "사용자가 말했는가?"
- 오디오 파일에서 음성 활동 구간 감지
- backchannel(맞장구) vs actual speech 판단 보조

**문제점** (이 프로젝트에서 해결하려는 것):
- VAD-only는 "사용자가 말했는가"만 알 수 있음
- "뭐라고 말했는가?" "주제가 바뀌었는가?"는 판단 불가
- 결과: false stop (맞장구도 중단), missed switch (주제 전환 놓침)

### Soundfile (>=0.13.1)
**용도**: 오디오 파일 I/O - WAV, FLAC 등 읽기/쓰기

```python
import soundfile as sf

data, samplerate = sf.read("audio.wav")
# data: numpy array of audio samples
```

### Librosa (>=0.11.0)
**용도**: 음성 신호 분석 및 전처리

**기능**:
- 오디오 로드 및 resampling
- Mel-spectrogram 변환
- 음성 특성 추출 (pitch, MFCC, etc.)
- 음향 특성 기반 backchannel 판단 보조

**사용 예**:
```python
import librosa

y, sr = librosa.load("audio.wav")
mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
```

---

## 🧠 Intent Shift Detection (의도 변화 감지)

### sentence-transformers (>=5.4.1)
**용도**: Semantic embedding - 문장의 의미를 벡터로 변환

**역할**:
- Intent shift 감지의 핵심
- 사용자 발화 → 임베딩 벡터
- 기존 intent와의 유사도 계산 (cosine similarity)
- 다음 질문: "새로운 intent로 전환했는가?"

**사용 예**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

current_intent = "배송조회"  # "Delivery Status"
user_utterance = "환불받고 싶은데요"  # "I want a refund"

current_emb = model.encode(current_intent)
user_emb = model.encode(user_utterance)

similarity = cosine_similarity(current_emb, user_emb)
# similarity < threshold → intent shift detected
```

---

## 📈 데이터 처리 & 분석

### NumPy (>=2.4.4)
**용도**: 수치 계산의 기초

- 오디오 신호 배열 연산
- 유사도 계산 (cosine similarity)
- 신호 정규화, normalization

### Pandas (>=3.0.2)
**용도**: 시나리오 데이터셋 관리

**주요 작업**:
```python
import pandas as pd

# Scenario bank 로드
scenarios = pd.read_csv("scenarios.csv")

# 평가 결과 정리
eval_df = pd.DataFrame({
    "scenario_id": [...],
    "policy_version": [...],
    "expected_action": [...],
    "actual_action": [...],
    "is_correct": [...],
})

# Confusion matrix, 지표 계산
false_stop_rate = (eval_df["event_type"] == "backchannel") & (eval_df["actual_action"] == "stop")
```

### scikit-learn (>=1.8.0)
**용도**: 머신러닝 도구 (주로 평가 지표)

**사용**:
```python
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score

# Confusion matrix
cm = confusion_matrix(expected_actions, actual_actions)

# 지표
accuracy = accuracy_score(expected, actual)
false_stop_recall = recall_score(expected, actual, labels=["backchannel"], target=["stop"])
```

---

## 🛠️ 파일 처리 & 설정

### python-multipart (>=0.0.27)
**용도**: 파일 업로드 처리 (Audio File Test)

**역할**:
- 프론트엔드에서 오디오 파일 업로드 수신
- FastAPI의 `UploadFile` 지원

```python
from fastapi import UploadFile

@app.post("/upload-audio")
async def upload_audio(file: UploadFile):
    contents = await file.read()
    # 파일 처리
```

### PyYAML (>=6.0.3)
**용도**: 설정 파일 및 데이터 포맷

**사용**:
```yaml
# config.yaml
ai_action_policy:
  baseline:
    display_name: "Baseline"
    description: "VAD-only"
  policy_v1:
    display_name: "Policy v1"
    description: "VAD + Backchannel Rule"
  policy_v2:
    display_name: "Policy v2"
    description: "STT + Intent Shift"
  policy_v3:
    display_name: "Policy v3"
    description: "AI Action Policy Decision Table"

intent_descriptions:
  배송조회: "배송 상태 확인, 배송 일정"
  환불요청: "환불 신청, 환불 절차"
  반품요청: "반품 신청"
  결제문제: "결제 실패, 결제 오류"
```

---

## 🎨 출력 포맷팅

### Rich (>=15.0.0)
**용도**: 콘솔 출력 포맷팅 및 테이블

**용도**:
- Decision log를 읽기 좋은 형식으로 표시
- Evaluation metric을 테이블로 출력
- 결과 리포트 생성

```python
from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="AI Action Policy Evaluation")
table.add_column("Scenario", style="cyan")
table.add_column("Policy", style="magenta")
table.add_column("Expected", style="green")
table.add_column("Actual", style="yellow")
table.add_column("Result", style="red")

console.print(table)
```

---

## ✅ 테스트 (Dev Dependencies)

### pytest (>=9.0.3)
**용도**: 단위 테스트 및 통합 테스트 프레임워크

```bash
pytest tests/
```

### pytest-asyncio (>=1.3.0)
**용도**: 비동기 함수 테스트 (FastAPI async routes)

```python
@pytest.mark.asyncio
async def test_prediction():
    response = await client.post("/predict", json={...})
    assert response.status_code == 200
```

### pytest-cov (>=7.1.0)
**용도**: 테스트 커버리지 측정

```bash
pytest --cov=src --cov-report=html tests/
```

### httpx (>=0.28.1)
**용도**: FastAPI 테스트용 HTTP 클라이언트

```python
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/scenario/1", json={"user_input": "..."})
```

---

## 🔍 코드 품질 (Dev Dependencies)

### black (>=26.3.1)
**용도**: 코드 자동 포매팅

```bash
black src/
```

### ruff (>=0.15.12)
**용도**: 빠른 linting 및 import 정렬

```bash
ruff check src/
```

### mypy (>=2.0.0)
**용도**: 정적 타입 체커

```bash
mypy src/
```

---

## 📦 설치 및 실행

### 설치
```bash
poetry install
```

### 개발 모드 실행
```bash
poetry run uvicorn backend.main:app --reload
```

### 테스트
```bash
poetry run pytest tests/ -v
```

### 타입 체크
```bash
poetry run mypy src/
```

### 코드 포매팅
```bash
poetry run black src/
poetry run ruff check src/
```

---

## 🏗️ 아키텍처 개요

```
FastAPI 앱
├── 입력 모드 처리
│   ├── Text Replay: 텍스트 직접 입력
│   └── Audio File Test: 음성 파일 → Whisper (STT) → 텍스트
├── Signal 계산
│   ├── VAD: webrtcvad + librosa
│   ├── STT: openai-whisper
│   └── Intent Embedding: sentence-transformers
├── AI Action Policy 실행
│   ├── Baseline      — VAD-only
│   ├── Policy v1     — VAD + Backchannel Rule
│   ├── Policy v2     — STT + Intent Shift
│   └── Policy v3     — AI Action Policy Decision Table
├── Evaluation
│   ├── Accuracy, Confusion Matrix
│   ├── False Stop Rate, Missed Switch Rate
│   └── Intent Shift Recall, Backchannel Precision
└── 결과 출력
    ├── Rich 콘솔 포맷팅
    ├── pandas DataFrame 저장
    └── 평가 리포트 생성
```

---

## 📝 주요 파일 구조 (예상)

```
프로젝트 루트
├── pyproject.toml          # Poetry + src layout
├── poetry.lock             # 정확한 버전 지정
│
├── src/
│   └── backend/            # FastAPI API 표면
│       ├── main.py         # FastAPI 앱 진입점
│       ├── config.py       # pydantic-settings로 정의
│       └── app/
│           ├── models.py   # Pydantic 스키마 정의
│           ├── api/
│           │   ├── scenario.py     # Scenario 조회/관리
│           │   ├── predict.py      # Action 예측
│           │   └── evaluate.py     # 평가 결과
│           ├── services/           # ※ 정책 로직 직접 구현 금지 — src/runner.py 호출
│           │   ├── vad.py          # webrtcvad 래퍼
│           │   ├── stt.py          # openai-whisper 래퍼
│           │   ├── intent.py       # sentence-transformers intent shift
│           │   └── policy.py       # runner 호출 어댑터 (정책 로직은 src/policies/에)
│           └── utils/
│               ├── audio.py        # soundfile, librosa 유틸리티
│               └── metrics.py      # scikit-learn 기반 평가
│
├── data/                   # 원본 시나리오 (read-only ground truth)
│   ├── scenarios.json      # Scenario bank
│   └── intents.yaml        # Intent descriptions (PyYAML)
│
├── results/                # Test Bench artifact (run_id 단위, append-only)
│   └── runs/{run_id}/
│       ├── run_meta.json
│       ├── evaluation.json
│       ├── decision_logs.jsonl
│       └── error_analysis.md
│
└── tests/
    ├── test_api.py         # FastAPI + httpx 테스트
    ├── test_intent.py      # Intent shift 테스트
    └── test_policy.py      # AI Action Policy 테스트
```

---

## 💡 PRD 매핑

| PRD 요구사항 | 관련 패키지 |
| --- | --- |
| FR0: Input Mode Console (Text/Audio) | FastAPI, python-multipart, openai-whisper |
| FR1: Scenario Bank | Pydantic, pandas |
| FR2: AI Action Policy (Policy v1~v3) | 모든 패키지 (통합) |
| FR3: Intent Shift Detection | sentence-transformers, numpy |
| FR4: Text Replay Evaluation | scikit-learn, pandas, rich |
| FR5: Audio File Test | soundfile, librosa, openai-whisper |
| FR6: Decision Log | Pydantic, pandas |
| FR7: Result Report | pandas, rich, numpy |

---

## 🚀 다음 단계

1. **데이터 준비**: `scenarios.json` 작성 (30개 이상 시나리오, `.claude/rules/experiments.md` Source of Truth 참조)
2. **API 개발**: scenario 조회, predict, evaluate 엔드포인트 구현
3. **Signal 처리**: VAD, STT, Intent embedding 통합
4. **AI Action Policy**: P0~P3 판단 로직 구현
5. **평가 및 리포트**: confusion matrix, 지표 계산, 실패 분석

---

**작성일**: 2026-05-07  
**대상**: AI Engineer, 코드 리뷰어
