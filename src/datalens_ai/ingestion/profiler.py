from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from datalens_ai.core.constants import (
    DTYPE_CATEGORICAL,
    DTYPE_DATETIME,
    DTYPE_NUMERIC,
)
from datalens_ai.core.models import ColumnProfile, CorrelationPair, DataProfile
from datalens_ai.ingestion.detector import detect_semantic_type
from datalens_ai.utils.data_utils import (
    classify_cardinality,
    detect_dtype,
    get_sample_values,
)


def profile_table(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
) -> DataProfile:
    """Generate a complete statistical profile of a DuckDB table."""
    df = conn.execute(f"SELECT * FROM {table_name}").fetchdf()
    row_count = len(df)
    columns = []

    for col_name in df.columns:
        series = df[col_name]
        col_profile = _profile_column(series, col_name, row_count)
        columns.append(col_profile)

    # Compute correlations between numeric columns
    numeric_cols = [c.name for c in columns if c.dtype == DTYPE_NUMERIC]
    correlations = _compute_correlations(df, numeric_cols)

    # Generate suggested questions
    suggested = _generate_suggestions(columns, table_name)

    return DataProfile(
        table_name=table_name,
        row_count=row_count,
        column_count=len(columns),
        columns=columns,
        correlations=correlations,
        suggested_questions=suggested,
    )


def _profile_column(
    series: pd.Series, col_name: str, total_rows: int
) -> ColumnProfile:
    """Profile a single column."""
    dtype = detect_dtype(series)
    semantic_type = detect_semantic_type(series, col_name)
    null_count = int(series.isna().sum())
    null_pct = null_count / max(total_rows, 1)
    unique_count = int(series.nunique())
    cardinality = classify_cardinality(unique_count, total_rows)
    sample_values = get_sample_values(series)

    stats: dict = {}
    distribution: list = []

    if dtype == DTYPE_NUMERIC:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) > 0:
            stats = {
                "min": float(numeric.min()),
                "max": float(numeric.max()),
                "mean": float(numeric.mean()),
                "median": float(numeric.median()),
                "std": float(numeric.std()) if len(numeric) > 1 else 0.0,
                "q25": float(numeric.quantile(0.25)),
                "q75": float(numeric.quantile(0.75)),
            }
            # Histogram bins
            try:
                counts, bin_edges = np.histogram(
                    numeric, bins=min(20, unique_count)
                )
                distribution = [
                    {
                        "bin": f"{bin_edges[i]:.2f}-{bin_edges[i + 1]:.2f}",
                        "count": int(counts[i]),
                    }
                    for i in range(len(counts))
                ]
            except (ValueError, TypeError):
                pass

    elif dtype == DTYPE_CATEGORICAL:
        value_counts = series.value_counts().head(20)
        distribution = [
            {"value": str(val), "count": int(count)}
            for val, count in value_counts.items()
        ]
        if len(value_counts) > 0:
            stats["mode"] = str(value_counts.index[0])
            stats["mode_count"] = float(value_counts.iloc[0])

    elif dtype == DTYPE_DATETIME:
        try:
            dt_series = pd.to_datetime(series, errors="coerce").dropna()
            if len(dt_series) > 0:
                stats["min"] = dt_series.min().timestamp()
                stats["max"] = dt_series.max().timestamp()
                stats["range_days"] = (dt_series.max() - dt_series.min()).days
        except (ValueError, TypeError):
            pass

    return ColumnProfile(
        name=col_name,
        dtype=dtype,
        semantic_type=semantic_type,
        null_count=null_count,
        null_pct=round(null_pct, 4),
        unique_count=unique_count,
        cardinality=cardinality,
        sample_values=sample_values,
        stats=stats,
        distribution=distribution,
    )


def _compute_correlations(
    df: pd.DataFrame, numeric_cols: list[str]
) -> list[CorrelationPair]:
    """Compute Pearson correlations between numeric columns."""
    if len(numeric_cols) < 2:
        return []

    corr_matrix = df[numeric_cols].corr()
    pairs: list[CorrelationPair] = []
    seen: set[tuple[str, str]] = set()

    for i, col_a in enumerate(numeric_cols):
        for j, col_b in enumerate(numeric_cols):
            if i >= j:
                continue
            key = (col_a, col_b)
            if key in seen:
                continue
            seen.add(key)

            corr_val = corr_matrix.loc[col_a, col_b]
            if pd.isna(corr_val):
                continue

            abs_corr = abs(corr_val)
            if abs_corr < 0.3:
                continue  # Skip weak correlations

            strength = "weak"
            if abs_corr >= 0.7:
                strength = "strong"
            elif abs_corr >= 0.5:
                strength = "moderate"

            pairs.append(
                CorrelationPair(
                    column_a=col_a,
                    column_b=col_b,
                    correlation=round(float(corr_val), 4),
                    strength=strength,
                )
            )

    return sorted(pairs, key=lambda p: abs(p.correlation), reverse=True)


def _generate_suggestions(
    columns: list[ColumnProfile], table_name: str
) -> list[str]:
    """Generate suggested questions based on column profiles."""
    suggestions: list[str] = []

    numeric_cols = [c for c in columns if c.dtype == DTYPE_NUMERIC]
    categorical_cols = [c for c in columns if c.dtype == DTYPE_CATEGORICAL]
    datetime_cols = [c for c in columns if c.dtype == DTYPE_DATETIME]

    # Basic aggregation questions
    for num_col in numeric_cols[:3]:
        suggestions.append(f"What is the average {num_col.name}?")

    # Group by questions
    for cat_col in categorical_cols[:2]:
        for num_col in numeric_cols[:2]:
            suggestions.append(
                f"What is the total {num_col.name} by {cat_col.name}?"
            )

    # Top N questions
    for cat_col in categorical_cols[:2]:
        for num_col in numeric_cols[:1]:
            suggestions.append(
                f"What are the top 5 {cat_col.name} by {num_col.name}?"
            )

    # Time series questions
    for dt_col in datetime_cols[:1]:
        for num_col in numeric_cols[:2]:
            suggestions.append(
                f"How has {num_col.name} changed over time?"
            )

    # Distribution questions
    for num_col in numeric_cols[:2]:
        suggestions.append(
            f"What is the distribution of {num_col.name}?"
        )

    # Count questions
    if categorical_cols:
        suggestions.append(
            f"How many records are there by {categorical_cols[0].name}?"
        )

    return suggestions[:12]  # Cap at 12 suggestions
