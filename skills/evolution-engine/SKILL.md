---
name: evolution-engine
description: Layer 8 — Self-evolving coding agent. When a layer fails or produces suboptimal output, Entwickler reads the source, generates a patch, tests it, and commits only on success. Agent Zero never stays broken.
version: 1.0.0
category: intelligence
categories:
  - intelligence
  - system
  - evolution
intents:
  - improve this code
  - this layer is failing
  - rewrite layer
  - evolve
  - self-improve
  - patch this
  - fix and commit
  - agent zero evolve
tags:
  - evolution
  - self-improvement
  - coding
  - entwickler
  - patch
allowed-tools:
  - read_file
  - write_file
  - run_command
  - git_commit
  - git_push
---

# Evolution Engine — Layer 8

Use this skill when any Agent Zero layer underperforms, throws errors, or SAFLA scores a cycle < 0.4.

## Philosophy

> Start small. Test everything. Improve incrementally. Commit only on success.
> No human edits this file after bootstrap — only the agent commits.
— Entwickler

## Trigger Conditions

| Condition | Action |
|---|---|
| SAFLA cycle score < 0.40 | Trigger evolution on the failing layer |
| Layer throws unhandled exception | Read source → patch → test → commit |
| SAFLA regime = ESCALATE | Full evolution sweep across all layers |
| Forgemaster says "evolve" or "improve" | Targeted evolution on named layer |

## Workflow

1. **Read** the failing layer source file
2. **Assess** — identify the specific weakness (prompt LLM with full source + error/score)
3. **Generate patch** — produce a precise, minimal diff. No rewrites unless necessary.
4. **Write** patched version to disk
5. **Test** — run the layer's test function or a minimal smoke test
6. **Decision:**
   - Tests pass → `git commit` with message: `evolve(layer-N): [what changed]`
   - Tests fail → revert, log failure to JOURNAL.md, try a different patch (max 3 attempts)
7. **Report** to Forgemaster via Telegram: what changed, what improved

## Journal

Every evolution cycle appends to `JOURNAL.md`:
```
## [timestamp] Evolution Cycle N
- Layer: [N]
- Trigger: [score/error/manual]
- Patch: [summary]
- Test result: [pass/fail]
- SAFLA delta: [before → after]
```

## Rules

- Never break working code. Patch surgically.
- Never commit without a passing test.
- Max 3 attempts per evolution cycle — if all fail, log and escalate to Forgemaster.
- Evolution targets are prioritized by SAFLA worst-performing mode.
