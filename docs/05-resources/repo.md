# Repository & Code Structure

## GitHub Repository

**주소:** (구현 완료 후 링크 추가)

```bash
git clone https://github.com/[user]/whisper-intent-interruption-detection.git
cd whisper-intent-interruption-detection
```

---

## 폴더 구조

```
whisper-intent-interruption-detection/
│
├─ README.md                          # 프로젝트 개요
├─ requirements.txt                   # 의존성
│
├─ docs/                              # 문서 (Wind Docs)
│  ├─ index.md
│  ├─ 01-problem/
│  ├─ 02-design/
│  ├─ 03-data/
│  ├─ 04-demo/
│  └─ 05-resources/
│
├─ data/                              # 데이터
│  ├─ scenarios.json                  # 30개 시나리오
│  ├─ scenario_stats.json             # 통계
│  └─ audio_samples/                  # 음성 샘플 (10개)
│
├─ src/                               # 코드
│  ├─ scenario_loader.py              # 데이터 로드
│  ├─ intent_detector.py              # Intent 분류
│  ├─ evaluator.py                    # 평가 로직
│  └─ policies/
│     ├─ p0_vad_only.py
│     ├─ p1_backchannel_rule.py
│     ├─ p2_intent_shift.py
│     └─ p3_action_policy.py
│
├─ results/                           # 평가 결과
│  ├─ evaluation.json                 # 지표
│  ├─ decision_logs.jsonl             # 판단 로그
│  ├─ run_meta.json                   # 실행 설정과 기준 snapshot
│  ├─ metrics_comparison.png
│  └─ error_analysis.md               # 실패 분석
│
├─ demo/                              # 데모 콘솔
│  ├─ index.html                      # Text Replay UI
│  ├─ audio_test.html                 # Audio File Test UI
│  └─ console.js
│
└─ notebooks/                         # 분석 노트북
   ├─ 01_scenario_analysis.ipynb
   ├─ 02_evaluation_results.ipynb
   └─ 03_error_analysis.ipynb
```

---

## 설치 및 실행

### 1️⃣ 환경 설정

```bash
# Python 3.8+ 필요
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 데이터 준비

```bash
# scenarios.json이 data 폴더에 있는지 확인
ls data/scenarios.json
```

### 3️⃣ 정책 실행

```python
# 기본 평가 실행
python src/evaluator.py --data data/scenarios.json --output results/

# 결과 확인
cat results/evaluation.json
cat results/error_analysis.md
```

### 4️⃣ 데모 콘솔 실행

```bash
# Text Replay 콘솔
python -m http.server 8000
# 브라우저에서 http://localhost:8000/demo/index.html 접속
```

---

## 주요 파일별 설명

### `src/policies/*.py`

각 정책(Baseline~Policy v3)의 구현

```python
# Baseline: VAD-only
def vad_only_policy(has_user_speech):
    return "stop_and_switch" if has_user_speech else "continue"

# Policy v1: + Backchannel
def backchannel_policy(has_user_speech, utterance):
    if not has_user_speech:
        return "continue"
    if is_backchannel(utterance):
        return "brief_ack"
    return "stop_and_switch"

# Policy v2: + Intent Shift
def intent_shift_policy(utterance, current_intent):
    # SBERT로 의도 유사도 계산
    similarity = sbert_similarity(utterance, current_intent)
    return "stop_and_switch" if similarity < 0.6 else "pause"

# Policy v3: Full Policy
def full_action_policy(event_type, intent_similarity, complaint_severity):
    # 모든 신호를 종합해 6가지 action 중 선택
    ...
```

---

### `src/evaluator.py`

평가 실행 및 지표 계산

```bash
python src/evaluator.py \
  --data data/scenarios.json \
  --policies p0 p1 p2 p3 \
  --output results/ \
  --generate_report
```

---

### `demo/index.html`

Text Replay 모드 UI

**기능:**
- Scenario 선택 또는 직접 입력
- AI 발화 표시
- 사용자 발화 입력
- 각 정책의 판단 결과 표시
- Decision reason 설명

---

## 개발 가이드

### 새로운 정책 추가

```python
# src/policies/p4_prosody_aware.py
def prosody_aware_policy(event_type, intent_shift, tone_intensity):
    # 새로운 신호 추가
    if tone_intensity > URGENT_THRESHOLD:
        return "handoff"
    # ... 기존 로직 + 새 신호
```

### 새로운 intent 추가

```python
# data/scenarios.json에 새로운 intent 추가
{
  "scenario_id": "commerce_subscription_001",
  "ai_current_intent": "subscription_inquiry",
  "expected_user_intent": "subscription_cancellation",
  # ...
}
```

---

## 테스트

```bash
# Unit test (아직 미구현, Day 4에 추가)
pytest tests/

# 전체 파이프라인 테스트
python tests/test_full_pipeline.py
```

---

## 배포

### Wind Docs (GitHub Pages)

```bash
# mkdocs 설치
pip install mkdocs mkdocs-material

# 로컬에서 미리보기
mkdocs serve

# 배포 (자동 - GitHub Actions)
git push origin main
```

### 실제 콘솔 배포 (이후)

```bash
# Netlify, Vercel 등으로 배포 가능
# 1주차: 로컬 데모만
# 이후: 실제 호스팅
```

---

## 문제 해결 (FAQ)

### Q: scenarios.json이 로드되지 않음

```bash
# 1. 파일 경로 확인
ls data/scenarios.json

# 2. JSON 형식 검증
python -c "import json; json.load(open('data/scenarios.json'))"
```

### Q: SBERT 모델 다운로드가 느림

```python
# 더 가벼운 모델 사용
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
# 또는 캐시 설정
export SENTENCE_TRANSFORMERS_HOME=/path/to/cache
```

### Q: 콘솔 UI가 시나리오를 못 찾음

```bash
# demo 폴더에서 데이터 경로 확인
# index.html의 data path: ../data/scenarios.json (상대경로)
```

---

## 다음 단계 (이후 작업)

**Week 2+:**
- Real STT (Whisper, Google) 통합
- Prosody 신호 추가
- 100개 시나리오로 확장
- 논문화 준비

---

## 연락처

질문이나 제안: (구현자 이메일)

---

## 라이선스

MIT License (자유롭게 사용, 수정, 배포 가능)

---

**Wind Docs v1.0 — 2026-05-07**
