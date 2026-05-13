from __future__ import annotations

import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client(tmp_path):
    previous_dataset = getattr(app.state, "dataset_path", None)
    previous_output = getattr(app.state, "output_root", None)
    app.state.dataset_path = Path("data/scenarios.json")
    app.state.output_root = tmp_path
    try:
        yield TestClient(app)
    finally:
        if previous_dataset is None:
            del app.state.dataset_path
        else:
            app.state.dataset_path = previous_dataset
        if previous_output is None:
            del app.state.output_root
        else:
            app.state.output_root = previous_output


def test_audio_transcribe_with_precomputed_transcript(
    client: TestClient, tmp_path
) -> None:
    audio_path = tmp_path / "upload.wav"
    write_wav(audio_path)

    response = client.post(
        "/audio/transcribe",
        data={"transcriber": "precomputed", "transcript": "환불받고 싶어요."},
        files={"file": ("upload.wav", audio_path.read_bytes(), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"]["text"] == "환불받고 싶어요."
    assert body["transcript"]["source"] == "precomputed"
    assert body["audio_signal"]["exists"] is True


def test_audio_transcribe_allows_empty_precomputed_transcript(
    client: TestClient, tmp_path
) -> None:
    audio_path = tmp_path / "upload.wav"
    write_wav(audio_path)

    response = client.post(
        "/audio/transcribe",
        data={"transcriber": "precomputed"},
        files={"file": ("upload.wav", audio_path.read_bytes(), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"]["text"] == ""
    assert body["transcript"]["has_user_speech"] is False
    assert body["transcript"]["source"] == "precomputed"


def test_audio_predict_uses_runner(client: TestClient, tmp_path) -> None:
    audio_path = tmp_path / "upload.wav"
    write_wav(audio_path)

    response = client.post(
        "/audio/predict",
        data={
            "scenario_id": "commerce_shipping_to_refund_001",
            "policy": "policy_v1",
            "transcriber": "precomputed",
            "transcript": "아 그게 아니라 환불받고 싶어요.",
        },
        files={"file": ("upload.wav", audio_path.read_bytes(), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["expected_actions"] == ["stop_and_switch"]
    assert body["decision"]["actual_action"] == "stop_and_switch"
    assert body["decision"]["signals"]["input_mode"] == "audio_file"
    audio = body["decision"]["signals"]["audio"]
    assert audio["transcript_source"] == "precomputed"
    assert audio["transcriber"]["provider"] == "precomputed_manifest"


def write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    frames = []

    for index in range(sample_rate // 10):
        value = 1200 if index % 2 == 0 else -1200
        frames.append(value.to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"".join(frames))
