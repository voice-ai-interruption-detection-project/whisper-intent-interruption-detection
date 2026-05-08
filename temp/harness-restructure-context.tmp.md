# Harness Restructure Context Brief

이 문서는 PR 리뷰어가 이번 하네스 구조 정리의 배경과 판단 기준을 빠르게 이해하도록 돕는 임시 공유 메모다. 구현 기준 문서가 아니라 PR 설명을 보조하는 context brief다.

## 왜 지금 정리했나

`feat/harness`와 `chore/project-initialization`이 합류한 뒤, 프로젝트에는 세 종류의 문서가 함께 남았다.

- `docs/`: mkdocs로 공유/공개되는 문서
- `기획/`: 하네스 정리 이전에 작성된 PRD, 계획서, 용어 결정 노트
- `.claude/rules/`: 실험과 작업 흐름을 제어하는 active 가드

각 문서는 모두 필요하지만, 어느 문서가 "지금 기준"인지가 명확하지 않으면 라벨, 정책, 평가 기준 변경이 일부 파일에만 반영될 수 있다. 실제로 `pause`와 `respond_and_continue`가 함께 남아 있거나, `results/` 산출물 트리 설명이 문서와 rule에서 갈라지는 문제가 생겼다.

이번 PR은 이런 내용 불일치를 바로 고치는 PR이 아니다. 먼저 자료가 흘러갈 위치와 책임을 정리해, 다음 정합성 작업이 한 방향으로 진행되게 만드는 기반 작업이다.

## 새 구조의 핵심

| 영역 | 의도 |
| --- | --- |
| `internal/` | 기획 보강, 용어, 정책 초안, 평가 기준, 설계 메모처럼 팀 안에서 먼저 맞출 내부 기준 자료 |
| `decisions/` | 결정, 고민, AI 대화 맥락을 사안별 폴더로 남기는 기록 |
| `archive/` | 현재 기준에서 물러난 자료를 보관하는 루트 archive |
| `temp/` | 잠깐 공유하거나 정리 전 상태로 둘 임시 자료 |

중요한 흐름은 아래와 같다.

```text
기획/ 또는 대화/실험에서 나온 재료
-> internal/에서 현재 기준으로 정리
-> 기준 변경이면 decisions/에 맥락 기록
-> 외부 공유가 필요하면 docs/에 발췌
-> 더 이상 기준이 아니면 archive/로 이동
```

## 왜 docs를 바로 고치지 않았나

`docs/`에는 이미 라벨 잔재, 미실측 수치, results 트리 불일치가 보인다. 하지만 이번 PR에서 그것까지 같이 고치면 "구조 정리"와 "공개 문서 내용 정정"이 한 변경에 섞인다.

그래서 이번 PR은 `docs/` 본문을 건드리지 않는다. 대신 `internal/`, `decisions/`, rule, agent 경계를 먼저 잡고, follow-up에서 공개 문서를 현재 기준에 맞춰 정리한다.

## 왜 기획/을 바로 삭제하지 않았나

`기획/`은 현재 기준 문서가 아니라 하네스 이전 배경 자료다. 다만 그 안에는 용어 결정과 제품 방향의 흔적이 남아 있어 바로 삭제하면 맥락을 잃을 수 있다.

이번 PR에서는 `기획/`을 freeze된 참고 자료로 두고, 새 결정과 기준은 `internal/`과 `decisions/`로 흐르게 했다. 자료가 충분히 옮겨진 뒤 삭제 여부를 follow-up에서 판단한다.

## 왜 record-decision skill을 추가했나

결정 기록은 "해야 한다"는 규칙만 두면 쉽게 밀린다. `record-decision` skill은 사안별 폴더, `README.md`, `context.md`, `raw.md` 골격을 만들어 결정과 원문 맥락을 남기는 비용을 줄이기 위한 보조 도구다.

이 프로젝트에서는 특히 AI 대화 중 결정이 만들어지는 일이 많으므로, 결정 결과뿐 아니라 어떤 대화와 고민을 거쳤는지도 함께 남기는 구조가 필요하다.

## 왜 agent 설명도 같이 바꿨나

새 폴더만 만들고 agent가 예전 위치만 보면 다시 drift가 생긴다.

- `experiment-material-collector`는 자료를 모을 때 `internal/`, `decisions/`, `data/`, `results/`를 우선 보도록 했다.
- `harness-structure-reviewer`는 `internal/`, `decisions/`, `archive/`가 active rule이나 코드와 충돌하는지 보도록 했다.
- `result-evidence-checker`는 수치는 `results/runs/{run_id}/`, 어휘는 `decisions/`와 active rules 기준으로 확인하도록 했다.

Codex bridge toml도 함께 갱신해 Claude/Codex 쪽 정의가 갈라지지 않게 했다.

## 이번 PR이 만들고 싶은 상태

- `CLAUDE.md`만 봐도 어느 자료가 어디로 가야 하는지 알 수 있다.
- 내부 기준 자료와 공개 문서가 섞이지 않는다.
- 결정과 대화 맥락을 저장할 자리가 있다.
- 과거 자료와 현재 기준이 충돌할 때 active 쪽이 우선이라는 경계가 있다.
- follow-up 문서 정합성 작업이 `internal/`과 `decisions/`를 기준으로 진행될 수 있다.

## Follow-up으로 남긴 것

- `docs/`의 `pause` / `respond_and_continue` 라벨 잔재 정리
- 미실측 수치를 가설 표현 또는 run artifact 기반 수치로 정리
- `docs/02-design/evaluation.md`의 results 트리 설명 정리
- 완료: `docs/archive/` 자료를 루트 `archive/`로 이전
- `기획/` 삭제 여부 검토
