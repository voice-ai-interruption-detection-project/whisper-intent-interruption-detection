from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from interruption_detection.audio.tts import (
    OpenAITTSClient,
    SayTTSClient,
    SilenceTTSClient,
    TTSClient,
    TTSRequest,
)
from interruption_detection.scenarios import load_scenarios


def main() -> int:
    """판단 케이스(Scenario) 기준 오디오 파일 입력용 TTS fixture와 manifest를 생성한다."""
    parser = argparse.ArgumentParser(
        description="판단 케이스(Scenario) 기준 오디오 파일 입력 fixture와 manifest를 생성한다."
    )
    parser.add_argument("--dataset", default="data/scenarios.json")
    parser.add_argument("--output-dir", default="data/audio/fixtures")
    parser.add_argument("--manifest", default="data/audio/manifest.json")
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--all-speech", action="store_true")
    parser.add_argument("--include-no-speech", action="store_true")
    parser.add_argument("--provider", choices=["openai", "say"], default="openai")
    parser.add_argument("--voice")
    parser.add_argument("--format", default="wav")
    parser.add_argument(
        "--instructions",
        default="Speak naturally as a Korean commerce support customer.",
    )
    args = parser.parse_args()

    scenarios = load_scenarios(args.dataset)
    selected_ids = set(args.scenario_id)

    selected = [
        scenario
        for scenario in scenarios
        if should_generate_scenario(
            scenario.scenario_id,
            scenario.has_user_speech,
            selected_ids=selected_ids,
            all_speech=args.all_speech,
            include_no_speech=args.include_no_speech,
        )
    ]

    if not selected:
        raise ValueError(
            "no scenarios selected; pass --scenario-id, --all-speech, or --include-no-speech"
        )

    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    voice = tts_voice(args.provider, args.voice)
    speech_tts = build_tts_client(args.provider, voice)
    silence_tts = SilenceTTSClient()
    manifest_items = []

    for scenario in selected:
        suffix = args.format.lower().lstrip(".") if scenario.has_user_speech else "wav"
        audio_path = output_dir / f"{scenario.scenario_id}.{suffix}"
        text = scenario.user_utterance

        if scenario.has_user_speech:
            speech_tts.synthesize(
                TTSRequest(
                    text=text,
                    output_path=str(audio_path),
                    voice=voice,
                    response_format=suffix,
                    instructions=args.instructions,
                )
            )
            audio_kind = "tts_user_utterance"
            transcript_source = "precomputed"
        else:
            silence_tts.synthesize(
                TTSRequest(
                    text="",
                    output_path=str(audio_path),
                    voice=voice,
                    response_format="wav",
                )
            )
            audio_kind = "silence"
            transcript_source = "precomputed"

        manifest_items.append(
            {
                "scenario_id": scenario.scenario_id,
                "audio_path": os.path.relpath(audio_path, manifest_path.parent),
                "audio_kind": audio_kind,
                "transcript_source": transcript_source,
                "expected_transcript": text,
                "expected_has_user_speech": scenario.has_user_speech,
                "language": "ko",
                "notes": "Generated from data/scenarios.json user_utterance",
            }
        )

    manifest = {"version": "audio_fixture_v1", "items": manifest_items}

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "count": len(manifest_items),
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


def should_generate_scenario(
    scenario_id: str,
    has_user_speech: bool,
    *,
    selected_ids: set[str],
    all_speech: bool,
    include_no_speech: bool,
) -> bool:
    """명령행 선택 기준으로 fixture 생성 대상 판단 케이스(Scenario)인지 판단한다."""
    if scenario_id in selected_ids:
        return True

    if has_user_speech and all_speech:
        return True

    return not has_user_speech and include_no_speech


def build_tts_client(provider: str, voice: str) -> TTSClient:
    """명령행 provider를 실제 TTS client로 바꾼다."""
    if provider == "openai":
        return OpenAITTSClient()

    if provider == "say":
        return SayTTSClient(voice=voice)

    raise ValueError(f"unknown TTS provider: {provider}")


def tts_voice(provider: str, requested: str | None) -> str:
    """provider별 기본 voice를 고른다."""
    if requested:
        return requested

    if provider == "say":
        return os.getenv("LOCAL_TTS_VOICE", "Yuna")

    return os.getenv("OPENAI_TTS_VOICE", "coral")


if __name__ == "__main__":
    raise SystemExit(main())
