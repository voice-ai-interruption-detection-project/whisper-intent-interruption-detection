# Context

## 선택지

1. 기존 `baseline`, `policy_v1`을 그대로 두고 `policy_v2`에만 LLM을 붙인다.
2. 기존 `baseline`, `policy_v1`을 LLM 기반으로 전환한다.
3. `vad_baseline`, `event_mapping_policy` 같은 별도 이름으로 Day 2 placeholder를 보존하고 새 LLM policy를 추가한다.

## 기각한 이유

`policy_v2`에만 LLM을 붙이면 MVP의 핵심 판단 로직이 여전히 뒤로 밀린다. 사용자가 의도한 baseline은 VAD가 action을 결정하는 구조가 아니라 VAD/STT 이후 transcript를 LLM이 판단하는 구조다.

별도 이름으로 Day 2 placeholder를 보존하는 방식은 비교에는 유용하지만 현재 제품 표면의 기본 판단 흐름을 더 헷갈리게 만든다. Day 2 artifact는 기존 run으로 남아 있으므로, 코드의 기본 policy는 LLM 판단으로 전환한다.

## 판단이 바뀐 지점

처음에는 `policy_v2`를 LLM policy 후보로 보았지만, 사용자 설명을 통해 baseline부터 LLM이 개입해야 MVP의 판단 구조가 맞다는 점을 확인했다.

## 연결된 파일

- `src/interruption_detection/llm.py`
- `src/interruption_detection/policies/llm_action.py`
- `src/interruption_detection/policies/baseline.py`
- `src/interruption_detection/policies/policy_v1.py`
- `context/internal/mvp/current.md`
- `context/internal/mvp/current-iteration-plan.md`
