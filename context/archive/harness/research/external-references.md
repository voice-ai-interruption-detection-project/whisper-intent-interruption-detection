# AI 개발 하네스 레퍼런스 조사

작성일: 2026-05-07

## 목적

`gstack`을 비롯해 2026년 현재 개발 작업에서 많이 언급되는 AI 코딩 하네스 구성 사례를 조사하고, `whisper-intent-interruption-detection` 프로젝트에 어떤 형태로 차용하면 좋은지 정리한다.

결론부터 말하면, 지금 이 프로젝트에는 완성형 skill pack을 통째로 설치하기보다 **얇은 root instruction + 반복될 때만 추가하는 skill/agent + 실험 결과를 검증하는 gate**가 맞다. 좋은 하네스의 공통점은 “AI에게 많은 규칙을 먹이는 것”이 아니라, 원천 자료, 실행 절차, 검증 증거, 회고를 서로 헷갈리지 않게 만드는 것이다.

## 조사 기준

- 2026년에 실제 사용자가 많이 언급하거나 공식 문서에서 지원하는 구성일 것.
- Claude Code, Codex, Cursor, Copilot, Gemini 같은 여러 agentic coding 환경과 연결 가능한 패턴일 것.
- 이 프로젝트의 현재 상태처럼 아직 코드/데이터 구조가 얇은 실험 repo에도 단계적으로 적용 가능할 것.
- 장기적으로 raw audio, transcript, label, experiment, eval report의 근거 사슬을 보존하는 데 도움이 될 것.

## 핵심 관찰

### 1. `AGENTS.md`/`CLAUDE.md`는 짧을수록 좋다

OpenAI Codex 공식 문서는 Codex가 실행 시작 시 global `AGENTS.md`와 프로젝트/하위 디렉토리의 `AGENTS.md`를 계층적으로 읽는다고 설명한다. 가까운 디렉토리의 지침이 뒤에 붙어 override 역할을 하며, 기본 결합 한도도 있다.

하지만 2026년 arXiv 연구는 repository-level context file이 과도하면 task success를 낮추고 inference cost를 20% 이상 늘릴 수 있다고 보고했다. 특히 불필요한 요구사항이 agent의 탐색 범위를 넓혀서 문제를 어렵게 만든다는 결론이 중요하다.

이 프로젝트에 대한 시사점:

- 루트 `CLAUDE.md`/`AGENTS.md`에는 항상 필요한 것만 둔다.
- 세부 규칙은 실제 폴더와 반복 절차가 생긴 뒤 하위 문서로 내린다.
- “좋은 말”보다 특정 명령, 보호 경로, 검증 기준처럼 빠지면 실수하는 정보만 남긴다.

### 2. 좋은 하네스는 surface를 나눈다

Claude Code 공식 문서는 `CLAUDE.md`, rules, skills, subagents, hooks, MCP가 각각 다른 문제를 푼다고 구분한다.

- `CLAUDE.md`: 매 세션 필요한 프로젝트 핵심 관습, 빌드/테스트 명령, 아키텍처 지도.
- rules: 언어별, 경로별, 디렉토리별 지침.
- skills: 가끔만 필요한 반복 workflow와 reference material.
- subagents: 탐색, 검증, 리뷰처럼 main context를 더럽히지 않아야 하는 작업.
- hooks: 사람의 기억이 아니라 실행 장치로 강제해야 하는 guard.
- MCP: 외부 시스템이나 live data에 접근해야 할 때.

이 프로젝트에 대한 시사점:

- 현재는 `CLAUDE.md`와 조사 문서만 유지한다.
- raw data, label, eval 구조가 생기면 `data/`, `experiments/`, `evals/` 아래에 좁은 지침을 둔다.
- 같은 검증을 2-3번 반복한 뒤에야 local skill/agent로 승격한다.
- hook은 반복 사고가 확인된 뒤에만 둔다.

### 3. `gstack`의 강점은 도구 수가 아니라 단계 gate다

Garry Tan의 `gstack`은 자신을 “process, not a collection of tools”라고 설명하고, sprint 흐름을 `Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect`로 둔다. 각 skill은 다음 skill의 입력이 되는 artifact를 남긴다. 예를 들어 초기 design doc이 plan review로 이어지고, test plan이 QA로 이어지며, review 결과가 ship 검증으로 이어진다.

좋은 점:

- idea에서 ship까지 단계가 끊기지 않는다.
- planning, architecture, design, review, QA 역할을 분리한다.
- `/careful`, `/freeze`, `/guard` 같은 안전 장치로 scope creep과 위험 명령을 줄인다.
- `/codex` 같은 cross-model second opinion 패턴을 둔다.

주의점:

- 이 프로젝트에는 아직 제품 기능 개발 workflow가 안정되지 않았다.
- 20개 이상의 role/skill을 지금 들이면 context와 운영 비용이 먼저 늘어난다.
- safety command는 유용하지만, 현재 Codex/Claude 브릿지 구조와 맞춰 별도 설계가 필요하다.

차용안:

- 전체 gstack 설치보다 “단계 gate”만 차용한다.
- 각 실험은 `Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect`의 얇은 버전으로 기록한다.
- 특히 `Review`와 `Test`는 코드 리뷰뿐 아니라 metric, dataset split, threshold, sample evidence 검증까지 포함한다.

### 4. Superpowers는 강한 개발 규율을 skill로 만든 사례다

`obra/superpowers`는 brainstorming, worktree, writing plan, subagent-driven development, TDD, code review, branch finish를 하나의 기본 workflow로 묶는다. README는 TDD, systematic debugging, evidence over claims를 핵심 철학으로 둔다.

좋은 점:

- 계획을 작은 task로 쪼개고 verification step을 붙인다.
- fresh subagent와 two-stage review를 통해 spec compliance와 code quality를 분리한다.
- TDD와 systematic debugging처럼 반복 실패를 줄이는 절차가 뚜렷하다.

주의점:

- 탐색형 ML/ASR 실험에서는 모든 변경을 TDD로 강제하기 어렵다.
- 실험 notebook, dataset prep, threshold 탐색에는 “test first”보다 baseline/eval evidence가 더 중요할 수 있다.

차용안:

- “evidence over claims”와 “verification before completion”을 가져온다.
- implementation task에는 TDD를 권장하되, 실험 task에는 baseline/eval/sample evidence를 동등한 검증 단위로 둔다.

### 5. Compound Engineering은 학습을 다음 작업의 자산으로 남기는 데 강하다

Every의 Compound Engineering plugin은 strategy, brainstorm, plan, work, review, compound note의 loop를 제안한다. 핵심은 “각 engineering unit이 다음 engineering unit을 쉽게 만들어야 한다”는 점이다.

좋은 점:

- `STRATEGY.md` 같은 짧은 durable anchor를 둔다.
- review에서 끝나지 않고, 배운 내용을 reusable knowledge로 남긴다.
- planning/review 비중을 높게 잡아 ad hoc coding을 줄인다.

주의점:

- 제품 전략과 feature delivery를 중심으로 설계되어 있다.
- 이 프로젝트의 초기 단계에서는 `STRATEGY.md`보다 실험 decision record가 먼저일 수 있다.

차용안:

- 모델/metric/threshold/dataset split 변경은 `decisions/YYYY-MM-DD-*.md`로 남기는 방향이 좋다.
- 실험 실패에서 얻은 재사용 가능한 교훈은 나중에 local skill이나 eval checklist로 승격한다.

### 6. BMAD는 큰 product lifecycle에는 좋지만 지금은 과하다

BMAD Method는 PM, Architect, Developer, UX 등 여러 전문 agent와 agile workflow를 제공한다. 구조화된 PRD/architecture/story handoff가 필요한 큰 제품 개발에는 강하다.

좋은 점:

- brainstorming부터 deployment까지 lifecycle이 분명하다.
- 프로젝트 규모에 따라 planning depth를 조정하려는 철학이 있다.
- agent handoff artifact를 중시한다.

주의점:

- 현재 repo는 아직 구현과 실험 구조가 거의 없어서 full lifecycle framework가 무겁다.
- Whisper intent/interruption detection의 핵심 리스크는 PRD보다 data/eval provenance다.

차용안:

- 앱/서비스로 커진 뒤 feature story와 architecture handoff가 필요할 때 다시 검토한다.
- 지금은 “scale-adaptive” 원칙만 기억한다. 작은 실험에는 작은 하네스면 충분하다.

## 레퍼런스별 적용 요약

| 레퍼런스 | 핵심 패턴 | 지금 차용 | 보류 |
| --- | --- | --- | --- |
| `garrytan/gstack` | 단계별 role skill과 ship gate | `Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect` 얇은 실험 gate | 전체 skill pack, safety command 설치 |
| Superpowers | TDD, systematic debugging, two-stage review | evidence before completion, verification gate | 전면 TDD 강제 |
| Compound Engineering | strategy anchor, plan/review/compound loop | decision record, reusable learning | 제품 전략 plugin 구조 |
| BMAD Method | agile lifecycle, specialist agents | scale-adaptive planning 철학 | PRD/story 중심 full framework |
| Codex `AGENTS.md` | 계층형 project instruction | root symlink 유지, 하위 폴더 지침은 필요 시 추가 | 큰 monolithic instruction |
| Claude Code docs | CLAUDE/rules/skills/subagents/hooks/MCP 분리 | surface별 책임 구분 | 초기 hook/MCP 과잉 도입 |
| Copilot/Cursor/Gemini 계열 | path-specific instruction, cross-tool context | 단일 원천과 drift 관리 | 도구별 instruction 중복 복사 |
| arXiv AGENTS.md 연구 | context file 과잉의 역효과 | 최소 요구사항만 문서화 | 자동 생성 장문 context |

## 이 프로젝트용 추천 하네스 형태

### 현재 유지할 것

- `CLAUDE.md`를 root instruction 원천으로 유지한다.
- `AGENTS.md -> CLAUDE.md` symlink를 유지한다.
- 하네스 문서는 root에 두되, 실행 규칙으로 승격하기 전에는 분석/결정 문서로 취급한다.

### 첫 실험 루프용 gate

각 실험이나 구현 slice는 다음 질문에 답할 수 있어야 한다.

1. Think: 어떤 실패 케이스나 목표 지표를 다루는가?
2. Plan: baseline, dataset/sample, 변경 변수, 평가 방법은 무엇인가?
3. Build: 바꾼 코드는 어디이며, config/threshold/prompt 변경은 무엇인가?
4. Review: data leakage, label drift, threshold overfit, ASR noise 처리 문제가 없는가?
5. Test: 자동 eval, 수동 sample, before/after evidence가 있는가?
6. Ship: 결과 report나 README/decision에 반영했는가?
7. Reflect: 다음 실험에 재사용할 교훈이 생겼는가?

### 폴더가 생길 때 추천 경계

```text
data/raw/          # 원본 audio/transcript, evidence-only 또는 gitignore 후보
data/labels/       # label 원천, 변경 이력 중요
data/prepared/     # 재생성 가능한 파생 데이터
experiments/       # run 단위 config, command, metrics, notes
evals/             # 평가셋, scoring 기준, report
src/               # 구현 코드
decisions/         # 모델/eval/harness 결정 기록
notes/             # 빠른 관찰, 세션 메모
```

이 구조는 지금 바로 만들 필요는 없다. raw data나 label이 들어오는 순간에 먼저 정하는 것이 좋다.

### local skill/agent 후보

반복 패턴이 생기면 아래만 로컬로 검토한다.

- `experiment-material-collector`: 특정 run의 config, commit, dataset slice, metrics, sample evidence를 report-only 카드로 모은다.
- `eval-evidence-checker`: report의 수치와 실제 metrics/config/dataset split이 맞는지 검증한다.
- `failure-case-review`: false interrupt, missed interrupt, ambiguous intent 같은 실패 케이스를 lens별로 분류한다.
- `experiment-ship-check`: 완료 전 baseline/eval/sample/decision 기록이 빠졌는지 확인한다.

agent는 기본적으로 read-only/report-only로 둔다. 파일 수정은 메인 작업자만 한다.

## 도입 순서

### Phase 0: 지금

- 이 문서를 reference map으로 둔다.
- root `CLAUDE.md`는 더 늘리지 않는다.
- 외부 skill pack은 설치하지 않는다.

### Phase 1: 데이터/라벨이 들어올 때

- `data/raw`, `data/labels`, `data/prepared` 경계를 정한다.
- raw source와 파생물의 수정 권한을 문서화한다.
- label schema 변경은 decision record로 남긴다.

### Phase 2: 첫 eval loop가 반복될 때

- run artifact contract를 정한다.
- 각 run에 command, config snapshot, commit, dataset slice, metrics, manual sample을 남긴다.
- report 숫자는 `eval-evidence-checker` 후보 절차로 수동 검증한다.

### Phase 3: 반복 실패가 보일 때

- 같은 실수를 막는 rule, skill, hook을 하나씩 승격한다.
- 예: raw data 수정 사고가 반복되면 hook이나 deny rule 검토.
- 예: eval report 숫자 오류가 반복되면 checker agent 검토.

## 가져오지 않을 것

- gstack/Superpowers/BMAD 전체를 현재 repo에 vendoring하지 않는다.
- 외부 skill pack을 읽지 않고 설치하지 않는다.
- 자동 memory나 telemetry를 하네스의 기본 전제로 두지 않는다.
- tool-specific instruction 파일을 여러 개 복사해 drift를 만들지 않는다.
- “언젠가 유용할 규칙”을 루트 instruction에 미리 넣지 않는다.

## 출처

- Garry Tan, `gstack`: <https://github.com/garrytan/gstack>
- Dench blog, gstack overview: <https://www.dench.com/blog/gstack-explained>
- OpenAI Codex `AGENTS.md` guide: <https://developers.openai.com/codex/guides/agents-md>
- OpenAI Codex CLI docs: <https://developers.openai.com/codex/cli>
- Claude Code feature overview: <https://code.claude.com/docs/en/features-overview>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Claude Code subagents: <https://code.claude.com/docs/en/sub-agents>
- Claude Code hooks: <https://code.claude.com/docs/en/hooks>
- Superpowers: <https://github.com/obra/superpowers>
- Compound Engineering plugin: <https://github.com/EveryInc/compound-engineering-plugin>
- BMAD Method: <https://github.com/bmad-code-org/BMAD-METHOD>
- GitHub Copilot custom instructions: <https://docs.github.com/en/copilot/concepts/prompting/response-customization>
- Cursor rules: <https://cursor.com/docs/rules>
- Gemini CLI configuration: <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md>
- arXiv, Evaluating AGENTS.md: <https://arxiv.org/abs/2602.11988>
- arXiv, Configuring Agentic AI Coding Tools: <https://arxiv.org/abs/2602.14690>
- arXiv, ABTest: Behavior-Driven Testing for AI Coding Agents: <https://arxiv.org/abs/2604.03362>
