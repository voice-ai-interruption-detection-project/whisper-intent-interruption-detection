from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def list_run_artifacts(
    output_root: str | Path = "results/runs",
) -> list[dict[str, Any]]:
    root = Path(output_root)
    if not root.exists():
        return []

    runs = []
    for run_dir in sorted(root.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        meta_path = run_dir / "run_meta.json"
        evaluation_path = run_dir / "evaluation.json"
        if not meta_path.exists() or not evaluation_path.exists():
            continue
        meta = _read_json(meta_path)
        evaluation = _read_json(evaluation_path)
        runs.append(
            {
                "run_id": run_dir.name,
                "timestamp": meta.get("timestamp"),
                "policy_version": meta.get("policy_version"),
                "dataset": meta.get("dataset"),
                "action_accuracy": evaluation.get("action_accuracy"),
                "total": evaluation.get("total"),
                "failures": evaluation.get("failures", {}),
                "latency_ms": evaluation.get("latency_ms", {}),
            }
        )
    return runs


def read_run_artifacts(
    run_id: str, output_root: str | Path = "results/runs"
) -> dict[str, Any]:
    if Path(run_id).name != run_id:
        raise ValueError("run_id must not contain path separators")
    run_dir = Path(output_root) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"run not found: {run_id}")

    decision_logs = []
    logs_path = run_dir / "decision_logs.jsonl"
    if logs_path.exists():
        with logs_path.open(encoding="utf-8") as handle:
            decision_logs = [json.loads(line) for line in handle if line.strip()]

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "run_meta": _read_json(run_dir / "run_meta.json"),
        "evaluation": _read_json(run_dir / "evaluation.json"),
        "decision_logs": decision_logs,
        "error_analysis": (run_dir / "error_analysis.md").read_text(encoding="utf-8"),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
