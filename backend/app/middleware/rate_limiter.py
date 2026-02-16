"""Rate limiting middleware to prevent API abuse."""

from __future__ import annotations

import time
from collections import deque
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimiter:
    """Simple in-memory rate limiter tracking requests per endpoint per session."""

    def __init__(self):
        """Initialize the rate limiter with empty request tracking."""
        # key: f"{session_id}:{endpoint}" -> deque of timestamps
        self.requests: dict[str, deque[float]] = {}

    def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit.

        Args:
            key: Unique key for rate limiting (e.g., session_id:endpoint)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds

        # Get or create request queue for this key
        if key not in self.requests:
            self.requests[key] = deque()

        request_queue = self.requests[key]

        # Remove old requests outside the time window
        while request_queue and request_queue[0] < cutoff:
            request_queue.popleft()

        # Check if limit exceeded
        if len(request_queue) >= max_requests:
            # Calculate retry after time
            oldest_request = request_queue[0]
            retry_after = int(oldest_request + window_seconds - now) + 1
            return False, retry_after

        # Add current request
        request_queue.append(now)
        return True, 0

    def clear_old_entries(self, max_age_seconds: int = 3600):
        """
        Clean up old entries to prevent memory leaks.

        Args:
            max_age_seconds: Remove entries older than this (default 1 hour)
        """
        now = time.time()
        cutoff = now - max_age_seconds

        # Remove keys with only old timestamps
        keys_to_remove = []
        for key, queue in self.requests.items():
            # Remove old timestamps
            while queue and queue[0] < cutoff:
                queue.popleft()

            # Mark empty queues for removal
            if not queue:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.requests[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits on API endpoints."""

    # Rate limit configurations: {path_pattern: (max_requests, window_seconds)}
    RATE_LIMITS = {
        "/api/v1/games/.*/command": (30, 60),  # 30 requests per minute
        "/api/v1/games/.*/persuade": (30, 60),  # 30 requests per minute
        "/api/v1/games/.*/chat": (60, 60),  # 60 requests per minute
        "/api/v1/ai/": (10, 60),  # 10 requests per minute for AI endpoints
    }

    def __init__(self, app, limiter: InMemoryRateLimiter | None = None):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            limiter: Optional custom rate limiter (for testing)
        """
        super().__init__(app)
        self.limiter = limiter or InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response (429 if rate limited, otherwise normal response)
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Get session ID from header (or use IP as fallback)
        session_id = request.headers.get("x-session-id")
        if not session_id:
            # Fallback to IP address
            session_id = request.client.host if request.client else "unknown"

        # Find matching rate limit rule
        rate_limit = self._get_rate_limit(request.url.path)
        if not rate_limit:
            # No rate limit configured for this endpoint
            return await call_next(request)

        max_requests, window_seconds = rate_limit

        # Check rate limit
        key = f"{session_id}:{request.url.path}"
        is_allowed, retry_after = self.limiter.check_rate_limit(
            key, max_requests, window_seconds
        )

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Periodically clean up old entries (every ~100th request)
        if hash(key) % 100 == 0:
            self.limiter.clear_old_entries()

        return await call_next(request)

    def _get_rate_limit(self, path: str) -> tuple[int, int] | None:
        """
        Get rate limit configuration for a path.

        Args:
            path: Request path

        Returns:
            Tuple of (max_requests, window_seconds) or None if no limit
        """
        import re

        for pattern, limit in self.RATE_LIMITS.items():
            if re.search(pattern, path):
                return limit

        return None
