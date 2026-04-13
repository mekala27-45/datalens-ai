from __future__ import annotations

import pandas as pd

from datalens_ai.core.constants import (
    CARDINALITY_LOW,
    DTYPE_DATETIME,
    DTYPE_NUMERIC,
)
from datalens_ai.core.models import ResultShape
from datalens_ai.utils.data_utils import detect_dtype


class ResultAnalyzer:
    """Analyze query result DataFrames to determine visualization strategy."""

    def analyze(self, df: pd.DataFrame) -> ResultShape:
        """Analyze a DataFrame and return its shape classification."""
        if df.empty:
            return ResultShape(
                row_count=0, column_count=0, pattern="table"
            )

        row_count = len(df)
        column_count = len(df.columns)

        dimensions: list[str] = []
        measures: list[str] = []
        temporals: list[str] = []

        for col in df.columns:
            dtype = detect_dtype(df[col])
            if dtype == DTYPE_DATETIME:
                temporals.append(col)
            elif dtype == DTYPE_NUMERIC:
                measures.append(col)
            else:
                dimensions.append(col)

        pattern = self._detect_pattern(
            df, dimensions, measures, temporals, row_count
        )

        return ResultShape(
            row_count=row_count,
            column_count=column_count,
            dimensions=dimensions,
            measures=measures,
            temporals=temporals,
            pattern=pattern,
        )

    def _detect_pattern(
        self,
        df: pd.DataFrame,
        dimensions: list[str],
        measures: list[str],
        temporals: list[str],
        row_count: int,
    ) -> str:
        """Detect the data pattern for chart selection."""
        num_dims = len(dimensions)
        num_measures = len(measures)
        num_temporals = len(temporals)

        # Single value (scalar result)
        if row_count == 1 and num_measures == 1 and num_dims == 0:
            return "single_value"

        # Single value with label
        if row_count == 1 and num_measures >= 1:
            return "single_value"

        # Time series: has temporal column + numeric
        if num_temporals >= 1 and num_measures >= 1:
            return "time_series"

        # Ranking: ordered categorical + numeric, few rows
        if num_dims == 1 and num_measures == 1 and row_count <= 20:
            return "ranking"

        # Composition: one categorical + one numeric, low cardinality
        if num_dims == 1 and num_measures == 1:
            nunique = df[dimensions[0]].nunique()
            if nunique <= CARDINALITY_LOW:
                return "composition"
            return "ranking"

        # Distribution: single numeric column
        if num_dims == 0 and num_measures == 1 and row_count > 20:
            return "distribution"

        # Correlation: two numeric columns
        if num_dims == 0 and num_measures == 2:
            return "correlation"

        # Comparison: multiple measures or two dimensions
        if num_dims >= 1 and num_measures >= 2:
            return "comparison"

        if num_dims == 2 and num_measures == 1:
            return "comparison"

        # Default: table
        return "table"
