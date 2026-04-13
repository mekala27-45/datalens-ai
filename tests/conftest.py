"""Shared fixtures for DataLens AI tests."""

from __future__ import annotations

import pandas as pd
import pytest

from datalens_ai.engine.duckdb_engine import DuckDBEngine


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """Simple test DataFrame."""
    return pd.DataFrame({
        "product": ["Laptop", "Phone", "Tablet", "Headphones", "Camera"],
        "category": ["Electronics", "Electronics", "Electronics", "Electronics", "Electronics"],
        "price": [999.99, 699.99, 499.99, 149.99, 549.99],
        "quantity": [10, 25, 15, 50, 8],
        "order_date": pd.to_datetime([
            "2024-01-15", "2024-02-20", "2024-03-10",
            "2024-04-05", "2024-05-18",
        ]),
    })


@pytest.fixture()
def engine(sample_df: pd.DataFrame) -> DuckDBEngine:
    """DuckDB engine with sample data loaded."""
    eng = DuckDBEngine(memory_limit="256MB")
    eng.register_dataframe("test_data", sample_df)
    yield eng
    eng.close()


@pytest.fixture()
def schema_string(engine: DuckDBEngine) -> str:
    """Schema string for the test table."""
    return engine.get_schema_string("test_data")
