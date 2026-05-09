from __future__ import annotations

from pathlib import Path
from time import perf_counter

from interruption_detection.audio.manifest import AudioManifestItem
from interruption_detection.audio.signals import (
    analyze_audio_file,
    audio_signal_dump,
)
from interruption_detection.audio.stt import AudioTranscriber
from interruption_detection.models import PolicyDecision, RunnerInput, Scenario
from interruption_detection.runner import run_input


def run_audio_item(
    *,
    scenario: Scenario,
    item: AudioManifestItem,
    audio_path: str | Path,
    policy_name: str,
    transcriber: AudioTranscriber,
) -> PolicyDecision:
    """오디오 fixture 하나를 RunnerInput으로 변환한 뒤 기존 policy runner를 호출한다."""
    signal_started = perf_counter()
    signal_summary = analyze_audio_file(audio_path)
    signal_ms = round((perf_counter() - signal_started) * 1000, 3)
    transcript = transcriber.transcribe(audio_path, item)
    runner_input = RunnerInput(
        scenario_id=scenario.scenario_id,
        domain=scenario.domain,
        level=scenario.level,
        ai_current_intent=scenario.ai_current_intent,
        ai_utterance=scenario.ai_utterance,
        user_utterance=transcript.text,
        event_type=scenario.event_type,
        expected_user_intent=scenario.expected_user_intent,
        user_tone_hint=scenario.user_tone_hint,
        has_user_speech=transcript.has_user_speech,
        notes=scenario.notes,
    )
    decision = run_input(runner_input, policy_name)
    stage_latencies = {
        **transcript.stage_latencies_ms,
        "audio_signal_ms": signal_ms,
        **decision.stage_latencies_ms,
    }
    signals = {
        **decision.signals,
        "input_mode": "audio_file",
        "audio": {
            "scenario_id": item.scenario_id,
            "audio_path": str(audio_path),
            "audio_kind": item.audio_kind,
            "transcript_source": transcript.source,
            "transcript": transcript.text,
            "has_user_speech": transcript.has_user_speech,
            "language": transcript.language,
            "signal": audio_signal_dump(signal_summary),
            "transcriber": transcriber.snapshot(),
            "metadata": transcript.metadata,
        },
    }
    return decision.model_copy(
        update={
            "signals": signals,
            "stage_latencies_ms": stage_latencies,
            "latency_ms": round(sum(stage_latencies.values()), 3),
        }
    )
