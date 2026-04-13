"""Generate statistical insights from query results."""

from __future__ import annotations

import pandas as pd

from datalens_ai.ai.base import BaseAIProvider
from datalens_ai.utils.text import format_number


def generate_insights(
    df: pd.DataFrame,
    question: str = "",
    provider: BaseAIProvider | None = None,
) -> list[str]:
    """Generate insights from a DataFrame."""
    if df.empty:
        return ["No data to analyze."]

    insights: list[str] = []

    # Try AI-based insights first
    if provider and provider.is_available():
        try:
            summary = _build_summary(df, question)
            ai_insights = provider.generate_insights(summary)
            if ai_insights:
                return ai_insights
        except Exception:
            pass

    # Rule-based insights
    insights.extend(_numeric_insights(df))
    insights.extend(_categorical_insights(df))
    insights.extend(_general_insights(df))

    return insights[:6] if insights else ["Data loaded successfully."]


def _build_summary(df: pd.DataFrame, question: str) -> str:
    lines = [f"Question: {question}"]
    lines.append(f"Result: {len(df)} rows, {len(df.columns)} columns")
    lines.append(f"Columns: {', '.join(df.columns)}")
    for col in df.select_dtypes(include="number").columns[:5]:
        lines.append(
            f"  {col}: min={df[col].min()}, max={df[col].max()}, "
            f"mean={df[col].mean():.2f}"
        )
    return "\n".join(lines)


def _numeric_insights(df: pd.DataFrame) -> list[str]:
    insights = []
    for col in df.select_dtypes(include="number").columns[:3]:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        max_val = series.max()
        min_val = series.min()
        mean_val = series.mean()

        if len(series) > 1:
            max_idx = series.idxmax()
            if len(df.columns) > 1:
                first_col = df.columns[0]
                label = df.loc[max_idx, first_col]
                insights.append(
                    f"Highest {col}: {format_number(max_val)} "
                    f"({label})"
                )

        if max_val > 0 and min_val > 0:
            ratio = max_val / min_val
            if ratio > 5:
                insights.append(
                    f"Large spread in {col}: highest is "
                    f"{ratio:.1f}x the lowest"
                )

        std = series.std()
        if std > 0 and std / abs(mean_val) > 0.5:
            insights.append(
                f"High variability in {col} "
                f"(CV: {std / abs(mean_val):.0%})"
            )

    return insights


def _categorical_insights(df: pd.DataFrame) -> list[str]:
    insights = []
    for col in df.select_dtypes(include="object").columns[:2]:
        vc = df[col].value_counts()
        if len(vc) > 0:
            top = vc.index[0]
            top_pct = vc.iloc[0] / len(df)
            if top_pct > 0.3:
                insights.append(
                    f"'{top}' dominates {col} "
                    f"({top_pct:.0%} of records)"
                )
    return insights


def _general_insights(df: pd.DataFrame) -> list[str]:
    insights = []
    if len(df) == 1:
        insights.append("Single result returned.")
    elif len(df) <= 5:
        insights.append(f"Compact result with {len(df)} rows.")
    return insights
