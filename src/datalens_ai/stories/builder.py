"""Build data stories from templates and query results."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datalens_ai.core.constants import DTYPE_CATEGORICAL, DTYPE_NUMERIC
from datalens_ai.core.models import DataStory, StorySection

if TYPE_CHECKING:
    from datalens_ai.ai.nl_to_sql import NLToSQLOrchestrator
    from datalens_ai.core.models import DataProfile
    from datalens_ai.stories.templates import StoryTemplate

logger = logging.getLogger(__name__)


class StoryBuilder:
    """Build data stories by executing template prompts."""

    def __init__(
        self,
        orchestrator: NLToSQLOrchestrator,
        profile: DataProfile,
    ) -> None:
        self.orchestrator = orchestrator
        self.profile = profile

    def build(
        self,
        template: StoryTemplate,
        *,
        max_sections: int = 6,
    ) -> DataStory:
        """Build a data story from a template."""
        prompts = self._resolve_prompts(template.section_prompts)
        sections: list[StorySection] = []

        for prompt in prompts[:max_sections]:
            section = self._build_section(prompt)
            if section:
                sections.append(section)

        return DataStory(
            title=template.name,
            sections=sections,
            dataset_name=self.profile.table_name,
        )

    def build_custom(
        self,
        title: str,
        questions: list[str],
    ) -> DataStory:
        """Build a custom story from a list of questions."""
        sections: list[StorySection] = []
        for question in questions:
            section = self._build_section(question)
            if section:
                sections.append(section)

        return DataStory(
            title=title,
            sections=sections,
            dataset_name=self.profile.table_name,
        )

    def _build_section(self, question: str) -> StorySection | None:
        """Build a single story section by executing a question."""
        try:
            result = self.orchestrator.query(question)
            if not result.success:
                return None

            chart_config = None
            if result.chart_recommendation:
                chart_config = result.chart_recommendation.model_dump()

            narrative = ""
            if result.insights:
                narrative = " ".join(result.insights[:3])
            if result.sql_explanation:
                narrative += f"\n\n**Query:** {result.sql_explanation}"

            return StorySection(
                title=question,
                narrative=narrative,
                query_result=result,
                chart_config=chart_config,
            )
        except Exception:
            logger.debug("Failed to build section for: %s", question)
            return None

    def _resolve_prompts(self, templates: list[str]) -> list[str]:
        """Replace placeholders with actual column names."""
        numeric_cols = [
            c.name for c in self.profile.columns
            if c.dtype == DTYPE_NUMERIC
        ]
        categorical_cols = [
            c.name for c in self.profile.columns
            if c.dtype == DTYPE_CATEGORICAL
        ]

        resolved: list[str] = []
        for tmpl in templates:
            prompt = tmpl
            if "{numeric}" in prompt and numeric_cols:
                prompt = prompt.replace("{numeric}", numeric_cols[0])
            if "{numeric2}" in prompt and len(numeric_cols) > 1:
                prompt = prompt.replace("{numeric2}", numeric_cols[1])
            if "{categorical}" in prompt and categorical_cols:
                prompt = prompt.replace("{categorical}", categorical_cols[0])

            # Skip prompts with unresolved placeholders
            if "{" not in prompt:
                resolved.append(prompt)

        return resolved
