# 2. Product Requirements

[← Back to PRD Index](./readme.md) | [Previous: Executive Summary](./01-executive-summary.md) | [Next: System Architecture →](./03-system-architecture.md)

---

## 2.1 Functional Requirements

### Authentication & User Management

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-001 | Email/Password Signup | P0 | User can sign up with email and password via Supabase Auth. Email verification required. |
| FR-002 | Google OAuth Sign-in | P1 | User can sign in via Google OAuth 2.0 through Supabase Auth. |
| FR-003 | User Profile | P0 | Profile includes username (unique), avatar (upload or default), games played, win/loss record, and win rate percentage. |
| FR-004 | Guest Mode | P2 | Unregistered users can play with a temporary session. Prompt to create account after first game to save progress. |
| FR-005 | Profile Editing | P1 | User can update username, avatar, and display preferences. |

#### User Stories

**US-001:** As a new user, I want to sign up with my email so I can save my game progress and stats.

```
Given   I am on the sign-up page
When    I enter a valid email and password
And     I complete email verification
Then    My account is created and I am redirected to the home page
```

**US-002:** As a returning user, I want to sign in with Google so I can quickly access my account.

```
Given   I am on the login page
When    I click "Sign in with Google"
And     I authorize the app
Then    I am logged in and redirected to the home page
And     My profile is created/linked automatically
```

**US-003:** As a guest, I want to play without creating an account so I can try the game immediately.

```
Given   I am on the home page
When    I click "Play as Guest"
Then    A temporary session is created
And     I can create/join games with limited features
And     After the game, I am prompted to create an account
```

---

### Game Creation & Lobby

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-006 | Create PvP Game | P0 | User can create a PvP game and receive a unique shareable link (e.g., `chessalive.gg/game/abc123`). |
| FR-007 | Preset Templates | P1 | User can select from preset game templates: Classic Chess, Power Chess, Leaper Madness, Hopper Havoc, Pawn Revolution. |
| FR-008 | Customize Personalities | P1 | Before game start, user can assign custom personalities to pieces (e.g., themed armies). |
| FR-009 | Surprise Mode | P1 | User can enable "surprise mode" — opponent doesn't see custom piece personalities until they move. |
| FR-010 | Create PvAI Game | P0 | User can create a single-player game against AI with selectable difficulty (Easy, Medium, Hard). |
| FR-011 | Lobby Waiting State | P0 | PvP lobby shows waiting state with game link, auto-starts when opponent joins. |

#### User Stories

**US-004:** As a player, I want to create a game and share a link so my friend can join easily.

```
Given   I am logged in and on the home page
When    I click "Play vs Friend"
Then    A game lobby is created with a unique URL
And     I can copy/share the link
And     The lobby shows "Waiting for opponent..."
When    My friend opens the link and joins
Then    Both players enter the pre-game customization screen
```

**US-005:** As a player, I want to choose a preset template so I can try different chess variants.

```
Given   I am in the game lobby
When    I select "Power Chess" from the template dropdown
Then    The piece roster updates to show hybrid pieces (Chancellor, Archbishop, Amazon)
And     Each hybrid piece has a unique personality displayed
```

**US-006:** As a player, I want to customize my piece personalities so I can create a themed army.

```
Given   I am in the game lobby
When    I click "Customize Pieces"
Then    A modal opens showing all my pieces
And     I can type a prompt like "Make my Pawns Space Marines from Warhammer 40K"
And     AI generates personality, dialogue style, and behavioral traits
And     I can preview and confirm the customization
```

**US-007:** As a player, I want surprise mode so my custom pieces are hidden from my opponent.

```
Given   I have customized my pieces
When    I toggle "Surprise Mode" on
Then    My opponent sees default piece appearances
And     Custom personalities are revealed only when a piece makes its first move
```

---

### Core Gameplay

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-012 | Chat-Based Commands | P0 | User can @-tag pieces in the group chat to issue move commands (e.g., `@Knight-g1 move to f3`). |
| FR-013 | Piece Responses | P0 | Pieces respond in chat based on their personality, morale, and the commanded move. |
| FR-014 | Text Persuasion | P0 | When a piece refuses, user can type persuasion arguments in chat. |
| FR-015 | Voice Persuasion | P1 | User can speak persuasion arguments via microphone; speech is converted to text and displayed in chat. |
| FR-016 | Move Acceptance/Refusal | P0 | Pieces accept or refuse moves based on morale level, move risk, personality traits, and persuasion quality. |
| FR-017 | Real-time Board Updates | P0 | Board state updates in real-time for both players via Supabase Realtime. |
| FR-018 | Legal Move Validation | P0 | All moves validated against chess rules. Illegal moves are rejected with clear error messages. |
| FR-019 | Morale System | P0 | Each piece has a morale score (0–100) that affects obedience. Morale changes based on game events. |
| FR-020 | Morale Change Events | P0 | Morale updates triggered by: captures, danger, protection, idle turns, blunders, compliments, good positioning. |
| FR-021 | Click-to-Move Alternative | P1 | User can click a piece on the board, see legal moves highlighted, click a destination — auto-generates a chat command. |
| FR-022 | Turn Timer | P2 | Optional configurable turn timer (30s, 60s, 120s, unlimited). Timeout results in random legal move. |

#### Morale System Details

**Morale Decrease Events:**

| Event | Morale Change | Example |
|-------|--------------|---------|
| Friendly piece captured nearby | -10 | "My Bishop friend just got taken..." |
| Left in danger (undefended) | -8 | "I'm hanging here! Anyone going to help?" |
| Bad move (blunder) | -5 to all pieces | "That was terrible. We're losing." |
| Sitting idle for 5+ turns | -5 | "Am I invisible? Let me play!" |
| Player lied in persuasion | -15 | "You said I'd be safe! I wasn't!" |
| Endangered repeatedly | -10 | "Stop putting me in danger!" |

**Morale Increase Events:**

| Event | Morale Change | Example |
|-------|--------------|---------|
| Captures an enemy piece | +15 | "Got 'em! Who's next?" |
| Protected from threat | +10 | "Thanks for having my back." |
| Part of clever tactic | +10 | "Brilliant plan! I see it now." |
| Player compliments piece | +5 | "Aw shucks, thanks boss." |
| Good positional placement | +5 | "Nice spot. I can see the whole board." |
| Successful promotion (Pawn) | +30 | "I'M A QUEEN NOW!" |

**Morale Thresholds:**

| Range | Behavior | Obedience |
|-------|----------|-----------|
| 80–100 | Enthusiastic, confident, offers suggestions | Always obeys, bonus dialogue |
| 60–79 | Normal, cooperative | Obeys standard moves, may question risky ones |
| 40–59 | Reluctant, cautious | Questions most commands, refuses high-risk moves |
| 20–39 | Demoralized, fearful | Refuses risky moves, needs strong persuasion |
| 0–19 | Nearly mutinous | Refuses most moves, may suggest surrender |

#### Piece Personality Specifications

| Piece | Personality Archetype | Dialogue Style | Key Traits |
|-------|----------------------|----------------|------------|
| **Pawn** | Naive Recruit | Eager, nervous, anxious | Wants to please, scared of combat, willing to sacrifice, dreams of promotion |
| **Knight** | Cocky Maverick | Boastful, adventurous, impatient | Loves flashy moves, hates retreating, motivated by glory |
| **Bishop** | Intellectual Strategist | Analytical, cautious, eloquent | Wants logical explanations, appreciates tactics, dislikes reckless play |
| **Rook** | Loyal Soldier | Disciplined, stoic, reliable | Follows orders, rarely complains, only refuses when morale is very low |
| **Queen** | Confident Diva | Commanding, dramatic, self-assured | Expects protection, refuses suicide moves, high standards |
| **King** | Nervous Leader | Anxious, grateful, commanding | Panics in check, compliments protectors, issues desperate commands |

#### Persuasion Mechanics

**Persuasion Success Formula:**

```
success_probability = base_rate
    + logic_bonus        (0-25: does the move actually do what the player claims?)
    + personality_match  (0-15: arguments aligned with piece personality)
    + morale_modifier    (-20 to +20: based on current morale)
    + trust_modifier     (-15 to +10: have past promises been kept?)
    + urgency_factor     (0-10: is the game state critical?)
```

**Base Rates by Morale:**

| Morale | Base Rate |
|--------|-----------|
| 80–100 | 90% |
| 60–79 | 70% |
| 40–59 | 45% |
| 20–39 | 25% |
| 0–19 | 10% |

**What the AI evaluates:**
1. **Board State Accuracy** — Does the player's argument match reality? (e.g., "this forks their Queen and Rook" — is that true?)
2. **Personality Alignment** — Knights respond to "glory," Bishops to "logic," Pawns to "sacrifice for the team"
3. **Risk Assessment** — Will this move likely result in the piece being captured?
4. **Promise Tracking** — Has the player made and broken promises before? (e.g., "I'll protect you" → piece was captured)

---

### AI & Analysis

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-023 | Post-Move Analysis | P0 | AI analyzes board after each move, providing: move quality score (1–10), positional evaluation (centipawn), threats, opportunities. |
| FR-024 | Threat Detection | P0 | AI identifies immediate threats and warns the player in chat. |
| FR-025 | Morale Impact Prediction | P1 | AI predicts how a move will affect morale before execution. |
| FR-026 | Opponent King Taunts | P0 | Opponent's King generates contextual taunts based on game state (material balance, position, check status). |
| FR-027 | Persuasion Validation | P0 | AI validates player's persuasion arguments against actual board state to determine logic quality. |
| FR-028 | Your King Reactions | P1 | Your King reacts to game events: boosts morale on good moves, shows worry on bad positions. |

#### AI Analysis Output Format

After each move, the AI provides commentary in chat:

```
✅ Strong move. Knight develops actively.
   📊 Evaluation: +0.5 (slight advantage)
   💪 Knight morale: +10 (now at 85/100)
   ⚠️ Watch out: Their Bishop eyes your Rook on a1
   💡 Consider: Castle kingside soon for safety
```

```
🚨 Blunder! Queen is now hanging on d5.
   📊 Evaluation: -3.2 (losing)
   😰 All pieces morale: -5
   💔 Queen morale: -15 (now at 35/100)
   🎯 Opponent's best response: Bxd5
```

#### Opponent King Taunt Scenarios

| Game State | Taunt Category | Example Taunts |
|------------|---------------|----------------|
| Player loses a piece | Mockery | "Lost your Knight? How careless." / "Down material already?" |
| Player blunders | Schadenfreude | "Did you just hang your Queen? Wow." / "Even my Pawns saw that coming." |
| Player is in check | Aggression | "Run, little King, run!" / "Nowhere to hide!" |
| Opponent is winning | Confidence | "This is almost too easy." / "Should we just call it?" |
| Opponent is losing | Defiance | "A lucky move. This isn't over." / "I've come back from worse." |
| Stalemate approaching | Frustration | "Don't you dare stalemate me!" |
| Player makes a great move | Grudging respect | "...I'll admit, that was decent." |

---

### Chat & Communication

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-029 | Group Chat Interface | P0 | All game communication happens in a unified group chat: player messages, piece responses, AI analysis, King taunts. |
| FR-030 | Message Types | P0 | Chat visually distinguishes: player commands, piece dialogue, AI analysis, King taunts, system messages. |
| FR-031 | Chat History | P0 | Full chat history persists for game duration. Scrollable with lazy loading (50 messages per batch). |
| FR-032 | Voice-to-Text Display | P1 | Voice messages are converted to text and displayed in chat with a 🎤 indicator. |
| FR-033 | @-Mention Autocomplete | P1 | Typing `@` in chat shows autocomplete dropdown of available pieces with their current morale. |
| FR-034 | Piece Status in Chat | P1 | Each piece's messages include a morale indicator (emoji or bar) next to their name. |

---

### Game Completion

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-035 | Standard End Conditions | P0 | Game ends on checkmate, stalemate, draw by repetition, 50-move rule, insufficient material, or resignation. |
| FR-036 | Post-Game Analysis | P1 | Final screen shows: move-by-move quality breakdown, best/worst moves, total morale changes, persuasion success rate. |
| FR-037 | Rematch | P1 | Option to rematch with same settings (pieces, template, opponent). |
| FR-038 | Game Replay | P2 | Full replay with chat messages synchronized to moves. Shareable link. |
| FR-039 | Resignation | P0 | Player can resign. Confirmation dialog prevents accidental resignation. |
| FR-040 | Draw Offer | P1 | Player can offer a draw. Opponent receives notification to accept/decline. |

---

## 2.2 Non-Functional Requirements

### Performance

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-001 | Move validation latency | <100ms | P0 |
| NFR-002 | AI response generation | <2 seconds | P0 |
| NFR-003 | Realtime update latency | <500ms | P0 |
| NFR-004 | Concurrent game support | 100 games | P0 |
| NFR-005 | Frontend First Contentful Paint | <3 seconds | P0 |
| NFR-006 | Frontend Time to Interactive | <5 seconds | P1 |
| NFR-007 | Backend cold start | <3 seconds | P1 |
| NFR-008 | Database query response | <50ms (indexed queries) | P0 |

### Security

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-009 | JWT Authentication | All API endpoints authenticated via Supabase JWT | P0 |
| NFR-010 | Input Sanitization | XSS prevention on all user-generated text (DOMPurify) | P0 |
| NFR-011 | Rate Limiting | Rate limits on AI API calls to prevent abuse (10 req/min/user) | P0 |
| NFR-012 | Secure WebSockets | All realtime connections via `wss://` | P0 |
| NFR-013 | Environment Variables | API keys stored in env vars, never in source code | P0 |
| NFR-014 | Row Level Security | RLS policies on all Supabase tables | P0 |
| NFR-015 | CORS Configuration | Whitelist only production and staging domains | P0 |
| NFR-016 | Content Moderation | Filter offensive content in custom piece prompts and chat | P1 |

### Accessibility

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-017 | WCAG 2.1 AA | Full compliance with WCAG 2.1 Level AA guidelines | P1 |
| NFR-018 | Keyboard Navigation | All interactions accessible without mouse | P0 |
| NFR-019 | Screen Reader Support | ARIA labels on all interactive elements, semantic HTML | P1 |
| NFR-020 | High Contrast Mode | Toggle for high contrast color scheme | P1 |
| NFR-021 | Text-to-Speech | Optional TTS for piece responses and AI analysis | P2 |
| NFR-022 | Touch Targets | Minimum 44×44px touch targets on mobile | P0 |
| NFR-023 | Focus Indicators | Visible 2px focus outlines on all interactive elements | P0 |
| NFR-024 | Reduced Motion | Respect `prefers-reduced-motion` media query | P1 |
| NFR-025 | Font Scaling | UI remains functional up to 200% font zoom | P1 |

### Code Quality

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-026 | TypeScript Strict Mode | `strict: true` in tsconfig.json, no implicit any | P0 |
| NFR-027 | Frontend Linting | ESLint + Prettier with auto-format on save/commit | P0 |
| NFR-028 | Backend Linting | Black + Ruff for Python code formatting/linting | P0 |
| NFR-029 | Test Coverage | 80%+ combined; 95%+ for critical paths (morale, persuasion, move validation) | P1 |
| NFR-030 | Pre-commit Hooks | Husky + lint-staged for linting/formatting before commit | P1 |
| NFR-031 | Documentation | JSDoc for TypeScript, docstrings for Python, component-level docs | P1 |

### Efficiency

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| NFR-032 | Database Indexing | Proper indexes on frequently queried columns (game_id, user_id, created_at) | P0 |
| NFR-033 | Chat Pagination | Load last 50 messages initially, load more on scroll | P0 |
| NFR-034 | Lazy Loading | Game replays and non-critical assets loaded on demand | P1 |
| NFR-035 | Optimistic UI | Moves update board immediately; validation happens async | P1 |
| NFR-036 | AI Response Caching | Cache identical AI prompts for 5 min TTL | P1 |
| NFR-037 | Bundle Optimization | Code splitting, tree shaking, <200KB JS initial bundle | P1 |

---

## 2.3 Requirements Traceability Matrix

| Feature | Functional Reqs | Non-Functional Reqs | Test Coverage |
|---------|----------------|---------------------|---------------|
| Authentication | FR-001 to FR-005 | NFR-009, NFR-013 | [Section 8.1](./08-testing-strategy.md) |
| Game Lobby | FR-006 to FR-011 | NFR-005, NFR-006 | [Section 8.3](./08-testing-strategy.md) |
| Core Gameplay | FR-012 to FR-022 | NFR-001, NFR-003, NFR-018 | [Section 8.1, 8.2](./08-testing-strategy.md) |
| AI & Analysis | FR-023 to FR-028 | NFR-002, NFR-011, NFR-036 | [Section 8.1, 8.4](./08-testing-strategy.md) |
| Chat | FR-029 to FR-034 | NFR-003, NFR-010, NFR-033 | [Section 8.1, 8.2](./08-testing-strategy.md) |
| Game Completion | FR-035 to FR-040 | NFR-001, NFR-034 | [Section 8.3](./08-testing-strategy.md) |

---

[← Back to PRD Index](./readme.md) | [Previous: Executive Summary](./01-executive-summary.md) | [Next: System Architecture →](./03-system-architecture.md)
