# reference

`context/internal/reference/`는 schema key와 enum value를 빠르게 확인하기 위한 하위 참조 문서 묶음이다.

상위 흐름은 [Project Language Map](../project-language-map.md)에서 보고, 특정 key나 값이 헷갈릴 때 이 폴더의 문서를 본다.

## 문서

- [Schema Keys](schema-keys.md): 판단 케이스(`scenario`) 원본 key와 run result key의 역할 구분
- [Event Types](event-types.md): `event_type` 7종의 개념, 대표 신호, 경계 기준
- [Action Labels](action-labels.md): action label 6종의 의미와 expected/actual 역할 구분

## 운영 기준

- 이 폴더는 공개 문서가 아니라 내부 기준 reference다.
- 새 enum value나 schema key를 추가하면 상위 지도와 평가 계약에 영향이 있는지 같이 확인한다.
- `docs/`의 오래된 표현을 그대로 옮기지 않고, 현재 기준 어휘로 정규화한다.
