from __future__ import annotations

import json
import wave
from pathlib import Path

import pytest

from interruption_detection.audio.adapter import run_audio_item
from interruption_detection.audio.manifest import (
    AudioManifestError,
    audio_path_for_item,
    load_audio_manifest,
)
from interruption_detection.audio.stt import PrecomputedTranscriber
from interruption_detection.evaluation.audio_evaluator import evaluate_audio_manifest
from interruption_detection.models import ActionLabel
from interruption_detection.scenarios import get_scenario_by_id


def test_load_audio_manifest_resolves_relative_audio_path(tmp_path) -> None:
    audio_path = tmp_path / "fixtures" / "refund.wav"
    write_wav(audio_path)
    manifest_path = write_manifest(tmp_path, audio_path)

    manifest = load_audio_manifest(manifest_path)
    item = manifest.items[0]

    assert item.scenario_id == "commerce_shipping_to_refund_001"
    assert audio_path_for_item(item, manifest_path) == audio_path


def test_audio_manifest_rejects_result_fields(tmp_path) -> None:
    audio_path = tmp_path / "fixtures" / "refund.wav"
    write_wav(audio_path)
    manifest_path = write_manifest(
        tmp_path, audio_path, extra={"actual_action": "continue"}
    )

    with pytest.raises(AudioManifestError, match="actual_action"):
        load_audio_manifest(manifest_path)


def test_run_audio_item_uses_existing_policy_runner(tmp_path) -> None:
    audio_path = tmp_path / "fixtures" / "refund.wav"
    write_wav(audio_path)
    manifest_path = write_manifest(tmp_path, audio_path)
    item = load_audio_manifest(manifest_path).items[0]
    scenario = get_scenario_by_id("data/scenarios.json", item.scenario_id)

    decision = run_audio_item(
        scenario=scenario,
        item=item,
        audio_path=audio_path,
        policy_name="policy_v1",
        transcriber=PrecomputedTranscriber(),
    )

    assert decision.actual_action == ActionLabel.STOP_AND_SWITCH
    assert decision.signals["input_mode"] == "audio_file"
    assert decision.signals["audio"]["transcript_source"] == "precomputed"
    assert "stt_ms" in decision.stage_latencies_ms


def test_evaluate_audio_manifest_writes_run_artifact(tmp_path) -> None:
    audio_path = tmp_path / "fixtures" / "refund.wav"
    write_wav(audio_path)
    manifest_path = write_manifest(tmp_path, audio_path)

    result = evaluate_audio_manifest(
        "data/scenarios.json",
        manifest_path,
        "policy_v1",
        PrecomputedTranscriber(),
        output_root=tmp_path / "runs",
        run_id="audio_test_policy_v1",
    )

    assert result["evaluation"]["total"] == 1
    assert result["evaluation"]["correct"] == 1
    run_dir = tmp_path / "runs" / "audio_test_policy_v1"
    meta = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
    assert meta["mode"] == "audio_file"
    assert meta["input_adapter_snapshot"]["transcriber"]["provider"] == (
        "precomputed_manifest"
    )
    assert (run_dir / "decision_logs.jsonl").exists()


def write_manifest(
    root: Path,
    audio_path: Path,
    *,
    extra: dict[str, object] | None = None,
) -> Path:
    manifest_path = root / "manifest.json"
    item = {
        "scenario_id": "commerce_shipping_to_refund_001",
        "audio_path": str(audio_path.relative_to(root)),
        "audio_kind": "tts_user_utterance",
        "transcript_source": "precomputed",
        "expected_transcript": "아 그게 아니라 환불받고 싶어요.",
        "expected_has_user_speech": True,
        "language": "ko",
    }
    if extra:
        item.update(extra)
    manifest_path.write_text(
        json.dumps({"version": "audio_fixture_v1", "items": [item]}),
        encoding="utf-8",
    )
    return manifest_path


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
