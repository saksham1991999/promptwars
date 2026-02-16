"""FastAPI main application — CORS, middleware, routers, error handling."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("PromptWars API starting up (env=%s)", settings.environment)
    yield
    logger.info("PromptWars API shutting down")


app = FastAPI(
    title="PromptWars API",
    description="Chess with AI personalities — move command, persuasion, morale, and analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0", "environment": settings.environment}


@app.get("/api/v1")
async def api_root():
    """API root — returns available endpoints."""
    return {
        "message": "Welcome to PromptWars API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "games": "/api/v1/games",
            "chat": "/api/v1/games/{game_id}/chat",
            "ai": "/api/v1/ai",
        },
    }
