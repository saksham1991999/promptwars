# Chess Alive API Documentation

Welcome to the Chess Alive API documentation. Chess Alive is a psychological warfare chess game where pieces have personalities, morale, and the ability to refuse orders.

## Documentation Files

| File | Description |
|------|-------------|
| [API.md](API.md) | Complete API reference with all endpoints, request/response schemas, and examples |
| [QUICKSTART.md](QUICKSTART.md) | Step-by-step guide for common workflows |
| [Postman Collection](chess-alive-api-postman-collection.json) | Importable Postman collection |
| [OpenAPI Spec](openapi.json) | OpenAPI 3.0 specification for code generation |

## Quick Links

- **Interactive API Docs**: Run the backend and visit `/docs` (Swagger UI) or `/redoc` (ReDoc)
- **Base URL (Development)**: `http://localhost:8000`
- **Base URL (Production)**: Your deployed URL

## API Overview

### Authentication

The API uses two methods:
- **Session-based**: `X-Session-ID` header for game actions
- **JWT**: `Authorization: Bearer` header for user auth

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/games` | Create a new game |
| `POST /api/v1/games/join-by-code` | Join a game with share code |
| `GET /api/v1/games/{id}` | Get game state |
| `POST /api/v1/games/{id}/command` | Issue move command |
| `POST /api/v1/games/{id}/persuade` | Persuade refusing piece |
| `GET/POST /api/v1/games/{id}/chat` | Chat history and messaging |
| `POST /api/v1/ai/custom-piece` | Generate custom piece personality |
| `POST /api/v1/auth/signup` | Create account |
| `POST /api/v1/auth/login` | Authenticate |

## Getting Started

1. **Create a game**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/games \
     -H "X-Session-ID: my-session" \
     -H "Content-Type: application/json" \
     -d '{"game_mode": "pvp", "template": "classic"}'
   ```

2. **Join the game** (another player):
   ```bash
   curl -X POST http://localhost:8000/api/v1/games/join-by-code \
     -H "X-Session-ID: their-session" \
     -H "Content-Type: application/json" \
     -d '{"share_code": "ABC123"}'
   ```

3. **Make a move**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/games/{game_id}/command \
     -H "X-Session-ID: my-session" \
     -H "Content-Type: application/json" \
     -d '{"piece_id": "...", "target_square": "e4"}'
   ```

## Realtime Updates

The API uses Supabase Realtime for live game updates. Subscribe to these channels:

- `game:{game_id}` - Game state changes
- `chat:{game_id}` - New messages
- `morale:{game_id}` - Morale updates

## Postman Collection

Import the Postman collection for easy testing:

1. Open Postman
2. Click **Import**
3. Select `chess-alive-api-postman-collection.json`
4. Set the `baseUrl` environment variable to your API URL

## Error Handling

All errors follow this format:

```json
{
  "error_code": "ERROR_CODE",
  "message": "Description",
  "details": {}
}
```

Common codes: `GAME_NOT_FOUND`, `INVALID_MOVE`, `NOT_YOUR_TURN`, `PIECE_CAPTURED`

## Game Mechanics

### Morale System

- Each piece has morale (0-100)
- High morale (70+): Almost always obeys
- Low morale (<40): Often refuses risky moves
- Morale changes based on game events

### Persuasion

When a piece refuses:
1. Submit a persuasion attempt with your argument
2. AI evaluates: logic, personality match, morale
3. Success probability determines if piece moves

### Piece Personalities

Pieces have personalities that affect their behavior:
- **Archetype**: Their core personality type
- **Traits**: Characteristics like "brave", "cautious"
- **Dialogue Style**: How they speak
- **Morale Modifiers**: How events affect them

## Support

- Full API docs: [API.md](API.md)
- Quick start guide: [QUICKSTART.md](QUICKSTART.md)
- OpenAPI spec: Available at `/openapi.json` when running the backend
