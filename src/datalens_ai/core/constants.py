"""Constants used across DataLens AI."""

from __future__ import annotations

# Supported chart types
CHART_TYPES = [
    "bar", "horizontal_bar", "stacked_bar", "grouped_bar",
    "line", "area",
    "scatter", "bubble",
    "pie", "donut",
    "heatmap", "correlation_matrix",
    "histogram",
    "treemap", "sunburst",
    "table",
    "kpi",
    "box", "violin",
    "geo",
]

# Column data types
DTYPE_NUMERIC = "numeric"
DTYPE_CATEGORICAL = "categorical"
DTYPE_DATETIME = "datetime"
DTYPE_TEXT = "text"
DTYPE_BOOLEAN = "boolean"

# Semantic types
SEMANTIC_TYPES = [
    "currency", "percentage", "email", "url", "phone",
    "country", "city", "state", "zipcode",
    "id", "name", "date", "timestamp",
    "latitude", "longitude", "ip_address",
]

# Dangerous SQL keywords (blocked)
DANGEROUS_SQL_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE",
]

# Query limits
MAX_QUERY_ROWS = 10000

# Chart color palette
COLORS = [
    "#6366F1",  # Indigo
    "#8B5CF6",  # Violet
    "#EC4899",  # Pink
    "#F59E0B",  # Amber
    "#10B981",  # Emerald
    "#3B82F6",  # Blue
    "#EF4444",  # Red
    "#14B8A6",  # Teal
    "#F97316",  # Orange
    "#84CC16",  # Lime
]

# Cardinality thresholds
CARDINALITY_LOW = 8
CARDINALITY_MEDIUM = 30
CARDINALITY_HIGH = 100
