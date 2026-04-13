"""Export query results to CSV."""

from __future__ import annotations

import csv
import io

from datalens_ai.core.models import QueryResult


def results_to_csv(results: list[QueryResult]) -> str:
    """Export query results to CSV string.

    Each row includes the question, SQL, and data columns.
    """
    if not results:
        return ""

    buffer = io.StringIO()

    # Collect all unique data columns across results
    all_data_cols: list[str] = []
    for r in results:
        for c in r.columns:
            if c not in all_data_cols:
                all_data_cols.append(c)

    header = ["question", "sql_query", "row_index"] + all_data_cols
    writer = csv.DictWriter(buffer, fieldnames=header)
    writer.writeheader()

    for result in results:
        for idx, row in enumerate(result.data[:1000]):
            out_row: dict[str, str] = {
                "question": result.question if idx == 0 else "",
                "sql_query": result.sql_query if idx == 0 else "",
                "row_index": str(idx),
            }
            for col in all_data_cols:
                out_row[col] = str(row.get(col, ""))
            writer.writerow(out_row)

    return buffer.getvalue()


def result_to_csv(result: QueryResult) -> str:
    """Export a single QueryResult to CSV."""
    return results_to_csv([result])
