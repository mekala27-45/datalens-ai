from __future__ import annotations

import time
from typing import Any

import duckdb
import pandas as pd

from datalens_ai.core.exceptions import SQLExecutionError
from datalens_ai.utils.sql_utils import add_limit


class DuckDBEngine:
    """In-process DuckDB SQL engine for data analytics."""

    def __init__(self, memory_limit: str = "512MB"):
        self._conn = duckdb.connect(":memory:")
        self._conn.execute(f"SET memory_limit = '{memory_limit}'")
        self._tables: dict[str, list[dict[str, str]]] = {}  # table -> [{name, type}]

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        return self._conn

    def register_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        """Register a DataFrame as a named table."""
        self._conn.register(table_name, df)
        self._update_schema_cache(table_name)

    def execute_sql(self, sql: str, limit: int | None = None) -> tuple[pd.DataFrame, float]:
        """Execute SQL and return (DataFrame, execution_time_ms)."""
        if limit:
            sql = add_limit(sql, limit)

        start = time.perf_counter()
        try:
            result = self._conn.execute(sql)
            df = result.fetchdf()
        except duckdb.Error as e:
            raise SQLExecutionError(f"SQL execution failed: {e}") from e
        elapsed_ms = (time.perf_counter() - start) * 1000

        return df, elapsed_ms

    def get_schema(self, table_name: str) -> list[dict[str, str]]:
        """Get column names and types for a table."""
        if table_name in self._tables:
            return self._tables[table_name]
        self._update_schema_cache(table_name)
        return self._tables.get(table_name, [])

    def get_sample_rows(self, table_name: str, n: int = 5) -> list[dict[str, Any]]:
        """Get sample rows from a table."""
        try:
            df, _ = self.execute_sql(f'SELECT * FROM "{table_name}" LIMIT {n}')
            return df.to_dict(orient="records")
        except SQLExecutionError:
            return []

    def get_table_names(self) -> list[str]:
        """Get all registered table names."""
        result = self._conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]

    def get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        try:
            result = self._conn.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()
            return result[0] if result else 0
        except duckdb.Error:
            return 0

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self.get_table_names()

    def get_schema_string(self, table_name: str) -> str:
        """Get a formatted schema string for AI prompts."""
        schema = self.get_schema(table_name)
        if not schema:
            return f"Table '{table_name}': no columns found"

        lines = [f"Table: {table_name}"]
        lines.append("Columns:")
        for col in schema:
            lines.append(f"  - {col['name']} ({col['type']})")

        # Add sample rows
        samples = self.get_sample_rows(table_name, 3)
        if samples:
            lines.append("Sample rows:")
            for row in samples:
                row_str = ", ".join(f"{k}={v}" for k, v in row.items())
                lines.append(f"  {row_str}")

        return "\n".join(lines)

    def explain(self, sql: str) -> str:
        """Get DuckDB's query plan explanation."""
        try:
            result = self._conn.execute(f"EXPLAIN {sql}").fetchall()
            return "\n".join(str(row[1]) for row in result)
        except duckdb.Error as e:
            return f"Explain failed: {e}"

    def close(self) -> None:
        """Close the DuckDB connection."""
        self._conn.close()

    def _update_schema_cache(self, table_name: str) -> None:
        """Update the schema cache for a table."""
        try:
            result = self._conn.execute(
                f"DESCRIBE \"{table_name}\""
            ).fetchall()
            self._tables[table_name] = [
                {"name": row[0], "type": row[1]}
                for row in result
            ]
        except duckdb.Error:
            pass
