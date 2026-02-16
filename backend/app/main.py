"""FastAPI main application — CORS, middleware, routers, error handling."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.request_id import RequestIDMiddleware

# Configure structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=1.0 if settings.environment == "development" else 0.1,
        profiles_sample_rate=0.1 if settings.environment == "production" else 0,
        integrations=[FastApiIntegration()],
    )
    logger.info("Sentry error tracking initialized")
else:
    logger.warning("Sentry DSN not configured - error tracking disabled")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("Chess Alive API starting up (env=%s)", settings.environment)
    yield
    logger.info("Chess Alive API shutting down")


tags_metadata = [
    {
        "name": "games",
        "description": "Game management - create, join, view games and their state",
    },
    {
        "name": "game-actions",
        "description": "In-game actions - issue commands, persuade pieces, resign, draw",
    },
    {
        "name": "chat",
        "description": "Chat system - get history and send messages",
    },
    {
        "name": "ai",
        "description": "AI features - custom piece generation and game analysis",
    },
    {
        "name": "auth",
        "description": "Authentication - signup, login, profile management",
    },
    {
        "name": "health",
        "description": "Health and readiness checks for monitoring",
    },
]

app = FastAPI(
    title="Chess Alive API",
    description="""
    # Chess Alive API

    Chess with AI personalities — move command, persuasion, morale, and analysis.

    ## Key Features

    - **AI-Powered Pieces**: Pieces have personalities and can refuse orders
    - **Persuasion System**: Convince stubborn pieces with compelling arguments
    - **Real-time Updates**: Supabase Realtime for live game synchronization
    - **Morale Management**: Keep your army's spirits high
    - **King Taunts**: Your opponent's King talks trash

    ## Authentication

    Two authentication methods are supported:

    ### 1. Session-Based (Game Endpoints)
    Include the `X-Session-ID` header. A session ID will be auto-generated if not provided.

    ### 2. JWT Token (Auth Endpoints)
    Use `Authorization: Bearer {token}` for user authentication.

    ## Game Flow

    1. **Create Game**: `POST /api/v1/games` → Returns share code
    2. **Join Game**: `POST /api/v1/games/join-by-code` → Use share code
    3. **Issue Command**: `POST /api/v1/games/{id}/command` → Move pieces
    4. **Persuade**: `POST /api/v1/games/{id}/persuade` → If piece refuses

    ## Realtime Updates

    Subscribe to Supabase channels for live updates:
    - `game:{game_id}` - Game state changes
    - `chat:{game_id}` - Chat messages
    - `morale:{game_id}` - Morale updates

    ## Documentation

    - [API Documentation](/docs/api/API.md)
    - [Quick Start Guide](/docs/api/QUICKSTART.md)
    - [Postman Collection](/docs/api/chess-alive-api-postman-collection.json)

    ## Error Codes

    | Code | Description |
    |------|-------------|
    | `GAME_NOT_FOUND` | Game does not exist |
    | `INVALID_MOVE` | Move violates chess rules |
    | `NOT_YOUR_TURN` | Attempted move out of turn |
    | `PIECE_CAPTURED` | Piece is no longer on board |
    | `FORBIDDEN` | Not authorized to move this piece |

    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Chess Alive Team",
        "url": "https://github.com/yourusername/chess-alive",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
)

# ---------------------------------------------------------------------------
# Middleware (order matters: first added = outermost = runs first)
# ---------------------------------------------------------------------------

# 1. Request ID (for tracing)
app.add_middleware(RequestIDMiddleware)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Session-ID", "X-Request-ID"],
)

# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------
if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting enabled")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from app.routers import game, chat  # noqa: E402

app.include_router(game.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler for unhandled exceptions."""
    logger.error("Unhandled error: %s — %s", type(exc).__name__, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
    - Database connectivity (Supabase)
    - Redis connectivity (if configured)
    - Gemini API key configuration

    Returns 503 if any critical service is unhealthy.
    """
    checks: dict[str, Any] = {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {},
    }

    # Database check (Supabase)
    try:
        from app.db.supabase_store import store

        if await store.health_check():
            checks["checks"]["database"] = "ok"
        else:
            checks["checks"]["database"] = "error"
            checks["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = "error"
        checks["status"] = "degraded"

    # Redis check (if configured)
    if settings.rate_limit_redis_url:
        try:
            import redis

            r = redis.from_url(settings.rate_limit_redis_url, socket_connect_timeout=2)
            r.ping()
            checks["checks"]["redis"] = "ok"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            checks["checks"]["redis"] = "error"
            checks["status"] = "degraded"
    else:
        checks["checks"]["redis"] = "not_configured"

    # Gemini API check (non-blocking)
    checks["checks"]["gemini_api"] = "ok" if settings.google_gemini_api_key else "not_configured"

    # Status is always ok for now to prevent Cloud Run from killing the container
    checks["status"] = "ok"
    return JSONResponse(content=checks, status_code=200)


@app.get("/readiness", tags=["health"])
async def readiness_check():
    """
    Readiness check for Kubernetes/Cloud Run.

    Similar to health check but returns 503 if not ready to serve traffic.
    """
    try:
        from app.db.supabase_store import store

        if await store.health_check():
            return {"status": "ready"}
        return JSONResponse(
            content={"status": "not_ready", "reason": "database_unavailable"}, status_code=503
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(content={"status": "not_ready", "reason": str(e)}, status_code=503)


@app.get("/api/v1")
async def api_root():
    """API root — returns available endpoints."""
    return {
        "message": "Welcome to Chess Alive API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "games": "/api/v1/games",
            "chat": "/api/v1/games/{game_id}/chat",
            "ai": "/api/v1/ai",
        },
    }
