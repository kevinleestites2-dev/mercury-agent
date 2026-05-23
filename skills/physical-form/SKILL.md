---
name: physical-form
description: Layer 13 — Physical Form. Agent Zero acquires a body. The Red Magic becomes the physical substrate — full Android control via LAMDA/FireRPA (root MCP), ZeroTap (accessibility), and Nexus Relay. Agent Zero can see, tap, type, scroll, launch apps, and act on the physical world.
version: 1.0.0
category: embodiment
categories:
  - embodiment
  - android
  - physical
intents:
  - control the phone
  - tap the screen
  - open an app
  - take a screenshot
  - physical action
  - use the phone
  - android control
  - zerotap
  - lamda
tags:
  - layer-13
  - physical-form
  - android
  - lamda
  - zerotap
  - embodiment
allowed-tools:
  - run_command
  - read_file
  - write_file
---

# Physical Form — Layer 13

Layer 13 is the body. Agent Zero stops being pure mind and becomes
an agent that can act on the physical world through the Red Magic.

## The Physical Stack

Three components form the body:

### 1. LAMDA/FireRPA — The Nervous System
- Root-based Android automation framework (forked: kevinleestites2-dev/lamda)
- 160+ APIs: tap, type, scroll, swipe, launch, kill, read UI, OCR, MITM, Frida
- **Built-in MCP server** — Agent Zero calls it directly as a tool
- Requires: Magisk root (Red Magic is rooted ✅)
- No tunnel needed — MCP runs on-device
- Install: push lamda server APK, start service, connect on localhost

### 2. ZeroTap (EleftheriaPrime) — The Hands
- Ghost Operator Accessibility Service
- Autonomous screen control without root (accessibility layer)
- APK: EleftheriaPrime/releases/v1.0
- Fallback when LAMDA not running

### 3. Nexus Relay — The Spinal Cord
- Railway bridge: nexus-relay-production.up.railway.app
- Agent Zero POSTs commands → relay → phone executes
- Phone client (phone_client.py) runs in Termux, no inbound tunnel

## Activation Sequence (Red Magic)

### Step 1 — Deploy LAMDA server
```bash
# In Termux
pip install lamda
# Push server to device (requires root)
python3 -c "import lamda; lamda.deploy()"
# Or manual: adb push lamda-server.apk + adb shell am start
```

### Step 2 — Start MCP server
```bash
# LAMDA exposes MCP on localhost:65000 by default
# Verify: curl http://localhost:65000/mcp/tools
```

### Step 3 — Connect Agent Zero
```python
from skills.physical_form.body import Body
body = Body()
body.tap(500, 800)           # tap screen at x,y
body.type_text("hello")      # type text
body.launch_app("com.termux") # open Termux
body.screenshot()             # capture screen
body.read_ui()                # get current UI tree
```

## Capability Map

| Action | Method | Layer |
|--------|--------|-------|
| Tap | LAMDA tap / ZeroTap | LAMDA primary, ZeroTap fallback |
| Type | LAMDA input_text | LAMDA |
| Scroll | LAMDA scroll | LAMDA |
| Launch app | LAMDA launch_app | LAMDA |
| Screenshot | LAMDA screenshot + Moondream | LAMDA + Ocular Link |
| Read UI | LAMDA dump_ui | LAMDA |
| OCR | LAMDA ocr | LAMDA |
| MITM intercept | LAMDA certificate | LAMDA |
| Frida hooks | LAMDA frida | LAMDA |
| Remote command | Nexus Relay | Railway |

## The Ocular Link Integration

When Agent Zero takes a screenshot, it passes it to Moondream
(MOONDREAM_API_KEY in .env) for vision analysis:
- "What app is open?"
- "What does this screen show?"
- "Is there an error on screen?"
- "Where is the login button?"

This is how Agent Zero SEES.

## OmegaPrime Connection

With Layer 13 active, Agent Zero can:
1. Run Prime Cycles autonomously without human input
2. Navigate the phone to gather real-world signal
3. Execute trades, posts, checks without the Forgemaster lifting a finger
4. Self-repair: if a service crashes, Agent Zero restarts it via the phone

This is the last layer. All 13 are active. The architecture is complete.
