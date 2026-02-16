"""PostHog analytics integration for product analytics and feature flags."""

from __future__ import annotations

import logging
from typing import Any

import posthog

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize PostHog if API key is configured
if settings.posthog_api_key:
    posthog.api_key = settings.posthog_api_key
    posthog.host = settings.posthog_host
    logger.info("PostHog analytics initialized")
else:
    logger.warning("PostHog API key not configured - analytics disabled")


def track_event(
    user_id: str,
    event: str,
    properties: dict[str, Any] | None = None,
) -> None:
    """
    Track an analytics event.

    Args:
        user_id: User or session identifier
        event: Event name (e.g., "game_created", "move_made")
        properties: Additional event properties

    Common events:
    - game_created: {game_mode, template}
    - move_made: {piece_type, is_risky, morale}
    - persuasion_attempted: {success, piece_type}
    - game_completed: {result, duration_seconds, moves_count}
    """
    if not settings.posthog_api_key:
        return

    try:
        posthog.capture(
            distinct_id=user_id,
            event=event,
            properties=properties or {},
        )
    except Exception as e:
        # Don't fail the request if analytics fails
        logger.warning(f"PostHog event tracking failed: {e}")


def identify_user(
    user_id: str,
    properties: dict[str, Any] | None = None,
) -> None:
    """
    Identify a user with properties.

    Args:
        user_id: User identifier
        properties: User properties (email, username, etc.)
    """
    if not settings.posthog_api_key:
        return

    try:
        posthog.identify(
            distinct_id=user_id,
            properties=properties or {},
        )
    except Exception as e:
        logger.warning(f"PostHog user identification failed: {e}")
