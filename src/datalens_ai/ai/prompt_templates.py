"""Prompt templates for AI interactions."""

from __future__ import annotations

NL_TO_SQL_SYSTEM = (
    "You are a SQL expert. Given a database schema and a "
    "natural language question, generate a DuckDB SQL query.\n\n"
    "RULES:\n"
    "- Only generate SELECT queries. Never INSERT/UPDATE/DELETE/DROP.\n"
    "- Use DuckDB SQL syntax (similar to PostgreSQL).\n"
    "- Quote column names with double quotes if they have spaces.\n"
    "- Use aggregations (SUM, AVG, COUNT, MIN, MAX) when implied.\n"
    "- Add ORDER BY for top/best/highest/lowest questions.\n"
    "- Add LIMIT for a specific number of results.\n"
    "- For time questions, use DATE_TRUNC or EXTRACT.\n"
    "- Return ONLY valid SQL, no explanations.\n\n"
    "SCHEMA:\n{schema}\n\n{context}\n\n"
    "Respond in this exact JSON format:\n"
    '{{"sql": "YOUR SQL QUERY", '
    '"chart_hint": "bar|line|scatter|pie|heatmap|histogram|kpi|table", '
    '"explanation": "Brief explanation"}}'
)

INSIGHT_GENERATION = """Analyze this data summary and generate 3-5 key insights.
Each insight should be a concise, actionable observation.

Data summary:
{data_summary}

Return insights as a JSON array of strings:
["insight 1", "insight 2", "insight 3"]
"""

SQL_EXPLANATION = """Explain this SQL query in plain English. Be concise and clear.
Break it down by clause (SELECT, FROM, WHERE, GROUP BY, ORDER BY, LIMIT).

Schema context:
{schema}

SQL:
{sql}

Provide a clear, non-technical explanation:
"""

QUESTION_SUGGESTION = (
    "Given this database schema, suggest 8 interesting analytical "
    "questions that a data analyst would ask. "
    "Mix simple and complex questions.\n\n"
    "Schema:\n{schema}\n\n"
    'Return as a JSON array of question strings:\n'
    '["question 1", "question 2", ...]'
)
