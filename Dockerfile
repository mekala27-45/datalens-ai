FROM python:3.12-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (cache layer)
COPY pyproject.toml README.md ./
COPY src/datalens_ai/__init__.py src/datalens_ai/__init__.py
RUN pip install --no-cache-dir ".[streamlit]"

# Copy source code
COPY src/ src/
COPY app/ app/
COPY data/ data/
COPY .streamlit/ .streamlit/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# HuggingFace Spaces uses port 7860
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:7860/_stcore/health || exit 1

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
