from __future__ import annotations

import unicodedata
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
            "reference_transcript": item.expected_transcript,
            "transcript_matches_reference": _transcript_matches_reference(
                transcript.text,
                item.expected_transcript,
            ),
            "transcript_edit_distance": _transcript_edit_distance(
                transcript.text,
                item.expected_transcript,
            ),
            "transcript_similarity": _transcript_similarity(
                transcript.text,
                item.expected_transcript,
            ),
            "has_user_speech": transcript.has_user_speech,
            "reference_has_user_speech": item.expected_has_user_speech,
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


def _transcript_matches_reference(
    actual: str,
    reference: str | None,
) -> bool | None:
    """STT transcript가 manifest 기준 transcript와 같은지 비교한다."""
    if reference is None:
        return None
    return _normalize_transcript(actual) == _normalize_transcript(reference)


def _transcript_edit_distance(
    actual: str,
    reference: str | None,
) -> int | None:
    """Whisper run 분석용으로 간단한 문자 편집 거리를 계산한다."""
    if reference is None:
        return None
    return _levenshtein_distance(
        _normalize_transcript(actual),
        _normalize_transcript(reference),
    )


def _transcript_similarity(
    actual: str,
    reference: str | None,
) -> float | None:
    """편집 거리 기반 0~1 transcript 유사도를 반환한다."""
    if reference is None:
        return None
    normalized_actual = _normalize_transcript(actual)
    normalized_reference = _normalize_transcript(reference)
    max_length = max(len(normalized_actual), len(normalized_reference))
    if max_length == 0:
        return 1.0
    distance = _levenshtein_distance(normalized_actual, normalized_reference)
    return round(1 - (distance / max_length), 4)


def _normalize_transcript(value: str) -> str:
    """공백 차이와 Unicode 표현 차이를 줄여 transcript를 비교한다."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(normalized.split())


def _levenshtein_distance(left: str, right: str) -> int:
    """짧은 transcript 비교를 위한 표준 Levenshtein distance."""
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)

    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            deletion = previous[right_index] + 1
            insertion = current[right_index - 1] + 1
            substitution = previous[right_index - 1] + (left_char != right_char)
            current.append(min(deletion, insertion, substitution))
        previous = current
    return previous[-1]
