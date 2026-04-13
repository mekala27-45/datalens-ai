# Asking Questions

## How It Works

1. Type your question in plain English
2. DataLens AI converts it to SQL using the AI provider
3. The SQL is validated and executed against DuckDB
4. Results are displayed with auto-generated charts and insights

## Example Questions

### Aggregations
- "What is the total revenue?"
- "What is the average salary by department?"
- "How many orders are there by category?"

### Rankings
- "What are the top 10 products by revenue?"
- "Which department has the lowest satisfaction?"

### Trends
- "How has revenue changed over time?"
- "What is the monthly trend of temperature?"

### Distributions
- "What is the distribution of salaries?"
- "Show me the spread of order amounts"

### Comparisons
- "Compare revenue across regions"
- "What is the total by category and region?"

## Tips

- **Be specific** — "top 5 products by revenue" works better than "best products"
- **Reference column names** — the AI can match column names mentioned in your question
- **Follow-up questions** — the system remembers previous queries for context
- **Click suggestions** — use the suggested question chips for quick queries

## How SQL Generation Works

### Mock Provider (Demo Mode)
Pattern-matching rules detect query intent (count, top N, average, trend, etc.) and generate appropriate SQL. No API key required.

### Gemini Provider
Uses Google's Gemini model to generate SQL from your question and the table schema. Falls back to MockProvider on failure.
