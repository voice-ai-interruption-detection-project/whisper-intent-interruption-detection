# Related Papers & References

## 음성 인식 (Speech Recognition)

### VAD (Voice Activity Detection)

**원리:** 음성과 음성이 아닌 신호를 구분

- WebRTC VAD (Chromium)
- Silero VAD (경량, 실시간)
- 참고: 단순 threshold 기반 → False Positive/Negative 많음

---

## 대화 시스템 (Dialogue Systems)

### Interruption Handling

**문제:** 사용자가 언제 개입하는가를 이해하고 대응하는 방식

- **Turn-taking in conversation**
  - 대화에서 언제가 "자연스러운 발화 끝"인가?
  - 누가 다음에 말할 차례인가?

- **Grounding & Confirmation**
  - 고객의 입력을 이해했음을 표현하는 방식
  - Backchannel의 역할

---

## Intent Recognition

### 의도 분류 (Intent Classification)

- **Traditional**: Keyword matching, Rule-based
- **Modern**: SBERT, Transformer-based sentence embeddings

#### 추천 도구

**SBERT (Sentence-BERT)**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

embedding1 = model.encode("배송조회")
embedding2 = model.encode("환불요청")
similarity = cosine_similarity(embedding1, embedding2)
```

**장점:** 다국어 지원, 빠른 속도, 한국어 학습

---

## 한국어 음성 상담 도메인

### 현황

- 상용 시스템: Kakao i, Naver Clovabot
- 학술 데이터: 제한적
- 우리의 시도: 개방형 데이터셋 구축

---

## 구현 레퍼런스

### Python 라이브러리

| 라이브러리 | 용도 | 설치 |
|-----------|------|------|
| `sentence-transformers` | Intent 유사도 | `pip install sentence-transformers` |
| `librosa` | 음성 처리 | `pip install librosa` |
| `soundfile` | WAV 읽기/쓰기 | `pip install soundfile` |
| `numpy`, `pandas` | 데이터 분석 | `pip install numpy pandas` |

---

## 성능 평가 메트릭

### Confusion Matrix & F1 Score

```python
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

# 예측과 실제 비교
y_true = ["continue", "stop_and_switch", ...]
y_pred = ["continue", "pause", ...]

# 평가
cm = confusion_matrix(y_true, y_pred)
f1 = f1_score(y_true, y_pred, average='weighted')
precision, recall, f1, _ = precision_recall_fscore_support(...)
```

---

## 향후 리서치 방향

### 우리가 생각하는 다음 단계

1. **Real-time STT Integration**
   - Whisper API 또는 Google Speech-to-Text
   - STT 오류의 영향 평가

2. **Prosody & Tone Analysis**
   - Pitch, RMS (음량)
   - 감정 신호 추출

3. **Contextual Intent**
   - 이전 대화 맥락 포함
   - Multi-turn dialogue understanding

4. **Live Commerce Scenario**
   - 실제 커머스 상담 시스템 통합
   - 사용자 피드백 수집

---

## 커뮤니티 & 도구

### 오픈소스

- **OpenAI Whisper** — STT 모델
- **Hugging Face Transformers** — 각종 NLP 모델
- **Rasa** — 오픈소스 대화 관리 플랫폼

### 커뮤니티

- Hugging Face Discussions
- Kaggle (유사 태스크 예시)
- Papers with Code (최신 리서치)

---

## 다음

👉 **[Repository](./repo.md)** — 코드 저장소와 실행 방법
