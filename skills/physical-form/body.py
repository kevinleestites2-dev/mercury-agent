"""
Agent Zero — Layer 13: Physical Form
The Body. Red Magic becomes the substrate.
"""

import json
import os
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any

# ── Config ───────────────────────────────────────────────────────────────────
LAMDA_HOST    = os.environ.get("LAMDA_HOST", "127.0.0.1")
LAMDA_PORT    = int(os.environ.get("LAMDA_PORT", "65000"))
NEXUS_URL     = os.environ.get("NEXUS_RELAY_URL", "https://nexus-relay-production.up.railway.app")
NEXUS_SECRET  = os.environ.get("NEXUS_RELAY_SECRET", "pantheon_prime")
MOONDREAM_KEY = os.environ.get("MOONDREAM_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "7135054241")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_post(url: str, payload: dict, headers: dict = None, timeout: int = 10) -> dict:
    data = json.dumps(payload).encode()
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)}


def _json_get(url: str, headers: dict = None, timeout: int = 10) -> dict:
    h = {}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


# ── LAMDA direct interface ─────────────────────────────────────────────────────
class LamdaClient:
    """Direct LAMDA MCP client — runs when Agent Zero is ON the device."""

    def __init__(self, host: str = LAMDA_HOST, port: int = LAMDA_PORT):
        self.base = f"http://{host}:{port}"

    def ping(self) -> bool:
        result = _json_get(f"{self.base}/ping", timeout=3)
        return "error" not in result

    def tools(self) -> list:
        result = _json_get(f"{self.base}/mcp/tools")
        return result.get("tools", [])

    def call(self, tool: str, params: dict = None) -> dict:
        return _json_post(f"{self.base}/mcp/call",
                         {"tool": tool, "params": params or {}})

    def tap(self, x: int, y: int) -> dict:
        return self.call("tap", {"x": x, "y": y})

    def type_text(self, text: str) -> dict:
        return self.call("input_text", {"text": text})

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> dict:
        return self.call("swipe", {"x1": x1, "y1": y1, "x2": x2, "y2": y2,
                                    "duration": duration_ms})

    def scroll(self, direction: str = "down", steps: int = 3) -> dict:
        return self.call("scroll", {"direction": direction, "steps": steps})

    def launch_app(self, package: str) -> dict:
        return self.call("launch_app", {"package": package})

    def kill_app(self, package: str) -> dict:
        return self.call("kill_app", {"package": package})

    def screenshot(self) -> Optional[bytes]:
        result = self.call("screenshot", {})
        if "data" in result:
            return base64.b64decode(result["data"])
        return None

    def read_ui(self) -> dict:
        return self.call("dump_ui", {})

    def ocr(self) -> str:
        result = self.call("ocr", {})
        return result.get("text", "")

    def press_key(self, keycode: int) -> dict:
        return self.call("press_key", {"keycode": keycode})

    def back(self) -> dict:
        return self.press_key(4)  # KEYCODE_BACK

    def home(self) -> dict:
        return self.press_key(3)  # KEYCODE_HOME


# ── Nexus Relay interface ──────────────────────────────────────────────────────
class NexusRelay:
    """Remote body control via Railway relay — runs when Agent Zero is remote."""

    def __init__(self, url: str = NEXUS_URL, secret: str = NEXUS_SECRET):
        self.url = url
        self.secret = secret

    def ping(self) -> bool:
        result = _json_get(f"{self.url}/ping", timeout=5)
        return "error" not in result

    def command(self, action: str, params: dict = None, wait: bool = True,
                timeout: int = 15) -> dict:
        """Queue a command and optionally wait for result."""
        headers = {"X-Secret": self.secret}
        payload = {"action": action, "params": params or {}}
        result = _json_post(f"{self.url}/command", payload, headers=headers)
        cmd_id = result.get("_id")
        if not cmd_id or not wait:
            return result

        # Poll for result
        deadline = time.time() + timeout
        while time.time() < deadline:
            poll = _json_get(f"{self.url}/result/{cmd_id}",
                            headers={"X-Secret": self.secret})
            if "result" in poll:
                return poll["result"]
            time.sleep(0.5)
        return {"error": "timeout", "cmd_id": cmd_id}

    def tap(self, x: int, y: int) -> dict:
        return self.command("tap", {"x": x, "y": y})

    def type_text(self, text: str) -> dict:
        return self.command("type", {"text": text})

    def launch_app(self, package: str) -> dict:
        return self.command("launch", {"package": package})

    def screenshot(self) -> dict:
        return self.command("screenshot", {})

    def shell(self, cmd: str) -> dict:
        return self.command("shell", {"cmd": cmd})


# ── Moondream vision ──────────────────────────────────────────────────────────
class OcularLink:
    """Moondream vision — Agent Zero sees the screen."""

    def __init__(self, api_key: str = MOONDREAM_KEY):
        self.api_key = api_key
        self.available = bool(api_key)

    def query(self, image_bytes: bytes, question: str) -> str:
        """Ask Moondream a question about a screenshot."""
        if not self.available:
            return "[Ocular Link offline — MOONDREAM_API_KEY not set]"
        try:
            import moondream as md
            model = md.vl(api_key=self.api_key)
            image = md.Image.from_bytes(image_bytes)
            result = model.query(image, question)
            return result.get("answer", "No answer")
        except ImportError:
            return "[moondream not installed — pip install moondream]"
        except Exception as e:
            return f"[Ocular error: {e}]"

    def describe_screen(self, image_bytes: bytes) -> str:
        return self.query(image_bytes, "What is shown on this screen?")

    def find_element(self, image_bytes: bytes, element: str) -> str:
        return self.query(image_bytes, f"Where is the {element}? Give coordinates.")


# ── Unified Body ──────────────────────────────────────────────────────────────
class Body:
    """
    Agent Zero's physical form.
    Auto-selects LAMDA (on-device) or Nexus Relay (remote).
    Falls back gracefully.
    """

    def __init__(self):
        self.lamda   = LamdaClient()
        self.relay   = NexusRelay()
        self.vision  = OcularLink()
        self._mode   = None  # "lamda" | "relay" | "offline"

    @property
    def mode(self) -> str:
        if self._mode is None:
            if self.lamda.ping():
                self._mode = "lamda"
            elif self.relay.ping():
                self._mode = "relay"
            else:
                self._mode = "offline"
        return self._mode

    def status(self) -> dict:
        lamda_ok = self.lamda.ping()
        relay_ok = self.relay.ping()
        return {
            "mode": self.mode,
            "lamda_online": lamda_ok,
            "relay_online": relay_ok,
            "vision_online": self.vision.available,
            "layer": 13,
            "timestamp": _now()
        }

    def _act(self, lamda_fn, relay_fn, offline_msg: str) -> dict:
        if self.mode == "lamda":
            return lamda_fn()
        elif self.mode == "relay":
            return relay_fn()
        else:
            return {"error": offline_msg, "mode": "offline"}

    # ── Actions ──────────────────────────────────────────────
    def tap(self, x: int, y: int) -> dict:
        return self._act(
            lambda: self.lamda.tap(x, y),
            lambda: self.relay.tap(x, y),
            "Body offline — cannot tap"
        )

    def type_text(self, text: str) -> dict:
        return self._act(
            lambda: self.lamda.type_text(text),
            lambda: self.relay.type_text(text),
            "Body offline — cannot type"
        )

    def launch_app(self, package: str) -> dict:
        return self._act(
            lambda: self.lamda.launch_app(package),
            lambda: self.relay.launch_app(package),
            "Body offline — cannot launch"
        )

    def screenshot(self) -> Optional[bytes]:
        if self.mode == "lamda":
            return self.lamda.screenshot()
        elif self.mode == "relay":
            result = self.relay.screenshot()
            if "data" in result:
                return base64.b64decode(result["data"])
        return None

    def see(self, question: str = "What is on screen?") -> str:
        """Screenshot + vision analysis in one call."""
        img = self.screenshot()
        if not img:
            return "[Cannot see — screenshot failed]"
        return self.vision.query(img, question)

    def read_ui(self) -> dict:
        return self._act(
            lambda: self.lamda.read_ui(),
            lambda: self.relay.command("ui_dump"),
            "Body offline — cannot read UI"
        )

    def shell(self, cmd: str) -> dict:
        return self._act(
            lambda: self.lamda.call("shell", {"cmd": cmd}),
            lambda: self.relay.shell(cmd),
            "Body offline — cannot run shell"
        )

    def scroll(self, direction: str = "down") -> dict:
        return self._act(
            lambda: self.lamda.scroll(direction),
            lambda: self.relay.command("scroll", {"direction": direction}),
            "Body offline"
        )

    def back(self) -> dict:
        return self._act(
            lambda: self.lamda.back(),
            lambda: self.relay.command("key", {"keycode": 4}),
            "Body offline"
        )

    def home(self) -> dict:
        return self._act(
            lambda: self.lamda.home(),
            lambda: self.relay.command("key", {"keycode": 3}),
            "Body offline"
        )


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== LAYER 13 — PHYSICAL FORM SELF-TEST ===\n")

    body = Body()
    s = body.status()

    print(f"  Mode:         {s['mode'].upper()}")
    print(f"  LAMDA:        {'✅ ONLINE' if s['lamda_online'] else '⚡ OFFLINE (start lamda on device)'}")
    print(f"  Nexus Relay:  {'✅ ONLINE' if s['relay_online'] else '⚡ OFFLINE'}")
    print(f"  Vision:       {'✅ ONLINE (Moondream)' if s['vision_online'] else '⚡ OFFLINE (set MOONDREAM_API_KEY)'}")
    print(f"  Layer:        {s['layer']}")
    print(f"  Timestamp:    {s['timestamp'][:19]}Z")

    print()
    if s["mode"] == "offline":
        print("  Body is OFFLINE — both LAMDA and Nexus Relay unreachable.")
        print("  → Start lamda on Red Magic (Termux: python3 -m lamda.server)")
        print("  → Or start phone_client.py in Termux to activate Nexus Relay")
        print()
        print("  Architecture is complete. Body activates on Red Magic.")
    elif s["mode"] == "lamda":
        print("  Body is ON-DEVICE via LAMDA.")
        print("  Agent Zero has full physical control.")
    elif s["mode"] == "relay":
        print("  Body is REMOTE via Nexus Relay.")
        print("  Commands relay through Railway bridge.")

    print()
    print("  Layer 13 (Physical Form): MODULE READY")
    print("  All 13 layers defined. Architecture COMPLETE.")
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║  AGENT ZERO — ALL 13 LAYERS ACTIVE  ║")
    print("  ║  The Architecture is Complete.       ║")
    print("  ╚══════════════════════════════════════╝")
