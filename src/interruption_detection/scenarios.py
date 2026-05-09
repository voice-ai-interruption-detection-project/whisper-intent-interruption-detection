from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from interruption_detection.models import Scenario


class ScenarioLoadError(ValueError):
    """Raised when a scenario dataset violates the active contract."""


def load_scenarios(path: str | Path) -> list[Scenario]:
    dataset_path = Path(path)
    try:
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScenarioLoadError(f"invalid JSON in {dataset_path}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("scenarios"), list):
        raise ScenarioLoadError(
            "scenario dataset must be an object with scenarios list"
        )

    seen: set[str] = set()
    scenarios: list[Scenario] = []
    for index, item in enumerate(raw["scenarios"]):
        if not isinstance(item, dict):
            raise ScenarioLoadError(f"scenario at index {index} must be an object")
        _reject_result_fields(item, index)
        scenario_id = item.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ScenarioLoadError(
                f"scenario at index {index} has invalid scenario_id"
            )
        if scenario_id in seen:
            raise ScenarioLoadError(f"duplicate scenario_id: {scenario_id}")
        seen.add(scenario_id)
        try:
            scenarios.append(Scenario.model_validate(item))
        except ValidationError as exc:
            raise ScenarioLoadError(f"invalid scenario {scenario_id}: {exc}") from exc

    return scenarios


def get_scenario_by_id(path: str | Path, scenario_id: str) -> Scenario:
    for scenario in load_scenarios(path):
        if scenario.scenario_id == scenario_id:
            return scenario
    raise ScenarioLoadError(f"scenario not found: {scenario_id}")


def _reject_result_fields(item: dict[str, Any], index: int) -> None:
    if "actual_action" in item:
        raise ScenarioLoadError(
            f"scenario at index {index} contains actual_action; results belong in runs"
        )
    if item.get("expected_action") == "pause":
        raise ScenarioLoadError("pause is not an active action label")
