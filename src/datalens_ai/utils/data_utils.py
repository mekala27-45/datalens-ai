"""DataFrame and data type utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def detect_dtype(series: pd.Series) -> str:
    """Detect the high-level data type of a pandas Series."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if series.dtype == object:
        sample = series.dropna().head(20)
        if len(sample) > 0:
            try:
                pd.to_datetime(sample)
                return "datetime"
            except (ValueError, TypeError):
                pass
        nunique = series.nunique()
        total = len(series)
        if nunique / max(total, 1) < 0.5:
            return "categorical"
        return "text"
    return "text"


def safe_numeric(value) -> float | None:
    """Safely convert a value to float."""
    try:
        result = float(value)
        if np.isnan(result) or np.isinf(result):
            return None
        return result
    except (ValueError, TypeError):
        return None


def get_sample_values(series: pd.Series, n: int = 5) -> list[str]:
    """Get sample non-null values as strings."""
    samples = series.dropna().head(n)
    return [str(v) for v in samples.tolist()]


def classify_cardinality(nunique: int, total: int) -> str:
    """Classify column cardinality."""
    if total == 0:
        return "low"
    ratio = nunique / total
    if ratio > 0.9:
        return "id"
    if nunique <= 8:
        return "low"
    if nunique <= 30:
        return "medium"
    return "high"
