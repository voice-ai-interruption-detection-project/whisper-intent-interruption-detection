# archive

현재 기준에서 물러난 자료를 보관하는 루트 archive 영역이다.

archive는 history/evidence로만 본다. active 가드, `internal/`, `decisions/`, 코드, 데이터와 충돌하면 active 쪽을 우선한다.

## 운영 기준

- 현재 작업 기준이나 구현 근거로 직접 쓰지 않는다.
- 다시 사용할 내용은 그대로 참조하지 말고 `internal/`, `decisions/`, `.claude/rules/`, 코드/테스트 같은 active 위치로 승격한 뒤 사용한다.
- `docs/archive/`에 남아 있는 기존 자료는 follow-up에서 이 영역으로 이전할 수 있다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
