"""Tests for text utilities."""

from datalens_ai.utils.text import (
    format_duration_ms,
    format_number,
    normalize_text,
    slugify,
    truncate,
)


class TestNormalizeText:
    def test_basic(self):
        assert normalize_text("  Hello   World  ") == "hello world"

    def test_empty(self):
        assert normalize_text("") == ""


class TestTruncate:
    def test_short_string(self):
        assert truncate("hello", 10) == "hello"

    def test_long_string(self):
        result = truncate("a" * 200, 100)
        assert len(result) == 100
        assert result.endswith("...")


class TestFormatNumber:
    def test_billions(self):
        assert format_number(2_500_000_000) == "2.50B"

    def test_millions(self):
        assert format_number(1_234_567) == "1.23M"

    def test_thousands(self):
        assert format_number(5_432) == "5.43K"

    def test_small(self):
        assert format_number(42.7) == "42.70"


class TestFormatDuration:
    def test_microseconds(self):
        assert "us" in format_duration_ms(0.5)

    def test_milliseconds(self):
        assert "ms" in format_duration_ms(123)

    def test_seconds(self):
        assert "s" in format_duration_ms(2500)


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World!") == "hello_world"

    def test_special_chars(self):
        assert slugify("test@foo#bar") == "testfoobar"
