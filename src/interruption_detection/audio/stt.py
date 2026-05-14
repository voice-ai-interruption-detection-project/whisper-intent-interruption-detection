from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter
from typing import Protocol

from interruption_detection.audio.manifest import AudioManifestItem
from interruption_detection.models import StrictModel


class AudioProcessingError(ValueError):
    """오디오 adapter/STT 경계에서 발생한 오류."""


class AudioTranscript(StrictModel):
    """오디오 파일에서 얻은 transcript와 speech 여부."""

    text: str
    has_user_speech: bool
    source: str
    language: str | None = None
    confidence: float | None = None
    stage_latencies_ms: dict[str, float]
    metadata: dict[str, object]


class AudioTranscriber(Protocol):
    """오디오 파일을 transcript로 바꾸는 최소 인터페이스."""

    name: str

    def transcribe(
        self,
        audio_path: str | Path,
        item: AudioManifestItem,
    ) -> AudioTranscript:
        """오디오 파일 하나를 transcript로 변환한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """run artifact에 남길 STT 설정을 반환한다."""
        ...


class PrecomputedTranscriber:
    """manifest의 expected_transcript를 그대로 쓰는 안정적인 adapter."""

    name = "precomputed"

    def transcribe(
        self,
        audio_path: str | Path,
        item: AudioManifestItem,
    ) -> AudioTranscript:
        """STT 품질과 무관하게 오디오 runner 경계를 검증한다."""
        started = perf_counter()
        text = item.expected_transcript

        if text is None:
            raise AudioProcessingError(
                "expected_transcript is required for precomputed transcriber"
            )

        has_speech = (
            item.expected_has_user_speech
            if item.expected_has_user_speech is not None
            else bool(text.strip())
        )

        return AudioTranscript(
            text=text,
            has_user_speech=has_speech,
            source=self.name,
            language=item.language,
            stage_latencies_ms={"stt_ms": round((perf_counter() - started) * 1000, 3)},
            metadata={"audio_path": str(audio_path), "audio_kind": item.audio_kind},
        )

    def snapshot(self) -> dict[str, object]:
        return {"provider": "precomputed_manifest", "mode": "manifest_transcript"}


class WhisperTranscriber:
    """local openai-whisper 모델로 오디오 파일을 transcript로 변환한다."""

    name = "whisper"

    def __init__(self, model_name: str = "medium") -> None:
        self.model_name = model_name
        self._model = None

    def transcribe(
        self,
        audio_path: str | Path,
        item: AudioManifestItem,
    ) -> AudioTranscript:
        """Whisper 결과 text를 RunnerInput의 user_utterance로 사용한다."""
        path = Path(audio_path)
        if not path.exists():
            raise AudioProcessingError(f"audio file not found: {path}")

        started = perf_counter()
        model = self._load_model()
        result = model.transcribe(str(path), language=item.language, fp16=False)
        text = str(result.get("text") or "").strip()
        segments = result.get("segments") or []

        return AudioTranscript(
            text=text,
            has_user_speech=bool(text),
            source=self.name,
            language=str(result.get("language") or item.language),
            stage_latencies_ms={"stt_ms": round((perf_counter() - started) * 1000, 3)},
            metadata={
                "audio_path": str(path),
                "audio_kind": item.audio_kind,
                "model": self.model_name,
                "segment_count": len(segments) if isinstance(segments, list) else None,
            },
        )

    def snapshot(self) -> dict[str, object]:
        return {"provider": "openai_whisper_local", "model": self.model_name}

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            import whisper
        except ImportError as exc:
            raise AudioProcessingError(
                "openai-whisper is required for whisper transcriber"
            ) from exc

        self._model = whisper.load_model(self.model_name)

        return self._model


def build_transcriber(
    name: str,
    *,
    whisper_model: str | None = None,
) -> AudioTranscriber:
    """CLI/API 문자열 설정을 transcriber 구현체로 바꾼다."""
    if name == "precomputed":
        return PrecomputedTranscriber()

    if name == "whisper":
        model_name = whisper_model or os.getenv("WHISPER_MODEL", "medium")
        return WhisperTranscriber(model_name=model_name)

    raise AudioProcessingError(
        "unknown audio transcriber " f"'{name}'. available: precomputed, whisper"
    )
