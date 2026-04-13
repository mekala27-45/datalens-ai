"""Token-bucket rate limiter."""

from __future__ import annotations

import threading
import time


class RateLimiter:
    """Token-bucket rate limiter for API calls."""

    def __init__(self, max_requests: int = 15, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.tokens = float(max_requests)
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Acquire a token, blocking if necessary."""
        with self._lock:
            self._refill()
            if self.tokens <= 0:
                sleep_time = self.window_seconds / self.max_requests
                time.sleep(sleep_time)
                self._refill()
            self.tokens -= 1

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * (self.max_requests / self.window_seconds)
        self.tokens = min(self.max_requests, self.tokens + new_tokens)
        self.last_refill = now
