# context/archive

현재 기준에서 물러난 자료를 보관하는 루트 archive 영역이다.

archive는 history/evidence로만 본다. active 가드, `context/internal/`, `context/decisions/`, 코드, 데이터와 충돌하면 active 쪽을 우선한다.

제품 방향과 현재 범위는 [context/internal/product-context.md](../internal/product-context.md)를 우선한다. archive 안의 문서가 더 자세해 보여도 현재 기준으로 직접 쓰지 않는다.

## 운영 기준

- 현재 작업 기준이나 구현 근거로 직접 쓰지 않는다.
- 다시 사용할 내용은 그대로 참조하지 말고 `context/internal/`, `context/decisions/`, `.claude/rules/`, 코드/테스트 같은 active 위치로 승격한 뒤 사용한다.

## 보관 자료

- `harness/`: Work Bench 하네스 설계 배경과 적용 후보를 보관한 자료.
- `product-planning/`: 초반 MVP 방향, 계획서, PRD, 용어 결정 원문을 보관한 자료. 현재 제품 기준은 `context/internal/product-context.md`를 우선한다.

이 폴더는 mkdocs 공개 문서 영역이 아니다.
