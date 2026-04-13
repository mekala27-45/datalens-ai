from __future__ import annotations

import duckdb

from datalens_ai.core.models import DataProfile


class ColumnRelationship:
    """A discovered relationship between columns in different tables."""

    def __init__(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
        overlap_pct: float,
    ):
        self.source_table = source_table
        self.source_column = source_column
        self.target_table = target_table
        self.target_column = target_column
        self.overlap_pct = overlap_pct

    def __repr__(self) -> str:
        return (
            f"{self.source_table}.{self.source_column} -> "
            f"{self.target_table}.{self.target_column} "
            f"({self.overlap_pct:.0%} overlap)"
        )


def discover_relationships(
    conn: duckdb.DuckDBPyConnection,
    profiles: list[DataProfile],
) -> list[ColumnRelationship]:
    """Discover potential foreign key relationships between tables.

    Compares columns across every pair of profiled tables.  Only columns
    whose cardinality is ``"id"``, ``"low"``, or ``"medium"`` are
    considered, and both columns must share the same detected dtype.
    Value overlap is checked via DuckDB and pairs with more than 50%
    overlap are returned, sorted by overlap percentage descending.
    """
    relationships: list[ColumnRelationship] = []

    for i, profile_a in enumerate(profiles):
        for j, profile_b in enumerate(profiles):
            if i >= j:
                continue

            for col_a in profile_a.columns:
                if col_a.cardinality not in ("id", "low", "medium"):
                    continue

                for col_b in profile_b.columns:
                    if col_b.cardinality not in ("id", "low", "medium"):
                        continue
                    if col_a.dtype != col_b.dtype:
                        continue

                    # Name similarity check
                    if not _names_related(col_a.name, col_b.name):
                        continue

                    # Check value overlap via DuckDB
                    overlap = _check_overlap(
                        conn,
                        profile_a.table_name,
                        col_a.name,
                        profile_b.table_name,
                        col_b.name,
                    )

                    if overlap > 0.5:
                        relationships.append(
                            ColumnRelationship(
                                source_table=profile_a.table_name,
                                source_column=col_a.name,
                                target_table=profile_b.table_name,
                                target_column=col_b.name,
                                overlap_pct=overlap,
                            )
                        )

    return sorted(relationships, key=lambda r: r.overlap_pct, reverse=True)


def _names_related(name_a: str, name_b: str) -> bool:
    """Check if two column names might refer to the same entity."""
    a = name_a.lower().replace("_", "")
    b = name_b.lower().replace("_", "")

    # Exact match
    if a == b:
        return True

    # One is a prefix/suffix of the other with "id"
    if a.endswith("id") and b.endswith("id"):
        return a.replace("id", "") == b.replace("id", "") or a == b

    # One contains the other
    if a in b or b in a:
        return True

    return False


def _check_overlap(
    conn: duckdb.DuckDBPyConnection,
    table_a: str,
    col_a: str,
    table_b: str,
    col_b: str,
) -> float:
    """Check value overlap between two columns using DuckDB."""
    try:
        result = conn.execute(
            f"""
            SELECT
                COUNT(DISTINCT a.val) AS overlap_count,
                (SELECT COUNT(DISTINCT "{col_a}") FROM {table_a}) AS total_a
            FROM (
                SELECT DISTINCT CAST("{col_a}" AS VARCHAR) AS val FROM {table_a}
            ) a
            INNER JOIN (
                SELECT DISTINCT CAST("{col_b}" AS VARCHAR) AS val FROM {table_b}
            ) b ON a.val = b.val
        """
        ).fetchone()

        if result and result[1] > 0:
            return result[0] / result[1]
    except Exception:
        pass

    return 0.0
