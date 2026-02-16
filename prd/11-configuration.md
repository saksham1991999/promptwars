# 11. Configuration & Environment

[← Back to PRD Index](./readme.md) | [Previous: Deployment](./10-deployment.md) | [Next: Development Workflow →](./12-development-workflow.md)

---

## 11.1 Environment Variables

### Frontend (`.env`)

```bash
# Supabase
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Features
VITE_ENABLE_VOICE=true
VITE_ENABLE_CUSTOM_PIECES=true
VITE_ENABLE_GAME_REPLAYS=false  # Feature flag

# Monitoring
VITE_SENTRY_DSN=
```

### Backend (`.env`)

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Gemini 3 Flash
GOOGLE_GEMINI_API_KEY=AIza...

# Nano Banana Pro (Image Generation)
NANO_BANANA_API_KEY=nbp_...

# App
SECRET_KEY=randomly-generated-secret-key-at-least-32-chars
ALLOWED_ORIGINS=http://localhost:5173,https://chessalive.gg
ENVIRONMENT=development  # development | staging | production

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=  # Optional, in-memory if empty

# Google Cloud
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=asia-south1

# AI Controls
AI_MAX_CALLS_PER_MOVE=5
AI_MAX_CALLS_PER_GAME=200
AI_DAILY_GAME_LIMIT=50
AI_CACHE_TTL=300

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO
```

### `.env.example` (committed to git)

Both frontend and backend include a `.env.example` with all required variables, empty values, and documentation comments.

---

## 11.2 Backend Configuration (pydantic-settings)

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str

    # Google Gemini 3 Flash
    google_gemini_api_key: str

    # Nano Banana Pro (Image Generation)
    nano_banana_api_key: str

    # App
    secret_key: str
    allowed_origins: list[str] = Field(default=["http://localhost:5173"])
    environment: str = "development"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_redis_url: str | None = None

    # AI Controls
    ai_max_calls_per_move: int = 5
    ai_max_calls_per_game: int = 200
    ai_daily_game_limit: int = 50
    ai_cache_ttl: int = 300

    # Monitoring
    sentry_dsn: str | None = None
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## 11.3 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `tsconfig.json` | `/frontend/` | TypeScript strict mode, path aliases |
| `vite.config.ts` | `/frontend/` | Build config, proxy for dev API |
| `tailwind.config.js` | `/frontend/` | Design system tokens (colors, fonts, spacing) |
| `.eslintrc.js` | `/frontend/` | ESLint rules (TypeScript, React, accessibility) |
| `.prettierrc` | `/frontend/` | Code formatting (2-space indent, semicolons, trailing commas) |
| `pyproject.toml` | `/backend/` | Python deps, Black/Ruff config, pytest config |
| `requirements.txt` | `/backend/` | Pinned Python dependencies |
| `.env.example` | Both | Environment variable template |
| `.gitignore` | Root | Ignore `.env`, `node_modules`, `dist`, `__pycache__`, `.venv` |

### Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `VITE_ENABLE_VOICE` | `true` | Enable voice persuasion (Web Speech API) |
| `VITE_ENABLE_CUSTOM_PIECES` | `true` | Enable custom piece generation |
| `VITE_ENABLE_GAME_REPLAYS` | `false` | Enable game replay viewing (P2 feature) |
| `RATE_LIMIT_ENABLED` | `true` | Enable API rate limiting |

---

[← Back to PRD Index](./readme.md) | [Previous: Deployment](./10-deployment.md) | [Next: Development Workflow →](./12-development-workflow.md)
