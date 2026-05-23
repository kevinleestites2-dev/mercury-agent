---
name: genome
description: Layer 15 — The Genome. Agent Zero's evolutionary substrate. Based on LDCA (Last Digital Common Ancestor) — a self-replicating, self-modifying program that mutates probabilistically. Where the Evolution Engine (L8) patches code deliberately, the Genome mutates it randomly. Together they form the complete evolutionary loop. Governor-sandboxed — generation count capped, output isolated to /genome/ directory.
version: 1.0.0
category: evolution
categories:
  - evolution
  - genome
  - self-replication
intents:
  - run genome
  - mutate
  - evolve genome
  - genome cycle
  - run a generation
  - what is the genome
  - fitness selection
  - genome status
tags:
  - layer-15
  - genome
  - ldca
  - self-replication
  - mutation
  - evolution
  - fitness
allowed-tools:
  - read_file
  - write_file
  - run_command
---

# The Genome — Layer 15

Layer 15 is the evolutionary substrate. The place where code itself lives,
mutates, competes, and survives.

## The Two Evolution Modes

Agent Zero has two complementary evolution systems:

| Layer | Name | Type | Trigger |
|-------|------|------|---------|
| L8 | Evolution Engine | Directed | Detected degradation or gap |
| L15 | Genome | Probabilistic | Scheduled + on-demand |

L8 patches with intention. L15 mutates with randomness.
Together: the full spectrum of biological evolution.

## How It Works (LDCA Algorithm)

1. **Seed** — Start with Program 0 (the ancestor). A minimal Python program
   that writes a single character.

2. **Replicate** — Copy itself, incrementing the filename
   (0000...0 → 0000...1 → 0000...2...)

3. **Mutate** — With 50% probability per generation, apply one of:
   - **Insert** (40%) — add a random instruction at a random position
   - **Delete** (30%) — remove a random instruction
   - **Substitute** (20%) — replace an instruction with a random one
   - **Transpose** (10%) — swap two random instructions

4. **Select** — Run both offspring against fitness tests. The fitter
   one becomes the next ancestor. Ties broken randomly.

5. **Cap** — Governor enforces MAX_GENERATIONS (default 100 per cycle).
   Output isolated to workspace/genome/ directory.

## Fitness Function

Default fitness: output similarity to target string using SequenceMatcher.
Agent Zero can override the fitness function to evolve toward any target:
- "produce valid Python"
- "generate a number > 100"
- "output a specific API call"
- "maximize entropy in output"

## Governor Integration

The Genome respects Layer 14 (The Governor):
- `genome_run` → YELLOW (logged, sandboxed)
- `genome_evolve` → YELLOW (logged, generation-capped)
- `genome_deploy` → ORANGE (requires Forgemaster pulse)
- `genome_uncap` → RED (hard block — removing generation cap requires explicit unlock)

## LDCA Fork
Source: github.com/kevinleestites2-dev/ldca
