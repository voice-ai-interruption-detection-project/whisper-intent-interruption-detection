from __future__ import annotations

import json

import pytest

from interruption_detection.evaluation.artifacts import read_run_artifacts
from interruption_detection.evaluation.evaluator import evaluate_dataset


def test_evaluate_dataset_writes_run_artifacts(tmp_path) -> None:
    result = evaluate_dataset(
        "data/scenarios.json",
        "policy_v1",
        output_root=tmp_path,
        run_id="20260509_120000_policy_v1",
    )
    run_dir = tmp_path / result["run_id"]

    assert (run_dir / "run_meta.json").exists()
    assert (run_dir / "evaluation.json").exists()
    assert (run_dir / "decision_logs.jsonl").exists()
    assert (run_dir / "error_analysis.md").exists()

    evaluation = json.loads((run_dir / "evaluation.json").read_text(encoding="utf-8"))
    assert set(
        ["action_accuracy", "failures", "confusion_matrix", "latency_ms"]
    ).issubset(evaluation)
    assert evaluation["total"] == 30

    logs = (run_dir / "decision_logs.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(logs) == 30
    first = json.loads(logs[0])
    assert set(
        ["expected_action", "actual_action", "reason", "signals", "stage_latencies_ms"]
    ).issubset(first)
    assert {
        "predicted_event_type",
        "predicted_user_intent",
        "confidence",
        "ambiguity",
        "signal_source",
        "interpreter_steps",
    }.issubset(first["signals"])


def test_evaluate_dataset_rejects_overwrite(tmp_path) -> None:
    run_id = "20260509_120000_baseline"
    evaluate_dataset(
        "data/scenarios.json", "baseline", output_root=tmp_path, run_id=run_id
    )

    with pytest.raises(FileExistsError):
        evaluate_dataset(
            "data/scenarios.json", "baseline", output_root=tmp_path, run_id=run_id
        )


def test_read_run_artifacts(tmp_path) -> None:
    result = evaluate_dataset(
        "data/scenarios.json",
        "baseline",
        output_root=tmp_path,
        run_id="20260509_120001_baseline",
    )

    artifacts = read_run_artifacts(result["run_id"], output_root=tmp_path)

    assert artifacts["run_meta"]["run_id"] == result["run_id"]
    assert artifacts["evaluation"]["total"] == 30
    assert len(artifacts["decision_logs"]) == 30
