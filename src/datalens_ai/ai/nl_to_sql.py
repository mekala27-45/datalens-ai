"""NL-to-SQL orchestrator — ties AI providers with engine."""

from __future__ import annotations

import logging

from datalens_ai.ai.base import BaseAIProvider
from datalens_ai.ai.mock_provider import MockProvider
from datalens_ai.core.exceptions import SQLValidationError
from datalens_ai.core.models import QueryResult
from datalens_ai.engine.duckdb_engine import DuckDBEngine
from datalens_ai.engine.query_context import QueryContext
from datalens_ai.engine.sql_validator import SQLValidator

logger = logging.getLogger(__name__)


class NLToSQLOrchestrator:
    """Orchestrate NL question -> SQL -> execution -> result."""

    def __init__(
        self,
        engine: DuckDBEngine,
        provider: BaseAIProvider | None = None,
    ):
        self.engine = engine
        self.provider = provider or MockProvider()
        self.validator = SQLValidator(engine)
        self.context = QueryContext()

    def process(
        self, question: str, table_name: str
    ) -> QueryResult:
        """Process a natural language question end-to-end."""
        schema = self.engine.get_schema_string(table_name)
        context_str = self.context.get_context_string()

        # Generate SQL
        try:
            response = self.provider.nl_to_sql(
                question, schema, context_str
            )
        except Exception as e:
            logger.warning("AI provider failed: %s, falling back to mock", e)
            fallback = MockProvider()
            response = fallback.nl_to_sql(question, schema, context_str)

        sql = response.sql
        if not sql:
            return QueryResult(
                question=question,
                sql_query="",
                error="Could not generate SQL for this question.",
            )

        # Validate SQL
        try:
            sql = self.validator.validate(sql)
        except SQLValidationError as e:
            # Try once more with the error context
            if self.provider.is_available():
                try:
                    retry_ctx = f"Previous SQL failed: {e}. Fix it."
                    response = self.provider.nl_to_sql(
                        question, schema, retry_ctx
                    )
                    sql = self.validator.validate(response.sql)
                except (SQLValidationError, Exception):
                    return QueryResult(
                        question=question,
                        sql_query=response.sql,
                        error=f"SQL validation failed: {e}",
                    )
            else:
                return QueryResult(
                    question=question,
                    sql_query=sql,
                    error=f"SQL validation failed: {e}",
                )

        # Execute SQL
        try:
            df, exec_ms = self.engine.execute_sql(sql)
        except Exception as e:
            return QueryResult(
                question=question,
                sql_query=sql,
                error=f"SQL execution failed: {e}",
            )

        # Build explanation
        explanation = response.explanation
        if not explanation:
            try:
                explanation = self.provider.explain_sql(sql, schema)
            except Exception:
                explanation = ""

        # Update conversation context
        self.context.add_user_query(question)
        self.context.add_assistant_response(explanation, sql)

        return QueryResult(
            question=question,
            sql_query=sql,
            sql_explanation=explanation,
            execution_time_ms=round(exec_ms, 2),
            row_count=len(df),
            columns=list(df.columns),
            data=df.to_dict(orient="records"),
            insights=[],
        )
