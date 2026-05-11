from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Any

from interruption_detection.models import StrictModel


class AudioSignalSummary(StrictModel):
    """정책 입력으로 넘기기 전 기록해 둘 오디오 파일 요약."""

    path: str
    exists: bool
    format: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    duration_ms: float | None = None
    rms: float | None = None
    peak: float | None = None
    has_audio_energy: bool | None = None


def analyze_audio_file(
    audio_path: str | Path,
    *,
    energy_threshold: float = 0.001,
) -> AudioSignalSummary:
    """오디오 파일의 기본 신호 정보를 계산한다."""
    path = Path(audio_path)

    if not path.exists():
        return AudioSignalSummary(path=str(path), exists=False)

    try:
        return _analyze_with_soundfile(path, energy_threshold=energy_threshold)
    except Exception:
        if path.suffix.lower() == ".wav":
            return _analyze_wav(path, energy_threshold=energy_threshold)

        return AudioSignalSummary(
            path=str(path),
            exists=True,
            format=path.suffix.lower().lstrip(".") or None,
        )


def _analyze_with_soundfile(
    path: Path,
    *,
    energy_threshold: float,
) -> AudioSignalSummary:
    import numpy as np
    import soundfile as sf

    samples, sample_rate = sf.read(path, always_2d=True)

    if samples.size == 0:
        rms = 0.0
        peak = 0.0
    else:
        rms = float(np.sqrt(np.mean(np.square(samples))))
        peak = float(np.max(np.abs(samples)))

    duration_ms = round((len(samples) / sample_rate) * 1000, 3) if sample_rate else 0

    return AudioSignalSummary(
        path=str(path),
        exists=True,
        format=path.suffix.lower().lstrip(".") or None,
        sample_rate=int(sample_rate),
        channels=int(samples.shape[1]) if samples.ndim == 2 else 1,
        duration_ms=duration_ms,
        rms=round(rms, 6),
        peak=round(peak, 6),
        has_audio_energy=rms >= energy_threshold,
    )


def _analyze_wav(
    path: Path,
    *,
    energy_threshold: float,
) -> AudioSignalSummary:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        sample_width = handle.getsampwidth()
        frames = handle.getnframes()
        raw = handle.readframes(frames)

    sample_count = max(frames * channels, 1)
    values = _pcm_values(raw, sample_width)

    if not values:
        rms = 0.0
        peak = 0.0
    else:
        normalizer = float(2 ** (8 * sample_width - 1))
        normalized = [value / normalizer for value in values]
        rms = math.sqrt(sum(value * value for value in normalized) / len(normalized))
        peak = max(abs(value) for value in normalized)

    duration_ms = round((frames / sample_rate) * 1000, 3) if sample_rate else 0

    return AudioSignalSummary(
        path=str(path),
        exists=True,
        format="wav",
        sample_rate=sample_rate,
        channels=channels,
        duration_ms=duration_ms,
        rms=round(rms, 6),
        peak=round(peak, 6),
        has_audio_energy=rms >= energy_threshold and sample_count > 0,
    )


def _pcm_values(raw: bytes, sample_width: int) -> list[int]:
    if sample_width not in {1, 2, 4}:
        return []

    values: list[int] = []

    for index in range(0, len(raw), sample_width):
        chunk = raw[index : index + sample_width]

        if len(chunk) != sample_width:
            continue

        if sample_width == 1:
            values.append(int.from_bytes(chunk, "little", signed=False) - 128)
        else:
            values.append(int.from_bytes(chunk, "little", signed=True))

    return values


def audio_signal_dump(summary: AudioSignalSummary) -> dict[str, Any]:
    """PolicyDecision.signals에 넣을 JSON 직렬화 가능한 신호 요약."""
    return summary.model_dump(mode="json")
