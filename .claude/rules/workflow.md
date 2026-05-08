# Workflow Rules

이 파일은 commit, PR/공유 메모, 문서 업데이트 같은 작업 운영 기준을 잡는 가벼운 가이드다. 작업 라우팅은 루트 [CLAUDE.md](../../CLAUDE.md)를 본다.

이 규칙은 강한 gate가 아니라 기본값이다. 예외가 필요하면 commit message나 PR/작업 메모에 짧게 이유를 남긴다.

## 작업 단위

- 한 작업은 가능하면 하나의 질문에 답한다. 예: "P1 policy 추가", "runner/app 책임 분리", "README quickstart 갱신".
- 동작 변경, 리팩토링, 문서 정리는 가능하면 commit을 나눈다.
- 한 번에 섞어야 하면 어느 부분이 주요 변경인지 commit body나 PR 메모에 적는다.
- 수치나 성능을 말하는 작업은 Playground 화면이 아니라 Test Bench run artifact를 기준으로 남긴다.

## Commit Convention

commit 제목은 기본적으로 아래 타입 중 하나로 시작한다. type과 scope는 영어 소문자 키워드로 쓰고, 설명 문장은 한국어로 쓴다. scope는 선택이다.

```text
feat(policy): policy_v1 이벤트 매핑 추가
fix(eval): 결과 덮어쓰기 방지
refactor(runner): adapter와 policy 호출 분리
test(harness): 필수 run metadata 검증 추가
docs: quickstart 추가
chore: ruff와 pre-commit 기본 설정 추가
exp: baseline/policy_v1 경계 사례 비교
```

| 타입 | 언제 쓰나 |
| --- | --- |
| `feat` | 사용자/작업자가 쓰는 새 기능이나 새 policy 동작 |
| `fix` | 버그, 잘못된 평가, 덮어쓰기 방지 같은 수정 |
| `refactor` | 동작을 바꾸지 않는 구조 변경 |
| `test` | 테스트 추가/수정 |
| `docs` | README, 가이드, 리포트 문서 |
| `chore` | 포맷터, lock, pre-commit, 설정 정리 |
| `exp` | 실험 실행, 결과 비교, run artifact 추가 |

제목은 짧게 쓰고, body는 필요할 때만 쓴다. body가 필요한 경우:

- 왜 이 변경이 필요한지 제목만으로 부족할 때
- 동작 변경과 구조 변경이 한 commit에 같이 들어갈 때
- 새 의존성, 외부 서비스, 환경 변수가 생길 때
- README/report/slack에 인용할 수치나 run id가 있을 때
- 검증하지 못한 부분이나 의도적 후속 작업이 있을 때

아직 branch naming, PR template, commit message hook은 요구하지 않는다. 반복되는 혼선이 보이면 그때 작은 Sensor로 올린다.

## PR / 작업 메모

PR이나 공유 메모는 길게 쓰기보다 아래 4가지를 빠뜨리지 않는 쪽을 우선한다.

- 변경 요약: 무엇이 달라졌는가
- 이유: 왜 지금 필요한가
- 검증: 어떤 명령, 테스트, run artifact로 확인했는가
- 남은 위험: 아직 확인하지 못한 것, 다음 작업으로 넘길 것

실험 결과를 공유할 때는 run id, dataset, policy version, changed 항목을 같이 적는다. 수치만 단독으로 쓰지 않는다.

수치를 PR/메모에 인용할 때는 `result-evidence-checker` agent로 한 번 본다 — Playground 화면 수치는 인용 출처로 쓰지 않는다.

## 문서 업데이트 기준

아래가 바뀌면 README 또는 관련 가이드를 같이 본다.

- 설치/실행 명령
- Python 버전, 의존성, 외부 서비스, 환경 변수
- data/scenario 형식
- run artifact 필수 필드
- action label, policy version, 평가 기준
- 팀원이 같은 repo만 보고 재현해야 하는 절차

개인 로컬 경로, 개인 AI 도구 설정, 비공개 원천 자료 경로는 프로젝트 문서에 넣지 않는다.

## Sensor로 올릴 기준

처음부터 hook으로 막지 않는다. 아래 중 하나가 확인되면 자동 체크를 검토한다.

- 같은 실수가 두 번 이상 반복된다.
- 한 번의 실수로 result, credential, 공개 수치 신뢰성이 크게 깨진다.
- 사람이 매번 기억해서 확인하기 어렵다.

초기 Sensor 후보는 ruff, pre-commit, secret scan, result overwrite 방지 테스트 정도다. commit message hook, fixture write 차단, harness scanner는 실제 반복 패턴이 보일 때 추가한다.
