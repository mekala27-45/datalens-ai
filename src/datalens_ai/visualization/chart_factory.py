"""Create Plotly figures from data and chart recommendations."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from datalens_ai.core.constants import COLORS
from datalens_ai.core.models import ChartRecommendation
from datalens_ai.visualization.theme import apply_theme


def create_chart(
    df: pd.DataFrame,
    rec: ChartRecommendation,
    title: str = "",
) -> go.Figure:
    """Create a Plotly figure based on chart recommendation."""
    ct = rec.chart_type
    x = rec.x_column
    y = rec.y_column
    color = rec.color_column

    # Validate columns exist
    cols = set(df.columns)
    if x and x not in cols:
        x = df.columns[0] if len(df.columns) > 0 else None
    if y and y not in cols:
        y = df.columns[-1] if len(df.columns) > 1 else None

    builders = {
        "bar": _bar,
        "horizontal_bar": _horizontal_bar,
        "stacked_bar": _stacked_bar,
        "grouped_bar": _grouped_bar,
        "line": _line,
        "area": _area,
        "scatter": _scatter,
        "bubble": _scatter,
        "pie": _pie,
        "donut": _donut,
        "heatmap": _heatmap,
        "correlation_matrix": _heatmap,
        "histogram": _histogram,
        "kpi": _kpi,
        "table": _table,
        "box": _box,
        "violin": _violin,
        "treemap": _treemap,
    }

    builder = builders.get(ct, _bar)
    fig = builder(df, x, y, color, title)
    return apply_theme(fig)


def _bar(df, x, y, color, title):
    if x and y:
        return px.bar(
            df, x=x, y=y, color=color, title=title,
            color_discrete_sequence=COLORS,
        )
    return px.bar(df, title=title, color_discrete_sequence=COLORS)


def _horizontal_bar(df, x, y, color, title):
    if x and y:
        return px.bar(
            df, x=y, y=x, color=color, title=title,
            orientation="h", color_discrete_sequence=COLORS,
        )
    return px.bar(df, title=title, orientation="h",
                  color_discrete_sequence=COLORS)


def _stacked_bar(df, x, y, color, title):
    if x and y:
        return px.bar(
            df, x=x, y=y, color=color, title=title,
            barmode="stack", color_discrete_sequence=COLORS,
        )
    return px.bar(df, title=title, barmode="stack",
                  color_discrete_sequence=COLORS)


def _grouped_bar(df, x, y, color, title):
    if x and y:
        return px.bar(
            df, x=x, y=y, color=color, title=title,
            barmode="group", color_discrete_sequence=COLORS,
        )
    return px.bar(df, title=title, barmode="group",
                  color_discrete_sequence=COLORS)


def _line(df, x, y, color, title):
    if x and y:
        return px.line(
            df, x=x, y=y, color=color, title=title,
            color_discrete_sequence=COLORS, markers=True,
        )
    return px.line(df, title=title, color_discrete_sequence=COLORS)


def _area(df, x, y, color, title):
    if x and y:
        return px.area(
            df, x=x, y=y, color=color, title=title,
            color_discrete_sequence=COLORS,
        )
    return px.area(df, title=title, color_discrete_sequence=COLORS)


def _scatter(df, x, y, color, title):
    if x and y:
        return px.scatter(
            df, x=x, y=y, color=color, title=title,
            color_discrete_sequence=COLORS,
        )
    cols = df.select_dtypes(include="number").columns
    if len(cols) >= 2:
        return px.scatter(
            df, x=cols[0], y=cols[1], title=title,
            color_discrete_sequence=COLORS,
        )
    return px.scatter(df, title=title, color_discrete_sequence=COLORS)


def _pie(df, x, y, color, title):
    names = x or (df.columns[0] if len(df.columns) > 0 else None)
    values = y or (df.columns[-1] if len(df.columns) > 1 else None)
    if names and values:
        return px.pie(
            df, names=names, values=values, title=title,
            color_discrete_sequence=COLORS,
        )
    return px.pie(df, title=title, color_discrete_sequence=COLORS)


def _donut(df, x, y, color, title):
    fig = _pie(df, x, y, color, title)
    fig.update_traces(hole=0.4)
    return fig


def _heatmap(df, x, y, color, title):
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        return px.imshow(
            corr, title=title or "Correlation Matrix",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            text_auto=".2f",
        )
    if x and y and color:
        pivot = df.pivot_table(index=x, columns=y, values=color)
        return px.imshow(pivot, title=title)
    return _table(df, x, y, color, title)


def _histogram(df, x, y, color, title):
    col = y or x or df.select_dtypes(include="number").columns[0]
    return px.histogram(
        df, x=col, title=title, nbins=30,
        color_discrete_sequence=COLORS,
    )


def _kpi(df, x, y, color, title):
    """Create a KPI card using a Plotly indicator."""
    value = None
    label = title or "Value"

    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        value = df[num_cols[0]].iloc[0] if len(df) > 0 else 0
        label = num_cols[0]

    fig = go.Figure(go.Indicator(
        mode="number",
        value=value,
        title={"text": label},
        number={"font": {"size": 48, "color": COLORS[0]}},
    ))
    fig.update_layout(height=200)
    return fig


def _table(df, x, y, color, title):
    fig = go.Figure(go.Table(
        header=dict(
            values=list(df.columns),
            fill_color=COLORS[0],
            font=dict(color="white", size=13),
            align="left",
        ),
        cells=dict(
            values=[df[col].tolist() for col in df.columns],
            fill_color=[["#F9FAFB", "#FFFFFF"] * (len(df) // 2 + 1)],
            align="left",
            font=dict(size=12),
        ),
    ))
    fig.update_layout(title=title)
    return fig


def _box(df, x, y, color, title):
    col = y or x or df.select_dtypes(include="number").columns[0]
    return px.box(df, y=col, x=x if x != col else None,
                  title=title, color_discrete_sequence=COLORS)


def _violin(df, x, y, color, title):
    col = y or x or df.select_dtypes(include="number").columns[0]
    return px.violin(df, y=col, x=x if x != col else None,
                     title=title, color_discrete_sequence=COLORS)


def _treemap(df, x, y, color, title):
    names = x or df.columns[0]
    values = y or (df.columns[-1] if len(df.columns) > 1 else df.columns[0])
    return px.treemap(
        df, path=[names], values=values, title=title,
        color_discrete_sequence=COLORS,
    )
