from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from interruption_detection.models import StrictModel


class AudioManifestError(ValueError):
    """오디오 파일 입력 manifest가 현재 계약을 어길 때 발생하는 오류."""


class AudioManifestItem(StrictModel):
    """판단 케이스(Scenario) 하나에 대응하는 오디오 fixture 입력."""

    scenario_id: str
    audio_path: str
    audio_kind: str = "tts_user_utterance"
    transcript_source: Literal["precomputed", "whisper"] = "precomputed"
    expected_transcript: str | None = None
    expected_has_user_speech: bool | None = None
    language: str = "ko"
    notes: str | None = None

    @model_validator(mode="after")
    def validate_transcript_source(self) -> "AudioManifestItem":
        """precomputed transcript mode에서는 transcript 값을 명시하게 한다."""
        if self.transcript_source == "precomputed" and self.expected_transcript is None:
            raise ValueError(
                "expected_transcript is required when transcript_source is precomputed"
            )

        return self


class AudioManifest(StrictModel):
    """오디오 파일 입력 fixture manifest."""

    version: str = "audio_fixture_v1"
    items: list[AudioManifestItem] = Field(default_factory=list)


def load_audio_manifest(path: str | Path) -> AudioManifest:
    """오디오 manifest를 읽고 중복/결과 필드 혼입을 검증한다."""
    manifest_path = Path(path)
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AudioManifestError(f"invalid JSON in {manifest_path}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
        raise AudioManifestError("audio manifest must be an object with items list")

    seen: set[str] = set()
    for index, item in enumerate(raw["items"]):
        if not isinstance(item, dict):
            raise AudioManifestError(f"audio item at index {index} must be an object")

        _reject_result_fields(item, index)
        scenario_id = item.get("scenario_id")

        if not isinstance(scenario_id, str) or not scenario_id:
            raise AudioManifestError(
                f"audio item at index {index} has invalid scenario_id"
            )

        if scenario_id in seen:
            raise AudioManifestError(f"duplicate audio scenario_id: {scenario_id}")

        seen.add(scenario_id)

    try:
        return AudioManifest.model_validate(raw)
    except ValidationError as exc:
        raise AudioManifestError(
            f"invalid audio manifest {manifest_path}: {exc}"
        ) from exc


def audio_path_for_item(item: AudioManifestItem, manifest_path: str | Path) -> Path:
    """manifest 기준 상대 경로를 실제 파일 경로로 해석한다."""
    raw_path = Path(item.audio_path)
    if raw_path.is_absolute():
        return raw_path

    return Path(manifest_path).parent / raw_path


def _reject_result_fields(item: dict[str, object], index: int) -> None:
    """오디오 기준 입력에 실행 결과 필드가 섞였는지 확인한다."""
    forbidden = {
        "actual_action",
        "decision",
        "evaluation",
        "latency_ms",
        "primary_failure",
        "policy_name",
    }
    leaked = sorted(forbidden.intersection(item))

    if leaked:
        fields = ", ".join(leaked)
        raise AudioManifestError(
            f"audio item at index {index} contains result fields: {fields}"
        )
