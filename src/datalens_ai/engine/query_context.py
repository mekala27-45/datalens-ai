from __future__ import annotations

from collections import deque

from datalens_ai.core.models import ConversationTurn


class QueryContext:
    """Manages conversational context for follow-up queries."""

    def __init__(self, max_turns: int = 10):
        self._history: deque[ConversationTurn] = deque(maxlen=max_turns)

    def add_user_query(self, question: str) -> None:
        """Record a user question."""
        self._history.append(ConversationTurn(
            role="user",
            content=question,
        ))

    def add_assistant_response(self, response: str, sql_query: str | None = None) -> None:
        """Record an assistant response with optional SQL."""
        self._history.append(ConversationTurn(
            role="assistant",
            content=response,
            sql_query=sql_query,
        ))

    def get_history(self) -> list[ConversationTurn]:
        """Get the full conversation history."""
        return list(self._history)

    def get_context_string(self) -> str:
        """Build a context string for AI prompts."""
        if not self._history:
            return "No previous queries."

        lines = ["Previous conversation:"]
        for turn in self._history:
            if turn.role == "user":
                lines.append(f"User: {turn.content}")
            else:
                if turn.sql_query:
                    lines.append(f"SQL: {turn.sql_query}")
                lines.append(f"Assistant: {turn.content}")

        return "\n".join(lines)

    def get_last_sql(self) -> str | None:
        """Get the most recent SQL query."""
        for turn in reversed(self._history):
            if turn.sql_query:
                return turn.sql_query
        return None

    def has_context(self) -> bool:
        """Check if there's any conversation history."""
        return len(self._history) > 0

    def clear(self) -> None:
        """Clear the conversation history."""
        self._history.clear()
