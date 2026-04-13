"""Rule-based chart type recommendation engine."""

from __future__ import annotations

from datalens_ai.core.constants import CARDINALITY_LOW
from datalens_ai.core.models import ChartRecommendation, ResultShape


def recommend_chart(shape: ResultShape, hint: str | None = None) -> ChartRecommendation:
    """Recommend the best chart type based on result shape."""
    if hint and hint in (
        "bar", "horizontal_bar", "line", "scatter", "pie",
        "heatmap", "histogram", "kpi", "table", "donut",
        "area", "box", "treemap",
    ):
        return ChartRecommendation(
            chart_type=hint,
            x_column=_pick_x(shape),
            y_column=_pick_y(shape),
            color_column=_pick_color(shape),
            reasoning=f"Chart type '{hint}' was suggested by the AI provider.",
            alternatives=_get_alternatives(hint),
        )

    chart_type, reasoning = _decide(shape)
    return ChartRecommendation(
        chart_type=chart_type,
        x_column=_pick_x(shape),
        y_column=_pick_y(shape),
        color_column=_pick_color(shape),
        reasoning=reasoning,
        alternatives=_get_alternatives(chart_type),
    )


def _decide(shape: ResultShape) -> tuple[str, str]:
    p = shape.pattern
    nd = len(shape.dimensions)
    nm = len(shape.measures)
    nt = len(shape.temporals)

    if p == "single_value":
        return "kpi", "Single numeric result displayed as a KPI card."

    if p == "time_series":
        if nd >= 1:
            return "line", "Time series with categories shown as multi-line chart."
        return "line", "Time series data is best shown as a line chart."

    if p == "ranking":
        return "horizontal_bar", "Ranking data shown as a horizontal bar chart."

    if p == "composition":
        if shape.row_count <= CARDINALITY_LOW:
            return "pie", "Low-cardinality composition shown as a pie chart."
        return "bar", "Composition with many categories shown as a bar chart."

    if p == "distribution":
        return "histogram", "Numeric distribution shown as a histogram."

    if p == "correlation":
        return "scatter", "Two numeric variables shown as a scatter plot."

    if p == "comparison":
        if nt >= 1:
            return "line", "Comparison over time shown as a multi-line chart."
        if nd == 2 and nm == 1:
            return "heatmap", "Two dimensions with one measure as a heatmap."
        return "grouped_bar", "Multi-measure comparison as a grouped bar chart."

    # Fallback
    if shape.row_count <= 50:
        return "table", "Data displayed as a table."
    return "bar", "Default chart type for this data shape."


def _pick_x(shape: ResultShape) -> str | None:
    if shape.temporals:
        return shape.temporals[0]
    if shape.dimensions:
        return shape.dimensions[0]
    if shape.measures:
        return shape.measures[0]
    return None


def _pick_y(shape: ResultShape) -> str | None:
    if shape.measures:
        return shape.measures[0]
    return None


def _pick_color(shape: ResultShape) -> str | None:
    if len(shape.dimensions) >= 2:
        return shape.dimensions[1]
    if shape.dimensions and shape.temporals:
        return shape.dimensions[0]
    return None


def _get_alternatives(chart_type: str) -> list[str]:
    alts = {
        "bar": ["horizontal_bar", "pie", "table"],
        "horizontal_bar": ["bar", "table", "pie"],
        "line": ["area", "bar", "scatter"],
        "scatter": ["line", "bubble", "heatmap"],
        "pie": ["donut", "bar", "treemap"],
        "donut": ["pie", "bar", "treemap"],
        "heatmap": ["bar", "table", "treemap"],
        "histogram": ["box", "violin", "table"],
        "kpi": ["table", "bar"],
        "table": ["bar", "horizontal_bar"],
        "area": ["line", "bar"],
        "box": ["histogram", "violin"],
        "treemap": ["pie", "bar"],
        "grouped_bar": ["stacked_bar", "line", "table"],
    }
    return alts.get(chart_type, ["bar", "table"])
