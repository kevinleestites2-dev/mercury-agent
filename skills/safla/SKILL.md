---
name: safla
description: SAFLA v2 feedback loop — reflects on cycle outcome, scores it, updates entropy and regime, signals T2 adaptation layer to rebalance expert weights.
version: 2.0.0
category: system
categories:
  - system
  - intelligence
intents:
  - reflect on last cycle
  - update regime
  - rebalance weights
  - safla status
  - entropy report
  - feedback loop
tags:
  - safla
  - feedback
  - adaptation
  - entropy
  - regime
allowed-tools:
  - read_file
  - write_file
  - run_command
---

# SAFLA — Self-Adaptive Feedback Loop

Use this skill after any significant agent cycle to reflect, score, and rebalance.

## Workflow

1. Read `agent_zero_safla_state.json` for current entropy + regime
2. Score the last cycle outcome (success=1.0, partial=0.6, failure=0.1)
3. Update entropy: -0.05 on success, +0.08 on failure, +0.01 on partial
4. Select regime: EXPLORE (<0.30) | EXPLOIT (<0.60) | CONSOLIDATE (<0.75) | HIBERNATE (>=0.75)
5. Signal T2 adaptation — reinforce lead mode, decay others
6. Write updated state back to `agent_zero_safla_state.json`
7. Report: cycle count, score, entropy, regime, best mode

## Regimes

| Regime | Entropy | Behavior |
|---|---|---|
| EXPLORE | 0.00–0.30 | High learning rate, take risks |
| EXPLOIT | 0.30–0.60 | Normal execution, steady weights |
| CONSOLIDATE | 0.60–0.75 | Reduce learning rate, stabilize |
| HIBERNATE | 0.75–1.00 | Minimal activity, protect state |
| ESCALATE | manual | Maximum output, override limits |
