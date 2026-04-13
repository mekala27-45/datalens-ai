"""Pre-built data story templates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoryTemplate:
    """A template defining the structure of a data story."""

    name: str
    description: str
    section_prompts: list[str]


OVERVIEW_TEMPLATE = StoryTemplate(
    name="Dataset Overview",
    description="A comprehensive overview of the entire dataset",
    section_prompts=[
        "How many records are in the dataset?",
        "What is the distribution of {categorical}?",
        "What are the key statistics for {numeric}?",
        "What are the top 5 {categorical} by {numeric}?",
    ],
)

TREND_TEMPLATE = StoryTemplate(
    name="Trend Analysis",
    description="Analyze how key metrics change over time",
    section_prompts=[
        "How has {numeric} changed over time?",
        "What is the average {numeric} by month?",
        "What is the trend of {numeric} over time?",
    ],
)

COMPARISON_TEMPLATE = StoryTemplate(
    name="Category Comparison",
    description="Compare performance across categories",
    section_prompts=[
        "What is the total {numeric} by {categorical}?",
        "What is the average {numeric} by {categorical}?",
        "What are the top 10 {categorical} by {numeric}?",
        "What are the bottom 5 {categorical} by {numeric}?",
    ],
)

DISTRIBUTION_TEMPLATE = StoryTemplate(
    name="Distribution Analysis",
    description="Understand the distribution and spread of key metrics",
    section_prompts=[
        "What is the distribution of {numeric}?",
        "What is the average {numeric}?",
        "How many records are there by {categorical}?",
    ],
)

CORRELATION_TEMPLATE = StoryTemplate(
    name="Correlation Explorer",
    description="Discover relationships between numeric variables",
    section_prompts=[
        "What is the correlation between {numeric} and {numeric2}?",
        "Show a scatter plot of {numeric} vs {numeric2}",
        "What is the average {numeric} by {categorical}?",
    ],
)

ALL_TEMPLATES: dict[str, StoryTemplate] = {
    "overview": OVERVIEW_TEMPLATE,
    "trend": TREND_TEMPLATE,
    "comparison": COMPARISON_TEMPLATE,
    "distribution": DISTRIBUTION_TEMPLATE,
    "correlation": CORRELATION_TEMPLATE,
}


def get_template(name: str) -> StoryTemplate:
    """Get a story template by name."""
    return ALL_TEMPLATES[name]


def list_templates() -> list[StoryTemplate]:
    """List all available story templates."""
    return list(ALL_TEMPLATES.values())
