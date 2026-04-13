# Contributing to DataLens AI

Thank you for your interest in contributing!

## Quick Start

```bash
git clone https://github.com/mekala27-45/datalens-ai.git
cd datalens-ai
pip install -e ".[all,dev,docs]"
```

## Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Run checks: `ruff check src/ tests/ && pytest tests/ -v`
5. Commit and push
6. Open a pull request

## Code Style

- Linter/Formatter: **ruff** (line length 99)
- Type hints on all public APIs
- Docstrings for public classes and functions

## Reporting Issues

Use the [GitHub issue templates](https://github.com/mekala27-45/datalens-ai/issues/new/choose).
