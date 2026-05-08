# 지식 허브 / 글쓰기 하네스 구조 분석과 차용안

작성일: 2026-05-07

## 목적

이 문서는 두 개의 외부 참고 프로젝트 — 장기 지식 허브 성격의 repo("dev-hub")와 글쓰기 운영 repo("blog") — 의 하네스 구조를 분석하고, `whisper-intent-interruption-detection` 프로젝트에 가져올 만한 개념과 아직 가져오지 않는 편이 나은 요소를 정리한다.

> 이 두 참고 프로젝트의 원천 저장소는 이 repo에 포함되어 있지 않다. 패턴과 결론만 가져오고, 폴더 구조나 도구 묶음은 그대로 복사하지 않는다.

결론부터 말하면, 지금 프로젝트에는 두 참고 프로젝트의 전체 구조를 복제하기보다 **연구/실험 프로젝트에 맞는 얇은 하네스**를 먼저 두는 편이 좋다. 핵심은 폴더를 많이 만드는 것이 아니라, raw data, label, experiment, eval, decision의 경계를 분명히 해서 AI가 작업할 때 근거와 수정 권한을 혼동하지 않게 만드는 것이다.

## 통합 컨텍스트 카드

### 참고한 자료의 역할

- 지식 허브 repo의 루트 가이드 — 장기 지식 허브의 폴더 역할, 주도권, 보호 경로, Gold-In 원칙이 가장 잘 드러난다.
- 지식 허브 repo의 결정 기록 한 건 — 프로젝트 특화 로직과 글로벌 공통 골격을 분리한 사례.
- 지식 허브 repo의 collector / checker agent 정의 — 흩어진 자료를 report-only 카드로 모으고, 작성물의 수치·용어·사실·출처 정합성을 검증하는 방식.
- 글쓰기 repo의 루트 가이드 — content / editorial / site 레이어 분리와 agent 역할 경계.
- 글쓰기 repo의 editorial 기준 문서 — core / lenses / guards / reference-profiles / context / decisions / audits로 기준 문서를 나눈 구조.
- 글쓰기 repo의 workflow 정의 — `Material -> Shaping -> Texture -> Prepublish` 단계 모델.
- 글쓰기 repo의 output contracts — 작업이 진단에 머물지 않고 실제 산출물을 남기게 하는 계약.
- 글쓰기 repo의 source policy — 원천 자료와 공개 산출물 사이의 경계.
- 본 프로젝트의 루트 가이드 — 최소 브릿지와 운영 기준만 둔 상태이며, 반복 패턴이 생긴 뒤 로컬 skill/agent/rule을 추가한다는 원칙이 있다.

### Related Areas

- 지식 허브 repo: 장기 지식, 면접, 이력서, 피드백, 트랙 자료가 섞이는 cross-folder 허브.
- 글쓰기 repo: 공개 글이라는 산출물 품질을 단계적으로 끌어올리는 editorial harness.
- whisper project: 아직 구현/자료 구조가 거의 없고, raw audio/transcript/label/eval의 provenance가 앞으로 핵심 리스크가 될 가능성이 크다.

### Constraints

- 현재 프로젝트 가이드는 세부 skill, agent, rule을 반복 패턴이 생긴 뒤 추가하라고 명시한다.
- agent는 report-only/read-only로 다루는 원칙을 유지해야 한다.
- raw audio, transcript, label 원천이 생기면 보호 경로와 파생물 경계를 먼저 정해야 한다.

## dev-hub 하네스의 핵심 컨셉

dev-hub는 폴더가 많은 프로젝트가 아니라, **장기 자산으로 남길 지식과 작업 흔적을 어느 층위에 둘지 결정하는 운영체제**에 가깝다.

핵심 패턴은 다섯 가지다.

1. **Root File Sync**
   `CLAUDE.md`를 원천으로 두고 `AGENTS.md -> CLAUDE.md` symlink로 Codex와 Claude가 같은 지침을 보게 한다. 같은 의도를 두 런타임에 복제하지 않고 한 곳에 둔다.

2. **주도권 기반 폴더 역할**
   폴더를 "누가 소유하는가"보다 "누가 주도하는가"로 나눈다. 예를 들어 `knowledge`는 AI 주도, `study`는 사용자 주도, `archive-db/source/feedback/input`은 수정 금지다. 이 방식은 AI가 어디를 고쳐도 되는지, 어디는 evidence로만 봐야 하는지 빠르게 판단하게 해준다.

3. **Gold-In 원칙**
   정식 자산을 만들기 전에 입력, 목적, 사용자 판단 영역이 분명한지 확인한다. 애매한 raw 자료를 바로 정식 지식으로 승격하지 않고, 필요하면 `inbox`라는 완충지대를 거친다.

4. **공통 엔진 + 로컬 프로필**
   `gather-context`, `session-bridge`, `material-collector`, `evidence-checker`처럼 여러 프로젝트에서 반복되는 골격은 글로벌로 승격하고, dev-hub의 9영역 검색 지도 같은 것은 로컬 프로필로 남겼다. 이 분리가 매우 좋다. 전역 도구가 특정 프로젝트 폴더명을 잘못 가정하는 일을 막는다.

5. **report-only agent**
   자료 수집이나 검증은 별도 agent가 맡되, 파일 수정 권한을 주지 않는다. 메인 작업자는 compact card나 검증 결과만 받아서 최종 판단과 수정을 수행한다.

### dev-hub의 이점

- 장기 지식이 쌓여도 "원천 / 파생 / 정리 / 회고 / 결정"이 섞이지 않는다.
- AI가 원본 보존 폴더를 건드릴 위험이 줄어든다.
- 한 작업이 resume, interview, feedback, track처럼 여러 영역에 영향을 줄 때 누락을 줄인다.
- 작업이 커질수록 context 수집 비용을 낮춘다.
- 글로벌로 뺄 것과 프로젝트 안에 둘 것을 구분해 하네스가 과잉 일반화되지 않는다.

## blog 하네스의 핵심 컨셉

blog는 dev-hub보다 범위가 좁지만, 산출물 품질 관리가 더 정교하다. 핵심은 **기준 문서와 실행 agent를 분리**한 점이다.

핵심 패턴은 여섯 가지다.

1. **레이어 분리**
   `content/`는 원고, `editorial/`은 글쓰기 판단 기준, `site/`는 구현 루트다. 같은 repo 안에 있어도 content, editorial, implementation의 책임이 섞이지 않게 한다.

2. **core / lenses / guards / decisions**
   `core`는 작업 흐름과 산출물 계약, `lenses`는 판단 렌즈, `guards`는 공개 안전과 발행 전 hard guard, `decisions`는 하네스 변경 이유를 기록한다. 렌즈를 단계처럼 쓰거나 guard를 초안 창작 기준으로 되돌리는 일을 막는 구조다.

3. **단계형 workflow**
   `Material -> Shaping -> Texture -> Prepublish` 순서로 작업을 나눈다. 글감 발굴, 구조 편집, 질감 보존, 발행 안전 점검을 한 번에 섞지 않는다.

4. **output contract**
   review-only여도 추상 조언으로 끝내지 않고, 그대로 옮길 수 있는 문구, 표, 슬롯, 이동 후보를 남기게 한다. 하네스가 "검토했다"가 아니라 "다음 행동이 가능하다"로 끝나게 하는 장치다.

5. **source policy**
   원천 자료는 evidence이고, 공개 글에는 해석된 문장만 남긴다. 내부 경로, 코드 원문, 개인 메모, 비공개 피드백은 노출하지 않는다.

6. **harness observer**
   새 렌즈나 agent가 생겼을 때, 그것이 기존 구조 안에서 제자리를 찾았는지 report-only로 본다. observer 자체가 새 기준 저장소가 되지 않도록 제한한다.

### blog의 이점

- 산출물 품질을 "톤" 하나로 뭉개지 않고, 글감/구조/질감/검증으로 나눠 볼 수 있다.
- 기준 본문은 `editorial/`이 소유하고 agent는 얇은 실행자로 남는다.
- 특정 글에서 생긴 임시 판단이 전체 규칙으로 과잉 승격되는 것을 막는다.
- 발행 전에는 hard guard를 적용해 공개 경계와 메타데이터를 안정적으로 확인한다.
- 구현 사이트와 원고 편집 기준이 섞이지 않는다.

## 현재 프로젝트에 바로 가져올 만한 것

### 1. Root File Sync는 이미 유지

현재 프로젝트의 `CLAUDE.md`는 이미 `AGENTS.md -> CLAUDE.md` 브릿지를 전제로 한다. 이건 그대로 유지하면 된다. 추가로 할 일은 많지 않고, 하위 작업 영역이 생겼을 때 같은 패턴을 반복하면 된다.

추천:

- 루트 `CLAUDE.md`는 계속 한 곳의 원천으로 둔다.
- `experiments/`, `evals/`, `data/`처럼 하위 지침이 필요한 영역이 생기면 그 폴더에 `CLAUDE.md`를 두고 `AGENTS.md -> CLAUDE.md` symlink를 둔다.
- 단, 지금은 아직 폴더 역할이 안정되지 않았으므로 하위 지침을 서두르지 않는다.

### 2. dev-hub의 "주도권/보호 경로" 개념

이 프로젝트에서 가장 먼저 필요해질 가능성이 큰 것은 skill이 아니라 **수정 가능 경로와 evidence-only 경로의 구분**이다.

추천 초안:

```text
data/raw/          # 원본 audio/transcript, 수정 금지 또는 gitignore
data/labels/       # label 원천, 수정 이력 중요
data/prepared/     # 파생 데이터, 재생성 가능
experiments/       # 실험 단위 기록, config/metrics/notes
evals/             # 평가셋, scoring 기준, report
src/               # 구현 코드
notes/             # 빠른 관찰, 세션 메모
decisions/         # 모델/eval/harness 결정 기록
```

이 구조는 지금 바로 다 만들 필요는 없다. 하지만 raw data나 label이 들어오는 순간에는 `data/raw`와 `data/labels`의 보호 규칙을 먼저 정하는 편이 좋다.

### 3. blog의 core/lens/guard 분리

Whisper intent/interruption 프로젝트에도 blog식 분리가 잘 맞는다. 이름만 연구 프로젝트식으로 바꾸면 된다.

- `core`: 실험 흐름, run 기록 방식, eval contract.
- `lenses`: 오류 분석 관점. 예: false interrupt, missed interrupt, intent ambiguity, latency, ASR noise, VAD/no-speech.
- `guards`: raw audio/transcript 보호, label provenance, metric 계산 재현성, public/private boundary.
- `decisions`: 모델 선택, metric 선택, threshold 변경, dataset split 변경 이유.

여기서 중요한 점은 lens를 hard rule로 만들지 않는 것이다. 예를 들어 "latency lens"는 실험을 볼 때 켜는 관점이지, 모든 실험의 유일한 목적이 되어서는 안 된다.

### 4. report-only collector/checker

반복 패턴이 생긴 뒤에는 로컬 agent 후보가 선명하다.

- `experiment-material-collector`: 특정 run이나 오류 케이스를 볼 때 config, dataset slice, transcript sample, metrics, commit을 compact card로 모은다.
- `eval-evidence-checker`: report나 README의 수치가 실제 metrics 파일, config, dataset split과 맞는지 검증한다.

지금 당장 agent 파일을 만들기보다는, 두세 번 수동으로 같은 검증을 반복한 뒤 로컬 agent로 승격하는 편이 좋다. 현재 루트 가이드의 "반복 패턴이 생긴 뒤 추가" 원칙과도 맞다.

### 5. decision record

ML/ASR 실험은 시간이 지나면 "왜 이 threshold였지?", "왜 이 metric을 봤지?", "이 label 기준은 언제 바뀌었지?"가 금방 흐려진다. dev-hub/blog 모두 decision record를 잘 쓰고 있고, 이 프로젝트에도 강하게 추천한다.

추천 decision record 대상:

- Whisper 모델/버전 변경.
- intent/interruption label schema 변경.
- evaluation metric 변경.
- threshold 또는 hysteresis 정책 변경.
- dataset split 변경.
- raw/audio/transcript 공개 가능 범위 변경.
- Claude/Codex 하네스 구조 변경.

가볍게 시작하려면 `decisions/YYYY-MM-DD-*.md` 한 파일씩이면 충분하다.

## 아직 가져오지 않는 편이 나은 것

1. **dev-hub의 9영역 검색 지도**
   현재 프로젝트에는 resume/interview/feedback/track처럼 복잡한 cross-folder 자산이 없다. 그대로 가져오면 빈 구조만 커진다.

2. **blog의 다중 writing agent 세트**
   `material`, `shaping`, `texture`, `tone`, `structure` 같은 역할 분리는 글쓰기 repo에는 맞지만, 이 프로젝트에는 과하다. 대신 collector/checker 두 축이 먼저다.

3. **글로벌 skill 승격**
   이 프로젝트에서 생기는 절차는 먼저 로컬에 둬야 한다. 다른 프로젝트에서도 반복된다는 증거가 생기기 전에는 전역으로 올리지 않는다.

4. **하네스 observer**
   blog처럼 하네스 변경이 자주 일어나는 단계가 되면 유용하지만, 지금은 루트 문서와 decision record만으로 충분하다.

5. **자동 hook/rule 강제**
   raw data 보호는 중요하지만, 실제 경로와 작업 흐름이 생기기 전부터 hook을 만들면 오히려 실험 속도를 떨어뜨릴 수 있다. 먼저 문서 규칙, 그 다음 필요할 때 script/hook이 맞다.

## 추천 도입 단계

### Phase 0: 지금

- 이 분석 문서를 루트 기준점으로 둔다.
- `CLAUDE.md`의 최소 브릿지 원칙은 유지한다.
- 아직 `.claude/skills`, `.claude/agents`, `.codex/agents`를 늘리지 않는다.

### Phase 1: raw data / label이 들어올 때

- `data/raw`, `data/labels`, `data/prepared`의 역할과 수정 규칙을 정한다.
- raw audio/transcript는 evidence-only인지, gitignore 대상인지, 파생본만 commit할지 결정한다.
- label schema 변경은 decision record로 남긴다.

### Phase 2: 첫 실험 루프가 반복될 때

- `experiments/{YYYY-MM-DD-slug}/` 또는 `runs/{run-id}/` 같은 run 기록 단위를 정한다.
- 각 run에 config, command, commit, dataset slice, metrics, error notes를 남기는 최소 contract를 둔다.
- eval report가 생기면 수치/용어/시점 정합성을 수동 체크한다.

### Phase 3: 같은 수집/검증이 2-3회 반복될 때

- 로컬 `experiment-material-collector` 또는 `eval-evidence-checker` agent를 검토한다.
- agent는 report-only로 두고, 파일 수정은 메인 작업자만 한다.
- skill은 dispatcher 역할만 하고, 기준 본문은 `docs/`, `evals/`, `decisions/` 같은 프로젝트 문서가 소유하게 한다.

## 이 프로젝트용 하네스 컨셉 초안

한 문장으로 요약하면:

> 이 프로젝트의 하네스는 Whisper 기반 intent/interruption detection 실험에서 raw/audio/label/eval/report의 근거 사슬을 보존하고, AI가 실험 결과를 해석할 때 원천과 파생물을 혼동하지 않게 하는 얇은 운영 레이어다.

핵심 질문:

- 이 파일은 raw source인가, 파생물인가, 정식 결과인가?
- 이 수치는 어떤 config, dataset split, commit에서 나온 것인가?
- 이 label 기준은 언제, 왜 바뀌었는가?
- 이 threshold나 metric은 어떤 실패 케이스 때문에 선택되었는가?
- AI가 수정해도 되는 파일인가, evidence로만 읽어야 하는 파일인가?

이 질문에 답하는 구조만 먼저 만들면 된다. 하네스의 목적은 프로젝트를 의식적으로 느리게 만드는 것이 아니라, 실험이 늘어날수록 다시 들어와도 길을 잃지 않게 하는 것이다.

## 최종 추천

지금 가져올 것은 세 가지다.

1. **Root bridge 유지**: `CLAUDE.md` 원천 + `AGENTS.md` symlink.
2. **보호 경로/파생 경로 개념**: raw, labels, prepared, experiments, evals의 경계.
3. **decision record 습관**: metric, threshold, dataset, label, harness 변경의 이유 보존.

조금 뒤에 가져올 것은 두 가지다.

1. **report-only collector/checker**: 실험 수집과 수치 검증이 반복될 때.
2. **core/lens/guard 문서 분리**: eval 기준과 오류 분석 관점이 많아질 때.

가져오지 않을 것은 "완성된 하네스의 모양"이다. dev-hub와 blog에서 배울 점은 폴더명이나 agent 수가 아니라, **원천을 보호하고, 판단 기준의 소유자를 분리하고, 반복된 작업만 도구화하는 태도**다.
