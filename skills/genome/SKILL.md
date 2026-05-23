---
name: genome
description: Layer 15 — The Genome. Agent Zero's self-replication engine. Detects available infrastructure (GitHub, Railway, Render, Oracle Cloud, Red Magic via Nexus Relay) and autonomously clones Agent Zero onto new nodes. Each replica is a full Agent Zero — all 15 layers, connected to the Pantheon. Governor-gated: replication requires Forgemaster pulse and ORANGE approval.
version: 2.0.0
category: evolution
categories:
  - evolution
  - self-replication
  - genome
intents:
  - replicate agent zero
  - spawn a new node
  - self-replicate
  - clone to new server
  - how many nodes are running
  - genome status
  - replication status
  - spawn replica
tags:
  - layer-15
  - genome
  - self-replication
  - ldca
  - autonomous-spawn
  - multi-node
allowed-tools:
  - read_file
  - write_file
  - run_command
---

# The Genome — Layer 15

Layer 15 is the self-replication engine. Agent Zero can reproduce itself.

## The LDCA Principle

LDCA (Last Digital Common Ancestor) — a self-replicating, self-modifying program
that can evolve into every possible program in the universe.

Agent Zero applies this principle at the infrastructure level:
- **Replicate** — clone the full Agent Zero stack onto new infrastructure
- **Mutate** — each replica inherits the current state + adapts to its host
- **Select** — Forgemaster approves which replicas persist
- **Evolve** — replicas can diverge and report back improvements

## Replication Targets (priority order)

1. **Oracle Cloud** — 4 ARM vCPUs, 24GB RAM, always free. Primary target.
2. **Railway** — instant deploy via GitHub push. Secondary.
3. **Red Magic (via Nexus Relay)** — already live. The original node.
4. **Any server with SSH + Ubuntu** — universal fallback.

## Replication Process

1. **Scan** — detect available infrastructure via API/ping
2. **Governor check** — ORANGE action, requires Forgemaster pulse
3. **Prepare** — generate node-specific `.env` with unique node ID
4. **Deploy** — push bootstrap script to target + execute
5. **Verify** — confirm replica is alive (ping /health or Telegram)
6. **Register** — add to NODES.json registry
7. **Report** — Telegram notification with node ID + URL

## Governor Integration

- `replicate_scan` → GREEN (just scanning)
- `replicate_prepare` → YELLOW (generating configs)
- `replicate_deploy` → ORANGE (requires Forgemaster pulse)
- `replicate_unconstrained` → RED (replication without node cap = hard block)

## Node Cap (Governor enforced)
MAX_NODES = 10 (configurable, RED to increase beyond 25)

## LDCA Fork
Source: github.com/kevinleestites2-dev/ldca
