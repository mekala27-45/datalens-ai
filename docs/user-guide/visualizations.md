# Visualizations

## Auto Chart Selection

DataLens AI automatically picks the best chart type based on:

- **Data shape** — number of rows, columns, dimensions, measures
- **Query pattern** — single value, time series, ranking, distribution, etc.
- **AI hints** — the provider can suggest a chart type

## Supported Chart Types

| Chart | Best For |
|-------|----------|
| Bar | Category comparisons |
| Horizontal Bar | Rankings (top N) |
| Stacked Bar | Composition across categories |
| Grouped Bar | Multi-measure comparison |
| Line | Time series, trends |
| Area | Cumulative trends |
| Scatter | Correlations, relationships |
| Pie | Composition (< 8 categories) |
| Donut | Same as pie, with center hole |
| Heatmap | Two-dimensional comparisons |
| Histogram | Distributions |
| KPI Card | Single numeric values |
| Table | Raw data display |
| Box Plot | Statistical distributions |
| Violin | Distribution shape |
| Treemap | Hierarchical composition |

## Switching Chart Types

Each chart shows alternative chart type suggestions. Click an alternative to switch the visualization.

## Theme

All charts use a consistent dark theme with the DataLens AI color palette:

- Indigo, Violet, Pink, Amber, Emerald, Blue, Red, Teal, Orange, Lime
