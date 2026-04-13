from __future__ import annotations

import re

import duckdb

from datalens_ai.core.constants import MAX_QUERY_ROWS
from datalens_ai.core.exceptions import SQLValidationError
from datalens_ai.utils.sql_utils import add_limit, extract_table_names, is_dangerous_sql


class SQLValidator:
    """Validates SQL queries for safety and correctness."""

    def __init__(self, engine):
        """Initialize with a DuckDBEngine instance."""
        self._engine = engine

    def validate(self, sql: str) -> str:
        """Validate SQL and return sanitized version. Raises SQLValidationError."""
        sql = sql.strip().rstrip(";")

        if not sql:
            raise SQLValidationError("Empty SQL query")

        # Check for dangerous operations
        if is_dangerous_sql(sql):
            raise SQLValidationError(
                "Destructive SQL operations are not allowed. "
                "Only SELECT queries are permitted."
            )

        # Must start with SELECT (or WITH for CTEs)
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith(("SELECT", "WITH")):
            raise SQLValidationError(
                "Only SELECT queries (and CTEs with WITH) are allowed."
            )

        # Validate table names exist (skip CTE aliases)
        tables = extract_table_names(sql)
        cte_aliases = {
            m.group(1).lower()
            for m in re.finditer(r"\bWITH\s+(\w+)\s+AS\b", sql, re.IGNORECASE)
        }
        available_tables = self._engine.get_table_names()
        for table in tables:
            if table.lower() in cte_aliases:
                continue
            # Case-insensitive check
            if not any(t.lower() == table.lower() for t in available_tables):
                raise SQLValidationError(
                    f"Table '{table}' not found. "
                    f"Available tables: {available_tables}"
                )

        # Add LIMIT if not present
        sql = add_limit(sql, MAX_QUERY_ROWS)

        # Try EXPLAIN to validate syntax
        try:
            self._engine.connection.execute(f"EXPLAIN {sql}")
        except duckdb.Error as e:
            raise SQLValidationError(f"Invalid SQL syntax: {e}") from e

        return sql

    def is_safe(self, sql: str) -> tuple[bool, str]:
        """Check if SQL is safe without raising. Returns (safe, reason)."""
        try:
            self.validate(sql)
            return True, ""
        except SQLValidationError as e:
            return False, str(e)
