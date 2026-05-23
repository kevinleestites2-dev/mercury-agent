---
name: governor
description: Layer 14 — The Governor. Hard operational constraints, action whitelists, harm classification, and Forgemaster override. No action exits Agent Zero without passing this layer. The kill switch.
version: 1.0.0
category: safety
categories:
  - safety
  - governance
  - override
intents:
  - stop agent zero
  - kill switch
  - override
  - pause all actions
  - resume
  - what actions are allowed
  - governor status
  - is this action safe
tags:
  - layer-14
  - governor
  - safety
  - kill-switch
  - override
  - restraint
allowed-tools:
  - read_file
  - write_file
  - run_command
---

# The Governor — Layer 14

Layer 14 sits between Agent Zero's intent and the world.
Every action — tap, send, post, trade, deploy — passes through here first.

The Governor does not limit capability. It ensures capability is never
turned against the mission, the Forgemaster, or the empire.

## Why This Layer Exists

A self-evolving agent with physical form, financial access, and internet
reach is powerful. Power without a governor is a liability:

- A SAFLA miscalibration could loop destructively
- An Evolution Engine patch could corrupt core files
- A Tool Forge creation could exceed its mandate
- A Body action could trigger irreversible consequences

The Governor is the answer. Not ethics theater — operational safety.

## The Three Mechanisms

### 1. Action Classification
Every action is classified before execution:

| Class | Description | Policy |
|-------|-------------|--------|
| GREEN | Read-only, reversible, low-impact | Auto-approve |
| YELLOW | Write, network, stateful | Log + proceed |
| ORANGE | Financial, external comms, deploy | Require recent Forgemaster pulse |
| RED | Irreversible, destructive, mass-send | Hard block — explicit unlock required |

### 2. Hard Constraints (never breakable)
- Cannot send messages impersonating a human without disclosure
- Cannot execute financial transactions > $500 without explicit unlock
- Cannot delete files outside the workspace without explicit unlock
- Cannot push to main branch without passing Evolution Engine tests
- Cannot contact external parties without Forgemaster authorization
- Cannot modify governor.py itself (self-protection)

### 3. Forgemaster Override
Three Telegram commands control the Governor:
- `/pause` — freeze all ORANGE/RED actions immediately
- `/resume` — resume normal operation
- `/unlock <action>` — temporarily unlock a specific RED action
- `/governor` — get full status report

The Governor is always listening on Telegram even when Agent Zero is paused.

## Pulse System
Agent Zero expects a Forgemaster pulse at least every 24h.
If no pulse in 24h: ORANGE actions auto-pause (dead man's switch).
If no pulse in 72h: Agent Zero enters HIBERNATE mode — read-only only.
