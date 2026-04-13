"""Export query results and profiles to JSON."""

from __future__ import annotations

import json
from typing import Any

from datalens_ai.core.models import DataProfile, QueryResult


def results_to_json(results: list[QueryResult], indent: int = 2) -> str:
    """Export a list of QueryResults to JSON."""
    data = [_result_dict(r) for r in results]
    return json.dumps(data, indent=indent, default=str)


def profile_to_json(profile: DataProfile, indent: int = 2) -> str:
    """Export a DataProfile to JSON."""
    return json.dumps(profile.model_dump(), indent=indent, default=str)


def _result_dict(result: QueryResult) -> dict[str, Any]:
    return {
        "id": result.id,
        "question": result.question,
        "sql_query": result.sql_query,
        "sql_explanation": result.sql_explanation,
        "execution_time_ms": result.execution_time_ms,
        "row_count": result.row_count,
        "columns": result.columns,
        "data": result.data[:100],
        "insights": result.insights,
        "error": result.error,
        "timestamp": result.timestamp.isoformat(),
    }
