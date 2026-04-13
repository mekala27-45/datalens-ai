# CLI Reference

## Commands

### `datalens demo`

Run a demo with built-in sample datasets.

```bash
datalens demo
```

### `datalens explore`

Profile a data file and show statistics.

```bash
datalens explore data.csv
```

### `datalens query`

Ask a question about a data file.

```bash
datalens query data.csv "What are the top 5 products by revenue?"
```

Options:

| Flag | Description |
|------|-------------|
| `--provider` | AI provider to use (`mock`, `gemini`) |
| `--limit` | Max rows to return |

### `datalens list-providers`

Show available AI providers and their status.

```bash
datalens list-providers
```

### `datalens list-datasets`

Show built-in sample datasets.

```bash
datalens list-datasets
```
