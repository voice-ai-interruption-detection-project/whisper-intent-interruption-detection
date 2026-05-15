# Input Modes: 입력 경로

## 개요

입력 경로는 제품 개념이 아니라 같은 판단 구조를 어떤 입력으로 실행해 볼지 나타내는 개발/테스트 경로입니다.

```text
Text Replay
Audio File Test
Mic Trial
-> 모두 RunnerInput으로 정규화
-> 같은 policy runner 실행
```

## 1. Text Replay

Text Replay는 판단 케이스나 직접 입력한 텍스트를 사용해 policy 판단을 빠르게 확인하는 경로입니다.

| 항목 | 현재 구현 |
| --- | --- |
| 입력 | `ai_current_intent`, `ai_utterance`, `user_utterance`, `has_user_speech`, `user_tone_hint` |
| 실행 | `/predict` 또는 `/scenarios/{scenario_id}/predict` |
| 평가 | Test Bench에서 `data/scenarios.json` 전체를 batch 실행 |
| 결과 | `results/runs/{run_id}/` artifact |

Text Replay는 음성 프로젝트를 포기하는 경로가 아닙니다. 오디오/STT 앞단을 고정하고 뒤쪽 판단 구조를 먼저 검증하는 방법입니다.

## 2. Audio File Test

Audio File Test는 대표 음성 파일을 transcript/signal adapter로 변환한 뒤 같은 runner에 태우는 경로입니다.

| 항목 | 현재 구현 |
| --- | --- |
| manifest | `data/audio/manifest.json` |
| fixture | `data/audio/fixtures/*.wav` |
| transcriber | `precomputed`, `whisper` |
| adapter | `src/interruption_detection/audio/adapter.py` |
| batch 평가 | `src/interruption_detection/evaluation/audio_evaluator.py` |

`precomputed` transcriber는 manifest의 `expected_transcript`를 사용합니다. 이는 STT 품질 평가가 아니라 오디오 입력이 같은 runner 경계로 합류하는지 확인하기 위한 안정적인 adapter입니다.

Whisper transcriber도 구현되어 있지만, 현재 최종 수치의 중심은 precomputed transcript 기준 policy 판단입니다.

## 3. Mic Trial

Mic Trial은 공식 Test Bench 수치가 아니라 Playground에서 live 입력과 기대 action override를 확인하는 보조 경로입니다.

| 항목 | 현재 구현 |
| --- | --- |
| endpoint | `/scenarios/{scenario_id}/mic/predict` |
| transcript | 업로드한 녹음에 대해 precomputed 또는 whisper transcriber 사용 |
| expected action override | 개발자가 이번 mic 발화의 기대 action을 선택 가능 |
| 평가 범위 | Playground 보조 판정. 공식 run artifact에 섞지 않음 |

Mic Trial의 expected action override는 policy prompt에 들어가지 않습니다. policy 실행 후 `action_match`를 계산할 때만 사용합니다.

## 공통 흐름

```text
입력 경로별 데이터
-> RunnerInput
-> PolicyInput
   - ai_current_intent
   - ai_utterance
   - user_utterance
   - has_user_speech
   - user_tone_hint
-> policy decision
-> expected_actions와 비교
```

`event_type`, `expected_user_intent`, `expected_actions`는 기준값입니다. policy prompt에는 들어가지 않고 evaluator와 error analysis에서 사용합니다.

## 다음

[Demo 1 - False Stop](../04-demo/demo1.md)
