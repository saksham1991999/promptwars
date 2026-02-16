# Chess Alive ♟️

> **Chess + Personality Management + Group Chat Interface + Psychological Warfare + AI Commentary**

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)

---

## What Makes This Different?

Traditional chess is about calculating moves and tactics. **Chess Alive** adds a psychological layer: **your pieces have personalities, moods, and opinions**. You have to manage their morale and sometimes convince them to follow your orders.

### The Group Chat Experience

Instead of silently moving pieces, you play chess through a group chat where all your pieces are present:

```
You: "@Knight move to f3"
Knight: "Finally getting some action! On my way!" ✓

You: "@Pawn move forward and attack their Queen"
Pawn: "That's suicide! I'll die instantly. No way." ✗

You: "Trust me, their Queen will have to retreat, opening up our attack"
Pawn: "...Fine. But you better be right about this."
```

---

## Features

### Morale System
Every piece has a morale score (0-100) that determines their willingness to follow orders:

| Morale | Behavior |
|--------|----------|
| **High (70-100)** | Pieces obey instantly, play confidently |
| **Medium (40-69)** | Pieces may question risky orders |
| **Low (0-39)** | Pieces refuse dangerous moves, need persuasion |

**Morale goes DOWN when:**
- You sacrifice their friends
- You leave them undefended
- You make bad moves with them
- They sit idle for too long

**Morale goes UP when:**
- They successfully capture enemy pieces
- You protect them from danger
- They participate in clever tactics
- You compliment them

### Piece Personalities

Each piece type has a distinct personality:

| Piece | Personality | Behavior |
|-------|-------------|----------|
| **Pawns** | Naive and eager | Want to please, scared of combat but willing to sacrifice |
| **Knights** | Cocky mavericks | Love flashy moves, hate retreating |
| **Bishops** | Intellectual strategists | Want logical explanations, cautious |
| **Rooks** | Loyal soldiers | Disciplined, obey orders unless morale is very low |
| **Queen** | Confident diva | Expects protection, refuses suicide moves |
| **King** | Nervous leader | Compliments pieces that protect him, panics in check |

### Persuasion System

When a piece refuses your command, enter persuasion mode:
- **Text persuasion:** Type your argument in chat
- **Voice integration:** Speak your case (speech-to-text)

Success depends on:
- Is your logic sound? (Does the move actually work?)
- Does it match their personality? (Knights like "glory", Bishops like "tactical advantage")
- Their current morale level

### AI Commentary

An AI analyst comments after every move:

> "Strong opening. Knight develops actively. Morale boost: Knight +10"

> "Warning: Their Bishop threatens your Rook on a1"

> "That was a blunder! You left your Queen undefended. All pieces morale -5"

### The Opponent's King

Your opponent's King is in the chat too, actively taunting you:

- **When you lose a piece:** "Lost your Knight? How careless."
- **When you blunder:** "Did you just hang your Queen? Wow."
- **When you're in check:** "Run, little King, run!"

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19 + TypeScript + Vite |
| **Backend** | FastAPI (Python) |
| **Database** | Supabase (PostgreSQL + Realtime) |
| **AI/LLM** | Pydantic AI + Google Gemini 3 Flash |
| **Infrastructure** | Google Cloud Run + Secret Manager + Container Registry |
| **Chess Engine** | chess.js (frontend) / python-chess (backend) |
| **Auth** | Supabase Auth |
| **Deployment** | Docker + Google Cloud Run + GitHub Actions |
| **Caching** | Google Memorystore (Redis) |

### Built on Google Cloud

Chess Alive leverages Google Cloud's infrastructure for scalability, security, AI capabilities, and comprehensive observability:

| Google Service | How We Use It |
|----------------|---------------|
| **Gemini 3 Flash** | Powers all AI personalities, move analysis, and persuasion evaluation |
| **Cloud Run** | Serverless container hosting for instant scaling and zero ops |
| **Secret Manager** | Secure storage of API keys and database credentials |
| **Container Registry** | Private Docker image repository for CI/CD deployments |
| **Memorystore (Redis)** | High-performance caching and rate limiting |
| **Cloud Storage** | Asset storage for custom piece images and game replays |
| **Cloud Monitoring** | Metrics, dashboards, and alerting for system health |
| **Cloud Logging** | Centralized structured logging and log-based metrics |
| **Cloud Trace** | Distributed tracing for performance analysis |
| **Cloud Error Reporting** | Automated error aggregation and notifications |
| **Speech-to-Text API** | Voice command processing for hands-free persuasion |
| **Cloud SDK** | Automated deployments via GitHub Actions |

---

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Supabase account
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chess-alive.git
   cd chess-alive
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your Supabase and Gemini credentials
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Set up the database**
   ```bash
   # Run Supabase migrations
   supabase db push
   ```

5. **Start development servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

6. **Open** `http://localhost:5173` in your browser

---

## API Documentation

Chess Alive provides a comprehensive REST API for game management, chat, and AI features.

### Documentation Files

| Resource | Description |
|----------|-------------|
| [API Documentation](docs/api/API.md) | Complete API reference with all endpoints, schemas, and examples |
| [Quick Start Guide](docs/api/QUICKSTART.md) | Step-by-step guide for common workflows |
| [Postman Collection](docs/api/chess-alive-api-postman-collection.json) | Importable Postman collection for testing |

### Interactive API Docs

When the backend is running, access interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

### Quick Example

```bash
# Create a game
curl -X POST http://localhost:8000/api/v1/games \
  -H "X-Session-ID: my-session" \
  -d '{"game_mode": "pvp", "template": "classic"}'

# Join with share code
curl -X POST http://localhost:8000/api/v1/games/join-by-code \
  -H "X-Session-ID: their-session" \
  -d '{"share_code": "ABC123"}'

# Issue a move command
curl -X POST http://localhost:8000/api/v1/games/{game_id}/command \
  -H "X-Session-ID: my-session" \
  -d '{"piece_id": "...", "target_square": "e4"}'
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/           # Config & security
│   │   ├── db/             # Database queries & client
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic & AI
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Route pages
│   │   ├── lib/            # API & Supabase clients
│   │   └── context/        # Auth context
│   ├── Dockerfile
│   └── package.json
├── docs/
│   └── api/                # API documentation
│       ├── API.md
│       ├── QUICKSTART.md
│       └── chess-alive-api-postman-collection.json
├── supabase/
│   └── migrations/         # Database migrations
└── prd/                    # Product Requirements Documents
```

---

## Game Modes

### Player vs Player
- Both players manage their own pieces' morale
- Private group chats for each side
- Cross-chat taunting from Kings
- Pieces can have custom personalities

### Player vs AI
- You manage your pieces normally
- AI controls opponent pieces (instant obedience but affected by morale)
- Low morale AI pieces occasionally blunder
- AI King trash talks based on board position

---

## The Psychological Strategy

Beyond chess tactics, you now manage:

- **Army morale:** Keep pieces happy so they obey in critical moments
- **Persuasion skills:** Learn what arguments work for each personality type
- **Relationship building:** Protect pieces early so they trust you later
- **Sacrifice timing:** Low-morale pieces are easier to sacrifice
- **Emotional reads:** Chatty, confident pieces might mean your opponent is winning

---

## Why It's Fun

**Party game appeal:**
- Hilarious moments when pieces rebel
- Reading your pieces' snarky responses
- Voice arguments with digital chess pieces
- Watching your friend beg their Queen to move

**Strategic depth:**
- Classic chess skill still matters
- Added layer: morale management
- Timing sacrifices when morale is high
- Using psychology alongside tactics

**Learning tool:**
- AI explains why moves are good/bad
- Pieces give feedback on positioning
- Learn chess while being entertained

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://react.dev/)
- Chess logic powered by [python-chess](https://python-chess.readthedocs.io/) and [chess.js](https://github.com/jhlywa/chess.js)
- **AI powered by [Google Gemini 3 Flash](https://deepmind.google/technologies/gemini/)** via Pydantic AI
- **Infrastructure hosted on [Google Cloud Run](https://cloud.google.com/run)** with Secret Manager, Container Registry, Memorystore, Cloud Storage, Monitoring, Logging, Trace, and Speech-to-Text API
- **Custom piece images** powered by [Nano Banana Pro](https://www.nanabanana.com/)
- Database and auth by [Supabase](https://supabase.com/)

---

<p align="center">
  Made with ♟️ and a lot of persuasion
</p>
