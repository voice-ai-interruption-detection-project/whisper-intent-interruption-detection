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
    """데이터셋 전체를 지정 정책으로 실행하고 run artifact를 생성한다."""
    dataset = Path(dataset_path)
    scenarios = load_scenarios(dataset)
    policy = get_policy(policy_name)
    timestamp = datetime.now().astimezone()
    run_id = run_id or f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{policy_name}"
    run_dir = Path(output_root) / run_id
    # run artifact는 근거 자료이므로 이전 측정값을 덮어쓰지 않는다.
    if run_dir.exists():
        raise FileExistsError(f"run artifact already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    logs: list[RunDecisionLog] = []
    for scenario in scenarios:
        # 평가기는 공통 runner를 재사용하고, 비교용 메타데이터만 추가한다.
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
    """판단 로그 목록에서 정확도, 실패 수, 혼동 행렬을 계산한다."""
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
    """예상 행동과 실제 행동의 교차표를 만든다."""
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
    """예상/실제 행동 불일치를 1차 실패 유형으로 분류한다."""
    # 1차 실패는 근본 원인이 아니라 불일치의 모양을 설명한다.
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
    """이번 평가에 사용한 라벨과 비교 기준을 스냅샷으로 반환한다."""
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
    """실패 케이스를 사람이 훑기 쉬운 마크다운 요약으로 만든다."""
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
    """사전 데이터를 사람이 읽기 쉬운 JSON 파일로 저장한다."""
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, logs: list[RunDecisionLog]) -> None:
    """판단 케이스(Scenario)별 판단 로그를 JSONL 형식으로 저장한다."""
    with path.open("w", encoding="utf-8") as handle:
        for item in logs:
            handle.write(json.dumps(item.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")
