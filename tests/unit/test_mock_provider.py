"""Tests for the MockProvider."""

from datalens_ai.ai.mock_provider import MockProvider

SCHEMA = """Table: orders
Columns:
  - product (VARCHAR)
  - category (VARCHAR)
  - price (DOUBLE)
  - quantity (INTEGER)
  - order_date (DATE)
"""


class TestMockProvider:
    def setup_method(self):
        self.provider = MockProvider()

    def test_is_available(self):
        assert self.provider.is_available() is True

    def test_name(self):
        assert self.provider.name == "Mock Provider"

    def test_count_query(self):
        resp = self.provider.nl_to_sql("How many orders are there?", SCHEMA)
        assert "COUNT" in resp.sql.upper()
        assert resp.confidence > 0

    def test_top_n_query(self):
        resp = self.provider.nl_to_sql(
            "What are the top 5 products by price?", SCHEMA
        )
        assert "LIMIT" in resp.sql.upper() or "5" in resp.sql
        assert "ORDER BY" in resp.sql.upper()

    def test_average_query(self):
        resp = self.provider.nl_to_sql(
            "What is the average price?", SCHEMA
        )
        assert "AVG" in resp.sql.upper()

    def test_total_query(self):
        resp = self.provider.nl_to_sql(
            "What is the total price by category?", SCHEMA
        )
        assert "SUM" in resp.sql.upper()
        assert "GROUP BY" in resp.sql.upper()

    def test_trend_query(self):
        resp = self.provider.nl_to_sql(
            "How has price changed over time?", SCHEMA
        )
        assert "DATE_TRUNC" in resp.sql.upper() or "ORDER BY" in resp.sql.upper()

    def test_distribution_query(self):
        resp = self.provider.nl_to_sql(
            "What is the distribution of price?", SCHEMA
        )
        assert "price" in resp.sql.lower()
        assert resp.chart_hint == "histogram"

    def test_default_fallback(self):
        resp = self.provider.nl_to_sql("xyzzy gibberish", SCHEMA)
        assert "SELECT" in resp.sql.upper()

    def test_generate_insights(self):
        insights = self.provider.generate_insights("some data")
        assert len(insights) > 0

    def test_explain_sql(self):
        explanation = self.provider.explain_sql(
            "SELECT * FROM t WHERE x = 1", SCHEMA
        )
        assert len(explanation) > 0

    def test_suggest_questions(self):
        questions = self.provider.suggest_questions(SCHEMA)
        assert len(questions) > 0
