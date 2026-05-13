from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from interruption_detection.models import Scenario


class ScenarioLoadError(ValueError):
    """판단 케이스(Scenario) 데이터셋이 현재 계약을 어길 때 발생하는 오류."""


def load_scenarios(path: str | Path) -> list[Scenario]:
    """JSON 데이터셋을 읽고 판단 케이스(Scenario) 목록으로 검증해 반환한다."""
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

        # 판단 케이스(Scenario) 파일은 기준 입력이고, 관측 결과는 run artifact 아래에 둔다.
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
    """데이터셋에서 판단 케이스(Scenario) 식별자가 일치하는 항목 하나를 찾는다."""
    for scenario in load_scenarios(path):
        if scenario.scenario_id == scenario_id:
            return scenario

    raise ScenarioLoadError(f"scenario not found: {scenario_id}")


def _reject_result_fields(item: dict[str, Any], index: int) -> None:
    """기준 입력에 결과 전용 필드가 섞였는지 확인한다."""
    if "actual_action" in item:
        raise ScenarioLoadError(
            f"scenario at index {index} contains actual_action; results belong in runs"
        )

    if "expected_action" in item:
        raise ScenarioLoadError(
            "expected_action is deprecated; use expected_actions list"
        )

    if "pause" in item.get("expected_actions", []):
        raise ScenarioLoadError("pause is not an active action label")
