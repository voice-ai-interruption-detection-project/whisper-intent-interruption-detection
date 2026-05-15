from __future__ import annotations

import json

import pytest

from interruption_detection.datasets import (
    DatasetRegistryError,
    get_dataset_by_id,
    load_dataset_registry,
)
from interruption_detection.scenarios import load_scenarios


def test_load_dataset_registry_lists_repo_local_datasets() -> None:
    datasets = load_dataset_registry("data/datasets.json")

    assert [item.id for item in datasets] == [
        "core",
        "policy_v2_edge",
        "policy_v3_edge",
        "policy_v3_challenge",
    ]
    assert datasets[0].scope == "official"
    assert datasets[1].scope == "diagnostic"
    assert datasets[2].scope == "diagnostic"
    assert datasets[3].scope == "diagnostic"


def test_get_dataset_by_id_returns_edge_slice() -> None:
    dataset = get_dataset_by_id("data/datasets.json", "policy_v2_edge")

    assert dataset.path == "data/scenarios_policy_v2_edge.json"
    assert dataset.input_modes == ["text"]


def test_policy_v2_edge_dataset_loads() -> None:
    scenarios = load_scenarios("data/scenarios_policy_v2_edge.json")

    assert len(scenarios) == 11
    assert scenarios[0].scenario_id == "policy_v2_no_speech_shipping_001"


def test_policy_v3_edge_dataset_loads() -> None:
    scenarios = load_scenarios("data/scenarios_policy_v3_edge.json")

    assert len(scenarios) == 12
    assert scenarios[0].scenario_id == "policy_v3_shipping_same_intent_fee_001"
    assert scenarios[1].ai_utterance == scenarios[0].ai_utterance
    assert scenarios[0].expected_actions[0].value == "respond_and_continue"
    assert scenarios[1].expected_actions[0].value == "stop_and_switch"


def test_policy_v3_challenge_dataset_loads() -> None:
    scenarios = load_scenarios("data/scenarios_policy_v3_challenge.json")

    assert len(scenarios) == 18
    assert scenarios[0].scenario_id == (
        "policy_v3_challenge_return_same_pickup_address_001"
    )
    assert scenarios[1].ai_utterance == scenarios[0].ai_utterance
    assert scenarios[0].expected_actions[0].value == "respond_and_continue"
    assert scenarios[1].expected_actions[0].value == "stop_and_switch"


def test_dataset_registry_rejects_absolute_path(tmp_path) -> None:
    registry = tmp_path / "datasets.json"
    registry.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "id": "bad",
                        "label": "Bad",
                        "path": str(tmp_path / "scenarios.json"),
                        "scope": "diagnostic",
                        "input_modes": ["text"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(DatasetRegistryError, match="dataset path must be relative"):
        load_dataset_registry(registry)
