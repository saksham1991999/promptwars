# 8. Testing Strategy

[← Back to PRD Index](./readme.md) | [Previous: UI/UX Design](./07-ui-ux-design.md) | [Next: Security →](./09-security.md)

---

## 8.1 Unit Tests

### Frontend (Jest + React Testing Library)

| Test Area | Examples | Coverage Target |
|-----------|----------|----------------|
| Component rendering | GameBoard renders 64 squares, ChatInterface shows messages | 75% |
| Hook behavior | `useGameState` updates on realtime events, `useMorale` clamps 0–100 | 80% |
| Utility functions | `chessLogic.ts` move parsing, `constants.ts` morale thresholds | 95% |
| Mock API calls | Verify correct endpoints called with correct payloads | 80% |
| Accessibility | ARIA labels present, keyboard handlers fire, focus management | 80% |

**Example test:**
```typescript
describe('GameBoard', () => {
  it('renders 64 squares', () => {
    render(<GameBoard fen={STARTING_FEN} />);
    expect(screen.getAllByRole('button', { name: /square/i })).toHaveLength(64);
  });

  it('highlights legal moves on piece click', () => {
    render(<GameBoard fen={STARTING_FEN} turn="white" />);
    fireEvent.click(screen.getByTestId('square-e2')); // white pawn
    expect(screen.getByTestId('square-e3')).toHaveClass('legal-move');
    expect(screen.getByTestId('square-e4')).toHaveClass('legal-move');
  });
});
```

### Backend (pytest)

| Test Area | Examples | Coverage Target |
|-----------|----------|----------------|
| Chess engine | Move validation, FEN generation, checkmate detection | 95% |
| Morale calculator | All morale events produce correct deltas, clamping | 95% |
| Persuasion engine | Probability calculations, boundary cases, formula correctness | 95% |
| API routes | Request validation, response format, error codes | 85% |
| Database queries | CRUD operations, pagination, filtering | 80% |
| AI service | Mock Gemini responses, fallback behavior, response validation | 85% |

**Example test:**
```python
class TestMoraleCalculator:
    def test_capture_enemy_increases_morale(self):
        piece = create_piece(morale=50)
        result = calculate_morale_change(piece, event_type="capture_enemy")
        assert result.morale_after == 65  # +15 for capture

    def test_morale_cannot_exceed_100(self):
        piece = create_piece(morale=95)
        result = calculate_morale_change(piece, event_type="capture_enemy")
        assert result.morale_after == 100  # clamped

    def test_morale_cannot_go_below_0(self):
        piece = create_piece(morale=5)
        result = calculate_morale_change(piece, event_type="player_lied")
        assert result.morale_after == 0  # clamped
```

---

## 8.2 Integration Tests

### API Integration

| Test Scenario | Description |
|---------------|-------------|
| Full move cycle | Create game → command piece → validate response includes analysis + morale |
| Persuasion cycle | Command → refusal → persuade → success/failure → board state |
| Game lifecycle | Create → join → play moves → checkmate → stats update |
| Auth flow | Signup → login → JWT → authorized API call |
| Realtime sync | Move by player A → player B receives update within 500ms |
| Chat pagination | Send 100 messages → paginate correctly (50 per page) |

### Real-time Testing

```typescript
describe('Realtime Sync', () => {
  it('syncs board state between two players', async () => {
    const player1 = createClient(player1Token);
    const player2 = createClient(player2Token);

    const receivedUpdate = new Promise((resolve) => {
      player2.channel(`game:${gameId}`).on('broadcast', { event: 'game_state' }, resolve);
    });

    await player1.post(`/api/v1/games/${gameId}/command`, { piece_id, target_square: 'e4' });
    const update = await receivedUpdate;
    expect(update.fen).toContain('e4');
  });
});
```

---

## 8.3 End-to-End Tests (Playwright)

### Critical User Flows

| Flow | Steps | Priority |
|------|-------|----------|
| Full game PvAI | Sign up → Create PvAI → Play 5 moves → Verify morale/chat | P0 |
| PvP game | Create game → Share link → Join → Both play → Verify sync | P0 |
| Persuasion | Command risky move → Piece refuses → Persuade → Success | P0 |
| Custom pieces | Create custom → Preview → Start game → Verify in play | P1 |
| Voice input | Click mic → Speak → Verify text appears → Send | P1 |
| Game completion | Play to checkmate → Verify post-game screen → Rematch | P0 |
| Guest mode | Play as guest → Complete game → Prompt to register | P2 |

---

## 8.4 Performance Tests

| Test | Tool | Target | Method |
|------|------|--------|--------|
| API latency (p95) | k6 | <200ms | 100 VUs, 5 min ramp |
| AI response time | Custom script | <2s (p95) | 50 concurrent requests |
| Concurrent games | k6 | 100 games stable | Simulate 200 users |
| WebSocket throughput | Artillery | <500ms latency | 100 connections, 10 msg/s |
| Frontend FCP | Lighthouse | <3s | Mobile + Desktop profiles |
| DB query time | pg_stat_statements | <50ms (indexed) | Monitor for 1 hour under load |

---

## 8.5 Accessibility Tests

| Test | Tool | Standard |
|------|------|----------|
| Automated audit | axe-core + @axe-core/playwright | WCAG 2.1 AA |
| Keyboard navigation | Manual + Playwright | All functions reachable |
| Screen reader | NVDA + VoiceOver | All content announced |
| Color contrast | axe-core | 4.5:1 minimum ratio |
| Focus management | Playwright | Focus visible at all times |
| Reduced motion | Playwright | Animations disabled |

---

## 8.6 Security Tests

| Test | Method | Target |
|------|--------|--------|
| Auth bypass | Attempt API calls without/invalid JWT | All endpoints return 401 |
| SQL injection | Parameterized query verification | No raw SQL in codebase |
| XSS | Submit `<script>` tags in chat/custom piece prompts | All sanitized |
| CSRF | Verify SameSite cookies + CORS | No cross-site requests accepted |
| Rate limiting | Exceed rate limits | 429 returned correctly |
| RLS bypass | Query with wrong user context | Zero unauthorized data access |
| Prompt injection | Submit adversarial prompts to AI agents | Output validated by Pydantic |

---

## 8.7 Test Commands

```bash
# Frontend unit tests
cd frontend && npm test -- --coverage

# Backend unit tests
cd backend && pytest --cov=app --cov-report=html

# E2E tests
cd frontend && npx playwright test

# Performance tests
k6 run tests/load/game_flow.js

# Accessibility audit
npx @axe-core/cli http://localhost:5173/game/test-id
```

---

[← Back to PRD Index](./readme.md) | [Previous: UI/UX Design](./07-ui-ux-design.md) | [Next: Security →](./09-security.md)
