.PHONY: install install-dev test lint format type-check clean docs-serve docker-build docker-run

install:
	pip install -e ".[streamlit]"

install-dev:
	pip install -e ".[all,dev,docs]"

test:
	pytest --cov=datalens_ai --cov-report=term-missing

lint:
	ruff check src/ tests/ app/

format:
	ruff format src/ tests/ app/
	ruff check --fix src/ tests/ app/

type-check:
	mypy src/datalens_ai/

clean:
	rm -rf dist/ build/ *.egg-info .ruff_cache .mypy_cache .pytest_cache htmlcov site/
	find . -type d -name __pycache__ -exec rm -rf {} +

docs-serve:
	mkdocs serve

docker-build:
	docker build -t datalens-ai .

docker-run:
	docker run -p 8501:7860 datalens-ai
