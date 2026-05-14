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

    assert [item.id for item in datasets] == ["core", "policy_v2_edge"]
    assert datasets[0].scope == "official"
    assert datasets[1].scope == "diagnostic"


def test_get_dataset_by_id_returns_edge_slice() -> None:
    dataset = get_dataset_by_id("data/datasets.json", "policy_v2_edge")

    assert dataset.path == "data/scenarios_policy_v2_edge.json"
    assert dataset.input_modes == ["text"]


def test_policy_v2_edge_dataset_loads() -> None:
    scenarios = load_scenarios("data/scenarios_policy_v2_edge.json")

    assert len(scenarios) == 11
    assert scenarios[0].scenario_id == "policy_v2_no_speech_shipping_001"


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
