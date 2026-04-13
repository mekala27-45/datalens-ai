"""Chart theming for consistent visual identity."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

from datalens_ai.core.constants import COLORS

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

DATALENS_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family=FONT_FAMILY, size=13, color="#374151"),
        title=dict(font=dict(size=18, color="#111827")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=COLORS,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            gridcolor="#F3F4F6",
            linecolor="#E5E7EB",
            zerolinecolor="#E5E7EB",
        ),
        yaxis=dict(
            gridcolor="#F3F4F6",
            linecolor="#E5E7EB",
            zerolinecolor="#E5E7EB",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=12),
        ),
    )
)

pio.templates["datalens"] = DATALENS_TEMPLATE
pio.templates.default = "plotly_white+datalens"


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the DataLens theme to a Plotly figure."""
    fig.update_layout(template="plotly_white+datalens")
    return fig
