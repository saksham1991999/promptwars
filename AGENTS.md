# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/` contains FastAPI code: `routers/`, `services/`, `models/`, `db/`, `core/`, and `middleware/`.
- `backend/tests/` holds pytest suites (`unit/` plus shared fixtures in `conftest.py`).
- `frontend/src/` contains the React app: `pages/`, `components/`, `lib/`, `types/`, and styles.
- `supabase/migrations/` stores ordered SQL migrations (`001_*.sql` to `010_*.sql`).
- `prd/` contains product and architecture docs; keep source-code changes out of this folder.

## Build, Test, and Development Commands
- `cd backend && uvicorn app.main:app --reload --port 8000` starts the API locally.
- `cd backend && pytest` runs backend tests with coverage settings from `pytest.ini`.
- `cd backend && ruff check . && black . && mypy app` runs linting, formatting, and type checks.
- `cd frontend && npm run dev` starts Vite dev server on `http://localhost:5173`.
- `cd frontend && npm run build` compiles TypeScript and builds production assets.
- `cd frontend && npm run lint` runs ESLint rules.
- `docker compose up --build` runs frontend, backend, and Redis together.

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints on public functions, `snake_case` file names, and `async def` for I/O-bound flows.
- TypeScript/React: explicit prop/type definitions, avoid `any`, `PascalCase.tsx` for pages/components, and domain-focused utility files under `src/lib/`.
- Follow surrounding formatting in edited files, then run lint/format commands before opening a PR.

## Testing Guidelines
- Backend testing uses `pytest`, `pytest-asyncio`, and `pytest-cov`.
- Naming is enforced in `backend/pytest.ini`: `test_*.py`, `Test*`, and `test_*`.
- Use markers to target runs (`unit`, `integration`, `api`, `db`, `ai`), e.g. `pytest -m unit`.
- Backend coverage must stay at or above 75% (`--cov-fail-under=75`).
- Frontend automated tests are not set up yet; include manual verification notes for UI changes.

## Commit & Pull Request Guidelines
- Recent commits use imperative subjects (examples: `Add ...`, `Implement ...`, `Initial commit: ...`).
- Keep commits focused to one logical change and describe impact clearly.
- PRs should include: summary, touched areas (`backend`, `frontend`, `supabase`), test evidence (commands run), and screenshots/video for UI updates.
- Link related issues and call out migrations or environment/config changes explicitly.

## Security & Configuration Tips
- Start from `backend/.env.example` and `frontend/.env.example`; never commit real secrets.
- Validate `SECRET_KEY`, CORS origins, and Supabase/Gemini keys before production deploys.
- Store schema changes as new, versioned files in `supabase/migrations/`.
