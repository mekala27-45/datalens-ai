"""Abstract base class for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from datalens_ai.core.models import NLToSQLResponse


class BaseAIProvider(ABC):
    """Base class for all AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""

    @abstractmethod
    def nl_to_sql(
        self, question: str, schema: str, context: str = ""
    ) -> NLToSQLResponse:
        """Convert a natural language question to SQL."""

    @abstractmethod
    def generate_insights(self, data_summary: str) -> list[str]:
        """Generate insights from a data summary."""

    @abstractmethod
    def explain_sql(self, sql: str, schema: str) -> str:
        """Explain a SQL query in plain English."""

    @abstractmethod
    def suggest_questions(self, schema: str) -> list[str]:
        """Suggest interesting questions based on a schema."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
