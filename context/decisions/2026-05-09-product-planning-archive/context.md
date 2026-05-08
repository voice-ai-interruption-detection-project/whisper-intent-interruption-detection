# Context

## 선택지

1. `기획/`을 루트에 freeze 자료로 계속 둔다.
2. `기획/` 원문을 삭제하고 필요한 내용만 `context/internal/`에 남긴다.
3. `기획/` 원문은 `context/archive/product-planning/`으로 이동하고, 현재 기준은 `context/internal/`로 분리한다.

## 기각한 이유

루트에 계속 두면 초반 PRD와 현재 기준이 같은 무게로 보인다. 특히 action label, result tree, scenario 단위처럼 이미 바뀐 기준을 다시 참조할 위험이 있다.

원문을 삭제하면 초반 페어에서 왜 Text Replay, Audio File Test, AI Action Policy 관점이 만들어졌는지 추적하기 어렵다.

## 판단이 바뀐 지점

`context/internal/product-context.md`가 생기면서 제품 문제, 범위, 비목표, 남은 결정 후보를 현재 기준으로 다시 읽을 수 있게 됐다. 동시에 `context/internal/project-language-map.md`와 `context/internal/reference/`가 schema, event type, action label의 active 기준을 맡게 됐다.

따라서 초반 기획 문서는 active 기준이 아니라 archive evidence로 낮추는 편이 자연스럽다.

## 연결된 파일

- `context/archive/product-planning/README.md`
- `context/internal/product-context.md`
- `context/internal/project-language-map.md`
- `context/internal/reference/`
- `context/archive/README.md`
- `src/backend/PACKAGES.md`
