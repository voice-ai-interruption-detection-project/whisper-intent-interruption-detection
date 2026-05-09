from __future__ import annotations

import json

import pytest

from interruption_detection.models import ActionLabel
from interruption_detection.scenarios import (
    ScenarioLoadError,
    get_scenario_by_id,
    load_scenarios,
)


DATASET = "data/scenarios.json"


def test_load_scenarios_loads_current_dataset() -> None:
    scenarios = load_scenarios(DATASET)

    assert len(scenarios) == 30
    assert scenarios[0].expected_action == ActionLabel.CONTINUE
    assert not hasattr(scenarios[0], "actual_action")


def test_get_scenario_by_id() -> None:
    scenario = get_scenario_by_id(DATASET, "commerce_no_speech_001")

    assert scenario.scenario_id == "commerce_no_speech_001"
    assert scenario.user_utterance == ""


def test_loader_rejects_duplicate_ids(tmp_path) -> None:
    base = load_scenarios(DATASET)[0].model_dump(mode="json")
    payload = {"scenarios": [base, base]}
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ScenarioLoadError, match="duplicate scenario_id"):
        load_scenarios(path)


def test_loader_rejects_actual_action(tmp_path) -> None:
    item = load_scenarios(DATASET)[0].model_dump(mode="json")
    item["actual_action"] = "continue"
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps({"scenarios": [item]}), encoding="utf-8")

    with pytest.raises(ScenarioLoadError, match="actual_action"):
        load_scenarios(path)


def test_loader_rejects_pause(tmp_path) -> None:
    item = load_scenarios(DATASET)[0].model_dump(mode="json")
    item["expected_action"] = "pause"
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps({"scenarios": [item]}), encoding="utf-8")

    with pytest.raises(ScenarioLoadError, match="pause"):
        load_scenarios(path)


def test_loader_rejects_invalid_root_shape(tmp_path) -> None:
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(ScenarioLoadError, match="scenarios list"):
        load_scenarios(path)


def test_loader_rejects_utterance_when_has_user_speech_false(tmp_path) -> None:
    item = load_scenarios(DATASET)[0].model_dump(mode="json")
    item["user_utterance"] = "hello"
    item["has_user_speech"] = False
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps({"scenarios": [item]}), encoding="utf-8")

    with pytest.raises(ScenarioLoadError, match="has_user_speech"):
        load_scenarios(path)
