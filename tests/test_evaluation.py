from __future__ import annotations

import json

import pytest

from interruption_detection.evaluation.artifacts import read_run_artifacts
from interruption_detection.evaluation.evaluator import (
    build_evaluation,
    classify_failure,
    evaluate_dataset,
    is_action_match,
)
from interruption_detection.models import ActionLabel, EventType, RunDecisionLog


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
        ["action_accuracy", "failures", "mismatch_matrix", "latency_ms"]
    ).issubset(evaluation)
    assert evaluation["total"] == 30

    logs = (run_dir / "decision_logs.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(logs) == 30
    first = json.loads(logs[0])
    assert set(
        [
            "expected_actions",
            "actual_action",
            "action_match",
            "reason",
            "signals",
            "stage_latencies_ms",
        ]
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


def test_action_match_uses_expected_actions_membership() -> None:
    assert is_action_match(
        [ActionLabel.BRIEF_ACK, ActionLabel.CONTINUE],
        ActionLabel.CONTINUE,
    )
    assert (
        classify_failure(
            expected_actions=[ActionLabel.BRIEF_ACK, ActionLabel.CONTINUE],
            actual=ActionLabel.CONTINUE,
            event_type=EventType.BACKCHANNEL,
        )
        is None
    )


def test_build_evaluation_counts_expected_actions_membership_as_correct() -> None:
    logs = [
        RunDecisionLog(
            scenario_id="commerce_backchannel_002",
            policy_name="policy_v1",
            event_type=EventType.BACKCHANNEL,
            expected_actions=[
                ActionLabel.BRIEF_ACK,
                ActionLabel.CONTINUE,
            ],
            actual_action=ActionLabel.CONTINUE,
            action_match=True,
            reason="Short acknowledgement.",
        )
    ]

    evaluation = build_evaluation(logs)

    assert evaluation["correct"] == 1
    assert evaluation["action_accuracy"] == 1.0
    assert evaluation["mismatch_matrix"] == {}


def test_mismatch_matrix_uses_expected_actions_as_unordered_set() -> None:
    logs = [
        RunDecisionLog(
            scenario_id="commerce_backchannel_002",
            policy_name="policy_v1",
            event_type=EventType.BACKCHANNEL,
            expected_actions=[
                ActionLabel.CONTINUE,
                ActionLabel.BRIEF_ACK,
            ],
            actual_action=ActionLabel.STOP_AND_SWITCH,
            action_match=False,
            reason="Stopped on a backchannel.",
        ),
        RunDecisionLog(
            scenario_id="commerce_backchannel_003",
            policy_name="policy_v1",
            event_type=EventType.BACKCHANNEL,
            expected_actions=[
                ActionLabel.BRIEF_ACK,
                ActionLabel.CONTINUE,
            ],
            actual_action=ActionLabel.STOP_AND_SWITCH,
            action_match=False,
            reason="Stopped on a backchannel.",
        ),
    ]

    evaluation = build_evaluation(logs)

    assert evaluation["mismatch_matrix"] == {
        "brief_ack|continue": {"stop_and_switch": 2}
    }
