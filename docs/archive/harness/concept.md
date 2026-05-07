# 하네스 컨셉

작성일: 2026-05-07 (Work Bench framing 정리)

> 상태: 참고 자료. Work Bench 하네스의 설계 원칙을 설명하며, 구현 중 필요한 부분만 규칙이나 코드 계약으로 승격한다.

## 이 문서가 답하는 것

- 이 프로젝트에 새로 합류한 팀원이나 페어가 **5분 안에 "왜 이런 구조인가"를 잡으려고** 본다.
- 하네스 구조를 논의할 때, "기준이 뭐였더라"를 다시 짚으려고 본다.
- 단계별 적용 방법은 [plan.md](plan.md)에 있다. 이 문서는 잘 바뀌지 않는 원칙만 담는다.

## 한 문단 요약

이 프로젝트는 Whisper 기반 intent/interruption detection을 다루는 작업대 — **Work Bench** — 다. 두 surface가 같은 runner와 정책 코드를 공유한다.

- **Playground** — 즉시 입력(text/audio/mic) → 정책 결과를 화면에서 바로 확인하는 평소 작업 표면. 영구 저장은 가벼운 session 로그 수준.
- **Test Bench** — scenario set에 정책을 batch로 돌려 결과를 누적·비교하는 표면. 마일스톤·회의·외부 공유에 들고 가는 숫자는 여기서만 나온다. `results/runs/{run_id}/`에 영구 보존.

두 surface가 같은 runner를 통과하기 때문에, "Playground에서 본 동작"과 "Test Bench가 측정한 동작"이 갈라지지 않는다.

## MVP가 답해야 할 질문

제품 질문은 "사용자가 말했는가?"에서 끝나지 않는다.

```text
AI가 말하는 중 고객 신호가 들어왔을 때
계속 말할지(continue), 짧게 반응할지(brief_ack), 잠깐 멈출지(pause),
새 흐름으로 전환할지(stop_and_switch), 확인 질문할지(confirm_question),
사람 상담원으로 이관할지(escalate)
상황별로 판단할 수 있는가?
```

이 질문에 답하기 위해 1주차에는 가장 가벼운 흐름부터 닫는다.

```text
Work Bench 1주차
  + Playground         (text input → policy → 화면 결과)
  + Test Bench batch   (scenarios.json → policy → run artifact)
  + Audio File Test와 Mic Trial은 후순위
```

## 보호해야 할 흐름

작업이 어느 단계에 있든, 결과는 이 사슬 위에서 설명될 수 있어야 한다.

```text
Scenario Bank          # 사람이 정한 고객 상황 + expected_action (Test Bench용 정답)
  -> Input Mode        # Text Replay / Audio File Test / Mic Trial
  -> Signal/Transcript # 어댑터를 거친 공통 입력 (PolicyInput)
  -> Event/Intent      # backchannel? interruption? intent shift?
  -> AI Action Policy  # 어떤 정책 버전이 판단했는지
  -> Action Label      # continue / brief_ack / pause / stop_and_switch / ...
  -> (분기) Playground 화면 표시  |  Test Bench Evaluation
  -> Decision Log      # 왜 그 action을 골랐는지
  -> Error Analysis    # 실패 사례 분류 (Test Bench)
```

이 사슬에서 **누가 만들었는지**(사람? 코드?)와 **어디에 저장되는지**(기준? 결과? 일시 화면?)가 섞이면 비교가 무너진다. Playground와 Test Bench가 갈라지는 지점은 "Action Label" 이후뿐이고, 그 앞은 모두 같은 runner·같은 정책 코드를 공유한다.

## 핵심 원칙

### 1. 기준 원본과 실행 결과를 섞지 않는다 (Test Bench scope)

사람이 정한 기준(`expected_action`, scenario, label 정의)과 코드가 만든 결과(`actual_action`, metric, decision log)는 다른 파일에 둔다. 평가 스크립트가 기준 원본에 결과를 덮어쓰면, "정답이 바뀐 건지 정책이 바뀐 건지" 더 이상 추적할 수 없다. 이 경계는 Test Bench 작업에 적용된다 — Playground는 자유 입력이므로 `expected_action`이 없다.

### 2. 입력 방식은 달라도 판단 구조는 하나로 둔다

Text Replay, Audio File Test, Mic Trial은 입력 방식이 다르지만, 최종적으로는 같은 형태(`PolicyInput`)로 정책에 들어간다. 이 통일은 Playground와 Test Bench 양쪽에 동시에 적용된다.

| 입력 모드 | 역할 | policy에 넘길 형태 |
| --- | --- | --- |
| Text Replay | scenario·label을 가장 빠르게 검증 | `user_utterance`, `event_type`, `current_intent` |
| Audio File Test | 음성 프로젝트라는 연결고리 | `audio_file`, `transcript`, `speech_event` |
| Mic Trial | 후속 live 입력 구조 확인 | `recording_state`, `transcript`, `latency_hint` |

핵심은 Audio File Test가 Text Replay와 다른 판단 로직을 타지 않게 하는 것이다. 그래야 정책 비교가 입력 방식에 휘둘리지 않는다.

### 3. 작은 완주 단위로 닫는다 (surface별로 다름)

기능 하나는 "코드가 컴파일된다"에서 끝나지 않는다. 두 surface는 완주 신호가 다르다.

```text
Playground 완주
-> 화면에 action/reason/signals 표시됨
-> 같은 입력으로 정책을 바꿔 다시 호출 가능
-> (선택) sessions/today.jsonl에 한 줄 기록

Test Bench 완주
-> scenarios.json을 batch로 통과
-> expected_action vs actual_action 자동 비교
-> results/runs/{run_id}/에 4개 artifact (run_meta, evaluation, decision_logs, error_analysis)
-> 실패 사례 분류
```

성능 수치는 Test Bench artifact에서 다시 확인할 수 있을 때만 확정 표현으로 쓴다. "정확도 80%"는 **어떤 run의, 어떤 dataset의, 어떤 정책 설정의 80%인지**가 함께 가야 의미를 가진다.

### 4. Test Bench artifact가 외부 인용의 유일한 출처다

README, report, presentation, slack 등에 들어가는 수치는 `results/runs/{run_id}/`에서만 가져온다. Playground 화면에서 본 수치는 작업용 신호일 뿐, 회의나 외부 공유에 들고 가지 않는다.

이 경계가 무너지면 "어제 화면에 떴던 정확도"가 슬랙에 올라가고, 일주일 뒤 출처를 못 찾는다. 그래서 Test Bench의 결과 폴더에는 **수치만 저장하지 않는다** — 어떤 입력으로 어떤 정책을 어떤 설정으로 실행했는지가 같이 들어간다. interruption detection은 정확도뿐 아니라 반응 시간이 결과의 일부라서, latency도 부가 정보가 아니라 핵심 결과다.

(필수 필드 목록은 [plan.md](plan.md)의 "Run artifact 최소 계약" 표에 있다.)

### 5. Playground와 Test Bench는 같은 runner를 호출한다

Playground UI, demo, CLI, eval, report가 각자 정책 판정을 따로 구현하면 결과가 빠르게 갈라진다. 같은 입력에 같은 답을 얻으려면 판정의 중심은 한 곳(공유 runner)에 두고, 표면(UI / batch loop)은 그 위에 얇게 얹어야 한다.

### 6. Agent와 skill은 역할로 본다

초기에도 agent나 skill을 쓸 수 있다. 다만 "사용한다"와 "저장소에 영구 정의로 둔다"는 다르다. 확정된 반복 절차는 처음부터 작은 checklist, skill, report-only agent로 둘 수 있다. 조심할 것은 아직 실체가 없는 미래 구조까지 예상해서 많이 만드는 것이다.

기본 원칙은 **report-only**다. agent는 조사·검증·분류 결과를 반환하고, 파일 수정은 메인 작업자가 판단한다.

## 한 줄 원칙

하네스는 프로젝트를 느리게 만드는 장식이 아니라, **Playground의 즉시 피드백과 Test Bench의 영구 비교를 같은 정책 코드로 묶어주는 최소 구조**다.
