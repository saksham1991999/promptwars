"""Auth router — signup, login, profile management."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import get_current_user
from app.db import queries

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    email: str
    password: str
    username: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    avatar_url: str | None = None
    settings: dict | None = None


class ProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar_url: str | None = None
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    games_drawn: int = 0
    settings: dict = {}


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    user: ProfileResponse


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Register a new user with email and password."""
    try:
        from app.db.supabase_client import get_supabase_anon_client

        client = get_supabase_anon_client()
        metadata = {}
        if request.username:
            metadata["username"] = request.username

        result = client.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {"data": metadata},
        })

        if result.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "SIGNUP_FAILED", "message": "Failed to create account"},
            )

        # Get the profile  (created by trigger)
        profile = queries.get_profile(str(result.user.id))
        if not profile:
            profile = {
                "id": str(result.user.id),
                "username": request.username or f"player_{str(result.user.id)[:8]}",
                "email": request.email,
            }

        return AuthResponse(
            access_token=result.session.access_token if result.session else "",
            refresh_token=result.session.refresh_token if result.session else None,
            user=ProfileResponse(**profile),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Signup failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "SIGNUP_FAILED", "message": str(exc)},
        ) from exc


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        from app.db.supabase_client import get_supabase_anon_client

        client = get_supabase_anon_client()
        result = client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if result.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "UNAUTHORIZED", "message": "Invalid credentials"},
            )

        profile = queries.get_profile(str(result.user.id))
        if not profile:
            profile = {
                "id": str(result.user.id),
                "username": f"player_{str(result.user.id)[:8]}",
                "email": request.email,
            }

        return AuthResponse(
            access_token=result.session.access_token if result.session else "",
            refresh_token=result.session.refresh_token if result.session else None,
            user=ProfileResponse(**profile),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Login failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "UNAUTHORIZED", "message": "Invalid credentials"},
        ) from exc


@router.get("/me", response_model=ProfileResponse)
async def get_me(user: dict[str, Any] = Depends(get_current_user)):
    """Get the current user's profile."""
    profile = queries.get_profile(user["id"])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
        )
    return ProfileResponse(**profile)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user: dict[str, Any] = Depends(get_current_user),
):
    """Update the current user's profile."""
    update_data = request.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": "No fields to update"},
        )

    profile = queries.update_profile(user["id"], update_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
        )
    return ProfileResponse(**profile)
