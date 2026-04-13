"""Tests for story templates and export."""

from datalens_ai.core.models import DataStory, QueryResult, StorySection
from datalens_ai.stories.export import story_to_dict, story_to_json, story_to_markdown
from datalens_ai.stories.templates import (
    ALL_TEMPLATES,
    get_template,
    list_templates,
)


class TestTemplates:
    def test_list_templates(self):
        templates = list_templates()
        assert len(templates) >= 4

    def test_get_template(self):
        t = get_template("overview")
        assert t.name == "Dataset Overview"
        assert len(t.section_prompts) > 0

    def test_all_templates_have_prompts(self):
        for name, t in ALL_TEMPLATES.items():
            assert len(t.section_prompts) > 0, f"{name} has no prompts"


def _make_story():
    return DataStory(
        title="Test",
        sections=[
            StorySection(
                title="Q1",
                narrative="Answer.",
                query_result=QueryResult(
                    question="Q1",
                    sql_query="SELECT 1",
                    row_count=1,
                    columns=["x"],
                    data=[{"x": 1}],
                ),
            ),
        ],
        dataset_name="data",
    )


class TestStoryExport:
    def test_to_dict(self):
        d = story_to_dict(_make_story())
        assert d["title"] == "Test"
        assert len(d["sections"]) == 1

    def test_to_json(self):
        j = story_to_json(_make_story())
        assert '"Test"' in j

    def test_to_markdown(self):
        md = story_to_markdown(_make_story())
        assert "# Test" in md
        assert "SELECT 1" in md
