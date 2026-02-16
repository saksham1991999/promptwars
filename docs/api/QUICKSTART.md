# Chess Alive API Quick Start Guide

This guide will walk you through the core workflows of the Chess Alive API, from creating a game to making your first move and handling piece refusal.

## Prerequisites

- API running locally at `http://localhost:8000` or production URL
- cURL or a tool like Postman/HTTPie

## Table of Contents

1. [Create a Game](#step-1-create-a-game)
2. [Join a Game](#step-2-join-a-game)
3. [View Game State](#step-3-view-game-state)
4. [Make Your First Move](#step-4-make-your-first-move)
5. [Handle Piece Refusal](#step-5-handle-piece-refusal)
6. [Send a Chat Message](#step-6-send-a-chat-message)
7. [Complete Workflow Example](#complete-workflow-example-with-curl)

---

## Step 1: Create a Game

**Player 1** creates a game and receives a share code to invite others.

### Request

```bash
curl -X POST http://localhost:8000/api/v1/games \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d '{
    "game_mode": "pvp",
    "template": "classic",
    "settings": {
      "surprise_mode": false,
      "turn_timer": null,
      "ai_difficulty": "medium"
    }
  }'
```

### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "waiting",
  "game_mode": "pvp",
  "template": "classic",
  "share_code": "ABC123",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "turn": "white",
  "white_player": {
    "id": "player1-session",
    "username": "Player-player1",
    "avatar_url": null
  },
  "black_player": null,
  "pieces": [
    {
      "id": "piece-1",
      "color": "white",
      "piece_type": "pawn",
      "square": "e2",
      "morale": 70,
      "personality": {
        "archetype": "default",
        "traits": [],
        "dialogue_style": "neutral"
      },
      "is_captured": false
    }
    // ... more pieces
  ],
  "created_at": "2026-02-16T10:00:00Z"
}
```

**Save these values:**
- `id`: Game ID (`550e8400-e29b-41d4-a716-446655440000`)
- `share_code`: Invite code (`ABC123`)
- `pieces[].id`: Piece IDs for making moves

---

## Step 2: Join a Game

**Player 2** uses the share code to join.

### Request

```bash
curl -X POST http://localhost:8000/api/v1/games/join-by-code \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player2-session" \
  -d '{
    "share_code": "ABC123"
  }'
```

### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "share_code": "ABC123",
  "turn": "white",
  "white_player": {
    "id": "player1-session",
    "username": "Player-player1"
  },
  "black_player": {
    "id": "player2-session",
    "username": "Player-player2"
  },
  "pieces": [ /* ... */ ]
}
```

The game is now `active` and ready to play!

---

## Step 3: View Game State

Both players can fetch the current game state at any time:

```bash
curl http://localhost:8000/api/v1/games/550e8400-e29b-41d4-a716-446655440000
```

---

## Step 4: Make Your First Move

**Player 1** (White) moves first. Let's move the king's pawn from e2 to e4.

### Request

```bash
curl -X POST http://localhost:8000/api/v1/games/550e8400-e29b-41d4-a716-446655440000/command \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d '{
    "piece_id": "piece-1",
    "target_square": "e4",
    "message": "@Pawn move to e4"
  }'
```

### Response - Move Accepted

```json
{
  "success": true,
  "move_executed": true,
  "piece_response": {
    "will_move": true,
    "response_text": "At your command! Advancing to e4.",
    "morale_before": 70,
    "morale_after": 73
  },
  "board_state": {
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "turn": "black",
    "is_check": false,
    "last_move": {
      "from_square": "e2",
      "to_square": "e4",
      "san": "e4",
      "piece_type": "pawn"
    }
  },
  "analysis": {
    "move_quality": 7,
    "analysis_text": "Solid positional move: e4."
  },
  "king_taunt": "You call that a move? My grandmother plays better chess!"
}
```

The board now shows the move, and it's **Black's turn** (`"turn": "black"`).

---

## Step 5: Handle Piece Refusal

Sometimes pieces refuse dangerous moves based on their morale. Here's how to handle it:

### When a Piece Refuses

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
    "turn": "white"
  },
  "analysis": null
}
```

### Persuade the Piece

Submit a persuasion attempt:

```bash
curl -X POST http://localhost:8000/api/v1/games/550e8400-e29b-41d4-a716-446655440000/persuade \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d '{
    "piece_id": "piece-1",
    "target_square": "e4",
    "argument": "This is a strong central move that will help us control the board! Trust me, I have a plan.",
    "is_voice": false
  }'
```

### Response - Persuasion Successful

```json
{
  "success": true,
  "probability": 0.75,
  "piece_response": "*sighs* Fine, you make a good point. I'll move to e4.",
  "move_executed": true,
  "board_state": {
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "turn": "black"
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

---

## Step 6: Send a Chat Message

Players can send messages in the game chat:

```bash
curl -X POST http://localhost:8000/api/v1/games/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d '{
    "content": "Good luck! May the best commander win!",
    "message_type": "player_message"
  }'
```

Get chat history:

```bash
curl "http://localhost:8000/api/v1/games/550e8400-e29b-41d4-a716-446655440000/chat?page=1&page_size=50"
```

---

## Complete Workflow Example (with cURL)

Here's a complete script demonstrating a game between two players:

```bash
#!/bin/bash

API_URL="http://localhost:8000"

# === PLAYER 1: Create Game ===
echo "=== Player 1: Creating Game ==="
GAME_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/games" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d '{
    "game_mode": "pvp",
    "template": "classic"
  }')

GAME_ID=$(echo $GAME_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
SHARE_CODE=$(echo $GAME_RESPONSE | grep -o '"share_code":"[^"]*"' | cut -d'"' -f4)

echo "Game ID: $GAME_ID"
echo "Share Code: $SHARE_CODE"

# === PLAYER 2: Join Game ===
echo ""
echo "=== Player 2: Joining Game ==="
curl -s -X POST "$API_URL/api/v1/games/join-by-code" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player2-session" \
  -d "{\"share_code\": \"$SHARE_CODE\"}" | jq '.'

# Get piece IDs
GAME_STATE=$(curl -s "$API_URL/api/v1/games/$GAME_ID")
WHITE_PAWN_ID=$(echo $GAME_STATE | grep -o '"id":"[^"]*","color":"white","piece_type":"pawn"' | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "=== White Pawn ID: $WHITE_PAWN_ID ==="

# === PLAYER 1: Move Pawn to e4 ===
echo ""
echo "=== Player 1: Moving Pawn to e4 ==="
curl -s -X POST "$API_URL/api/v1/games/$GAME_ID/command" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: player1-session" \
  -d "{
    \"piece_id\": \"$WHITE_PAWN_ID\",
    \"target_square\": \"e4\",
    \"message\": \"@Pawn-e2 move to e4\"
  }" | jq '.'

echo ""
echo "=== Game Complete! ==="
```

---

## Next Steps

- Explore the full [API Documentation](API.md)
- Download the [Postman Collection](chess-alive-api-postman-collection.json)
- Set up [Supabase Realtime](https://supabase.com/docs/guides/realtime) for live updates
- Learn about [piece personalities and morale](../GAMEPLAY.md)

## Common Issues

### "Game not found"
- Check that you're using the correct game ID
- Game IDs are UUIDs (e.g., `550e8400-e29b-41d4-a716-446655440000`)

### "It's not your turn"
- White moves first
- Check the `turn` field in the game state
- Make sure you're using the correct session ID

### "Invalid move"
- Ensure the target square is valid chess notation (e.g., `e4`, `Nf3`)
- The piece must legally be able to move to that square
- The piece must not be captured

### "Not your piece"
- You can only move pieces of your color
- White is the player who created the game
- Black is the player who joined

---

## Tips for Success

1. **Keep session IDs consistent** - Use the same `X-Session-ID` header for all requests from the same player
2. **Watch morale** - Pieces with low morale (below 40) are more likely to refuse
3. **Use persuasion wisely** - Save your best arguments for critical moves
4. **Check the FEN** - The `fen` field shows the board state; you can visualize it with any chess board viewer
