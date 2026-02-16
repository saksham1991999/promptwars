# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Chess Alive** is a psychological warfare chess game where pieces have personalities, morale, and the ability to refuse orders. Players command their pieces through a group chat interface and must persuade disobedient pieces to follow risky moves.

**Core Mechanic:** Chess + personality management + persuasion + AI commentary. Pieces can refuse dangerous moves based on their morale (0-100) and personality archetypes.

## Architecture

This is a **full-stack application** with:

- **Frontend:** React 19 + TypeScript + Vite (port 5173)
- **Backend:** FastAPI (Python) + Uvicorn (port 8000)
- **Database:** Supabase (PostgreSQL) with Realtime for live game updates
- **AI:** Pydantic AI + Google Gemini 3 Flash for piece personalities, analysis, and persuasion evaluation

### Key Architectural Patterns

1. **Realtime-First:** All game state changes flow through Supabase Realtime channels for instant synchronization between players
2. **Stateless Backend:** FastAPI is fully stateless; all game state lives in PostgreSQL
3. **Dual Chess Engines:**
   - `chess.js` on frontend for immediate move validation and optimistic UI updates
   - `python-chess` on backend as the authoritative source of truth
4. **AI as a Service:** All AI interactions centralized through `gemini_service.py` with fallback templates when API is unavailable
5. **Morale System:** Each piece has a morale score (0-100) that determines willingness to obey commands
6. **Persuasion Engine:** When pieces refuse, players can argue their case; AI evaluates argument quality, personality fit, and board accuracy

## Development Commands

### Backend (Python/FastAPI)

**Important:** All commands must be run from the `backend/` directory with the virtual environment activated. The backend uses absolute imports (e.g., `from app.core.config import settings`) so Python needs to find the `app` package in the current directory.

```bash
cd backend

# Setup environment (one-time)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env  # Edit with your API keys

# Run development server (must be in backend/ directory with venv activated)
cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000

# Alternative: separate commands
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000

# Testing (run from backend/ with venv activated)
pytest                          # Run all tests
pytest -m unit                  # Unit tests only
pytest -m integration           # Integration tests only
pytest tests/unit/test_chess_engine.py  # Single test file
pytest -v --cov --cov-report=html  # With coverage HTML report

# Code quality (run from backend/ with venv activated)
ruff check .                    # Lint
ruff check . --fix              # Auto-fix linting issues
black .                         # Format code
mypy app                        # Type checking
```

### Frontend (React/TypeScript)

```bash
cd frontend

# Setup
npm install
cp .env.example .env  # Edit with Supabase keys

# Development
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Production build (outputs to dist/)
npm run preview      # Preview production build

# Code quality
npm run lint         # ESLint check
```

## Critical Services & Their Roles

### Backend Services (`backend/app/services/`)

**`gemini_service.py`** — The AI orchestrator
- Manages 5 Pydantic AI agents (piece response, analysis, persuasion, taunts, custom pieces)
- Uses Google Gemini 3 Flash as the LLM backend
- Implements fallback templates when API is unavailable or rate-limited
- Includes TTL caching for analysis (5min) and taunts (30min)

**`chess_engine.py`** — Chess logic wrapper
- Wraps `python-chess` library
- Validates move legality
- Calculates board state (FEN), material balance, threats
- Determines if moves are "risky" (puts piece in danger)

**`morale_calculator.py`** — Morale update logic
- Increases morale: successful captures (+15), protected moves (+5), winning position (+10)
- Decreases morale: being threatened (-10), sacrificed allies (-20), bad positioning (-5)
- Events trigger morale changes across all affected pieces

**`persuasion_engine.py`** — Persuasion evaluation
- Combines logic score (0-40), personality match (0-30), morale bonus (0-30)
- Validates player claims against actual board state
- Different personality types respond to different arguments (Knights like "glory", Bishops like "logic")

**`king_taunts.py`** — Opponent King trash talk
- Generates contextual taunts based on game events (check, blunder, piece captured)
- Rate-limited to avoid spam (max 1 every 3 moves)

### Frontend Architecture (`frontend/src/`)

**Pages:**
- `HomePage.tsx` — Landing page, game creation
- `LobbyPage.tsx` — Pre-game setup, waiting room
- `GamePage.tsx` — Main game view (board + chat + morale tracker)
- `JoinPage.tsx` — Join existing game via invite code

**Key Components:**
- `ChessBoard.tsx` — Board rendering, piece dragging, move highlighting (uses chess.js)
- `ChatInterface.tsx` — Group chat with @-mentions for pieces, message types (player/piece/AI/King)
- `MoraleTracker.tsx` — Visual display of all 16 pieces' morale bars
- `PersuasionModal.tsx` — Modal for arguing with pieces that refuse orders

**State Management:**
- Auth state via Supabase Auth
- Game state via Supabase Realtime subscriptions
- No global state management library (Redux/Zustand) — kept simple with React hooks

## Game Flow: Move Execution

1. Player types `@Knight move to f3` in chat
2. Frontend validates with `chess.js`, sends to `/api/v1/games/{id}/command`
3. Backend:
   - Validates legality with `python-chess`
   - Fetches piece morale & personality from DB
   - Calls Gemini API to generate piece response (will_move: true/false)
   - If accepted: executes move, updates board state, broadcasts via Supabase Realtime
   - If refused: sends refusal message, triggers persuasion modal on frontend
   - Calls Gemini for move analysis (quality, eval, threats)
   - Optionally generates King taunt
4. Frontend receives updates via Realtime, animates board, displays chat messages

## Persuasion Flow

1. Piece refuses dangerous move
2. Frontend shows persuasion modal
3. Player types/speaks argument
4. Backend sends to `/api/v1/games/{id}/persuade`
5. `persuasion_engine.py` evaluates:
   - Logic score: Are the player's claims accurate? (checks board state)
   - Personality match: Does argument appeal to this piece type?
   - Morale modifier: Lower morale = harder to convince
6. Gemini provides final evaluation with reasoning
7. If successful: move executes with morale penalty; if failed: piece stands firm

## Environment Variables

### Backend (`backend/.env`)
- `SUPABASE_URL`, `SUPABASE_SECRET_KEY` — Database & auth
- `GOOGLE_GEMINI_API_KEY` — Required for AI features via Google GenAI (has fallbacks)
- `NANO_BANANA_API_KEY` — Optional, for custom piece image generation via Nano Banana Pro API
- `SECRET_KEY` — JWT signing (must be 32+ chars in production)
- `ALLOWED_ORIGINS` — CORS whitelist (e.g., `["http://localhost:5173"]`)
- `ENVIRONMENT` — `development` | `staging` | `production`
- `REDIS_URL` — Google Memorystore Redis connection string
- `SENTRY_DSN` — Error tracking (Cloud Error Reporting alternative)
- `POSTHOG_KEY` — Product analytics

### Frontend (`frontend/.env`)
- `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` — Supabase client init

## Database Schema Highlights

**Key Tables:**
- `games` — Game state (FEN, turn, status, player IDs)
- `game_pieces` — Each piece's morale, personality config, custom traits
- `game_moves` — Move history with SAN notation
- `chat_messages` — In-game chat (player messages, piece responses, AI analysis, taunts)
- `persuasion_attempts` — Logged persuasion attempts with success/failure
- `morale_events` — Audit log of morale changes with reasons

**Migrations:** Located in `supabase/migrations/` (001-010), apply with `supabase db push`

## Testing Strategy

### Backend Tests (`backend/tests/`)
- **Unit tests:** `tests/unit/test_chess_engine.py` — Chess logic validation
- **Markers:** Use pytest markers: `-m unit`, `-m integration`, `-m api`
- **Coverage:** Minimum 75% required (configured in `pytest.ini`)
- **Async:** Tests use `pytest-asyncio` with `asyncio_mode = auto`

### Frontend Tests
- Not yet implemented (no test infrastructure in place)

## Important Conventions

### Python (Backend)
- Type hints mandatory on all function signatures
- Async (`async def`) for all I/O-bound operations
- Pydantic models for all API request/response validation
- Google-style docstrings for public functions
- No bare `except:` — always catch specific exceptions
- File names: `snake_case.py`

### TypeScript (Frontend)
- Strict mode enabled (`tsconfig.json`)
- No `any` types (use `unknown` + type guards)
- Props with explicit types (not `React.FC<Props>` due to children issues)
- Named exports preferred over default exports (except pages)
- File names: `PascalCase.tsx` for components, `kebab-case.ts` for utilities

### Git Workflow
- Conventional commits: `feat(scope): description` | `fix(scope): description`
- Branch naming: `feature/description`, `fix/description`
- Main branch: `main` (protected)
- CI runs tests on all PRs (GitHub Actions: `.github/workflows/ci.yml`)

## AI Integration Notes

### Rate Limiting & Costs
- **Per-move budget:** Max 5 AI calls (piece response, analysis, taunt, morale dialogues)
- **Per-game cap:** 200 AI calls max
- **Daily limit:** 50 games/user/day
- **Fallbacks:** Pre-written templates in `FALLBACK_RESPONSES` dict when API unavailable

### Pydantic AI Agents
All agents use `gemini-3-flash` model (fast, cheap, capable):
1. **Piece Response Agent** — Determines if piece obeys + generates dialogue
2. **Analysis Agent** — Move quality scoring + commentary
3. **Persuasion Agent** — Evaluates player arguments
4. **Taunt Generator** — Opponent King trash talk
5. **Custom Piece Creator** — Generates themed personalities from user prompts

### Temperature Settings
- Piece Response: 0.8 (creative dialogue)
- Analysis: 0.3 (factual consistency)
- Persuasion: 0.5 (balanced)
- Taunt Generator: 0.9 (maximum variety)

## Common Gotchas

1. **Two Chess Engines:** Frontend uses `chess.js`, backend uses `python-chess`. Backend is authoritative.
2. **Morale Bounds:** Always clamp morale between 0-100 when updating
3. **Realtime Sync:** Game state updates must be broadcast via Supabase Realtime channels, not just saved to DB
4. **AI Fallbacks:** Always implement fallback responses; Gemini API may fail or rate-limit
5. **Persuasion Validation:** Player claims must be validated against actual board state before evaluation
6. **FEN Notation:** Game state is stored as FEN strings; use chess engines to parse

## Supabase Local Development

```bash
# Requires Docker
supabase start           # Start local Supabase (ports 54321-54323)
supabase db reset        # Apply all migrations from scratch
supabase db push         # Apply new migrations only
supabase status          # Check running services
supabase stop            # Stop local instance
```

## Deployment

- **Frontend:** Google Cloud Run (Docker container with nginx)
- **Backend:** Google Cloud Run (Docker container with Uvicorn)
- **Database:** Supabase hosted (production instance)

## Google Cloud Integration

Chess Alive runs entirely on Google Cloud Platform, leveraging multiple services for scalability, security, and AI capabilities.

### Services Used

1. **Google Gemini 3 Flash** — Primary LLM for all AI features
   - 5 specialized Pydantic AI agents for different tasks
   - Location: `backend/app/services/gemini_service.py`
   - Model ID: `google-gla:gemini-3-flash`
   - Temperature settings: 0.3 (analysis) to 0.9 (taunts)

2. **Google Cloud Run** — Serverless container hosting
   - Backend service: `chess-alive-backend` (1-10 instances, 1Gi memory)
   - Frontend service: `chess-alive-frontend` (1-20 instances, nginx static serving)
   - Region: `us-central1`
   - Features: Auto-scaling, CPU throttling, startup CPU boost
   - Timeout: 300s (backend), 60s (frontend)

3. **Google Container Registry (GCR)** — Docker image storage
   - Image path: `gcr.io/{PROJECT_ID}/chess-alive-{service}:{tag}`
   - Integrated with Cloud Build and GitHub Actions
   - Automatic vulnerability scanning available

4. **Google Secret Manager** — Secure credential storage
   - `chess-alive-gemini-key` — Gemini API key
   - `chess-alive-supabase-url` — Database URL
   - `chess-alive-supabase-secret` — Service role key
   - `chess-alive-secret-key` — JWT signing key
   - `chess-alive-redis-url` — Redis connection string
   - `chess-alive-sentry-dsn` — Error tracking
   - Mounted as environment variables in Cloud Run

5. **Google Memorystore for Redis** — Caching and rate limiting
   - Used by: `backend/app/middleware/rate_limiter.py`
   - Tier: Basic, Redis 7.0
   - Purpose: Rate limiting, session storage, move deduplication

6. **Google Cloud SDK & CLI** — Deployment tooling
   - Service account: `chess-alive-sa@{PROJECT}.iam.gserviceaccount.com`
   - IAM roles: Secret Manager Secret Accessor, Cloud Run Developer
   - CI/CD: GitHub Actions with workload identity federation

7. **Google Cloud Storage** — Asset and replay storage
   - Custom piece images generated via Nano Banana Pro
   - Game replay files (PGN/FEN history)
   - User-generated content and avatars
   - CORS-enabled for direct frontend access

8. **Cloud Monitoring** — Metrics and observability
   - Custom dashboards for game metrics (active games, AI usage)
   - Alerting policies for error rates and latency
   - Uptime checks for health monitoring
   - Custom metrics for morale events and persuasion attempts

9. **Cloud Logging** — Centralized log management
   - Structured JSON logs from all Cloud Run services
   - Log-based metrics for business events
   - Log sinks for long-term archival
   - Integration with Cloud Trace for request correlation

10. **Cloud Trace** — Distributed tracing
    - Request latency analysis across services
    - AI API call performance tracking
    - Database query performance insights
    - End-to-end request flow visualization

11. **Cloud Error Reporting** — Error aggregation
    - Automatic grouping of similar errors
    - Error notifications via email/SMS
    - Integration with Cloud Logging for context
    - Error trend analysis and reporting

12. **Speech-to-Text API** — Voice command processing
    - Real-time speech recognition for persuasion arguments
    - Multi-language support (future roadmap)
    - Premium accuracy for tactical move descriptions
    - Streaming recognition for continuous voice input

### Deployment Architecture

```
GitHub Repo
    ↓ (GitHub Actions)
Docker Build → GCR
    ↓
Cloud Run Deploy (backend + frontend)
    ↓
Secret Manager (runtime secrets)
    ↓
Memorystore Redis (caching)
    ↓
Cloud Storage (assets, replays)
    ↓
Cloud Monitoring/Logging/Trace (observability)
```

### Configuration Files

- `backend/cloudrun.yaml` — Backend service definition
- `frontend/cloudrun.yaml` — Frontend service definition
- `.github/workflows/deploy.yml` — CI/CD pipeline
- `backend/Dockerfile` — Backend container image
- `frontend/Dockerfile` — Frontend container image

## API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Key endpoints:
- `POST /api/v1/games` — Create new game
- `POST /api/v1/games/{id}/command` — Send move command
- `POST /api/v1/games/{id}/persuade` — Persuade a piece
- `GET /api/v1/games/{id}` — Get game state
- `GET /api/v1/games/{id}/chat` — Get chat history

## Project Goals

Focus on **psychological gameplay** over chess skill. The morale/persuasion system is the core innovation. Keep AI responses short, punchy, and entertaining. Prioritize user experience: fast load times, smooth animations, instant feedback.
