"""CLI interface for DataLens AI."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option()
def main():
    """DataLens AI — Talk to your data."""


@main.command()
@click.argument("file_path")
def explore(file_path: str):
    """Profile a dataset and show statistics."""
    import duckdb

    from datalens_ai.ingestion.loader import load_file
    from datalens_ai.ingestion.profiler import profile_table
    from datalens_ai.ingestion.quality import score_quality

    conn = duckdb.connect(":memory:")
    table_name = load_file(conn, file_path)
    profile = profile_table(conn, table_name)
    quality, issues = score_quality(profile)
    profile.quality_score = quality
    profile.quality_issues = issues

    console.print(f"\n[bold]Dataset:[/bold] {table_name}")
    console.print(f"[bold]Rows:[/bold] {profile.row_count:,}")
    console.print(f"[bold]Columns:[/bold] {profile.column_count}")
    console.print(f"[bold]Quality Score:[/bold] {quality}/100\n")

    table = Table(title="Column Profiles")
    table.add_column("Column", style="cyan")
    table.add_column("Type")
    table.add_column("Nulls")
    table.add_column("Unique")
    table.add_column("Semantic")

    for col in profile.columns:
        table.add_row(
            col.name, col.dtype,
            f"{col.null_pct:.0%}", str(col.unique_count),
            col.semantic_type or "-",
        )

    console.print(table)

    if profile.suggested_questions:
        console.print("\n[bold]Suggested Questions:[/bold]")
        for q in profile.suggested_questions[:5]:
            console.print(f"  ? {q}")

    conn.close()


@main.command()
@click.argument("file_path")
@click.argument("question")
def query(file_path: str, question: str):
    """Run a natural language query against a dataset."""
    import duckdb

    from datalens_ai.ai.nl_to_sql import NLToSQLOrchestrator
    from datalens_ai.engine.duckdb_engine import DuckDBEngine
    from datalens_ai.ingestion.loader import load_file

    conn = duckdb.connect(":memory:")
    table_name = load_file(conn, file_path)

    engine = DuckDBEngine()
    df = conn.execute(f'SELECT * FROM "{table_name}"').fetchdf()
    engine.register_dataframe(table_name, df)

    orchestrator = NLToSQLOrchestrator(engine)
    result = orchestrator.process(question, table_name)

    if result.error:
        console.print(f"[red]Error:[/red] {result.error}")
        return

    console.print(f"\n[bold]Question:[/bold] {question}")
    console.print(f"[bold]SQL:[/bold] {result.sql_query}")
    console.print(f"[bold]Time:[/bold] {result.execution_time_ms:.1f}ms")
    console.print(f"[bold]Rows:[/bold] {result.row_count}\n")

    if result.data:
        import pandas as pd
        df_result = pd.DataFrame(result.data)
        console.print(df_result.to_string(index=False))

    conn.close()
    engine.close()


@main.command()
def demo():
    """Launch the Streamlit demo app."""
    import subprocess
    import sys
    from pathlib import Path

    app_path = Path(__file__).parent.parent.parent / "app" / "streamlit_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


@main.command(name="list-providers")
def list_providers():
    """List available AI providers."""
    from datalens_ai.core.config import get_available_providers

    table = Table(title="AI Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Available")
    table.add_column("Cost")

    for p in get_available_providers():
        icon = "[green]Yes[/green]" if p["available"] else "[red]No[/red]"
        table.add_row(p["name"], icon, p["cost"])

    console.print(table)


@main.command(name="list-datasets")
def list_datasets():
    """List available sample datasets."""
    from datalens_ai.ingestion.samples import list_sample_datasets

    datasets = list_sample_datasets()
    if not datasets:
        console.print("No sample datasets found.")
        return

    table = Table(title="Sample Datasets")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Rows")
    table.add_column("Files")

    for info in datasets.values():
        table.add_row(
            f"{info.icon} {info.display_name}",
            info.description,
            f"{info.row_count:,}",
            str(len(info.files)),
        )

    console.print(table)
