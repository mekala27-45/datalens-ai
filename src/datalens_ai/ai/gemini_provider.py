"""Google Gemini Flash AI provider."""

from __future__ import annotations

import json
import os
import re

from datalens_ai.ai.base import BaseAIProvider
from datalens_ai.ai.prompt_templates import (
    INSIGHT_GENERATION,
    NL_TO_SQL_SYSTEM,
    QUESTION_SUGGESTION,
    SQL_EXPLANATION,
)
from datalens_ai.core.models import NLToSQLResponse
from datalens_ai.core.registry import register_provider
from datalens_ai.utils.rate_limiter import RateLimiter


@register_provider("gemini")
class GeminiProvider(BaseAIProvider):
    """Google Gemini Flash provider (free tier: 15 RPM)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        self._model_name = model
        self._api_key = os.getenv("GEMINI_API_KEY", "")
        self._rate_limiter = RateLimiter(max_requests=15)
        self._client = None

    @property
    def name(self) -> str:
        return "Gemini Flash"

    def is_available(self) -> bool:
        return bool(self._api_key)

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model_name)
            except ImportError:
                raise ImportError(
                    "google-generativeai is required. "
                    "Install with: pip install datalens-ai[gemini]"
                )
        return self._client

    def _call(self, prompt: str) -> str:
        self._rate_limiter.acquire()
        client = self._get_client()
        response = client.generate_content(prompt)
        return response.text

    def nl_to_sql(
        self, question: str, schema: str, context: str = ""
    ) -> NLToSQLResponse:
        prompt = NL_TO_SQL_SYSTEM.format(
            schema=schema,
            context=f"Conversation context:\n{context}" if context else "",
        ) + f"\nQuestion: {question}"

        raw = self._call(prompt)
        return self._parse_nl_to_sql(raw)

    def generate_insights(self, data_summary: str) -> list[str]:
        prompt = INSIGHT_GENERATION.format(data_summary=data_summary)
        raw = self._call(prompt)
        try:
            parsed = json.loads(self._extract_json(raw))
            if isinstance(parsed, list):
                return [str(i) for i in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
        return [line.strip("- ") for line in raw.strip().split("\n") if line.strip()]

    def explain_sql(self, sql: str, schema: str) -> str:
        prompt = SQL_EXPLANATION.format(sql=sql, schema=schema)
        return self._call(prompt).strip()

    def suggest_questions(self, schema: str) -> list[str]:
        prompt = QUESTION_SUGGESTION.format(schema=schema)
        raw = self._call(prompt)
        try:
            parsed = json.loads(self._extract_json(raw))
            if isinstance(parsed, list):
                return [str(q) for q in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
        return [line.strip("- ") for line in raw.strip().split("\n") if line.strip()][:8]

    def _parse_nl_to_sql(self, raw: str) -> NLToSQLResponse:
        try:
            data = json.loads(self._extract_json(raw))
            return NLToSQLResponse(
                sql=data.get("sql", ""),
                chart_hint=data.get("chart_hint"),
                explanation=data.get("explanation", ""),
                confidence=0.9,
            )
        except (json.JSONDecodeError, TypeError):
            sql_match = re.search(
                r"(SELECT\b.+?)(?:```|$)", raw, re.IGNORECASE | re.DOTALL
            )
            sql = sql_match.group(1).strip() if sql_match else raw.strip()
            return NLToSQLResponse(sql=sql, confidence=0.5)

    @staticmethod
    def _extract_json(text: str) -> str:
        json_match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            return brace_match.group(0)
        bracket_match = re.search(r"\[.*\]", text, re.DOTALL)
        if bracket_match:
            return bracket_match.group(0)
        return text
