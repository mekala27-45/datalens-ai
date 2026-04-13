"""Text utilities."""

from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Normalize whitespace and lowercase."""
    return re.sub(r"\s+", " ", text.strip().lower())


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_number(value: float, precision: int = 2) -> str:
    """Format large numbers with K/M/B suffix."""
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{precision}f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{precision}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.{precision}f}K"
    return f"{value:.{precision}f}"


def format_duration_ms(ms: float) -> str:
    """Format milliseconds to human-readable string."""
    if ms < 1:
        return f"{ms * 1000:.0f}us"
    if ms < 1000:
        return f"{ms:.1f}ms"
    return f"{ms / 1000:.2f}s"


def slugify(text: str) -> str:
    """Convert text to a URL/file-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "_", text)
