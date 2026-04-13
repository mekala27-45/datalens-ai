"""Pydantic domain models for DataLens AI."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    """Statistical profile of a single column."""

    name: str
    dtype: str
    semantic_type: str | None = None
    null_count: int = 0
    null_pct: float = 0.0
    unique_count: int = 0
    cardinality: str = "medium"
    sample_values: list[str] = Field(default_factory=list)
    stats: dict[str, float] = Field(default_factory=dict)
    distribution: list[dict[str, Any]] = Field(default_factory=list)


class QualityIssue(BaseModel):
    """A data quality issue found in a dataset."""

    severity: str
    column: str | None = None
    issue_type: str
    description: str
    recommendation: str


class CorrelationPair(BaseModel):
    """A correlation between two columns."""

    column_a: str
    column_b: str
    correlation: float
    strength: str


class DataProfile(BaseModel):
    """Complete profile of a dataset."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    table_name: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile] = Field(default_factory=list)
    quality_score: float = 0.0
    quality_issues: list[QualityIssue] = Field(default_factory=list)
    correlations: list[CorrelationPair] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ChartRecommendation(BaseModel):
    """Recommended chart type for a query result."""

    chart_type: str
    x_column: str | None = None
    y_column: str | None = None
    color_column: str | None = None
    size_column: str | None = None
    reasoning: str = ""
    alternatives: list[str] = Field(default_factory=list)


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""

    role: str
    content: str
    sql_query: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class NLToSQLResponse(BaseModel):
    """Response from the NL-to-SQL engine."""

    sql: str
    chart_hint: str | None = None
    explanation: str = ""
    confidence: float = 0.0


class QueryResult(BaseModel):
    """Complete result of a natural language query."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str
    sql_query: str
    sql_explanation: str = ""
    execution_time_ms: float = 0.0
    row_count: int = 0
    columns: list[str] = Field(default_factory=list)
    data: list[dict[str, Any]] = Field(default_factory=list)
    chart_recommendation: ChartRecommendation | None = None
    insights: list[str] = Field(default_factory=list)
    error: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def success(self) -> bool:
        """Whether the query executed successfully."""
        return self.error is None


class ResultShape(BaseModel):
    """Analysis of a query result's shape for chart selection."""

    row_count: int
    column_count: int
    dimensions: list[str] = Field(default_factory=list)
    measures: list[str] = Field(default_factory=list)
    temporals: list[str] = Field(default_factory=list)
    pattern: str = "table"


class StorySection(BaseModel):
    """A section in a data story."""

    title: str
    narrative: str = ""
    query_result: QueryResult | None = None
    chart_config: dict[str, Any] | None = None


class DataStory(BaseModel):
    """A composed data story with multiple sections."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    sections: list[StorySection] = Field(default_factory=list)
    dataset_name: str = ""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SampleDatasetInfo(BaseModel):
    """Metadata about a built-in sample dataset."""

    name: str
    display_name: str
    description: str
    files: list[str]
    row_count: int
    suggested_questions: list[str] = Field(default_factory=list)
    icon: str = "\U0001f4ca"
