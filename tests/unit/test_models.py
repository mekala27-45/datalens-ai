"""Tests for Pydantic domain models."""

from datalens_ai.core.models import (
    ChartRecommendation,
    ColumnProfile,
    CorrelationPair,
    DataProfile,
    DataStory,
    NLToSQLResponse,
    QueryResult,
    ResultShape,
    SampleDatasetInfo,
    StorySection,
)


class TestColumnProfile:
    def test_defaults(self):
        cp = ColumnProfile(name="price", dtype="numeric")
        assert cp.name == "price"
        assert cp.dtype == "numeric"
        assert cp.null_count == 0
        assert cp.sample_values == []
        assert cp.stats == {}

    def test_with_stats(self):
        cp = ColumnProfile(
            name="age",
            dtype="numeric",
            stats={"min": 18, "max": 65, "mean": 35.2},
        )
        assert cp.stats["mean"] == 35.2


class TestQueryResult:
    def test_success(self):
        qr = QueryResult(question="test", sql_query="SELECT 1")
        assert qr.success is True
        assert qr.error is None

    def test_failure(self):
        qr = QueryResult(
            question="test",
            sql_query="SELECT 1",
            error="Something failed",
        )
        assert qr.success is False

    def test_auto_id(self):
        qr1 = QueryResult(question="a", sql_query="SELECT 1")
        qr2 = QueryResult(question="b", sql_query="SELECT 2")
        assert qr1.id != qr2.id


class TestResultShape:
    def test_defaults(self):
        rs = ResultShape(row_count=10, column_count=3)
        assert rs.pattern == "table"
        assert rs.dimensions == []
        assert rs.measures == []
        assert rs.temporals == []


class TestNLToSQLResponse:
    def test_creation(self):
        resp = NLToSQLResponse(sql="SELECT * FROM t")
        assert resp.confidence == 0.0
        assert resp.chart_hint is None


class TestDataProfile:
    def test_creation(self):
        dp = DataProfile(
            table_name="test",
            row_count=100,
            column_count=5,
        )
        assert dp.table_name == "test"
        assert dp.quality_score == 0.0
        assert len(dp.id) == 8


class TestDataStory:
    def test_creation(self):
        ds = DataStory(
            title="Test Story",
            sections=[StorySection(title="Section 1")],
        )
        assert len(ds.sections) == 1
        assert ds.sections[0].narrative == ""


class TestChartRecommendation:
    def test_creation(self):
        cr = ChartRecommendation(chart_type="bar", x_column="x", y_column="y")
        assert cr.alternatives == []


class TestCorrelationPair:
    def test_creation(self):
        cp = CorrelationPair(
            column_a="a", column_b="b",
            correlation=0.85, strength="strong",
        )
        assert cp.strength == "strong"


class TestSampleDatasetInfo:
    def test_creation(self):
        info = SampleDatasetInfo(
            name="test", display_name="Test",
            description="A test", files=["test.csv"],
            row_count=100,
        )
        assert info.icon == "\U0001f4ca"
