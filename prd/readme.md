# Chess Alive — Product Requirements Document

> **Chess + Personality Management + Group Chat Interface + Psychological Warfare + AI Commentary + Custom Pieces**

**Version:** 1.0  
**Last Updated:** 2026-02-16  
**Status:** Draft  
**Author:** Chess Alive Team  

---

## Table of Contents

| # | Section | Description |
|---|---------|-------------|
| 1 | [Executive Summary](./01-executive-summary.md) | Vision, audience, differentiators, success metrics, timeline |
| 2 | [Product Requirements](./02-product-requirements.md) | Functional & non-functional requirements (FR/NFR) |
| 3 | [System Architecture](./03-system-architecture.md) | High-level architecture, component breakdown, folder structure |
| 4 | [Database Design](./04-database-design.md) | Schema, RLS policies, realtime channels, indexing |
| 5 | [API Design](./05-api-design.md) | Endpoints, request/response models, error handling |
| 6 | [AI Integration](./06-ai-integration.md) | Pydantic AI agents, prompt engineering, caching, rate limiting |
| 7 | [UI/UX Design](./07-ui-ux-design.md) | Design system, responsive layout, wireframes, interaction patterns, accessibility |
| 8 | [Testing Strategy](./08-testing-strategy.md) | Unit, integration, E2E, performance, accessibility, security tests |
| 9 | [Security](./09-security.md) | Auth, data protection, API security, AI security |
| 10 | [Deployment & Infrastructure](./10-deployment.md) | Environments, CI/CD, monitoring, scaling |
| 11 | [Configuration & Environment](./11-configuration.md) | Env vars, config files, feature flags |
| 12 | [Development Workflow](./12-development-workflow.md) | Git strategy, code standards, documentation |
| 13 | [Risks & Mitigation](./13-risks-and-mitigation.md) | Technical, operational, and business risks |
| 14 | [References](./14-references.md) | External documentation and resources |

---

## Tech Stack Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + TypeScript | UI, game board, chat interface |
| Backend | FastAPI (Python) | REST API, game logic, AI orchestration |
| Database | Supabase (PostgreSQL) | Data persistence, auth, realtime, storage |
| AI/LLM | Pydantic AI + Google Gemini 3 Flash | Piece personalities, analysis, persuasion |
| Image Gen | Nano Banana Pro API | Custom piece visual generation |
| Chess Engine | chess.js / python-chess | Move validation, board state management |
| Realtime | Supabase Realtime | WebSocket channels for live game updates |
| Voice | Web Speech API | Voice-to-text persuasion input |
| Deployment | Google Cloud Run | Containerized backend + frontend hosting |

---

## Quick Start

1. Read the [Executive Summary](./01-executive-summary.md) for project context
2. Review [Product Requirements](./02-product-requirements.md) for detailed user stories
3. Study [System Architecture](./03-system-architecture.md) for technical design
4. Check [Database Design](./04-database-design.md) and [API Design](./05-api-design.md) for implementation details
5. Understand [AI Integration](./06-ai-integration.md) for the core AI mechanics
6. Follow [Development Workflow](./12-development-workflow.md) to start contributing

---

## Document Conventions

- **FR-XXX** — Functional Requirement identifiers
- **NFR-XXX** — Non-Functional Requirement identifiers
- **Priority levels:** P0 (critical), P1 (important), P2 (nice-to-have)
- Mermaid diagrams are used for architecture and flow visualization
- Code blocks include syntax highlighting for implementation references
