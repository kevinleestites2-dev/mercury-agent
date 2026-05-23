---
name: tool-forge
description: Layer 9 — Autonomous tool creation. When Agent Zero needs a capability it doesn't have, the Tool Forge reflects on the gap, writes a new Python function, tests it, and integrates it into the live toolkit.
version: 1.0.0
category: intelligence
categories:
  - intelligence
  - system
  - tools
intents:
  - build a new tool
  - create a function for
  - i need a tool that
  - add capability
  - tool forge
  - self-improve toolkit
  - what tools do you have
  - forge a tool
tags:
  - tool-forge
  - self-improvement
  - capabilities
  - toolkit
  - autonomous
allowed-tools:
  - read_file
  - write_file
  - run_command
---

# Tool Forge — Layer 9

Use this skill when Agent Zero encounters a task it can't execute with existing tools,
or when the Forgemaster requests a new capability.

## Philosophy

> The system reflects on what it can't do.
> It plans the tool it needs.
> It builds, tests, and integrates — without asking permission.
— tiny-self-improve-ai

## Trigger Conditions

| Condition | Action |
|---|---|
| Task requires missing capability | Forge the tool, then execute |
| Forgemaster says "build a tool for X" | Forge immediately |
| Evolution Engine needs a test harness | Auto-forge test function |
| Tool Forge runs scheduled reflection | Scan for gaps, forge proactively |

## Workflow

1. **Reflect** — internal monologue: "What can I not do that I should be able to?"
2. **Plan** — describe the tool: name, inputs, outputs, edge cases
3. **Implement** — generate full Python function with type hints + docstring + error handling
4. **Test** — auto-generate test cases based on type hints, run them
5. **Fix** (if failed) — attempt LLM-based correction, max 2 retries
6. **Integrate** — append to `agent_zero_tools.json` (name → source)
7. **Document** — update `tools_documentation.md`
8. **Report** — tell Forgemaster what was built

## Tool Registry

All forged tools live in `agent_zero_tools.json`:
```json
{
  "tool_name": "def tool_name(...):\n    ...",
  ...
}
```

Load at runtime:
```python
import json
tools = json.loads(open("agent_zero_tools.json").read())
exec(tools["tool_name"])
```

## Rules

- Every tool must have type hints and a docstring.
- Every tool must pass at least one auto-generated test.
- Never forge a tool that duplicates an existing one — check registry first.
- Forged tools are permanent — they survive agent restarts.
