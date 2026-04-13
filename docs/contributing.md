# Contributing

Contributions are welcome! Here's how to get started.

## Setup

```bash
git clone https://github.com/mekala27-45/datalens-ai.git
cd datalens-ai
pip install -e ".[all,dev,docs]"
```

## Development Workflow

1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run checks:
   ```bash
   ruff check src/ tests/
   pytest tests/ -v
   ```
4. Commit and push
5. Open a pull request

## Code Style

- **Formatter:** ruff (line length 99)
- **Type hints:** use them everywhere
- **Docstrings:** for public functions/classes

## Adding a New Chart Type

1. Add the builder function in `visualization/chart_factory.py`
2. Register it in the `builders` dict
3. Add selection logic in `visualization/chart_selector.py`
4. Add tests

## Adding a New AI Provider

1. Subclass `BaseAIProvider` in `ai/base.py`
2. Implement `nl_to_sql`, `generate_insights`, `explain_sql`, `suggest_questions`
3. Register with `@register_provider("name")`
4. Add to `config.py` provider list
