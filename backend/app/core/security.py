"""Security utilities: JWT verification and auth dependency injection."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict[str, Any]:
    """Verify JWT token and return user info.

    Uses Supabase service client to verify the JWT. Returns a dict with
    at minimum ``id`` and ``email`` keys.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "UNAUTHORIZED", "message": "Missing auth token"},
        )

    token = credentials.credentials

    try:
        # Import here to avoid circular imports
        from app.db.supabase_client import get_supabase_client

        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)

        if user_response is None or user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "UNAUTHORIZED", "message": "Invalid token"},
            )

        user = user_response.user
        return {
            "id": str(user.id),
            "email": user.email or "",
            "role": user.role or "authenticated",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Auth verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "UNAUTHORIZED", "message": "Token verification failed"},
        ) from exc


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict[str, Any] | None:
    """Like get_current_user but returns None for unauthenticated requests."""
    if credentials is None:
        return None
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None
