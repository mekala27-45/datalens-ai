"""Integration tests for the full NL-to-SQL pipeline."""

import pandas as pd
import pytest

from datalens_ai.ai.mock_provider import MockProvider
from datalens_ai.ai.nl_to_sql import NLToSQLOrchestrator
from datalens_ai.engine.duckdb_engine import DuckDBEngine


@pytest.fixture()
def pipeline():
    """Create a full pipeline with sample data."""
    engine = DuckDBEngine(memory_limit="256MB")
    df = pd.DataFrame({
        "product": ["Laptop", "Phone", "Tablet", "Headphones", "Camera"] * 20,
        "category": ["Electronics"] * 100,
        "revenue": [999, 699, 499, 149, 549] * 20,
        "quantity": [10, 25, 15, 50, 8] * 20,
        "order_date": pd.date_range("2024-01-01", periods=100, freq="D"),
    })
    engine.register_dataframe("orders", df)
    provider = MockProvider()
    orchestrator = NLToSQLOrchestrator(engine, provider)
    yield orchestrator, engine
    engine.close()


class TestFullPipeline:
    def test_count_query(self, pipeline):
        orch, _ = pipeline
        result = orch.process("How many orders are there?", "orders")
        assert result.success
        assert result.row_count > 0
        assert "COUNT" in result.sql_query.upper()

    def test_top_n_query(self, pipeline):
        orch, _ = pipeline
        result = orch.process(
            "What are the top 5 products by revenue?", "orders"
        )
        assert result.success
        assert "ORDER BY" in result.sql_query.upper()

    def test_average_query(self, pipeline):
        orch, _ = pipeline
        result = orch.process(
            "What is the average revenue?", "orders"
        )
        assert result.success
        assert "AVG" in result.sql_query.upper()

    def test_total_by_category(self, pipeline):
        orch, _ = pipeline
        result = orch.process(
            "What is the total revenue by product?", "orders"
        )
        assert result.success
        assert "SUM" in result.sql_query.upper()
        assert "GROUP BY" in result.sql_query.upper()

    def test_invalid_question_still_returns(self, pipeline):
        orch, _ = pipeline
        result = orch.process("xyzzy random nonsense", "orders")
        # Should still return something (fallback query)
        assert result.sql_query != ""

    def test_context_updates(self, pipeline):
        orch, _ = pipeline
        orch.process("How many orders?", "orders")
        ctx = orch.context.get_context_string()
        assert len(ctx) > 0


class TestPipelineWithChart:
    def test_result_has_columns(self, pipeline):
        orch, _ = pipeline
        result = orch.process(
            "What is the total revenue by product?", "orders"
        )
        assert len(result.columns) > 0
        assert len(result.data) > 0

    def test_data_is_serializable(self, pipeline):
        orch, _ = pipeline
        result = orch.process("How many orders?", "orders")
        # Data should be list of dicts
        assert isinstance(result.data, list)
        if result.data:
            assert isinstance(result.data[0], dict)
