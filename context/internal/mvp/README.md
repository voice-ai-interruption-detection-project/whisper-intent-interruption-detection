# MVP Execution Hub

이 폴더는 MVP 실행 기준을 모아 두는 작은 허브다.

이 폴더의 기준은 "지금 active인 MVP"다. 과거 `context/archive/product-planning/`의 초기 MVP 기획 문서는 active 기준으로 쓰지 않고, 예전 의도 확인이 꼭 필요할 때만 본다. 여기서는 현재 action label, 판단 케이스(`scenario`) schema, run artifact 계약에 맞춘 MVP 범위와 Step별 작업 흐름만 정리한다.

다만 제품 의도 복원이나 문서 왜곡 점검을 할 때는 현재 MVP 문서도 검토 대상이 될 수 있다. 그때는 먼저 회의 원문과 `context/decisions/`를 확인하고, archive는 예전 의도 확인이 꼭 필요할 때만 본다.

MVP 문서는 앞으로도 바뀔 수 있다. 그래서 이 폴더는 한 번 확정한 PRD 보관소가 아니라, 현재 실행 기준을 작게 유지하고 새 기준이 생길 때 혼선을 줄이기 위한 작업 허브로 둔다.

## 읽는 순서

| 필요 | 먼저 볼 문서 |
| --- | --- |
| 현재 active MVP 범위와 완료 기준 | [Current MVP](current.md) |
| Step별 완료/예정 작업 | [Current MVP Iteration Plan](current-iteration-plan.md) |
| 왜 이 MVP인가 | [Product Context](../product-context.md) |
| 말이 헷갈릴 때 | [Project Language Map](../project-language-map.md), [Reference](../reference/README.md) |
| 수치와 run을 다룰 때 | [Evaluation and Results Contract](../evaluation-and-results-contract.md) |
| 예전 의도 확인이 꼭 필요할 때 | [Archived Product Planning](../../archive/product-planning/README.md), 단 active 기준으로 쓰지 않는다 |

읽는 순서는 고정된 절차가 아니다. 헷갈리는 지점이 바뀌면 이 README를 먼저 고쳐서 다음 사람이 같은 오해를 반복하지 않게 한다.

## 이 폴더의 역할

- [Current MVP](current.md)는 항상 지금 구현 판단의 기준만 담는다.
- [Current MVP Iteration Plan](current-iteration-plan.md)은 그 기준을 Step별 작업 흐름으로 풀어 둔다.
- Step 1, Step 2 같은 작업 순서를 현재 기준으로 유지한다.
- Step은 실행 경계가 아니라 작업 흐름을 설명하는 기록 단위다. 최신 사용자 지시를 우선하고, 필요하면 Step을 넘나들어 작업한다.
- 완료된 작업은 commit, run artifact, 현재 repo 상태와 함께 적는다.
- 예정 작업은 planned로만 적고, 완료처럼 쓰지 않는다.
- 기존 기획 자료에서 유용한 진행감은 가져오되, 현재 용어와 run artifact 기준으로 정규화한다.

## 문서 상태

| 상태 | 의미 | 둘 곳 |
| --- | --- | --- |
| `active` | 지금 구현자가 따라야 하는 기준 | `current.md`, `current-iteration-plan.md` |
| `planned` | 다음 Step/Week 후보. 아직 완료나 확정 기준이 아님 | `current-iteration-plan.md`의 planned/candidate 영역 |
| `candidate` | 새 MVP나 2주차 MVP 후보. active 기준과 섞이면 안 됨 | 필요하면 `context/temp/` 또는 새 decision 초안 |
| `evidence` | 왜 이 방향이 나왔는지 보는 과거 자료 | `context/decisions/`, 예전 의도 확인이 꼭 필요할 때만 `context/archive/` |

새 MVP가 생기면 먼저 그 문서가 `planned`인지 `active`인지 정한다. active로 바뀌기 전에는 [Current MVP](current.md)에 섞어 쓰지 않는다.

`current.md`와 `current-iteration-plan.md`는 한 쌍이다. active MVP가 바뀌면 둘 다 과거 기준으로 남길지, archive/decision으로 옮길지 먼저 정하고 새 current 쌍을 만든다.

## 현재 표현 기준

| 헷갈리기 쉬운 것 | 현재 기준 |
| --- | --- |
| Step N | 달력 날짜나 실행 경계가 아니라 MVP 작업 iteration이다. 완료된 Step은 실제 날짜와 commit을 함께 적는다 |
| 초기 MVP 문서 | active 기준이 아니며, 예전 의도 확인이 꼭 필요할 때만 본다 |
| 페어 기록과 외부 개인 기록 | 프로젝트 바깥의 보조 맥락이다. 이 repo 문서에는 개인 로컬 경로나 개인 작업 허브 경로를 넣지 않는다 |
| 새 MVP 후보 | current에 바로 덧붙이지 않는다. 먼저 planned/candidate 상태와 active 전환 조건을 적는다 |
| `pause` | 현재 action label이 아니다. `respond_and_continue`를 쓴다 |
| `P0`, `P1`, `P2`, `P3` | 단독 표기로 쓰지 않는다. `baseline`, `policy_v1`, `policy_v2`, `policy_v3`를 쓴다 |
| 목표 개선율 | 결과처럼 쓰지 않는다. 수치는 `results/runs/{run_id}/evaluation.json` 생성 후 인용한다 |
| 다른 브랜치의 scaffold/run artifact | current MVP의 근거로 쓰기 전 현재 브랜치, commit, run_id를 다시 확인한다 |
| Workbench | Playground와 Test Bench를 묶는 상위 UI 이름 후보다. 제품 컨셉으로 앞세우지 않는다 |

## 새 MVP 문서가 필요할 때

아래 중 하나면 [Current MVP](current.md)에 바로 이어 쓰지 말고, 먼저 상위 컨텍스트를 확인한다.

- action label, event type, policy version, evaluation contract가 바뀐다.
- Step별 계획이 아니라 MVP의 완료 기준 자체가 바뀐다.
- 2주차 MVP처럼 기존 MVP와 다른 목표/표면/데이터 범위를 잡는다.
- 과거 문서를 다시 가져오면서 현재 용어와 충돌할 수 있다.
- 공개 `docs/`에 옮길 문장과 내부 실행 기준이 섞이기 시작한다.

이때 먼저 볼 상위 컨텍스트:

1. [Product Context](../product-context.md)
2. [Project Language Map](../project-language-map.md)
3. [Evaluation and Results Contract](../evaluation-and-results-contract.md)
4. [context/decisions](../../decisions/)
5. 예전 의도 확인이 꼭 필요할 때만 [Archived Product Planning](../../archive/product-planning/README.md), 단 active 기준으로 쓰지 않는다

## 갱신 규칙

- action label, policy version, 평가 기준이 바뀌면 `context/decisions/`에 먼저 결정 맥락을 남긴다.
- 코드가 실제로 추가되면 [Current MVP](current.md)의 "현재 repo 상태"와 [Current MVP Iteration Plan](current-iteration-plan.md)을 같이 본다.
- 범위가 조금 바뀌면 `current.md`와 `current-iteration-plan.md`를 갱신한다.
- 범위가 크게 바뀌면 decision/context를 먼저 만들고, active가 된 뒤 `current.md`를 새 기준으로 갱신한다.
- 공개 문서로 옮길 때는 이 폴더 문장을 그대로 복사하지 말고 `docs/` 독자에 맞춰 다시 쓴다.
