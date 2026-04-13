# API Reference

## Core Models

### `DataProfile`
Complete statistical profile of a dataset.

```python
from datalens_ai.core.models import DataProfile

profile = DataProfile(
    table_name="orders",
    row_count=3000,
    column_count=10,
)
```

### `QueryResult`
Result of a natural language query.

```python
from datalens_ai.core.models import QueryResult

result = QueryResult(
    question="What is the total revenue?",
    sql_query="SELECT SUM(revenue) FROM orders",
    row_count=1,
    columns=["total"],
    data=[{"total": 150000}],
)
assert result.success  # True when error is None
```

### `ChartRecommendation`
Recommended visualization for a query result.

## Engine

### `DuckDBEngine`

```python
from datalens_ai.engine.duckdb_engine import DuckDBEngine

engine = DuckDBEngine()
engine.register_dataframe("orders", df)
result_df, exec_ms = engine.execute_sql("SELECT * FROM orders LIMIT 10")
```

## AI Providers

### `MockProvider`
Rule-based NL-to-SQL (no API key needed).

### `GeminiProvider`
Google Gemini-powered NL-to-SQL (free tier: 15 RPM).

```python
from datalens_ai.ai.gemini_provider import GeminiProvider

provider = GeminiProvider(api_key="your-key")
response = provider.nl_to_sql("total revenue", schema_string)
```

## Orchestrator

### `NLToSQLOrchestrator`

```python
from datalens_ai.ai.nl_to_sql import NLToSQLOrchestrator

orch = NLToSQLOrchestrator(engine, provider)
result = orch.process("What is the total revenue?", "orders")
```

## Visualization

### `create_chart`

```python
from datalens_ai.visualization.chart_factory import create_chart

fig = create_chart(df, chart_recommendation, title="Revenue by Category")
fig.show()
```

### `recommend_chart`

```python
from datalens_ai.visualization.chart_selector import recommend_chart

rec = recommend_chart(result_shape, hint="bar")
```
