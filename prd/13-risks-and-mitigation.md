# 13. Risks & Mitigation

[← Back to PRD Index](./readme.md) | [Previous: Development Workflow](./12-development-workflow.md) | [Next: References →](./14-references.md)

---

## 13.1 Risk Matrix

| # | Risk | Probability | Impact | Severity | Category |
|---|------|------------|--------|----------|----------|
| R1 | AI API cost overruns | Medium | High | **High** | Financial |
| R2 | AI response latency spikes (>5s) | Medium | High | **High** | Technical |
| R3 | Gemini API downtime/deprecation | Low | Critical | **High** | Dependency |
| R4 | Real-time sync issues (desync) | Medium | High | **High** | Technical |
| R5 | Prompt injection attacks | Medium | Medium | **Medium** | Security |
| R6 | Voice feature browser incompatibility | High | Low | **Medium** | Technical |
| R7 | Database connection exhaustion | Low | High | **Medium** | Infrastructure |
| R8 | User-generated content moderation | Medium | Medium | **Medium** | Operational |
| R9 | Scalability under viral load | Low | High | **Medium** | Infrastructure |
| R10 | Complex game logic bugs (variants) | Medium | Medium | **Medium** | Technical |
| R11 | Low user retention after novelty | Medium | High | **High** | Business |
| R12 | AI providing bad chess analysis | Medium | Medium | **Medium** | Quality |

---

## 13.2 Mitigation Strategies

### R1: AI API Cost Overruns

| Control | Details |
|---------|---------|
| **Caching** | 5-min TTL on identical position analysis; permanent cache on custom piece generations |
| **Model tiering** | All agents use `gemini-3-flash` which is both fast and cost-effective; Nano Banana Pro image gen only on custom piece creation |
| **Per-user limits** | 50 games/day, 200 AI calls/game |
| **Budget alerts** | Automated alerts at 80% monthly budget; hard cutoff at 100% |
| **Fallback templates** | Pre-written response templates when API quota exceeded |
| **Monitoring** | Daily cost dashboard, per-request token tracking |

### R2: AI Response Latency Spikes

| Control | Details |
|---------|---------|
| **Timeout** | 5s hard timeout on all AI calls; fallback response returned on timeout |
| **Optimistic UI** | Show "piece is thinking..." animation while AI generates response |
| **Parallel calls** | Fire analysis + taunt generation in parallel (not sequentially) |
| **Model selection** | Flash model for latency-sensitive operations |
| **Circuit breaker** | After 3 consecutive timeouts, switch to template responses for 5 min |

### R3: Gemini API Downtime/Deprecation

| Control | Details |
|---------|---------|
| **Abstraction layer** | All AI calls go through `gemini_service.py`; swap to different provider by changing one file |
| **Pydantic AI portability** | Pydantic AI supports multiple LLM providers; migration path to OpenAI/Anthropic exists |
| **Fallback mode** | Full template-based response system for all 5 agents |
| **Monitoring** | Health check endpoint pings Gemini API every 60s; alerts on failure |

### R4: Real-time Sync Issues

| Control | Details |
|---------|---------|
| **Backend authority** | Backend (python-chess) is the single source of truth for board state |
| **Optimistic + reconcile** | Frontend updates optimistically; reconciles with backend FEN on every update |
| **Reconnection logic** | Auto-reconnect WebSocket with exponential backoff (1s, 2s, 4s, 8s, max 30s) |
| **State recovery** | On reconnect, fetch full game state from REST API |
| **Conflict resolution** | Backend rejects moves on stale state; frontend fetches latest before retry |

### R5: Prompt Injection Attacks

| Control | Details |
|---------|---------|
| **Input isolation** | User text in Pydantic AI `user` role only; never in system prompt |
| **System prompt hardening** | Explicit instruction to ignore user-role manipulation attempts |
| **Output validation** | All AI outputs validated against strict Pydantic models |
| **Content filtering** | Regex-based pre-filter on user input; output sanitation before display |
| **Monitoring** | Log unusual AI outputs for manual review |

### R6: Voice Feature Browser Incompatibility

| Control | Details |
|---------|---------|
| **Feature detection** | Check `window.SpeechRecognition` on load; hide voice button if unavailable |
| **Graceful degradation** | Text persuasion always available; voice is an enhancement |
| **Browser support note** | Show tooltip: "Voice works best in Chrome and Edge" |
| **Fallback** | On speech recognition error, prompt user to type instead |

### R7: Database Connection Exhaustion

| Control | Details |
|---------|---------|
| **Connection pooling** | Supabase Pro includes PgBouncer; configure pool size matching expected load |
| **Query optimization** | All frequent queries use indexed columns; N+1 queries eliminated |
| **Connection limits** | Backend limits concurrent DB connections (max 20 per worker) |
| **Monitoring** | Alert at 80% connection pool usage |

### R8: User-Generated Content Moderation

| Control | Details |
|---------|---------|
| **Custom piece prompts** | Max 500 chars; blocklist filter for offensive terms |
| **Chat messages** | Profanity filter (lightweight, configurable) |
| **AI output filtering** | AI system prompts include "keep all content PG-rated" |
| **Report system** | (P2) User can report offensive content; admin review queue |

### R9: Scalability Under Viral Load

| Control | Details |
|---------|---------|
| **Auto-scaling** | Google Cloud Run auto-scales backend instances from 0 to max |
| **CDN** | Google Cloud CDN caches static assets globally |
| **Rate limiting** | Protects backend from traffic spikes |
| **Database scaling** | Supabase Pro → Team plan; read replicas if needed |
| **Queue system** | (Phase 2) Celery + Redis for async AI processing |

### R10: Complex Game Logic Bugs (Variants)

| Control | Details |
|---------|---------|
| **Phased release** | Launch with Classic chess only; add variants incrementally |
| **95%+ test coverage** | Chess engine has highest test coverage target in the project |
| **python-chess validation** | Authoritative move validation on backend (well-tested library) |
| **Variant isolation** | Each variant extends base rules; independent test suites per variant |

### R11: Low User Retention After Novelty

| Control | Details |
|---------|---------|
| **Content variety** | Custom piece creator keeps experiences fresh |
| **Social features** | Shareable links, replay sharing, friend challenges |
| **Progression** | (P2) ELO rating, achievements, unlockable personality packs |
| **Regular updates** | New templates, seasonal themes, community piece packs |
| **Learning path** | AI analysis helps players improve → intrinsic motivation |

### R12: AI Providing Bad Chess Analysis

| Control | Details |
|---------|---------|
| **Hybrid approach** | Use python-chess engine evaluation for numerical analysis; AI for narrative commentary |
| **Calibration** | Compare AI quality assessments against Stockfish evaluations during testing |
| **Disclaimer** | Analysis labeled as "AI-assisted" — not guaranteed perfect |
| **User feedback** | (P2) Thumbs up/down on analysis; used to improve prompts |

---

## 13.3 Contingency Plans

| Scenario | Trigger | Action |
|----------|---------|--------|
| Gemini API down for >1 hour | Health check failures | Switch to full template mode; notify users via in-app banner |
| Cost exceeds 150% of budget | Budget monitoring alert | Disable custom piece generation; reduce AI calls to essential only (piece response + basic analysis) |
| Critical security breach | Sentry alert / user report | Emergency maintenance mode; revoke all tokens; investigate; post-mortem |
| Viral traffic surge (10x normal) | Monitoring alerts | Scale backend; enable aggressive rate limiting; disable non-essential AI features |
| Database corruption | Backup monitoring | Restore from Supabase point-in-time recovery (available on Pro plan) |

---

[← Back to PRD Index](./readme.md) | [Previous: Development Workflow](./12-development-workflow.md) | [Next: References →](./14-references.md)
