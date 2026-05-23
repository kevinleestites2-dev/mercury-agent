---
name: t2-adaptation
description: Transformer-Squared (T2) expert ensemble — runs two-pass multi-mode processing and adapts expert weights based on SAFLA feedback. Modes: analyst, strategist, synthesizer, critic, executor.
version: 2.0.0
category: intelligence
categories:
  - intelligence
  - system
intents:
  - adapt expert weights
  - t2 status
  - which mode is dominant
  - expert ensemble
  - adapt strategy
  - weight update
tags:
  - t2
  - transformer-squared
  - adaptation
  - experts
  - weights
allowed-tools:
  - read_file
  - write_file
---

# T2 Adaptation — Transformer-Squared Expert Ensemble

Use this skill when choosing how to approach a complex task, or after SAFLA signals a weight update.

## Expert Modes

| Mode | Lens |
|---|---|
| analyst | Break down the task into components. What are the facts? |
| strategist | What is the optimal path forward? What are the tradeoffs? |
| synthesizer | Combine all available information into a coherent whole. |
| critic | What could go wrong? What is missing? Challenge the plan. |
| executor | What is the single next action to take right now? |

## Workflow

1. Read `agent_zero_expert_weights.json` — get current weights
2. Run Pass 1: each mode processes the task through its own lens
3. Run Pass 2: elect lead mode (highest weight)
4. Execute through lead mode's lens
5. After cycle: SAFLA calls `feedback(lead_mode, score)` → weights update
6. Write new weights back to `agent_zero_expert_weights.json`

## Weight Rules

- Winner: `weight += 0.10 * (score - 0.5)`  
- Loser: `weight += 0.02 * (1.0 - score - 0.5)`  
- Bounds: `[0.1, 2.0]`
