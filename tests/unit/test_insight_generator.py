"""Tests for the insight generator."""

import pandas as pd

from datalens_ai.ai.insight_generator import generate_insights


class TestInsightGenerator:
    def test_empty_df(self):
        df = pd.DataFrame()
        insights = generate_insights(df)
        assert "No data" in insights[0]

    def test_numeric_insights(self):
        df = pd.DataFrame({
            "product": ["A", "B", "C", "D", "E"],
            "revenue": [1000, 200, 50, 500, 5000],
        })
        insights = generate_insights(df, "revenue by product")
        assert len(insights) > 0

    def test_single_row(self):
        df = pd.DataFrame({"value": [42]})
        insights = generate_insights(df)
        assert any("Single" in i for i in insights)

    def test_categorical_dominance(self):
        df = pd.DataFrame({
            "category": ["A"] * 80 + ["B"] * 20,
            "value": range(100),
        })
        insights = generate_insights(df)
        assert any("dominates" in i or "A" in i for i in insights)
