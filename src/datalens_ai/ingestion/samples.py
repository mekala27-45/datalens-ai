from __future__ import annotations

from pathlib import Path

import yaml

from datalens_ai.core.config import get_data_dir
from datalens_ai.core.models import SampleDatasetInfo


def list_sample_datasets() -> dict[str, SampleDatasetInfo]:
    """List all available sample datasets.

    Reads ``metadata.yaml`` from the samples directory and returns a
    mapping of dataset key to :class:`SampleDatasetInfo`.  Datasets
    whose files are missing on disk are silently skipped.
    """
    samples_dir = get_data_dir() / "samples"
    metadata_path = samples_dir / "metadata.yaml"

    if not metadata_path.exists():
        return {}

    with open(metadata_path) as f:
        metadata = yaml.safe_load(f)

    datasets: dict[str, SampleDatasetInfo] = {}
    for key, info in metadata.get("datasets", {}).items():
        files = info.get("files", [])
        # Check all files exist
        existing_files = [f for f in files if (samples_dir / f).exists()]
        if not existing_files:
            continue

        datasets[key] = SampleDatasetInfo(
            name=key,
            display_name=info.get("display_name", key),
            description=info.get("description", ""),
            files=existing_files,
            row_count=info.get("row_count", 0),
            suggested_questions=info.get("suggested_questions", []),
            icon=info.get("icon", ""),
        )

    return datasets


def get_sample_file_paths(dataset_name: str) -> list[Path]:
    """Get full paths for a sample dataset's files.

    Raises :class:`KeyError` if the dataset name is not found in the
    available samples.
    """
    datasets = list_sample_datasets()
    if dataset_name not in datasets:
        available = list(datasets.keys())
        raise KeyError(
            f"Unknown sample dataset: {dataset_name}. Available: {available}"
        )

    samples_dir = get_data_dir() / "samples"
    return [samples_dir / f for f in datasets[dataset_name].files]
