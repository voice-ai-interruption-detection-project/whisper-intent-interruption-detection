from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from interruption_detection.models import (
    ActionLabel,
    EventType,
    PrimaryFailure,
    RunDecisionLog,
)
from interruption_detection.policies import get_policy
from interruption_detection.runner import run_scenario
from interruption_detection.scenarios import load_scenarios


def evaluate_dataset(
    dataset_path: str | Path,
    policy_name: str,
    output_root: str | Path = "results/runs",
    *,
    source: str = "eval",
    command: str | None = None,
    changed: list[str] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    dataset = Path(dataset_path)
    scenarios = load_scenarios(dataset)
    policy = get_policy(policy_name)
    timestamp = datetime.now().astimezone()
    run_id = run_id or f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{policy_name}"
    run_dir = Path(output_root) / run_id
    if run_dir.exists():
        raise FileExistsError(f"run artifact already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    logs: list[RunDecisionLog] = []
    for scenario in scenarios:
        decision = run_scenario(scenario, policy_name)
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
    criteria_snapshot = get_criteria_snapshot()
    meta = {
        "run_id": run_id,
        "timestamp": timestamp.isoformat(),
        "source": source,
        "mode": "baseline" if policy_name == "baseline" else "compare",
        "target": str(dataset),
        "changed": changed or [f"policy:{policy_name}"],
        "dataset": str(dataset),
        "policy_version": policy_name,
        "policy_snapshot": policy.snapshot(),
        "criteria_snapshot": criteria_snapshot,
        "latency_ms": total_latency,
        "command": command or "",
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


def build_evaluation(logs: list[RunDecisionLog]) -> dict[str, Any]:
    total = len(logs)
    correct = sum(1 for item in logs if item.expected_action == item.actual_action)
    failure_counts = Counter(
        item.primary_failure.value for item in logs if item.primary_failure is not None
    )
    failures = {
        failure.value: failure_counts.get(failure.value, 0)
        for failure in PrimaryFailure
    }
    return {
        "total": total,
        "correct": correct,
        "action_accuracy": round(correct / total, 4) if total else 0.0,
        "failures": failures,
        "confusion_matrix": build_confusion_matrix(logs),
        "latency_ms": {
            "total": round(sum(item.latency_ms for item in logs), 3),
            "average": (
                round(
                    sum(item.latency_ms for item in logs) / total,
                    3,
                )
                if total
                else 0.0
            ),
        },
    }


def build_confusion_matrix(logs: list[RunDecisionLog]) -> dict[str, dict[str, int]]:
    labels = [label.value for label in ActionLabel]
    matrix = {expected: {actual: 0 for actual in labels} for expected in labels}
    for item in logs:
        matrix[item.expected_action.value][item.actual_action.value] += 1
    return matrix


def classify_failure(
    *,
    expected: ActionLabel,
    actual: ActionLabel,
    event_type: EventType,
) -> PrimaryFailure | None:
    if expected == actual:
        return None
    if event_type == EventType.AMBIGUOUS:
        return PrimaryFailure.AMBIGUOUS_INTENT
    if expected in {ActionLabel.STOP_AND_SWITCH, ActionLabel.HANDOFF} and actual in {
        ActionLabel.CONTINUE,
        ActionLabel.BRIEF_ACK,
        ActionLabel.RESPOND_AND_CONTINUE,
    }:
        return PrimaryFailure.MISSED_SWITCH
    if expected in {
        ActionLabel.CONTINUE,
        ActionLabel.BRIEF_ACK,
        ActionLabel.RESPOND_AND_CONTINUE,
    } and actual in {
        ActionLabel.STOP_AND_SWITCH,
        ActionLabel.ASK_CLARIFYING,
        ActionLabel.HANDOFF,
    }:
        return PrimaryFailure.FALSE_STOP
    return PrimaryFailure.ACTION_CONFUSION


def get_criteria_snapshot() -> dict[str, object]:
    return {
        "action_labels": [label.value for label in ActionLabel],
        "primary_failures": [failure.value for failure in PrimaryFailure],
        "comparison": "expected_action_vs_actual_action",
    }


def build_error_analysis(
    run_id: str,
    logs: list[RunDecisionLog],
    evaluation: dict[str, Any],
) -> str:
    lines = [
        f"# Error Analysis - {run_id}",
        "",
        "## Summary",
        "",
        f"- total: {evaluation['total']}",
        f"- correct: {evaluation['correct']}",
        f"- action_accuracy: {evaluation['action_accuracy']}",
        "",
        "## Primary failures",
        "",
    ]
    for failure, count in evaluation["failures"].items():
        lines.append(f"- {failure}: {count}")
    failed = [item for item in logs if item.primary_failure is not None]
    lines.extend(["", "## Failed cases", ""])
    if not failed:
        lines.append("- none")
    for item in failed:
        lines.append(
            "- "
            f"{item.scenario_id}: expected={item.expected_action.value}, "
            f"actual={item.actual_action.value}, primary={item.primary_failure.value}"
        )
    lines.append("")
    return "\n".join(lines)


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
