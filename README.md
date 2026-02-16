# Chess Alive ♟️

> **Chess + Personality Management + Group Chat Interface + Psychological Warfare + AI Commentary**

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)

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
| **AI/LLM** | Pydantic AI + Google Gemini |
| **Chess Engine** | chess.js (frontend) / python-chess (backend) |
| **Auth** | Supabase Auth |
| **Deployment** | Docker + Google Cloud Run |

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
- AI powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Database and auth by [Supabase](https://supabase.com/)

---

<p align="center">
  Made with ♟️ and a lot of persuasion
</p>
