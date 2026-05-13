from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from interruption_detection.models import StrictModel


InputMode = Literal["text", "audio_file"]
DatasetScope = Literal["official", "diagnostic"]


class DatasetRegistryError(ValueError):
    """Test Bench dataset registry가 현재 계약을 어길 때 발생한다."""


class DatasetSpec(StrictModel):
    """UI/API가 선택할 수 있는 repo-local Test Bench dataset 항목."""

    id: str
    label: str
    path: str
    scope: DatasetScope
    description: str = ""
    input_modes: list[InputMode] = Field(default_factory=lambda: ["text"])

    @field_validator("path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        """dataset registry에는 repo 기준 상대 경로만 허용한다."""
        if Path(value).is_absolute():
            raise ValueError("dataset path must be relative to the repository")
        return value

    @model_validator(mode="after")
    def validate_input_modes(self) -> "DatasetSpec":
        """input_mode 목록은 비어 있거나 중복되면 선택 UI가 모호해진다."""
        if not self.input_modes:
            raise ValueError("input_modes must contain at least one mode")
        if len(set(self.input_modes)) != len(self.input_modes):
            raise ValueError("input_modes must not contain duplicates")
        return self


def load_dataset_registry(path: str | Path) -> list[DatasetSpec]:
    """repo-local dataset registry를 읽고 선택 가능한 dataset 목록을 반환한다."""
    registry_path = Path(path)

    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DatasetRegistryError(
            f"dataset registry not found: {registry_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DatasetRegistryError(f"invalid JSON in {registry_path}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("datasets"), list):
        raise DatasetRegistryError(
            "dataset registry must be an object with datasets list"
        )

    seen: set[str] = set()
    datasets: list[DatasetSpec] = []

    for index, item in enumerate(raw["datasets"]):
        if not isinstance(item, dict):
            raise DatasetRegistryError(f"dataset at index {index} must be an object")

        dataset_id = item.get("id")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise DatasetRegistryError(f"dataset at index {index} has invalid id")
        if dataset_id in seen:
            raise DatasetRegistryError(f"duplicate dataset id: {dataset_id}")

        seen.add(dataset_id)

        try:
            datasets.append(DatasetSpec.model_validate(item))
        except ValidationError as exc:
            raise DatasetRegistryError(f"invalid dataset {dataset_id}: {exc}") from exc

    return datasets


def get_dataset_by_id(path: str | Path, dataset_id: str) -> DatasetSpec:
    """registry에서 id가 일치하는 dataset 항목을 반환한다."""
    for dataset in load_dataset_registry(path):
        if dataset.id == dataset_id:
            return dataset

    raise DatasetRegistryError(f"unknown dataset_id: {dataset_id}")


def find_dataset_by_path(
    path: str | Path, dataset_path: str | Path
) -> DatasetSpec | None:
    """기본 dataset path와 registry 항목이 일치하면 해당 항목을 반환한다."""
    normalized = Path(dataset_path)

    for dataset in load_dataset_registry(path):
        if Path(dataset.path) == normalized:
            return dataset

    return None
