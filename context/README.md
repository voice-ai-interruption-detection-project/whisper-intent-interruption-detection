# context

프로젝트 운영과 내부 판단 맥락을 모아 두는 영역이다.

루트에는 실행 산출물(`src/`, `data/`, `results/`, `tests/`)과 공개 문서(`docs/`)를 두고, 개발 중 기준·결정·과거 자료·임시 메모는 이 폴더 아래로 접는다.

## 구조

| 폴더 | 역할 |
| --- | --- |
| [internal](internal/) | 현재 내부 기준. 제품 맥락, 용어, 정책 초안, 평가 기준, 설계 메모를 맞춘다 |
| [decisions](decisions/) | 결정·고민·AI 대화 맥락을 사안별로 남긴다 |
| [archive](archive/) | 현재 기준에서 물러난 자료를 history/evidence로 보관한다 |
| [temp](temp/) | PR/브랜치 설명, 짧은 공유 메모, 정리 전 임시 자료를 둔다 |

## 읽는 순서

작업 기준이 필요하면 [internal](internal/)을 먼저 본다.

왜 그렇게 정했는지가 필요하면 [decisions](decisions/)를 본다.

과거 자료나 폐기된 후보가 필요하면 [archive](archive/)를 보되, active 기준으로 직접 쓰지 않는다.

임시 메모는 [temp](temp/)에 둘 수 있지만, 오래 남으면 `context/internal/`이나 `context/decisions/`로 승격할지 검토한다.

## 의도 복원 / 문서 감사 예외

제품 의도 복원, 문서 왜곡 점검, 과거 합의 검증처럼 현재 기준 자체를 검토하는 작업에서는 [internal](internal/)을 곧바로 정답으로 두지 않는다.

이때는 회의 원문, `context/decisions/`, [archive](archive/)를 evidence로 함께 확인하고, 현재 `internal` 문서는 그 evidence에 비춰 검토 대상이 될 수 있다. 단, 코드 작업이나 실험 실행 기준을 정할 때는 다시 active 기준과 현재 코드 상태를 우선한다.
