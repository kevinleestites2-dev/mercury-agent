---
name: agent-zero-layers
description: Reference map of all 13 Agent Zero cognitive layers — what each does, which repo it sources from, and current phase status.
version: 3.0.0
category: system
categories:
  - system
  - reference
intents:
  - layer status
  - architecture overview
  - what layers are done
  - phase status
  - pantheon architecture
tags:
  - architecture
  - layers
  - pantheon
  - agent-zero
allowed-tools: []
---

# Agent Zero — 13-Layer Architecture

| Layer | Name | Source | Status |
|---|---|---|---|
| 1 | The Vault | agent-zero (COG) | ✅ Phase 1 |
| 2 | Perception | gpt-researcher | ✅ Phase 3 |
| 3 | Runtime Body | opencrabs | ✅ Phase 1 |
| 4 | Semantic Router | Brain.ai | ✅ Phase 2 |
| 5 | Cognition | Base-of-Self-Aware-AI | ✅ Phase 2 |
| 5b | Second Brain | **Mercury (this repo)** | ✅ Phase 2 |
| 6 | Adaptation | Transformer-Squared | ✅ Phase 3 |
| 7 | Feedback Loop | SAFLA v2 | ✅ Phase 3 |
| 8 | Evolution Engine | Entwickler | 🔄 Phase 4 |
| 9 | Tool Forge | tiny-self-improve-ai | 🔄 Phase 4 |
| 10 | Identity Layer | self-recognition | 🔄 Phase 5 |
| 11 | The Doctrine | Self-Evolving-Agents | 🔒 Locked |
| 12 | Super Intelligence | convergence of 1–11 | 🌀 Emergent |
| 13 | Physical Form | Psi0 | 🔄 Phase 8 |

## Signal Flow

```
Signal IN → Layer 4 (Router) → Layer 2/3/5/10
                              → Layer 6 (T2 Ensemble)
                              → Layer 7 (SAFLA Reflect)
                              → Response OUT
                              → Weights updated + memory persisted
```

## Mercury as the Chassis

Mercury provides:
- Soul files (soul.md, persona.md, taste.md, heartbeat.md)
- 31 hardened tools (filesystem, git, github, web, shell, scheduler)
- Dual-layer Second Brain (SQLite + FTS5, conscious/subconscious)
- Telegram + CLI channels
- Sub-agent supervisor
- Token budgeting
- Skill system (this directory)

Agent Zero adds:
- Pantheon soul identity
- SAFLA feedback loop (Layer 7)
- T2 adaptation engine (Layer 6)
- Pantheon Prime monitoring
- War Chest tracking
