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

Text Replay는 음성 테스트에 들어가기 전, 텍스트 입력만으로 판단 구조가 의도대로 동작하는지 먼저 확인하는 예비 테스트입니다.

## 2. Audio File Test

Audio File Test는 대표 오디오 파일을 입력으로 넣고, transcript와 audio signal을 `RunnerInput`으로 변환해 같은 policy runner에 태워보는 경로입니다.

| 항목 | 현재 구현 |
| --- | --- |
| manifest | `data/audio/manifest.json` |
| fixture | `data/audio/fixtures/*.wav` |
| transcriber | `precomputed`, `whisper` |
| adapter | `src/interruption_detection/audio/adapter.py` |
| batch 평가 | `src/interruption_detection/evaluation/audio_evaluator.py` |

현재 문서에서 비교하는 수치는 manifest에 미리 적어둔 transcript를 기준으로 합니다. 이 단계의 목적은 Whisper 성능을 평가하는 것이 아니라, 오디오 파일 입력이 Text Replay와 같은 판단 구조로 안정적으로 합류하는지 확인하는 것입니다.

Whisper 기반 transcript 생성도 구현되어 있지만, 현재 최종 비교 수치는 precomputed transcript 기준 policy 판단을 사용합니다.

## 3. Mic Trial

Mic Trial은 Playground에서 직접 녹음한 짧은 발화를 같은 runner에 태워보는 보조 테스트 경로입니다.

| 항목 | 현재 구현 |
| --- | --- |
| endpoint | `/scenarios/{scenario_id}/mic/predict` |
| transcript | 업로드한 녹음에 대해 precomputed 또는 whisper transcriber 사용 |
| expected action override | 개발자가 이번 mic 발화의 기대 action을 선택 가능 |
| 평가 범위 | Playground 보조 판정. 공식 run artifact에 섞지 않음 |

이 경로는 공식 평가 수치를 만들기보다는, 실제 마이크 입력이 transcript 변환과 adapter 단계를 거쳐 policy 판단까지 이어지는지 확인하는 용도입니다.

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

## 다음

[Demo 1 - False Stop](../04-demo/demo1.md)
