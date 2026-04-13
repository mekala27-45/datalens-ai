from __future__ import annotations

import io
from pathlib import Path

import duckdb
import pandas as pd

from datalens_ai.core.exceptions import IngestionError, UnsupportedFormatError

SUPPORTED_FORMATS = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".parquet", ".pq"}


def load_file(
    conn: duckdb.DuckDBPyConnection,
    file_path: str | Path,
    table_name: str | None = None,
) -> str:
    """Load a file into DuckDB and return the table name."""
    path = Path(file_path)
    if not path.exists():
        raise IngestionError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(
            f"Unsupported format: {suffix}. Supported: {SUPPORTED_FORMATS}"
        )

    if table_name is None:
        # Sanitize filename to valid table name
        table_name = path.stem.lower()
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
        if table_name[0].isdigit():
            table_name = f"t_{table_name}"

    if suffix in (".csv", ".tsv"):
        _load_csv(conn, path, table_name)
    elif suffix in (".xlsx", ".xls"):
        _load_excel(conn, path, table_name)
    elif suffix == ".json":
        _load_json(conn, path, table_name)
    elif suffix in (".parquet", ".pq"):
        _load_parquet(conn, path, table_name)

    return table_name


def load_from_bytes(
    conn: duckdb.DuckDBPyConnection,
    file_bytes: bytes,
    filename: str,
    table_name: str | None = None,
) -> str:
    """Load file from bytes (e.g., Streamlit UploadedFile) into DuckDB."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(f"Unsupported format: {suffix}")

    if table_name is None:
        stem = Path(filename).stem.lower()
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in stem)
        if table_name[0].isdigit():
            table_name = f"t_{table_name}"

    if suffix in (".csv", ".tsv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(io.BytesIO(file_bytes))
    elif suffix == ".json":
        df = pd.read_json(io.BytesIO(file_bytes))
    elif suffix in (".parquet", ".pq"):
        df = pd.read_parquet(io.BytesIO(file_bytes))
    else:
        raise UnsupportedFormatError(f"Unsupported format: {suffix}")

    conn.register(table_name, df)
    return table_name


def _load_csv(conn: duckdb.DuckDBPyConnection, path: Path, table_name: str) -> None:
    conn.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS "
        f"SELECT * FROM read_csv_auto('{path.as_posix()}')"
    )


def _load_excel(conn: duckdb.DuckDBPyConnection, path: Path, table_name: str) -> None:
    df = pd.read_excel(path)
    conn.register(table_name, df)


def _load_json(conn: duckdb.DuckDBPyConnection, path: Path, table_name: str) -> None:
    df = pd.read_json(path)
    conn.register(table_name, df)


def _load_parquet(
    conn: duckdb.DuckDBPyConnection, path: Path, table_name: str
) -> None:
    conn.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS "
        f"SELECT * FROM read_parquet('{path.as_posix()}')"
    )


def get_table_names(conn: duckdb.DuckDBPyConnection) -> list[str]:
    """Get all table names in the DuckDB connection."""
    result = conn.execute("SHOW TABLES").fetchall()
    return [row[0] for row in result]
