"""SQL parsing and formatting utilities."""

from __future__ import annotations

import re

from datalens_ai.core.constants import DANGEROUS_SQL_KEYWORDS


def is_dangerous_sql(sql: str) -> bool:
    """Check if SQL contains destructive operations."""
    sql_upper = sql.upper().strip()
    for keyword in DANGEROUS_SQL_KEYWORDS:
        if re.match(rf"^\s*{keyword}\b", sql_upper):
            return True
    return False


def add_limit(sql: str, limit: int = 10000) -> str:
    """Add a LIMIT clause if not already present."""
    sql_upper = sql.upper().strip()
    if "LIMIT" in sql_upper:
        return sql
    sql = sql.rstrip().rstrip(";")
    return f"{sql}\nLIMIT {limit}"


def extract_table_names(sql: str) -> list[str]:
    """Extract table names referenced in SQL."""
    pattern = r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)"
    matches = re.findall(pattern, sql, re.IGNORECASE)
    tables = []
    for match in matches:
        name = match[0] or match[1]
        if name:
            tables.append(name.lower())
    return list(set(tables))


def format_sql(sql: str) -> str:
    """Uppercase SQL keywords for display."""
    keywords = [
        "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY",
        "HAVING", "LIMIT", "JOIN", "LEFT JOIN", "RIGHT JOIN",
        "INNER JOIN", "ON", "AND", "OR", "AS", "UNION",
        "DISTINCT", "COUNT", "SUM", "AVG", "MIN", "MAX",
        "CASE", "WHEN", "THEN", "ELSE", "END", "IN", "NOT",
        "BETWEEN", "LIKE", "IS", "NULL", "ASC", "DESC", "WITH",
    ]
    result = sql.strip()
    for kw in sorted(keywords, key=len, reverse=True):
        result = re.sub(rf"\b{kw}\b", kw, result, flags=re.IGNORECASE)
    return result
