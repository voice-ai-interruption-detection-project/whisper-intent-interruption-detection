from __future__ import annotations

import json
import os
import subprocess
import wave
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from interruption_detection.models import StrictModel

load_dotenv()


class TTSError(ValueError):
    """TTS fixture 생성 경계에서 발생한 오류."""


class TTSRequest(StrictModel):
    """TTS provider에 넘길 음성 생성 요청."""

    text: str
    output_path: str
    voice: str
    instructions: str | None = None
    response_format: str = "wav"


class TTSClient(Protocol):
    """텍스트를 오디오 파일로 저장하는 최소 TTS 인터페이스."""

    def synthesize(self, request: TTSRequest) -> Path:
        """요청 텍스트를 output_path에 오디오 파일로 저장한다."""
        ...

    def snapshot(self) -> dict[str, object]:
        """fixture manifest나 로그에 남길 provider 설정을 반환한다."""
        ...


class OpenAITTSClient:
    """OpenAI Speech API를 직접 호출하는 얇은 TTS client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        self.base_url = (
            base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com"
        ).rstrip("/")
        self.timeout_s = timeout_s or float(os.getenv("OPENAI_TTS_TIMEOUT_S", "60"))

    def synthesize(self, request: TTSRequest) -> Path:
        if not self.api_key:
            raise TTSError(
                "OPENAI_API_KEY is required for OpenAI TTS fixture generation"
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "voice": request.voice,
            "input": request.text,
            "response_format": request.response_format,
        }

        if request.instructions:
            payload["instructions"] = request.instructions

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = Request(
            f"{self.base_url}/v1/audio/speech",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        output = Path(request.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        try:
            with urlopen(http_request, timeout=self.timeout_s) as response:
                output.write_bytes(response.read())
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise TTSError(f"OpenAI TTS API error: {exc.code} {detail}") from exc
        except URLError as exc:
            raise TTSError(f"OpenAI TTS API request failed: {exc.reason}") from exc

        return output

    def snapshot(self) -> dict[str, object]:
        return {
            "provider": "openai_audio_speech",
            "model": self.model,
            "base_url": self.base_url,
            "timeout_s": self.timeout_s,
        }


class SilenceTTSClient:
    """no_speech fixture를 WAV silence 파일로 만드는 local generator."""

    def __init__(self, *, duration_ms: int = 1000, sample_rate: int = 16000) -> None:
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate

    def synthesize(self, request: TTSRequest) -> Path:
        output = Path(request.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        frame_count = int(self.sample_rate * (self.duration_ms / 1000))

        with wave.open(str(output), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(self.sample_rate)
            handle.writeframes(b"\x00\x00" * frame_count)

        return output

    def snapshot(self) -> dict[str, object]:
        return {
            "provider": "local_silence_wav",
            "duration_ms": self.duration_ms,
            "sample_rate": self.sample_rate,
        }


class SayTTSClient:
    """macOS `say` command로 로컬 TTS WAV fixture를 생성한다."""

    def __init__(
        self,
        *,
        voice: str = "Yuna",
        sample_rate: int = 16000,
    ) -> None:
        self.voice = voice
        self.sample_rate = sample_rate

    def synthesize(self, request: TTSRequest) -> Path:
        output = Path(request.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        command = [
            "say",
            "-v",
            request.voice or self.voice,
            "-o",
            str(output),
            "--file-format=WAVE",
            f"--data-format=LEI16@{self.sample_rate}",
            request.text,
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise TTSError("macOS say command is required for local TTS") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or exc.stdout.strip()
            raise TTSError(f"macOS say command failed: {detail}") from exc

        return output

    def snapshot(self) -> dict[str, object]:
        return {
            "provider": "macos_say",
            "voice": self.voice,
            "sample_rate": self.sample_rate,
        }
