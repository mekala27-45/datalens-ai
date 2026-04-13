"""Tests for SQL validator."""

import pytest

from datalens_ai.core.exceptions import SQLValidationError
from datalens_ai.engine.sql_validator import SQLValidator


class TestSQLValidator:
    def test_valid_select(self, engine):
        v = SQLValidator(engine)
        sql = v.validate("SELECT * FROM test_data")
        assert "SELECT" in sql

    def test_rejects_drop(self, engine):
        v = SQLValidator(engine)
        with pytest.raises(SQLValidationError):
            v.validate("DROP TABLE test_data")

    def test_rejects_delete(self, engine):
        v = SQLValidator(engine)
        with pytest.raises(SQLValidationError):
            v.validate("DELETE FROM test_data")

    def test_rejects_empty(self, engine):
        v = SQLValidator(engine)
        with pytest.raises(SQLValidationError):
            v.validate("")

    def test_rejects_nonexistent_table(self, engine):
        v = SQLValidator(engine)
        with pytest.raises(SQLValidationError, match="not found"):
            v.validate("SELECT * FROM does_not_exist")

    def test_adds_limit(self, engine):
        v = SQLValidator(engine)
        sql = v.validate("SELECT * FROM test_data")
        assert "LIMIT" in sql.upper()

    def test_preserves_existing_limit(self, engine):
        v = SQLValidator(engine)
        sql = v.validate("SELECT * FROM test_data LIMIT 5")
        assert "LIMIT 5" in sql

    def test_allows_with_cte(self, engine):
        v = SQLValidator(engine)
        sql = v.validate(
            "WITH cte AS (SELECT * FROM test_data) SELECT * FROM cte"
        )
        assert "WITH" in sql

    def test_is_safe(self, engine):
        v = SQLValidator(engine)
        safe, reason = v.is_safe("SELECT * FROM test_data")
        assert safe is True
        assert reason == ""

    def test_is_not_safe(self, engine):
        v = SQLValidator(engine)
        safe, reason = v.is_safe("DROP TABLE test_data")
        assert safe is False
        assert reason != ""
