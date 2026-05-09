from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from interruption_detection.audio.adapter import run_audio_item
from interruption_detection.audio.manifest import (
    AudioManifestItem,
    audio_path_for_item,
    load_audio_manifest,
)
from interruption_detection.audio.stt import AudioProcessingError, AudioTranscriber
from interruption_detection.evaluation.evaluator import (
    build_error_analysis,
    build_evaluation,
    classify_failure,
    get_criteria_snapshot,
)
from interruption_detection.models import RunDecisionLog, Scenario
from interruption_detection.policies import get_policy
from interruption_detection.scenarios import load_scenarios


def evaluate_audio_manifest(
    dataset_path: str | Path,
    audio_manifest_path: str | Path,
    policy_name: str,
    transcriber: AudioTranscriber,
    output_root: str | Path = "results/runs",
    *,
    source: str = "eval",
    command: str | None = None,
    changed: list[str] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """오디오 manifest를 지정 정책으로 실행하고 run artifact를 생성한다."""
    dataset = Path(dataset_path)
    manifest_path = Path(audio_manifest_path)
    scenarios = _scenario_by_id(load_scenarios(dataset))
    manifest = load_audio_manifest(manifest_path)
    policy = get_policy(policy_name)
    prepared_items = []
    for item in manifest.items:
        scenario = _scenario_for_audio_item(scenarios, item)
        audio_path = audio_path_for_item(item, manifest_path)
        if not audio_path.exists():
            raise AudioProcessingError(f"audio file not found: {audio_path}")
        prepared_items.append((scenario, item, audio_path))

    timestamp = datetime.now().astimezone()
    run_id = run_id or f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{policy_name}_audio"
    run_dir = Path(output_root) / run_id
    if run_dir.exists():
        raise FileExistsError(f"run artifact already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    logs: list[RunDecisionLog] = []
    for scenario, item, audio_path in prepared_items:
        decision = run_audio_item(
            scenario=scenario,
            item=item,
            audio_path=audio_path,
            policy_name=policy_name,
            transcriber=transcriber,
        )
        primary_failure = classify_failure(
            expected=scenario.expected_action,
            actual=decision.actual_action,
            event_type=scenario.event_type,
        )
        logs.append(
            RunDecisionLog(
                scenario_id=scenario.scenario_id,
                policy_name=policy_name,
                event_type=scenario.event_type,
                expected_action=scenario.expected_action,
                actual_action=decision.actual_action,
                reason=decision.reason,
                signals=decision.signals,
                stage_latencies_ms=decision.stage_latencies_ms,
                latency_ms=decision.latency_ms,
                primary_failure=primary_failure,
            )
        )

    evaluation = build_evaluation(logs)
    total_latency = round(sum(item.latency_ms for item in logs), 3)
    meta = {
        "run_id": run_id,
        "timestamp": timestamp.isoformat(),
        "source": source,
        "mode": "audio_file",
        "target": str(manifest_path),
        "changed": changed
        or [f"policy:{policy_name}", f"input_mode:audio_file:{transcriber.name}"],
        "dataset": str(dataset),
        "policy_version": policy_name,
        "policy_snapshot": policy.snapshot(),
        "criteria_snapshot": get_criteria_snapshot(),
        "latency_ms": total_latency,
        "command": command or "",
        "input_adapter_snapshot": {
            "mode": "audio_file",
            "audio_manifest": str(manifest_path),
            "audio_manifest_version": manifest.version,
            "transcriber": transcriber.snapshot(),
        },
    }

    _write_json(run_dir / "run_meta.json", meta)
    _write_json(run_dir / "evaluation.json", evaluation)
    _write_jsonl(run_dir / "decision_logs.jsonl", logs)
    (run_dir / "error_analysis.md").write_text(
        build_error_analysis(run_id, logs, evaluation),
        encoding="utf-8",
    )

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "run_meta": meta,
        "evaluation": evaluation,
    }


def _scenario_by_id(scenarios: Iterable[Scenario]) -> dict[str, Scenario]:
    return {scenario.scenario_id: scenario for scenario in scenarios}


def _scenario_for_audio_item(
    scenarios: dict[str, Scenario],
    item: AudioManifestItem,
) -> Scenario:
    try:
        return scenarios[item.scenario_id]
    except KeyError as exc:
        raise AudioProcessingError(
            f"audio manifest references unknown scenario: {item.scenario_id}"
        ) from exc


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, logs: list[RunDecisionLog]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in logs:
            handle.write(json.dumps(item.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")
