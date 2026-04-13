# Getting Started

## Installation

### From PyPI

```bash
pip install datalens-ai[streamlit]
```

### From Source

```bash
git clone https://github.com/mekala27-45/datalens-ai.git
cd datalens-ai
pip install -e ".[dev,streamlit]"
```

### With Docker

```bash
docker compose up --build
```

Then open [http://localhost:8501](http://localhost:8501).

## Running the App

### Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

### CLI

```bash
# Demo mode (no API keys)
datalens demo

# Explore a CSV file
datalens explore data.csv

# Ask a question
datalens query data.csv "What are the top 5 products by revenue?"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | *(none — uses MockProvider)* |
| `DATALENS_DEMO_MODE` | Force demo mode | `false` |

### Demo Mode

DataLens AI works without any API keys in demo mode. It uses a rule-based MockProvider that handles common query patterns (count, top N, average, trend, distribution, etc.).

To use AI-powered features, get a free [Google Gemini API key](https://aistudio.google.com/apikey) and set it:

```bash
export GEMINI_API_KEY=your-key-here
```
