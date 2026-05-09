# 이전 RAG/QA 파이프라인 프로젝트 ("sprint-4") 하네스 이식 후보 분석

작성일: 2026-05-07

## 목적

이전에 진행된 RAG/QA 파이프라인 최적화 프로젝트(이하 "sprint-4")에 적용된 하네스와 규칙 중, 이 프로젝트(`whisper-intent-interruption-detection`)로 가져올 만한 것을 추린다.

> sprint-4의 원천 저장소는 이 repo에 포함되어 있지 않다. 패턴과 결론만 가져오고, RAG/QA 도메인에 묶인 규칙은 복사하지 않는다.

이번 정리는 sprint-4의 문서 규칙만 보지 않고, 실제 원본 코드에 들어간 하네스까지 함께 본다. 결론부터 말하면 가져올 핵심은 폴더 구조가 아니라 다음 실행 계약이다.

- 무엇을 바꿨는지에 따라 어느 부분을 새로 실행할지 결정하는 계획기
- 실행 당시의 config/prompt/policy를 결과와 함께 남기는 snapshot
- 실험용 설정 변경을 안전하게 되돌리는 override layer
- fixture/result가 현재 설정과 맞는지 확인하는 fingerprint
- eval이 실제 앱 pipeline을 우회하지 않게 하는 재사용 경계
- 실험 리포트가 Before/After와 실패 사례까지 남기게 하는 보고 계약

## 참고한 원천 (역할별)

### 운영 규칙 문서

- 루트 가이드와 `.claude/rules/*` 시리즈 — config 규약, code-style, app 구조, 관측, 실험 프로토콜
- `harness-scanner` 정의 한 건

### 실제 코드 하네스

- `evals/_planner.py` — 변경 영향에 따라 stage별 실행 계획을 만든다 (target/changed/fresh/fixture/skip)
- `evals/_common.py` — fixture fingerprint와 stage 공통 helper
- `evals/run_experiment.py` — run artifact를 생성하는 entry
- `evals/_stages.py` — stage 정의가 실제 앱 pipeline 함수를 직접 호출하는 형태
- `app/config.py` — Pydantic 기반 stage 설정과 `override_config(...)` context manager
- `app/snapshot.py` — config / prompt snapshot 기준 원본
- `app/diagnostics.py` — `source` 식별자, stage별 latency, snapshot attach
- `app/pipelines/*` — eval이 호출하는 ingest / QA pipeline
- `tests/test_config.py`, `test_override.py`, `test_diagnostics.py` — 하네스 invariants를 직접 테스트

### 실험/보고서 원형

- midweek upgrade report 한 건 — 가설/baseline/변경/결과/사례별 분석/실패/다음 실험 계약이 정착된 사례
- "vision correction off vs on" 실험 리포트 — 한 엣지 케이스를 Before/After로 끝까지 증명한 사례
- "vision model upgrade" delta 리포트 — 모델 교체 비교 보고 사례
- retrieval 진단 노트 두 건 — 실패 원인을 어디 층 문제로 귀속시킬지 진단하는 스타일

## 현재 프로젝트에 대한 판단

(이 분석을 작성한 시점 기준) 루트에는 `CLAUDE.md`, `AGENTS.md -> CLAUDE.md`, `README.md` 정도만 있었고, `app/`, `evals/`, `experiments/`, `.claude/rules/`, `.codex/rules/` 같은 실제 운영 표면은 거의 없었다.

따라서 지금 필요한 것은 sprint-4의 성숙한 구조를 통째로 복사하는 일이 아니다. 다만 아래 항목은 이미 이 프로젝트의 성격상 반복될 가능성이 높으므로, 너무 늦게까지 미루지 않는 편이 낫다.

- 반복 실험에서 입력, 기준, 결과가 섞이지 않게 하는 실행 기록
- intent/interruption 판단 기준이 바뀌었을 때 비교 가능한 run 단위
- 대표 실패 사례를 Before/After로 끝까지 증명하는 보고 방식
- 실험용 설정 변경이 다음 실행을 오염시키지 않게 하는 override/restore
- eval이 실제 판정 로직과 갈라지지 않게 하는 pipeline 재사용 경계

여기서 "얇게"는 아무 장치도 만들지 않는다는 뜻이 아니다. 이미 확정된 반복 행동은 초기에 작은 문서, checklist, local skill, 작은 helper로 둘 수 있다. 문제가 되는 것은 아직 실체가 없는 영역까지 넓게 예측해서 두껍게 깔아두는 것이다.

## sprint-4에서 실제로 작동하던 하네스

### 1. 실행 계획기: `target` / `changed` / `fresh` / `fixture` / `skip`

sprint-4의 `evals/_planner.py`는 CLI 인자를 받아 실행 계획을 만든다.

- `target`: 이번 실행에서 만들 결과물
- `changed`: 내가 바꾼 부분
- `fresh`: 새로 실행할 부분
- `fixture`: 기존 산출물을 재사용할 부분
- `skip`: 이번 목표에 필요 없는 부분

중요한 점은 "항상 전체를 다시 실행"하지 않는다는 것이다. baseline에서는 필요한 단계를 전부 fresh로 돌리고, compare에서는 변경된 부분과 그 downstream만 fresh로 돌린다.

이 프로젝트로 가져올 때는 sprint-4의 `transcribe`, `vision`, `embed`, `qa`를 그대로 가져오지 않고, 다음처럼 바꿔 생각한다.

- `input`: 음성/전사/이벤트 샘플 로딩
- `signal`: interruption 후보 신호 추출
- `intent`: intent 분류
- `policy`: 최종 interrupt/continue 판정
- `eval`: 지표 계산과 사례 기록
- `report`: 비교 요약

초기에는 꼭 코드 planner를 만들지 않아도 된다. 하지만 `run` 결과를 남기기 시작하면 이 개념은 빨리 필요해진다.

### 2. 실행 결과 계약: snapshot + latency + label + per-case result

sprint-4의 `evals/run_experiment.py`는 결과 JSON에 다음을 함께 저장한다.

- `label`
- `timestamp`
- `media_id`
- `dataset`
- `mode`
- `changed`
- `target`
- `config`
- `prompts`
- `latency_ms`
- `qa_results`
- `metrics`

이 구조의 핵심은 "결과값만 저장하지 않는다"는 점이다. 어떤 설정과 어떤 prompt로 실행했는지, 무엇을 바꿨다고 선언했는지, 어느 단계 시간이 얼마나 걸렸는지까지 같이 남긴다.

이 프로젝트에서는 다음 run artifact 계약으로 바꿔 가져오면 좋다.

```json
{
  "run_id": "20260507_120000_policy-threshold-v1",
  "timestamp": "2026-05-07T12:00:00+09:00",
  "mode": "baseline | compare",
  "target": "policy | eval | report",
  "changed": ["policy"],
  "dataset": "interrupt-edge-cases-v1",
  "input_snapshot": {},
  "policy_snapshot": {},
  "criteria_snapshot": {},
  "latency_ms": {},
  "case_results": [],
  "metrics": {},
  "notes": []
}
```

이건 강한 framework가 아니라 결과 파일이 최소한의 재현성을 갖게 하는 계약이다. 결과 파일 덮어쓰기 방지도 이 단계에서 같이 들어가야 한다.

### 3. config/policy snapshot: 기준 원본을 한 곳에서 만든다

sprint-4의 `app/snapshot.py`는 config와 prompt snapshot을 만드는 기준 원본 역할을 한다. `diagnostics.py`와 `evals/_common.py`가 각자 snapshot을 만들지 않고 같은 함수를 가져다 쓴다.

이 프로젝트에서는 "config/prompt"라는 이름보다 다음이 더 맞다.

- `policy_snapshot`: threshold, interruption decision rule, intent label map, debounce/window 값
- `criteria_snapshot`: eval 기준, positive/negative 판정 정의, manual review rubric
- `input_snapshot`: dataset id, sample id, transcript source, audio metadata

여기서 중요한 건 용어가 아니라 같은 실행 조건을 여러 곳에서 제각각 기록하지 않는 것이다. UI, CLI, eval, report가 같은 snapshot helper를 쓰게 해야 한다.

### 4. override layer: 실험 설정을 바꾸고 반드시 되돌린다

sprint-4의 `app/config.py`에는 `override_config(**stage_overrides)`가 있다. block 안에서 config를 바꾸고, 예외가 나도 원래 값으로 복원한다. `tests/test_override.py`는 정상 복원, 예외 후 복원, nested override, unknown field error까지 확인한다.

이 프로젝트에서 바로 유용한 후보:

- interruption threshold
- silence / overlap window
- intent confidence cutoff
- false positive suppression rule
- policy version
- model/provider option

초기에는 Pydantic stage config까지 바로 만들 필요는 없지만, 실험 runner가 생기는 순간 `with override_policy(...):` 같은 작은 형태는 가치가 크다.

### 5. fixture fingerprint: 재사용해도 되는 산출물인지 확인한다

sprint-4의 `evals/_common.py`는 fixture별 fingerprint key를 따로 둔다. 예를 들어 transcription fixture는 transcription provider/model/prompt가 같아야 재사용하고, vision fixture는 vision model/prompt/fps가 같아야 재사용한다.

이 프로젝트에서는 다음 fingerprint가 필요해질 가능성이 높다.

- transcript fixture: Whisper model, language, prompt, diarization 여부
- signal fixture: window size, silence threshold, overlap policy
- intent fixture: model/prompt/label schema/confidence cutoff
- policy result fixture: policy version, threshold, suppression rule
- report result: eval criteria version, dataset version

이 장치는 처음부터 hook으로 막을 필요는 없다. 하지만 fixture나 이전 결과를 재사용하는 순간에는 "현재 기준과 맞는가"를 확인해야 한다.

### 6. eval은 실제 pipeline을 재사용한다

sprint-4의 `evals/_stages.py`는 앱의 `_trace_transcribe`, `_trace_vision`, `_trace_embed`, `qa_pipeline.run_qa`를 직접 재사용한다. eval 전용으로 비슷한 로직을 새로 만들지 않는다.

이 프로젝트에서도 이 원칙은 강하게 가져올 만하다.

- demo runner
- CLI runner
- eval runner
- report generator

이 네 곳이 intent/interruption 판정 로직을 각자 구현하면 결과가 빨리 갈라진다. 판정의 중심은 하나의 pipeline/helper에 두고, eval은 그 위에 dataset loop와 metric 계산만 얹는 쪽이 맞다.

### 7. diagnostics: source와 latency를 남긴다

sprint-4의 `app/diagnostics.py`는 `source`를 받아 config snapshot을 run에 붙이고, stage별 latency를 기록한다. LangSmith 의존 부분은 지금 가져올 필요가 없지만, `source`와 latency 개념은 바로 유효하다.

이 프로젝트에서는 최소한 다음은 남기는 편이 좋다.

- `source`: `cli`, `eval`, `demo`, `manual-review`
- `latency_ms.total`
- `latency_ms.transcribe`
- `latency_ms.detect`
- `latency_ms.intent`
- `latency_ms.policy`

interruption detection은 정확도뿐 아니라 반응 시간이 중요할 수 있으므로 latency는 부가 정보가 아니라 핵심 결과에 가깝다.

### 8. 하네스 자체를 테스트한다

sprint-4에는 기능 테스트뿐 아니라 하네스 규칙을 지키는 테스트가 있다.

- `tests/test_config.py`: provider/model/dim/config 생성 확인
- `tests/test_override.py`: override 후 복원 보장
- `tests/test_diagnostics.py`: snapshot/source/stage cfg attach 확인
- `tests/test_ingest_chunking_multimodal.py`: chunking 경계와 regression 확인

이 프로젝트에서도 초기 테스트 후보는 다음이다.

- run artifact에 필수 key가 빠지지 않는다.
- policy override는 예외가 나도 복원된다.
- snapshot은 policy/criteria/dataset version을 포함한다.
- eval runner는 실제 detection pipeline을 호출한다.
- result filename은 기존 결과를 덮어쓰지 않는다.

## 문서/보고 하네스에서 가져올 것

### 1. 완주 스토리 1개

sprint-4 README와 track-b 문서의 핵심은 여러 모듈을 조금씩 건드리는 것보다, 하나의 엣지 케이스를 Before/After로 끝까지 증명하는 것이다.

이 프로젝트에서는 다음처럼 해석한다.

- 대표 실패 케이스 1개를 고른다.
- 동일 입력에 대해 Before/After를 비교한다.
- 자동 지표와 수동 검증 사례를 함께 남긴다.
- 실패하거나 애매한 사례도 지우지 않는다.

예시 후보:

- interruption false positive 감소
- true interruption 감지 latency 개선
- Whisper transcript noise가 있는 상황에서 intent 유지
- filler/hesitation을 interruption으로 오판하지 않기
- intent confidence가 낮을 때 interrupt를 보류하기

### 2. 실험 리포트 계약

sprint-4의 `upgrade-report.md`와 experiments report에는 다음 패턴이 반복된다.

- 실험 목적
- 선택한 실패 케이스
- 가설
- 변수 격리
- baseline
- 변경 내용
- 결과 표
- 사례별 분석
- 실패/부작용
- 다음 실험
- 최종 설정값

이 프로젝트의 대표 리포트도 이 계약을 가져오면 된다. 특히 "성공한 결과만 남기기"보다 실패/부작용을 남기는 쪽이 중요하다.

### 3. 진단 노트 스타일

sprint-4의 retrieval 진단 노트들은 바로 해결책을 만들기보다 실패가 어느 층에서 생겼는지 나눈다.

이 프로젝트에서도 interruption 오판을 볼 때 다음처럼 나누는 편이 좋다.

- transcription 문제인가
- acoustic/silence signal 문제인가
- intent label 문제인가
- policy threshold 문제인가
- eval 기준 문제인가
- latency/streaming 문제인가

이 구분은 구조를 많이 나누자는 뜻이 아니라, 실패 원인을 섞어서 해석하지 않기 위한 진단 프레임이다.

## 바로 가져올 것

### 1. run artifact 최소 계약

초기부터 결과 파일은 덮어쓰지 않고 `run_id`나 timestamp를 포함한다.

필수 필드:

- `run_id`
- `timestamp`
- `mode`
- `target`
- `changed`
- `dataset`
- `policy_snapshot`
- `criteria_snapshot`
- `latency_ms`
- `case_results`
- `metrics`

### 2. 대표 실패 케이스 기반 실험 원칙

- 대표 실패 케이스 1개를 고른다.
- baseline을 먼저 남긴다.
- 한 번에 하나의 변수만 바꾼다.
- Before/After를 같은 입력으로 비교한다.
- 자동 지표와 수동 판단을 함께 남긴다.
- n=1 결과만으로 결론 내리지 않는다.

### 3. snapshot 기준 helper

초기에는 `app/snapshot.py`가 없더라도, 첫 runner가 생기면 snapshot을 한 곳에서 만들도록 한다.

- `get_policy_snapshot()`
- `get_criteria_snapshot()`
- `get_input_snapshot()`

이름은 구현 시점에 바꿔도 되지만, CLI/eval/report가 각자 snapshot을 만들지 않는다는 원칙은 가져온다.

### 4. 실제 pipeline 재사용 원칙

eval이 실제 detection logic을 우회하지 않게 한다.

- eval은 dataset loop와 metric 계산을 맡는다.
- 판정은 실제 runner/pipeline/helper를 호출한다.
- demo와 eval에서 다른 policy 구현을 두지 않는다.

### 5. Guide / Sensor 분리

sprint-4는 하네스를 두 축으로 나눈다.

- Guide: 행동 전에 방향을 잡는 문서. `CLAUDE.md`, `.claude/rules/*.md`
- Sensor: 행동 후에 관찰하고 교정하는 장치. pre-commit hook, lint, scanner, test

이 프로젝트에도 그대로 유효하다. 다만 이 구분을 "문서에서 시작해서 반드시 hook까지 순서대로 올린다"는 뜻으로 읽지는 않는다. 확정된 반복 절차는 초기에 skill/checklist/helper가 될 수 있다. 강한 차단 장치는 반복되는 실패나 비용 큰 실수가 보일 때 그 지점에 덧댄다.

## 코드가 생기면 가져올 것

### 1. 실행 계획기

`evals/run_experiment.py` 같은 runner가 생기면 sprint-4의 planner를 작은 형태로 가져온다.

초기 후보:

```text
target: input | signal | intent | policy | eval | report
changed: input | signal | intent | policy | criteria
action: fresh | fixture | skip
```

처음에는 dict와 함수 하나로 충분하다. 복잡한 framework가 아니라 "이번 변경의 영향 범위만 새로 실행한다"는 계약이 핵심이다.

### 2. override layer

실험에서 threshold/policy/model을 반복 변경하기 시작하면 `override_config()`의 작은 버전을 만든다.

초기 후보:

```python
with override_policy(threshold=0.62, debounce_ms=300):
    run_eval(...)
```

반드시 테스트할 것:

- 정상 종료 후 복원
- 예외 발생 후 복원
- 중첩 override
- 모르는 field 입력 시 실패

### 3. fixture fingerprint

dataset이나 중간 산출물을 재사용하기 시작하면 fixture fingerprint를 둔다.

초기 후보:

- transcript fixture fingerprint
- signal fixture fingerprint
- intent fixture fingerprint
- policy result fingerprint

### 4. 하네스 invariant 테스트

코드가 생기면 기능 테스트와 별개로 하네스 자체의 invariants를 테스트한다.

- result 저장은 기존 파일을 덮어쓰지 않는다.
- snapshot 필수 key가 빠지면 실패한다.
- override는 항상 복원된다.
- eval runner는 실제 pipeline을 호출한다.
- criteria version이 바뀌면 이전 결과와 구분된다.

## 반복 후 강화할 것

### 1. `.claude/rules/*`

처음부터 rules 파일을 많이 나누지 않는다. 다만 같은 내용이 루트 `CLAUDE.md`에서 길어지거나, 특정 작업 영역에만 필요한 규칙이 생기면 하위 문서로 분리한다.

분리 후보:

- `.claude/rules/experiments.md`
- `.claude/rules/config.md`
- `.claude/rules/code-style.md`
- `.claude/rules/observability.md`

### 2. harness scanner

sprint-4의 `harness-scanner`는 코드가 충분히 생긴 뒤 효과가 있다.

나중에 이 프로젝트용 scanner가 볼 항목:

- hardcoded API key / token
- prompt/policy hardcoding
- result artifact 삭제 위험
- repeated threshold/window magic number
- snapshot과 실제 실행 config 불일치
- eval이 실제 pipeline을 우회하는 코드
- long function / long parameter list

### 3. pre-commit / hook

초기에는 formatting, lint, secret detection 정도면 충분하다. fixture write 차단, result overwrite 차단, no-verify 차단 같은 hook은 실수 패턴이 확인된 뒤 추가한다.

다만 결과 덮어쓰기는 반복 비용이 크므로, result writer 자체에서 timestamp/run id를 쓰는 것은 초기에 넣어도 된다.

### 4. tracing / LangSmith

LangSmith 구체 규칙은 지금 가져오지 않는다. 대신 source와 latency를 결과에 남기는 일반 원칙을 먼저 둔다.

나중에 tracing을 붙이면 가져올 원칙:

- root run과 stage run을 구분한다.
- function name보다 domain action name을 쓴다.
- 같은 함수가 여러 맥락에서 쓰이면 source를 명시한다.
- latency가 큰 작업은 stage별로 기록한다.

## 가져오지 말 것

아래는 sprint-4 맥락에 묶여 있으므로 현재 프로젝트에 복사하지 않는다.

- Track A/B 선택, delta-NN, PR 제출, 데모 영상 같은 교육 운영 규칙
- sprint-4의 비용 가이드
- sprint-4의 `evals/` 동결 규칙
- RAG/QA 전용 retrieval, embedding, Supabase table 규칙
- VLM frame analysis, multimodal QA 전용 규칙
- sprint-4의 LangSmith tree snapshot 세부 구조
- fixture 수동 편집 금지 hook
- `.claude/settings.json`의 fixture write 차단 hook
- `.githooks/commit-msg`의 `[Delta-03]` prefix 강제
- sprint-4 `CLAUDE.md` 전체 복붙

## 추천 도입 순서

이 순서는 강한 승격 규칙이 아니라, 현재 프로젝트에서 두꺼워지지 않게 가져오기 위한 현실적인 적용 순서다.

1. 루트 `CLAUDE.md`에 공통 원칙 추가
   - 기록 = 실행
   - 대표 실패 케이스 1개
   - 한 번에 하나의 변수
   - 결과 보존
   - Guide / Sensor 분리

2. 첫 runner/result가 생기면 run artifact 계약부터 고정
   - `run_id`
   - `policy_snapshot`
   - `criteria_snapshot`
   - `latency_ms`
   - `case_results`
   - `metrics`

3. 반복 실험이 시작되면 planner와 override를 작게 추가
   - `target/changed`
   - `fresh/fixture/skip`
   - `override_policy()` 또는 `override_config()`

4. 중간 산출물 재사용이 생기면 fingerprint 추가
   - transcript
   - signal
   - intent
   - policy

5. 같은 실수가 반복되면 Sensor 강화
   - test
   - lint
   - secret scanner
   - harness scanner
   - hook

## 루트 `CLAUDE.md`에 추가할 수 있는 초안

```md
## 실험 운영 원칙

- 대표 실패 케이스 1개를 고르고, 동일 입력에 대한 Before/After를 수치와 사례로 비교한다.
- 실험 전 baseline, policy/config, criteria, dataset 상태를 확인한다.
- 한 번에 하나의 변수만 바꾼다. 여러 변수를 동시에 바꾸면 원인 특정이 어렵다.
- 실험 결과와 실행 조건(policy snapshot, criteria version, dataset id)을 함께 남긴다.
- 실험용 policy/config 변경은 작업 후 baseline으로 복원한다.
- n=1 결과만으로 결론 내리지 않는다. 자동 지표와 수동 검증을 함께 본다.

## 실행 기록 원칙

- 결과 파일은 덮어쓰지 않고 run id 또는 timestamp를 포함한다.
- run artifact에는 입력, 변경점, 판단 기준, latency, case별 결과, metrics를 함께 남긴다.
- eval은 실제 detection pipeline을 호출하고, eval 전용 판정 로직을 따로 만들지 않는다.
- 같은 dataset이나 중간 산출물을 재사용할 때는 현재 policy/config와 맞는지 확인한다.

## 하네스 강화 기준

- 확정된 반복 절차는 초기에 얇게 둘 수 있다. 문서, 체크리스트, skill, helper 중 가장 가벼운 형태를 고른다.
- 아직 발생하지 않은 미래 구조를 예상해서 넓게 만들지는 않는다. 두꺼워지는 문제는 주로 이 지점에서 생긴다.
- 같은 실수가 반복되거나 한 번의 실수 비용이 크면, 새 영역을 늘리기보다 문제가 확인된 지점의 Sensor를 강화한다.
- 새 규칙은 "빼면 실수하는가?"를 통과해야 한다.
- 특정 폴더에만 필요한 규칙은 루트가 아니라 하위 `CLAUDE.md` 또는 `.claude/rules/`로 분리한다.
```

## 한 줄 결론

sprint-4에서 지금 가져올 핵심은 성숙한 앱 구조 전체가 아니라, 실제 코드로 검증된 실행 계약이다. 특히 `planner`, `snapshot`, `override`, `fingerprint`, `pipeline 재사용`, `run artifact`, `보고서 계약`은 이 프로젝트의 intent/interruption 실험 하네스에도 직접 연결된다.
