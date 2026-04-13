"""Tests for SQL utilities."""

from datalens_ai.utils.sql_utils import (
    add_limit,
    extract_table_names,
    format_sql,
    is_dangerous_sql,
)


class TestIsDangerousSQL:
    def test_select_is_safe(self):
        assert is_dangerous_sql("SELECT * FROM t") is False

    def test_drop_is_dangerous(self):
        assert is_dangerous_sql("DROP TABLE t") is True

    def test_delete_is_dangerous(self):
        assert is_dangerous_sql("DELETE FROM t") is True

    def test_insert_is_dangerous(self):
        assert is_dangerous_sql("INSERT INTO t VALUES (1)") is True

    def test_update_is_dangerous(self):
        assert is_dangerous_sql("UPDATE t SET x=1") is True

    def test_case_insensitive(self):
        assert is_dangerous_sql("drop table t") is True


class TestAddLimit:
    def test_adds_limit(self):
        result = add_limit("SELECT * FROM t", 100)
        assert "LIMIT 100" in result

    def test_preserves_existing_limit(self):
        sql = "SELECT * FROM t LIMIT 5"
        assert add_limit(sql, 100) == sql

    def test_strips_semicolons(self):
        result = add_limit("SELECT * FROM t;", 10)
        assert result.endswith("LIMIT 10")


class TestExtractTableNames:
    def test_single_table(self):
        tables = extract_table_names("SELECT * FROM orders")
        assert "orders" in tables

    def test_join(self):
        tables = extract_table_names(
            "SELECT * FROM orders JOIN customers ON orders.id = customers.id"
        )
        assert "orders" in tables
        assert "customers" in tables


class TestFormatSQL:
    def test_uppercase_keywords(self):
        result = format_sql("select * from t where x = 1")
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result
