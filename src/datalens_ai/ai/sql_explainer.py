"""Explain SQL queries in plain English."""

from __future__ import annotations

import re

from datalens_ai.ai.base import BaseAIProvider


def explain_sql(
    sql: str,
    schema: str = "",
    provider: BaseAIProvider | None = None,
) -> str:
    """Explain a SQL query in plain English."""
    if provider and provider.is_available():
        try:
            return provider.explain_sql(sql, schema)
        except Exception:
            pass

    return _rule_based_explain(sql)


def _rule_based_explain(sql: str) -> str:
    parts = []
    sql_upper = sql.upper()

    # SELECT clause
    select_match = re.search(
        r"SELECT\s+(.+?)\s+FROM", sql, re.IGNORECASE | re.DOTALL
    )
    if select_match:
        cols = select_match.group(1).strip()
        if cols == "*":
            parts.append("Retrieves all columns")
        else:
            agg_funcs = re.findall(
                r"(SUM|AVG|COUNT|MIN|MAX)\s*\(", cols, re.IGNORECASE
            )
            if agg_funcs:
                funcs = ", ".join(f.upper() for f in agg_funcs)
                parts.append(f"Calculates {funcs} aggregations")
            else:
                parts.append("Selects specific columns")

    # FROM clause
    from_match = re.search(r"FROM\s+\"?(\w+)\"?", sql, re.IGNORECASE)
    if from_match:
        parts.append(f"from the '{from_match.group(1)}' table")

    # WHERE clause
    if "WHERE" in sql_upper:
        parts.append("with filters applied")

    # GROUP BY
    group_match = re.search(
        r"GROUP\s+BY\s+\"?(\w+)\"?", sql, re.IGNORECASE
    )
    if group_match:
        parts.append(f"grouped by '{group_match.group(1)}'")

    # ORDER BY
    if "ORDER BY" in sql_upper:
        if "DESC" in sql_upper:
            parts.append("sorted from highest to lowest")
        else:
            parts.append("sorted in order")

    # LIMIT
    limit_match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
    if limit_match:
        parts.append(f"showing the top {limit_match.group(1)} results")

    if not parts:
        return "This query retrieves data from the database."

    explanation = " ".join(parts) + "."
    return explanation[0].upper() + explanation[1:]
