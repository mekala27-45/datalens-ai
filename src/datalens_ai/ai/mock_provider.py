"""Rule-based NL-to-SQL provider for demo mode (no API key needed)."""

from __future__ import annotations

import re

from datalens_ai.ai.base import BaseAIProvider
from datalens_ai.core.models import NLToSQLResponse
from datalens_ai.core.registry import register_provider


@register_provider("mock")
class MockProvider(BaseAIProvider):
    """Pattern-matching NL-to-SQL provider that works without any API."""

    @property
    def name(self) -> str:
        return "Mock Provider"

    def is_available(self) -> bool:
        return True

    def nl_to_sql(
        self, question: str, schema: str, context: str = ""
    ) -> NLToSQLResponse:
        q = question.lower().strip()
        table = self._extract_table(schema)
        columns = self._extract_columns(schema)

        num_cols = columns.get("numeric", [])
        cat_cols = columns.get("categorical", [])
        dt_cols = columns.get("datetime", [])

        sql, chart_hint, explanation = self._match_pattern(
            q, table, num_cols, cat_cols, dt_cols
        )

        return NLToSQLResponse(
            sql=sql,
            chart_hint=chart_hint,
            explanation=explanation,
            confidence=0.7,
        )

    def generate_insights(self, data_summary: str) -> list[str]:
        return [
            "The data shows clear patterns in the top categories.",
            "There is significant variation across groups.",
            "Some outliers may warrant further investigation.",
        ]

    def explain_sql(self, sql: str, schema: str) -> str:
        parts = []
        sql_upper = sql.upper()
        if "SELECT" in sql_upper:
            parts.append("This query retrieves data")
        if "WHERE" in sql_upper:
            parts.append("with specific filters applied")
        if "GROUP BY" in sql_upper:
            parts.append("grouped by categories")
        if "ORDER BY" in sql_upper:
            parts.append("sorted by the results")
        if "LIMIT" in sql_upper:
            parts.append("limited to a specific number of rows")
        return ", ".join(parts) + "." if parts else "This query selects data."

    def suggest_questions(self, schema: str) -> list[str]:
        table = self._extract_table(schema)
        cols = self._extract_columns(schema)
        suggestions = []

        for nc in cols.get("numeric", [])[:2]:
            suggestions.append(f"What is the average {nc}?")
        for cc in cols.get("categorical", [])[:1]:
            for nc in cols.get("numeric", [])[:1]:
                suggestions.append(f"What are the top 5 {cc} by {nc}?")
                suggestions.append(f"What is the total {nc} by {cc}?")
        for dc in cols.get("datetime", [])[:1]:
            for nc in cols.get("numeric", [])[:1]:
                suggestions.append(f"How has {nc} changed over time?")
        suggestions.append(f"How many rows are in {table}?")
        return suggestions[:8]

    def _match_pattern(
        self,
        q: str,
        table: str,
        num_cols: list[str],
        cat_cols: list[str],
        dt_cols: list[str],
    ) -> tuple[str, str, str]:
        # Find referenced columns
        ref_num = self._find_referenced(q, num_cols)
        ref_cat = self._find_referenced(q, cat_cols)
        ref_dt = self._find_referenced(q, dt_cols)

        nc = ref_num[0] if ref_num else (num_cols[0] if num_cols else "*")
        cc = ref_cat[0] if ref_cat else (cat_cols[0] if cat_cols else None)
        dc = ref_dt[0] if ref_dt else (dt_cols[0] if dt_cols else None)

        # Extract limit number
        limit_match = re.search(r"top\s+(\d+)|(\d+)\s+(?:best|worst)", q)
        limit_n = int(limit_match.group(1) or limit_match.group(2)) if limit_match else 10

        # Pattern: count / how many
        if re.search(r"\b(count|how many|number of)\b", q):
            if cc:
                sql = (
                    f'SELECT "{cc}", COUNT(*) AS count '
                    f'FROM "{table}" GROUP BY "{cc}" '
                    f"ORDER BY count DESC"
                )
                return sql, "bar", f"Count of records by {cc}"
            sql = f'SELECT COUNT(*) AS total_count FROM "{table}"'
            return sql, "kpi", "Total record count"

        # Pattern: top N / best / highest
        if re.search(r"\b(top|best|highest|largest|most)\b", q):
            if cc and nc != "*":
                sql = (
                    f'SELECT "{cc}", SUM("{nc}") AS total_{nc} '
                    f'FROM "{table}" GROUP BY "{cc}" '
                    f"ORDER BY total_{nc} DESC LIMIT {limit_n}"
                )
                return sql, "horizontal_bar", f"Top {limit_n} {cc} by {nc}"

        # Pattern: lowest / worst / bottom
        if re.search(r"\b(bottom|worst|lowest|smallest|least)\b", q):
            if cc and nc != "*":
                sql = (
                    f'SELECT "{cc}", SUM("{nc}") AS total_{nc} '
                    f'FROM "{table}" GROUP BY "{cc}" '
                    f"ORDER BY total_{nc} ASC LIMIT {limit_n}"
                )
                return sql, "horizontal_bar", f"Bottom {limit_n} {cc} by {nc}"

        # Pattern: total / sum
        if re.search(r"\b(total|sum)\b", q):
            if cc and nc != "*":
                sql = (
                    f'SELECT "{cc}", SUM("{nc}") AS total_{nc} '
                    f'FROM "{table}" GROUP BY "{cc}" '
                    f"ORDER BY total_{nc} DESC"
                )
                return sql, "bar", f"Total {nc} by {cc}"
            if nc != "*":
                sql = f'SELECT SUM("{nc}") AS total_{nc} FROM "{table}"'
                return sql, "kpi", f"Total {nc}"

        # Pattern: average / mean
        if re.search(r"\b(average|avg|mean)\b", q):
            if cc and nc != "*":
                sql = (
                    f'SELECT "{cc}", AVG("{nc}") AS avg_{nc} '
                    f'FROM "{table}" GROUP BY "{cc}" '
                    f"ORDER BY avg_{nc} DESC"
                )
                return sql, "bar", f"Average {nc} by {cc}"
            if nc != "*":
                sql = f'SELECT AVG("{nc}") AS avg_{nc} FROM "{table}"'
                return sql, "kpi", f"Average {nc}"

        # Pattern: trend / over time / by month / by year
        if re.search(r"\b(trend|over time|by month|by year|monthly|yearly)\b", q):
            if dc and nc != "*":
                trunc = "month" if "month" in q else "year"
                sql = (
                    f"SELECT DATE_TRUNC('{trunc}', \"{dc}\") AS period, "
                    f'SUM("{nc}") AS total_{nc} '
                    f'FROM "{table}" GROUP BY period ORDER BY period'
                )
                return sql, "line", f"{nc} trend over time"

        # Pattern: distribution / spread
        if re.search(r"\b(distribution|spread|histogram)\b", q):
            if nc != "*":
                sql = f'SELECT "{nc}" FROM "{table}"'
                return sql, "histogram", f"Distribution of {nc}"

        # Pattern: correlation / relationship / vs
        if re.search(r"\b(correlation|relationship|vs|versus)\b", q):
            if len(ref_num) >= 2:
                sql = (
                    f'SELECT "{ref_num[0]}", "{ref_num[1]}" '
                    f'FROM "{table}"'
                )
                return sql, "scatter", f"{ref_num[0]} vs {ref_num[1]}"

        # Pattern: group by / by
        by_match = re.search(r"\bby\s+(\w+)", q)
        if by_match and cc and nc != "*":
            sql = (
                f'SELECT "{cc}", SUM("{nc}") AS total_{nc} '
                f'FROM "{table}" GROUP BY "{cc}" '
                f"ORDER BY total_{nc} DESC"
            )
            return sql, "bar", f"{nc} by {cc}"

        # Default: show data sample
        sql = f'SELECT * FROM "{table}" LIMIT 20'
        return sql, "table", "Data sample"

    @staticmethod
    def _extract_table(schema: str) -> str:
        match = re.search(r"Table:\s*(\w+)", schema)
        return match.group(1) if match else "data"

    @staticmethod
    def _extract_columns(schema: str) -> dict[str, list[str]]:
        cols: dict[str, list[str]] = {
            "numeric": [], "categorical": [], "datetime": [],
        }
        for match in re.finditer(
            r"-\s+(\w+)\s+\((\w+)", schema
        ):
            name, dtype = match.group(1), match.group(2).upper()
            if any(t in dtype for t in (
                "INT", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC",
                "BIGINT", "SMALLINT", "REAL",
            )):
                cols["numeric"].append(name)
            elif any(t in dtype for t in ("DATE", "TIME", "TIMESTAMP")):
                cols["datetime"].append(name)
            else:
                cols["categorical"].append(name)
        return cols

    @staticmethod
    def _find_referenced(question: str, columns: list[str]) -> list[str]:
        found = []
        q_lower = question.lower()
        for col in columns:
            col_words = col.lower().replace("_", " ")
            if col.lower() in q_lower or col_words in q_lower:
                found.append(col)
        return found
