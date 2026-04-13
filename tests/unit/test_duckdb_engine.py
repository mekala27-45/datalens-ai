"""Tests for DuckDB engine."""

import pytest

from datalens_ai.core.exceptions import SQLExecutionError


class TestDuckDBEngine:
    def test_register_and_query(self, engine, sample_df):
        df, ms = engine.execute_sql("SELECT COUNT(*) AS cnt FROM test_data")
        assert df["cnt"].iloc[0] == len(sample_df)
        assert ms >= 0

    def test_get_table_names(self, engine):
        names = engine.get_table_names()
        assert "test_data" in names

    def test_table_exists(self, engine):
        assert engine.table_exists("test_data") is True
        assert engine.table_exists("nonexistent") is False

    def test_get_schema(self, engine):
        schema = engine.get_schema("test_data")
        assert len(schema) > 0
        col_names = [c["name"] for c in schema]
        assert "product" in col_names
        assert "price" in col_names

    def test_get_sample_rows(self, engine):
        rows = engine.get_sample_rows("test_data", 3)
        assert len(rows) == 3
        assert "product" in rows[0]

    def test_get_row_count(self, engine):
        count = engine.get_row_count("test_data")
        assert count == 5

    def test_get_schema_string(self, engine):
        s = engine.get_schema_string("test_data")
        assert "Table: test_data" in s
        assert "Columns:" in s

    def test_invalid_sql_raises(self, engine):
        with pytest.raises(SQLExecutionError):
            engine.execute_sql("SELECT * FROM nonexistent_table")

    def test_execute_with_limit(self, engine):
        df, _ = engine.execute_sql(
            "SELECT * FROM test_data", limit=2
        )
        assert len(df) == 2

    def test_explain(self, engine):
        result = engine.explain("SELECT * FROM test_data")
        assert len(result) > 0
