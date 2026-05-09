# Audio Fixtures

Audio File Test는 `data/scenarios.json`을 직접 수정하지 않고 별도 manifest로 오디오 파일을 연결한다.

```bash
export OPENAI_API_KEY=...
poetry run python scripts/generate_audio_fixtures.py \
  --scenario-id commerce_shipping_to_refund_001 \
  --scenario-id commerce_shipping_follow_001
```

OpenAI key 없이 macOS 로컬 TTS로 만들 수도 있다.

```bash
poetry run python scripts/generate_audio_fixtures.py \
  --provider say \
  --all-speech
```

생성 결과:

- `data/audio/fixtures/{scenario_id}.wav`
- `data/audio/manifest.json`

오디오 manifest는 기준 입력이다. `actual_action`, metric, decision log는 `results/runs/{run_id}/`에만 남긴다.
