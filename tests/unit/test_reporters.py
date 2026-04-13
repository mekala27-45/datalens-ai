"""Tests for reporter modules."""

from datalens_ai.core.models import DataProfile, DataStory, QueryResult, StorySection
from datalens_ai.reporters.csv_reporter import result_to_csv, results_to_csv
from datalens_ai.reporters.html import generate_html_report
from datalens_ai.reporters.json_reporter import profile_to_json, results_to_json
from datalens_ai.reporters.markdown import generate_markdown_report


def _make_result() -> QueryResult:
    return QueryResult(
        question="What is the total?",
        sql_query="SELECT SUM(x) FROM t",
        row_count=1,
        columns=["total"],
        data=[{"total": 42}],
        insights=["The total is 42."],
    )


def _make_story() -> DataStory:
    return DataStory(
        title="Test Story",
        sections=[
            StorySection(
                title="Section 1",
                narrative="This is the narrative.",
                query_result=_make_result(),
            ),
        ],
        dataset_name="test_data",
    )


def _make_profile() -> DataProfile:
    return DataProfile(
        table_name="test_data",
        row_count=100,
        column_count=3,
        quality_score=85.0,
    )


class TestHTMLReporter:
    def test_basic_report(self):
        html = generate_html_report(title="Test Report")
        assert "<!DOCTYPE html>" in html
        assert "Test Report" in html

    def test_with_story(self):
        html = generate_html_report(story=_make_story())
        assert "Section 1" in html
        assert "SELECT SUM" in html

    def test_with_profile(self):
        html = generate_html_report(profile=_make_profile())
        assert "100" in html
        assert "85" in html

    def test_with_results(self):
        html = generate_html_report(results=[_make_result()])
        assert "42" in html


class TestMarkdownReporter:
    def test_basic_report(self):
        md = generate_markdown_report(title="Test")
        assert "# Test" in md

    def test_with_story(self):
        md = generate_markdown_report(story=_make_story())
        assert "Section 1" in md

    def test_with_profile(self):
        md = generate_markdown_report(profile=_make_profile())
        assert "100" in md


class TestJSONReporter:
    def test_results_to_json(self):
        result = results_to_json([_make_result()])
        assert "42" in result
        assert '"question"' in result

    def test_profile_to_json(self):
        result = profile_to_json(_make_profile())
        assert "test_data" in result


class TestCSVReporter:
    def test_result_to_csv(self):
        csv = result_to_csv(_make_result())
        assert "total" in csv
        assert "42" in csv

    def test_empty_results(self):
        csv = results_to_csv([])
        assert csv == ""
