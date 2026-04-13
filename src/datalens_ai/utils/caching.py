"""SQLite-backed response cache."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path


class ResponseCache:
    """Cache AI responses in SQLite for deduplication."""

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path.home() / ".datalens" / "cache.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS cache "
                "(key TEXT PRIMARY KEY, value TEXT, created_at REAL)"
            )

    @staticmethod
    def _make_key(question: str, schema: str) -> str:
        content = f"{question}|{schema}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, question: str, schema: str) -> dict | None:
        """Get a cached response."""
        key = self._make_key(question, schema)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM cache WHERE key = ?", (key,)
            ).fetchone()
        if row:
            return json.loads(row[0])
        return None

    def set(self, question: str, schema: str, value: dict) -> None:
        """Cache a response."""
        key = self._make_key(question, schema)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created_at) "
                "VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time()),
            )

    def clear(self) -> None:
        """Clear all cached entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
