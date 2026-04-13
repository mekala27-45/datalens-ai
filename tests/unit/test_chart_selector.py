"""Tests for chart recommendation engine."""

from datalens_ai.core.models import ResultShape
from datalens_ai.visualization.chart_selector import recommend_chart


class TestRecommendChart:
    def test_single_value_kpi(self):
        shape = ResultShape(
            row_count=1, column_count=1,
            measures=["total"], pattern="single_value",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "kpi"

    def test_time_series_line(self):
        shape = ResultShape(
            row_count=12, column_count=2,
            temporals=["month"], measures=["revenue"],
            pattern="time_series",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "line"

    def test_ranking_horizontal_bar(self):
        shape = ResultShape(
            row_count=10, column_count=2,
            dimensions=["product"], measures=["sales"],
            pattern="ranking",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "horizontal_bar"

    def test_composition_low_cardinality_pie(self):
        shape = ResultShape(
            row_count=5, column_count=2,
            dimensions=["region"], measures=["count"],
            pattern="composition",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "pie"

    def test_distribution_histogram(self):
        shape = ResultShape(
            row_count=100, column_count=1,
            measures=["price"], pattern="distribution",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "histogram"

    def test_correlation_scatter(self):
        shape = ResultShape(
            row_count=50, column_count=2,
            measures=["x", "y"], pattern="correlation",
        )
        rec = recommend_chart(shape)
        assert rec.chart_type == "scatter"

    def test_hint_overrides(self):
        shape = ResultShape(
            row_count=10, column_count=2,
            dimensions=["x"], measures=["y"],
        )
        rec = recommend_chart(shape, hint="pie")
        assert rec.chart_type == "pie"

    def test_alternatives_populated(self):
        shape = ResultShape(
            row_count=10, column_count=2,
            dimensions=["x"], measures=["y"],
            pattern="ranking",
        )
        rec = recommend_chart(shape)
        assert len(rec.alternatives) > 0
