"""Generate interesting questions from schema analysis."""

from __future__ import annotations

from datalens_ai.ai.base import BaseAIProvider
from datalens_ai.core.models import DataProfile


def suggest_questions(
    profile: DataProfile,
    provider: BaseAIProvider | None = None,
) -> list[str]:
    """Generate suggested questions based on data profile."""
    if provider and provider.is_available():
        try:
            schema_str = _profile_to_schema(profile)
            return provider.suggest_questions(schema_str)
        except Exception:
            pass

    return _rule_based_suggestions(profile)


def _rule_based_suggestions(profile: DataProfile) -> list[str]:
    suggestions: list[str] = []
    numeric = [c for c in profile.columns if c.dtype == "numeric"]
    categorical = [c for c in profile.columns if c.dtype == "categorical"]
    temporal = [c for c in profile.columns if c.dtype == "datetime"]

    for nc in numeric[:3]:
        suggestions.append(f"What is the average {nc.name}?")

    for cc in categorical[:2]:
        for nc in numeric[:2]:
            suggestions.append(f"What is the total {nc.name} by {cc.name}?")

    for cc in categorical[:2]:
        for nc in numeric[:1]:
            suggestions.append(f"What are the top 5 {cc.name} by {nc.name}?")

    for tc in temporal[:1]:
        for nc in numeric[:2]:
            suggestions.append(f"How has {nc.name} changed over time?")

    for nc in numeric[:2]:
        suggestions.append(f"What is the distribution of {nc.name}?")

    if len(numeric) >= 2:
        suggestions.append(
            f"What is the correlation between {numeric[0].name} "
            f"and {numeric[1].name}?"
        )

    if categorical:
        suggestions.append(
            f"How many records by {categorical[0].name}?"
        )

    suggestions.append(f"Show me a summary of {profile.table_name}")

    return suggestions[:12]


def _profile_to_schema(profile: DataProfile) -> str:
    lines = [f"Table: {profile.table_name}"]
    lines.append(f"Rows: {profile.row_count}")
    lines.append("Columns:")
    for col in profile.columns:
        extras = []
        if col.semantic_type:
            extras.append(f"semantic: {col.semantic_type}")
        if col.stats.get("min") is not None:
            extras.append(f"range: {col.stats['min']:.0f}-{col.stats.get('max', 0):.0f}")
        extra_str = f" [{', '.join(extras)}]" if extras else ""
        lines.append(f"  - {col.name} ({col.dtype}){extra_str}")
    return "\n".join(lines)
