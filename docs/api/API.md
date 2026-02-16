# Chess Alive API Documentation

Welcome to the Chess Alive API! This is a psychological warfare chess game where pieces have personalities, morale, and the ability to refuse orders.

## Base URL

```
Development: http://localhost:8000
Production: https://your-production-url.com
```

## Authentication

The API uses two authentication methods:

### 1. Session-Based (for Games)

For game endpoints, include the `X-Session-ID` header. A session ID will be generated automatically if not provided.

```
X-Session-ID: your-session-id
```

### 2. JWT Token (for Auth-required endpoints)

For user authentication endpoints, use the `Authorization` header with a Bearer token:

```
Authorization: Bearer your-jwt-token
```

Obtain tokens from the `/api/v1/auth/login` or `/api/v1/auth/signup` endpoints.

## Content Types

All requests and responses use JSON:

```
Content-Type: application/json
```

## Error Handling

The API returns structured error responses with the following format:

```json
{
  "error_code": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {}
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `GAME_NOT_FOUND` | 404 | Game does not exist |
| `GAME_FULL` | 400 | Game is not accepting players |
| `GAME_ENDED` | 400 | Game is no longer active |
| `NOT_YOUR_TURN` | 400 | Attempted move out of turn |
| `PIECE_NOT_FOUND` | 404 | Piece does not exist |
| `PIECE_CAPTURED` | 400 | Piece has been captured |
| `FORBIDDEN` | 400 | Not authorized to move this piece |
| `INVALID_MOVE` | 400 | Move is illegal in chess rules |
| `UNAUTHORIZED` | 401 | Invalid or missing credentials |
| `SIGNUP_FAILED` | 400/500 | Account creation failed |
| `AI_SERVICE_ERROR` | 503 | AI service unavailable |

---

## Endpoints

### Health & Status

#### Health Check
```
GET /health
```

Comprehensive health check that verifies:
- Database connectivity (Supabase)
- Redis connectivity (if configured)
- Gemini API configuration

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "gemini_api": "ok"
  }
}
```

#### Readiness Check
```
GET /readiness
```

Kubernetes/Cloud Run readiness probe. Returns 503 if the service is not ready.

**Response:**
```json
{
  "status": "ready"
}
```

---

### Authentication

#### Sign Up
```
POST /api/v1/auth/signup
```

Register a new user account.

**Request Body:**
```json
{
  "email": "player@example.com",
  "password": "securePassword123",
  "username": "ChessMaster"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "username": "ChessMaster",
    "email": "player@example.com",
    "avatar_url": null,
    "games_played": 0,
    "games_won": 0,
    "games_lost": 0,
    "games_drawn": 0,
    "settings": {}
  }
}
```

#### Login
```
POST /api/v1/auth/login
```

Authenticate and receive access tokens.

**Request Body:**
```json
{
  "email": "player@example.com",
  "password": "securePassword123"
}
```

**Response:** Same as Sign Up

#### Get Current User
```
GET /api/v1/auth/me
```

Get the current authenticated user's profile.

**Headers:**
```
Authorization: Bearer {access_token}
```

#### Update Profile
```
PUT /api/v1/auth/profile
```

Update user profile information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "username": "NewName",
  "avatar_url": "https://example.com/avatar.png"
}
```

---

### Games

#### Create Game
```
POST /api/v1/games
```

Create a new chess game. You will be the white player.

**Headers:**
```
X-Session-ID: {session_id} (optional)
```

**Request Body:**
```json
{
  "game_mode": "pvp",
  "template": "classic",
  "settings": {
    "surprise_mode": false,
    "turn_timer": null,
    "ai_difficulty": "medium"
  }
}
```

**Parameters:**
- `game_mode`: `"pvp"` (player vs player) or `"pvai"` (player vs AI)
- `template`: Game variant - `"classic"`, `"power_chess"`, `"leaper_madness"`, `"hopper_havoc"`, `"pawn_revolution"`
- `settings`: Optional game settings
  - `surprise_mode`: Random events enabled
  - `turn_timer`: Time limit in seconds (null for no limit)
  - `ai_difficulty`: `"easy"`, `"medium"`, or `"hard"`

**Response:**
```json
{
  "id": "game-uuid",
  "status": "waiting",
  "game_mode": "pvp",
  "template": "classic",
  "share_code": "ABC123",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "turn": "white",
  "white_player": {
    "id": "session-id",
    "username": "Player-abc123",
    "avatar_url": null
  },
  "black_player": null,
  "pieces": [
    {
      "id": "piece-uuid",
      "color": "white",
      "piece_type": "pawn",
      "square": "a2",
      "morale": 70,
      "personality": {
        "archetype": "default",
        "traits": [],
        "dialogue_style": "neutral",
        "morale_modifiers": {}
      },
      "is_captured": false
    }
  ],
  "settings": {
    "surprise_mode": false,
    "turn_timer": null,
    "ai_difficulty": "medium"
  },
  "created_at": "2026-02-16T10:00:00Z"
}
```

#### Get Game
```
GET /api/v1/games/{game_id}
```

Get the current state of a game including board position, pieces, and morale.

**Response:** Same format as Create Game

#### Join Game by Code
```
POST /api/v1/games/join-by-code
```

Join an existing game using its share code.

**Headers:**
```
X-Session-ID: {session_id} (optional)
```

**Request Body:**
```json
{
  "share_code": "ABC123"
}
```

**Response:** Game state (same as Create Game)

#### Join Game (by Game ID)
```
POST /api/v1/games/{game_id}/join
```

Alternative join endpoint using game ID.

**Request Body:**
```json
{
  "share_code": "ABC123"
}
```

---

### Game Actions

#### Issue Command
```
POST /api/v1/games/{game_id}/command
```

Issue a move command to a piece. The piece may refuse based on its morale and the riskiness of the move.

**Headers:**
```
X-Session-ID: {session_id}
```

**Request Body:**
```json
{
  "piece_id": "piece-uuid",
  "target_square": "e4",
  "message": "@Pawn-e2 move to e4"
}
```

**Response - Piece Accepted:**
```json
{
  "success": true,
  "move_executed": true,
  "piece_response": {
    "will_move": true,
    "response_text": "At your command! Advancing to e4.",
    "morale_before": 70,
    "morale_after": 73,
    "reason_for_refusal": null
  },
  "board_state": {
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "turn": "black",
    "is_check": false,
    "is_checkmate": false,
    "is_stalemate": false,
    "last_move": {
      "from_square": "e2",
      "to_square": "e4",
      "san": "e4",
      "piece_type": "pawn"
    }
  },
  "morale_changes": [
    {
      "piece_id": "piece-uuid",
      "event_type": "good_position",
      "change": 3,
      "morale_after": 73,
      "description": "The Pawn feels good about this move."
    }
  ],
  "analysis": {
    "move_quality": 7,
    "evaluation": 0.2,
    "threats": [],
    "opportunities": ["Controls center"],
    "analysis_text": "Solid positional move: e4."
  },
  "king_taunt": "You call that a move? My grandmother plays better chess!"
}
```

**Response - Piece Refused:**
```json
{
  "success": true,
  "move_executed": false,
  "piece_response": {
    "will_move": false,
    "response_text": "That looks dangerous! I'm not going there.",
    "morale_before": 45,
    "morale_after": 43,
    "reason_for_refusal": "That looks dangerous! I'm not going there."
  },
  "board_state": {
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "turn": "white",
    "is_check": false,
    "is_checkmate": false,
    "is_stalemate": false,
    "last_move": null
  },
  "morale_changes": [],
  "analysis": null,
  "king_taunt": null
}
```

When a piece refuses, you can use the **Persuade** endpoint to try to convince it.

#### Persuade Piece
```
POST /api/v1/games/{game_id}/persuade
```

Submit a persuasion attempt when a piece refuses to move. The AI evaluates your argument.

**Headers:**
```
X-Session-ID: {session_id}
```

**Request Body:**
```json
{
  "piece_id": "piece-uuid",
  "target_square": "e4",
  "argument": "This is a strong central move that will help us control the board! Trust me, I have a plan.",
  "is_voice": false
}
```

**Evaluation Factors:**
- **Logic Score** (0-25): Accuracy of your claims about the board state
- **Personality Match** (0-15): How well your argument appeals to this piece's personality
- **Morale Modifier** (-20 to +20): Current morale impact
- **Trust Modifier** (-15 to +10): Based on previous interactions
- **Urgency Factor** (0-10): Whether you're in check or immediate danger

**Response:**
```json
{
  "success": true,
  "probability": 0.75,
  "piece_response": "*sighs* Fine, you make a good point. I'll move to e4.",
  "move_executed": true,
  "board_state": {
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "turn": "black",
    "is_check": false,
    "is_checkmate": false,
    "is_stalemate": false
  },
  "evaluation": {
    "logic_score": 18,
    "personality_match": 12,
    "morale_modifier": 5,
    "trust_modifier": 3,
    "urgency_factor": 8,
    "total_probability": 0.75
  }
}
```

#### Resign Game
```
POST /api/v1/games/{game_id}/resign
```

Resign from the current game.

**Headers:**
```
X-Session-ID: {session_id}
```

**Response:**
```json
{
  "success": true,
  "result": "black_wins"
}
```

#### Offer Draw
```
POST /api/v1/games/{game_id}/draw-offer
```

Offer a draw to your opponent.

**Headers:**
```
X-Session-ID: {session_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Draw offered"
}
```

#### Respond to Draw
```
POST /api/v1/games/{game_id}/draw-respond
```

Accept or decline a draw offer.

**Request Body:**
```json
{
  "accept": true
}
```

**Response:**
```json
{
  "success": true,
  "result": "draw"
}
```

#### Get Move History
```
GET /api/v1/games/{game_id}/moves
```

Get the complete move history for a game.

**Response:**
```json
{
  "moves": [
    {
      "id": "move-uuid",
      "game_id": "game-uuid",
      "piece_id": "piece-uuid",
      "player_id": "session-id",
      "move_number": 1,
      "from_square": "e2",
      "to_square": "e4",
      "san": "e4",
      "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
      "created_at": "2026-02-16T10:05:00Z"
    }
  ]
}
```

---

### Chat

#### Get Chat History
```
GET /api/v1/games/{game_id}/chat?page=1&page_size=50
```

Get paginated chat history for a game.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)

**Response:**
```json
{
  "data": [
    {
      "id": "message-uuid",
      "message_type": "player_command",
      "sender_name": "Player-abc123",
      "content": "@Pawn-e2 move to e4",
      "metadata": {
        "piece_id": "piece-uuid",
        "target_square": "e4"
      },
      "created_at": "2026-02-16T10:05:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

#### Send Message
```
POST /api/v1/games/{game_id}/chat
```

Send a message in the game chat.

**Headers:**
```
X-Session-ID: {session_id}
```

**Request Body:**
```json
{
  "content": "Good luck, opponent!",
  "message_type": "player_message"
}
```

**Message Types:**
- `player_message`: General chat message
- `player_command`: Move command (usually sent automatically by frontend)

---

### AI Features

#### Generate Custom Piece
```
POST /api/v1/ai/custom-piece
```

Generate a custom piece personality using AI.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "piece_type": "knight",
  "prompt": "A brave knight who speaks in Shakespearean English and values honor above all else",
  "color": "white"
}
```

**Response:**
```json
{
  "personality": {
    "archetype": "honorable_warrior",
    "traits": ["brave", "honorable", "dramatic"],
    "dialogue_style": "Shakespearean, uses thee/thou, speaks of honor and glory",
    "morale_modifiers": {
      "threatened": -5,
      "capture": 20,
      "protected": 10
    }
  },
  "preview_dialogue": [
    "Forsooth! I shall charge into battle!",
    "My honor compels me forward!",
    "Alas, 'tis a dangerous path..."
  ],
  "visual_description": "A noble knight in gleaming silver armor, wielding a lance..."
}
```

#### Get Latest Analysis
```
GET /api/v1/ai/games/{game_id}/analysis
```

Get the latest AI analysis for a game.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "analysis": {
    "content": "Solid positional move: e4.",
    "metadata": {
      "move_quality": 7,
      "evaluation": 0.2
    },
    "created_at": "2026-02-16T10:05:00Z"
  }
}
```

---

## Realtime Updates

Chess Alive uses Supabase Realtime for live game updates. The HTTP API endpoints listed above are for actions initiated by the client. Game state changes are broadcast via Realtime channels.

### WebSocket Channels

Subscribe to the following channels for real-time updates:

#### Game State Channel
```
channel: game:{game_id}
event: game_update
```

Receive updates when:
- A move is made
- Game status changes
- Player joins/leaves

#### Chat Channel
```
channel: chat:{game_id}
event: new_message
```

Receive new chat messages including:
- Player messages
- Piece responses
- AI analysis
- King taunts
- System messages

#### Morale Channel
```
channel: morale:{game_id}
event: morale_change
```

Receive updates when piece morale changes.

---

## Game Statuses

| Status | Description |
|--------|-------------|
| `waiting` | Game created, waiting for opponent to join |
| `active` | Game in progress |
| `completed` | Game finished (checkmate, resignation, or draw) |

---

## Game Results

| Result | Description |
|--------|-------------|
| `white_wins` | White player won |
| `black_wins` | Black player won |
| `draw` | Game ended in a draw |

---

## Morale System

Each piece has a morale score from 0-100:

- **70-100**: High morale - piece almost always obeys
- **40-69**: Medium morale - piece may refuse risky moves
- **0-39**: Low morale - piece often refuses, hard to convince

### Morale Modifiers

| Event | Morale Change |
|-------|---------------|
| Successful capture | +15 |
| Protected move | +5 |
| Winning position | +10 |
| Being threatened | -10 |
| Ally sacrificed | -20 |
| Bad positioning | -5 |

---

## Piece Types

Standard chess pieces:
- `pawn`
- `knight`
- `bishop`
- `rook`
- `queen`
- `king`

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Per-move AI calls**: Maximum 5 calls per move
- **Per-game AI cap**: Maximum 200 AI calls per game
- **Daily user limit**: Maximum 50 games per user per day

When rate limited, the API returns:
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded, please try again later",
  "details": {
    "retry_after": 60
  }
}
```

---

## SDKs and Libraries

### Official Clients

- **JavaScript/TypeScript**: Use with Supabase client for Realtime
- **Python**: Use `httpx` or `requests`

### Example: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"
SESSION_ID = "your-session-id"

# Create a game
response = requests.post(
    f"{BASE_URL}/api/v1/games",
    headers={"X-Session-ID": SESSION_ID},
    json={"game_mode": "pvp", "template": "classic"}
)
game = response.json()
print(f"Share code: {game['share_code']}")

# Make a move
piece_id = game["pieces"][0]["id"]
response = requests.post(
    f"{BASE_URL}/api/v1/games/{game['id']}/command",
    headers={"X-Session-ID": SESSION_ID},
    json={
        "piece_id": piece_id,
        "target_square": "e4",
        "message": "@Pawn move forward!"
    }
)
result = response.json()
print(result["piece_response"]["response_text"])
```

---

## Support

For issues and feature requests, please visit our GitHub repository or contact support.

---

## Changelog

### v1.0.0
- Initial API release
- Game management endpoints
- Chat and real-time messaging
- AI-powered piece personalities
- Persuasion system
- Authentication
