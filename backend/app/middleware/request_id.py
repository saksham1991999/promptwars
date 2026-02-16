"""Request ID middleware — adds correlation IDs to all requests for tracing."""

from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request IDs for distributed tracing.

    Generates or accepts X-Request-ID header and includes it in:
    - request.state for access in route handlers
    - response headers for client correlation
    """

    async def dispatch(self, request: Request, call_next):
        """Add request ID to request and response."""
        # Get existing request ID or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for logging access
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
