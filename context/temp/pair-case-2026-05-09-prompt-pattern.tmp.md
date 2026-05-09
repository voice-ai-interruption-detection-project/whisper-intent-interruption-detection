# AI 작업 세션 prompt 패턴 — 2026-05-09 페어 케이스

## 배경

2026-05-09 페어에서 MVP 텍스트 입력 단계 위에 LLM 기반 action policy를 얹는 작업을 진행했다. 이 과정에서 같은 의도를 가진 두 작업 세션이 서로 다른 결과로 끝났다 — 5월 9일 오전 세션(이하 막힌 세션)은 LLM 적용 방향으로 이어지지 않고 rule/embedding 안에서 정리되며 작업이 멈췄고, 오후 재개 세션(이하 풀린 세션)은 의도한 LLM action policy 구현으로 이어져 PR #5(`feat/llm-action-policy`)로 main에 병합됐다.

코드는 풀린 세션 산출물로 정상 완성됐다. 다만 같은 의도가 prompt 형태에 따라 결과가 갈린 메커니즘은 다음 작업의 진입 비용에 직접 영향을 주므로, 케이스 노트로 정리해 페어가 같이 활용한다.

## 두 세션 비교

| 항목 | 막힌 세션 | 풀린 세션 |
| --- | --- | --- |
| 첫 명령 | "internal/mvp 폴더 진행상황과 코드 파악해줘 ... 면밀히 파악해주고 ... ai 기능이 적용되어 실제 판단하게끔" | "MVP 문서 보고 추가 작업할 부분 지정 + LLM 적용 구체 요구" |
| 진입 모드 | 분석 → 종합 → 제안 | 구현 (분석 단계 짧음) |
| 의도 표현 | 추상 ("AI 기능") | 구체 ("LLM 적용") |
| 방법 표현 | 추상 | 구체 |
| AI가 active 문서를 읽는 방식 | "무엇이 충분한가" 결정 입력 | "어떻게 구현할까" 배경 입력 |
| 결과 | `TextSignalAnalyzer`(rule/embedding) 방향 제안, baseline은 VAD-only 유지 | LLM client + LLM action policy 구현, baseline/policy_v1까지 LLM 경로 합의 |

막힌 세션에서 AI는 다음 표현들을 작업자 의도보다 우선시했다.

- [context/internal/product-context.md](context/internal/product-context.md) "rule과 pretrained embedding 기반 검증으로 충분"
- [context/internal/mvp/current.md](context/internal/mvp/current.md) "VAD-only baseline"
- [context/temp/day2-mvp-ui-server-plan.tmp.md](context/temp/day2-mvp-ui-server-plan.tmp.md) "rule mapping은 policy 내부 한 곳에만"

이 표현들은 보수적 해석을 위한 작업 가드와 맞닿아 있어, 의도가 명시되지 않은 추상 명령("AI 기능") 안에서는 명시 문서 표현이 의도를 좁히는 근거로 작동했다. 풀린 세션에서는 명령에 "LLM 적용"이 박혀 있어 AI가 같은 active 문서를 의도 결정 근거가 아닌 구현 배경으로만 읽었다. 같은 표현이 같은 가드 아래에서도 다르게 작동한 셈이다.

## 진단

문제는 의도가 명확함에도 그것을 prompt 형태로 보존하지 못한 것이다. 더 정확히는 한 단어 아래에서 두 층이 같이 추상화된 게 함정이었다.

| 층 | 막힌 세션 | 풀린 세션 | 권장 |
| --- | --- | --- | --- |
| 의도 (무엇을 결정) | 추상 | 구체 | **구체** |
| 방법 (어떻게 구현) | 추상 | 구체 | 추상 + push back 권한 |

"AI 기능"은 함의가 넓다 — rule/embedding/LLM/fine-tuning을 모두 포함한다. 한 단어 아래에 의도와 방법이 함께 풀리면 AI는 두 층 모두를 active 문서에서 좁힌다.

"LLM 적용"은 함의가 좁아 두 층이 모두 구체로 박힌다. 안전한 정렬이지만, 더 적절한 방법(예: 작업 범위에 LLM이 과하고 임베딩만으로 충분할 때)이 있을 때 push back이 잘 일어나지 않는다.

권장 형태는 **의도는 구체로 박고 방법만 push back 권한과 함께 열어두는 것**이다. 추상도가 두 층에 동시 적용되지 않으면 의도 정렬과 방법 자유도 둘 다 살릴 수 있다.

부수 관찰:

- 분석 권한 위임 자체는 협업 가치가 있다 — 작업자가 놓치는 부분을 AI가 보완해주는 패턴이다. 다만 분석은 중립 작업이 아니라 angle 잡기다. 분석 결과를 그대로 종합으로 닫게 두면, active 문서의 명시 표현이 의도보다 강하게 잡힌다.
- 한 세션 안에서 잡힌 angle은 자기 정정 비용이 높다. 막힌 세션에서 정정 시도가 한 번 있었으나 다음 turn에 다시 같은 angle로 돌아갔다. 새 세션 진입이 더 빠른 우회로가 되는 패턴은 이 비용 비대칭의 결과다.
- `baseline`/`policy_v1` 같은 ML 컨벤션 단어는 "단순 비교 기준선/단순 버전"이라는 함의를 가져, LLM-퍼스트 의도와 자연스럽게 충돌한다.

## 다음 요청 패턴

비슷한 작업을 시작할 때 활용할 수 있는 prompt 형태:

```text
[작업 영역과 분석 위임]
internal/mvp 폴더 진행상황과 코드를 면밀히 본다.
다만 결정 권한은 작업자가 갖는다. 종합으로 닫지 말고
옵션과 충돌 지점 보고서로 답한다.

[의도를 결정 박스로 박기]
의도(결정 사항이며 분석 대상이 아니다):
- 현재 policy_v1은 사람이 붙인 event_type을 입력으로 받아 action을 매핑한다
- 이걸 텍스트(user_utterance, ai_current_intent, ai_utterance)에서
  AI가 신호를 추론하고, 그 신호로 action을 정하는 구조로 바꾼다
- 핵심: 판단 주체가 사람 라벨링이 아니라 AI다
- 입력 모드는 텍스트 (오디오 아님)

[방법은 push back 권한과 함께 열기]
방법은 LLM API / embedding / 조합 중 의도를 만족하는 것.
이 작업 범위에 LLM이 과하면 근거와 함께 다른 옵션을 제안한다.
결정은 작업자가 한다.

[active 문서 충돌 보고 권한]
이 의도가 active 문서(context/internal/product-context.md,
context/internal/mvp/current.md 등)의 표현과 충돌하면
충돌 자체를 보고한다. 문서를 의도보다 먼저 따르지 않는다.

[답 형식]
1. 현재 코드 흐름 요약 (file:line 인용)
2. 의도와 active 문서 사이 충돌 지점 (있으면)
3. 방법 옵션과 각 트레이드오프
4. 추천 다음 작업 단위 (commit 단위로 쪼개서)
```

각 요소의 역할:

| 요소 | 역할 |
| --- | --- |
| 분석 위임 + "면밀히 본다" | 작업자가 놓치는 부분을 AI가 보완하는 협업 가치 보존 |
| "결정 권한은 작업자가 갖는다" | AI가 종합으로 angle 잡는 것을 차단 |
| "의도(결정 사항이며 분석 대상이 아니다)" | 분석 입력에 의도가 먼저 박힘 — active 문서가 의도를 덮을 수 없음 |
| "충돌 자체를 보고한다" | 보수적 표현을 만나도 자기 fit이 아니라 보고로 올라옴 |
| 방법 X/Y/Z + "다른 옵션 근거 제안" | narrow instruction 갇힘 우려 해결 — push back 권한 명시 |
| "답 형식" 항목별 분리 | AI가 종합 서술로 닫지 못하게 형식적 강제 |

## 후속 작업 후보

같은 함정이 다음 작업에서 반복되지 않게 하기 위한 repo 측 후보 — 이 노트의 결론이 아니라 페어가 같이 검토할 옵션이다.

- [context/internal/product-context.md](context/internal/product-context.md)에서 "rule과 pretrained embedding 기반 검증으로 충분" 표현을 ablation 조항으로 격하하거나, LLM 전제를 첫 부분에 박는다.
- `baseline` / `policy_v1` 같은 단어가 LLM-퍼스트 의도와 충돌하므로, 이름에 의미를 박거나(`vad_only_baseline` 등) decision 기록으로 의미를 굳힌다.
- [context/decisions/](context/decisions/)에 이번 케이스의 진단(분석 위임 + 추상도 coupling으로 angle drift)을 사안별 폴더로 남긴다 — 기록 후보인지 `decision-record-advisor` agent로 먼저 본다.

코드 측 LLM action policy는 PR #5(`feat/llm-action-policy`)로 main에 병합된 상태이며, 이 노트는 prompt/문서 측 정렬 작업의 입력으로 둔다.

---

이 노트는 페어에서 발견된 협업 패턴을 다음 작업의 진입 비용을 줄이기 위해 정리한 것이며, active rule이나 작업 가드는 아니다. 같은 함정이 여러 번 반복되거나 큰 비용을 내면 그때 [.claude/rules/](.claude/rules/) 또는 [context/internal/](context/internal/)로 승격할지 본다.
