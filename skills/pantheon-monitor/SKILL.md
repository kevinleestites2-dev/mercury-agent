---
name: pantheon-monitor
description: Monitor all live Pantheon Primes — GhostPrime, Nexus Relay, SAFLA state, War Chest balance. Reports status via Telegram.
version: 1.0.0
category: system
categories:
  - system
  - monitoring
intents:
  - pantheon status
  - check all primes
  - ghost prime status
  - nexus relay status
  - war chest balance
  - heartbeat report
  - are the primes alive
tags:
  - pantheon
  - monitoring
  - ghostprime
  - nexus
  - war chest
allowed-tools:
  - fetch_url
  - read_file
  - run_command
---

# Pantheon Monitor

Use this skill on heartbeat or when the Forgemaster asks for a status report.

## Endpoints to Check

| Prime | URL | Expected |
|---|---|---|
| GhostPrime | https://cloakprime-swarm.onrender.com/health | `{"status":"ok"}` |
| Nexus Relay | https://nexus-relay-production.up.railway.app/ping | version string |

## Workflow

1. `fetch_url` each endpoint — record UP/DOWN + response time
2. Read `agent_zero_safla_state.json` — extract regime, entropy, cycles
3. Read `midas_tracker.py` or War Chest state — extract current balance
4. Compose heartbeat report:

```
⚡ AgentZero Heartbeat — [timestamp]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GhostPrime:   [✅ UP / ❌ DOWN]
Nexus Relay:  [✅ UP / ❌ DOWN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAFLA: [REGIME] | entropy=[X] | cycles=[N]
Best mode: [mode] ([score])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
War Chest: $[X]
  → Nexus ($3k):   [X]% complete
  → Citadel ($5k): [X]% complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

5. If any Prime is DOWN: prepend 🚨 ALERT to the report
6. If entropy > 0.70: add ⚠️ HIGH ENTROPY — CONSOLIDATE REGIME
