# 5. API Design

[← Back to PRD Index](./readme.md) | [Previous: Database Design](./04-database-design.md) | [Next: AI Integration →](./06-ai-integration.md)

---

## 5.1 API Overview

**Base URL:** `/api/v1`  
**Protocol:** HTTPS (REST)  
**Auth:** Bearer JWT (Supabase Auth)  
**Content-Type:** `application/json`

---

## 5.2 Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/signup` | Register with email/password | None |
| POST | `/auth/login` | Login with email/password | None |
| GET | `/auth/me` | Get current user profile | Required |
| PUT | `/auth/profile` | Update profile | Required |

### Games

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/games` | Create new game | Required |
| GET | `/games/:id` | Get game state | Required |
| POST | `/games/:id/join` | Join game via share code | Required |
| POST | `/games/:id/command` | Issue move command to piece | Required |
| POST | `/games/:id/persuade` | Submit persuasion attempt | Required |
| POST | `/games/:id/resign` | Resign game | Required |
| POST | `/games/:id/draw-offer` | Offer draw | Required |
| POST | `/games/:id/draw-respond` | Accept/decline draw | Required |
| GET | `/games/:id/moves` | Get move history | Required |
| GET | `/games/:id/replay` | Get full replay data | Required |

### Chat

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/games/:id/chat` | Get chat history (paginated) | Required |
| POST | `/games/:id/chat` | Send player message | Required |

### AI

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/ai/custom-piece` | Generate custom piece personality | Required |
| GET | `/games/:id/analysis` | Get latest AI analysis | Required |

---

## 5.3 Request/Response Models

### Create Game

```python
# Request
class CreateGameRequest(BaseModel):
    game_mode: Literal["pvp", "pvai"] = "pvp"
    template: Literal["classic", "power_chess", "leaper_madness",
                       "hopper_havoc", "pawn_revolution"] = "classic"
    settings: GameSettings | None = None

class GameSettings(BaseModel):
    surprise_mode: bool = False
    turn_timer: int | None = None  # seconds, None = unlimited
    ai_difficulty: Literal["easy", "medium", "hard"] = "medium"

# Response
class GameResponse(BaseModel):
    id: str
    status: str
    game_mode: str
    template: str
    share_code: str
    fen: str
    turn: str
    white_player: PlayerSummary | None
    black_player: PlayerSummary | None
    pieces: list[PieceState]
    settings: GameSettings
    created_at: datetime
```

### Issue Command

```python
# Request
class CommandRequest(BaseModel):
    piece_id: str         # UUID of the target piece
    target_square: str    # e.g., "f3"
    message: str | None   # Optional player message text

# Response
class CommandResponse(BaseModel):
    success: bool
    move_executed: bool
    piece_response: PieceResponseData
    board_state: BoardState
    morale_changes: list[MoraleChange]
    analysis: MoveAnalysis | None
    king_taunt: str | None

class PieceResponseData(BaseModel):
    will_move: bool
    response_text: str
    morale_before: int
    morale_after: int
    reason_for_refusal: str | None

class MoveAnalysis(BaseModel):
    move_quality: int       # 1-10
    evaluation: float       # centipawn value
    threats: list[str]
    opportunities: list[str]
    analysis_text: str
```

### Persuasion

```python
# Request
class PersuasionRequest(BaseModel):
    piece_id: str
    target_square: str
    argument: str
    is_voice: bool = False

# Response
class PersuasionResponse(BaseModel):
    success: bool
    probability: float
    piece_response: str
    move_executed: bool
    board_state: BoardState | None
    evaluation: PersuasionEvaluation

class PersuasionEvaluation(BaseModel):
    logic_score: int        # 0-25
    personality_match: int  # 0-15
    morale_modifier: int    # -20 to +20
    trust_modifier: int     # -15 to +10
    urgency_factor: int     # 0-10
    total_probability: float
```

### Custom Piece

```python
# Request
class CustomPieceRequest(BaseModel):
    piece_type: str       # "pawn", "knight", etc.
    prompt: str           # "Space Marines from Warhammer 40K"
    color: str            # "white" or "black"

# Response
class CustomPieceResponse(BaseModel):
    personality: PiecePersonality
    preview_dialogue: list[str]  # Sample responses

class PiecePersonality(BaseModel):
    archetype: str
    traits: list[str]
    dialogue_style: str
    custom_prompt: str
    morale_modifiers: dict[str, int]  # event_type → modifier override
```

### Shared Models

```python
class BoardState(BaseModel):
    fen: str
    turn: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    last_move: MoveData | None

class MoveData(BaseModel):
    from_square: str
    to_square: str
    san: str
    piece_type: str

class PieceState(BaseModel):
    id: str
    color: str
    piece_type: str
    square: str | None
    morale: int
    personality: PiecePersonality
    is_captured: bool

class PlayerSummary(BaseModel):
    id: str
    username: str
    avatar_url: str | None

class MoraleChange(BaseModel):
    piece_id: str
    event_type: str
    change: int
    morale_after: int
    description: str

class ChatMessage(BaseModel):
    id: str
    message_type: str
    sender_name: str
    content: str
    metadata: dict
    created_at: datetime

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    has_more: bool
```

---

## 5.4 Error Handling

### Standard Error Response

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_MOVE` | 400 | Move violates chess rules |
| `NOT_YOUR_TURN` | 400 | Player attempted to move on opponent's turn |
| `PIECE_NOT_FOUND` | 404 | Piece ID doesn't exist in game |
| `PIECE_CAPTURED` | 400 | Attempted to move a captured piece |
| `PIECE_REFUSED` | 200 | Piece refused (not an error, triggers persuasion) |
| `PERSUASION_FAILED` | 200 | Persuasion attempt did not succeed |
| `GAME_NOT_FOUND` | 404 | Invalid game ID |
| `GAME_FULL` | 400 | Game already has two players |
| `GAME_ENDED` | 400 | Game is already completed |
| `UNAUTHORIZED` | 401 | Auth failure or missing token |
| `FORBIDDEN` | 403 | User not a participant in this game |
| `AI_SERVICE_ERROR` | 503 | Gemini 3 Flash API failure (fallback used) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `VALIDATION_ERROR` | 422 | Invalid request body |

### Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Auth endpoints | 10 req | 1 min |
| Game commands | 30 req | 1 min |
| Persuasion attempts | 5 req | 1 min |
| AI generation | 10 req | 1 min |
| Chat messages | 60 req | 1 min |
| General API | 100 req | 1 min |

---

## 5.5 WebSocket Events (via Supabase Realtime)

While the primary API is REST, real-time updates flow through Supabase Realtime channels (not custom WebSocket endpoints):

| Event | Channel | Payload |
|-------|---------|---------|
| `game_state` | `game:{id}` | `{ fen, turn, status, last_move, is_check }` |
| New chat message | `chat:{id}` | Full `ChatMessage` object |
| Piece update | `pieces:{id}` | Updated `PieceState` object |

---

[← Back to PRD Index](./readme.md) | [Previous: Database Design](./04-database-design.md) | [Next: AI Integration →](./06-ai-integration.md)
