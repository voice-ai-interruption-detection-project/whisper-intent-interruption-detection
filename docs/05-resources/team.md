# Team & Timeline

## Team

### 👥 구성

**2인 페어 프로젝트**

| 역할 | 담당 영역 | 강점 |
|------|---------|------|
| **Role A** | 문제 정의, 데이터 설계 | 도메인 이해, 시나리오 기획 |
| **Role B** | 정책 구현, 평가 | 알고리즘, 성능 검증 |

### 협업 방식

- **Day 1 (첫날)**: 페어로 시작 (문제와 범위 일치)
- **Day 2~4**: 역할별 분담
- **Day 5 (마지막)**: 통합 및 정리

---

## 1주일 실행 일정 (2026-05-07 ~ 2026-05-14)

### 📅 Day 1 (2026-05-07, 목)

**목표:** 문제 정의와 데이터 설계

```
09:30~13:30 (4시간 페어)

1. 문제 정의 확정
   - Intent 범위
   - Event Type 분류
   
2. 데이터 설계
   - Scenario schema 확정
   - Action label 확정
   
3. 산출물
   - data/scenarios.json (30개 목표)
   - action label 정의 문서
```

---

### 💻 Day 2 (2026-05-08, 금)

**계획 목표:** Baseline 구현과 초기 평가

**📋 실제 진행 내용 (10:30~17:05)**

#### 완료된 작업

| 순서 | 내용 | 산출물 |
|------|------|--------|
| **1** | 전체 구조 파악 + 파이프라인 이해 (45분) | — |
| **2** | event_type + action label 토론 (35분) | 경계 기준 초안 |
| **3** | 6가지 intent 확정 + AI 발화 템플릿 (20~60자) | `기획/PHASE2-intent별-AI발화-템플릿.md` (18개 발화) |
| **4** | 30개 시나리오 생성 (영문 ID 표준화) | `기획/PHASE3-30개-시나리오-초안.md` |
| **5** | 대표 케이스 5개 선정 (False Stop, Missed Switch 등) | `기획/PHASE3-대표케이스-5개-선정.md` |
| **6** | JSON 변환 (30개 시나리오) | ✅ `data/scenarios.json`, `data/scenario_stats.json` |

#### 핵심 산출물

- ✅ **data/scenarios.json** — 30개 시나리오 완성 (JSON 유효성 검증)
  - Event Type 분포: no_speech 4개, noise 4개, backchannel 6개, same_intent_question 6개, intent_shift 6개, complaint 2개, ambiguous 2개
- ✅ **기획 문서 3개** — intent 발화 템플릿, 시나리오 초안, 대표 케이스 선정

#### 토론 결과: 세 가지 경계 기준 정의

1. **same_intent_question vs intent_shift** — 같은 범주인가, 다른 범주인가?
2. **complaint 심각도** (stop_and_switch vs handoff) — 불만 정도와 상담사 개입 필요성
3. **backchannel vs ambiguous** — 빠르고 명확한 "이해" vs 느리고 불명확한 "의문"

#### 커밋 이력

```
d78968e docs: scenario JSON 예시에서 intent ID를 영문 스네이크_케이스로 표준화
5fcacd2 docs: scenario schema 통일 - intent ID를 영문으로 표준화
640ccaf docs: action label 'pause' → 'respond_and_continue'로 명칭 변경
4273baa feat(data): 커머스 시나리오 30개 생성 및 분포 통계
```

**→ Day 2 계획(Baseline 구현)은 Day 3(2026-05-09)로 연기됨**

```
1. Scenario Loader 작성 (Role B)
   
2. Baseline (VAD-only) 구현 (Role B)
   - src/policies/p0_vad_only.py
   
3. Policy v1 (Backchannel Rule) 구현 (Role B)
   - src/policies/p1_backchannel.py
   
4. Evaluator 작성 (Role A/B)
   - src/evaluator.py
   
5. 첫 번째 평가 실행
   - results/baseline_eval.json
```

---

### 🧠 Day 3 (2026-05-09, 월)

**목표:** Intent Shift 감지와 Audio 연결

```
1. Intent Detector 설계 (Role B)
   - SBERT 모델 선택
   - Intent description 작성
   
2. Policy v2 (Intent Shift) 구현 (Role B)
   - src/intent_detector.py
   - src/policies/p2_intent_shift.py
   
3. 대표 Audio Sample 준비 (Role A)
   - 10개 representative case 선택
   - TTS 또는 수집으로 음성 생성
   - Transcript 라벨링
   
4. 구현 중 발생한 질문 정리
   - 논문 리뷰 주제 1개 선정
```

---

### 🔧 Day 4 (2026-05-10, 화)

**목표:** 전체 Policy와 평가 완성

```
1. Policy v3 (Full AI Action Policy) 구현 (Role B)
   - src/policies/p3_action_policy.py
   - Decision log 저장
   
2. 평가 완성 (Role A/B)
   - Confusion matrix 생성
   - False Stop Rate, Missed Switch Rate 계산
   - 실패 케이스 분석
   
3. 시각화 (Role A)
   - Confusion matrix 그래프
   - Metric comparison 그래프
   
4. 산출물
   - results/evaluation.json
   - results/decision_logs.jsonl
   - results/error_analysis.md
```

---

### 📝 Day 5 (2026-05-11, 수)

**목표:** 리포트 정리와 데모 준비

```
1. 콘솔 UI 정리 (Role A)
   - Text Replay 기본 완성
   - Audio File Test 최소 동작
   - Mic Trial 구조만 (선택)
   
2. 리포트 작성 (Role A/B)
   - README.md (구현, 결과, 방법)
   - report.md (정량 결과, 해석, 한계)
   - demo_scenarios.md (대표 3가지)
   
3. Wind Docs 배포
   - GitHub Pages 자동 배포
   - 메뉴 구성 및 네비게이션
   
4. 최종 검증
   - 모든 파일이 로드되는가?
   - 결과가 일관성 있는가?
   - 이야기가 명확한가?
```

---

## 타임라인 요약

```
Week 1 (MVP)
├─ Day 1: 설계
├─ Day 2: Baseline, Policy v1 구현 + 평가
├─ Day 3: Policy v2 구현 + Audio 연결
├─ Day 4: Policy v3 + 최종 평가
└─ Day 5: 리포트 + 배포

산출물:
├─ Code: policies (Baseline~Policy v3), evaluator
├─ Data: 30개 scenarios + audio samples
├─ Results: evaluation.json, confusion matrix
└─ Docs: README, report, Wind Docs
```

---

## 주간 동료 리뷰

| 요일 | 항목 | 포커스 |
|------|------|--------|
| 2026-05-08 (금) | Baseline, Policy v1 구현 | 기준선 확실한가? 개선이 보이는가? |
| 2026-05-09 (월) | Intent detector | SBERT threshold 적절한가? |
| 2026-05-10 (화) | Policy v3 + 평가 | 모든 지표가 일관성 있는가? |
| 2026-05-11 (수) | 최종 리포트 | 이야기가 명확한가? 채용자 입장에서 어떤가? |

---

## 위험 요소와 대응

| 위험 | 대응 |
|-----|-----|
| Audio 생성이 오래 걸림 | Text Replay를 먼저 완성, 대표 케이스 10개만 audio화 |
| Backchannel 규칙 예외 많음 | threshold 조정 후 error analysis에서 예외 케이스 기록 |
| SBERT threshold 애매함 | validation set으로 조정, threshold 고정 주장 안 함 |
| 정량 결과가 예상보다 안 좋음 | 실패 사례 분석과 개선 loop을 핵심 성과로 설명 |
| 1주차 완성 불가능 | Day 5 우선순위: Text Replay > Audio File > Mic Trial |

---

## 다음

👉 **[Related Papers](./papers.md)** — 참고하는 논문과 자료
