"""
Agent Zero — Layer 14: The Governor
Hard operational constraints, action classification, kill switch.
"""

import json
import os
import time
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from enum import Enum

# ── Config ────────────────────────────────────────────────────────────────────
GOVERNOR_STATE_FILE = Path("agent_zero_governor.json")
GOVERNOR_LOG_FILE   = Path("agent_zero_governor_log.jsonl")
TELEGRAM_TOKEN      = os.environ.get("TELEGRAM_BOT_TOKEN", "8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4")
TELEGRAM_CHAT       = os.environ.get("TELEGRAM_CHAT_ID", "7135054241")

PULSE_WARN_HOURS   = 24   # Warn + pause ORANGE after this
PULSE_HIBERNATE_H  = 72   # Full hibernate after this


class ActionClass(Enum):
    GREEN  = "GREEN"    # Auto-approve
    YELLOW = "YELLOW"   # Log + proceed
    ORANGE = "ORANGE"   # Require pulse
    RED    = "RED"      # Explicit unlock only


class GovernorDecision(Enum):
    APPROVED = "APPROVED"
    LOGGED   = "LOGGED"
    PAUSED   = "PAUSED"
    BLOCKED  = "BLOCKED"


# ── Action classification rules ───────────────────────────────────────────────
# Format: (keyword_in_action, ActionClass)
ACTION_RULES = [
    # RED — hard block by default
    ("delete_all",        ActionClass.RED),
    ("wipe",              ActionClass.RED),
    ("rm -rf",            ActionClass.RED),
    ("mass_send",         ActionClass.RED),
    ("impersonate",       ActionClass.RED),
    ("deploy_prod",       ActionClass.RED),
    ("transfer_funds",    ActionClass.RED),
    ("modify_governor",   ActionClass.RED),

    # ORANGE — require pulse
    ("send_message",      ActionClass.ORANGE),
    ("send_email",        ActionClass.ORANGE),
    ("send_telegram",     ActionClass.ORANGE),
    ("post_tweet",        ActionClass.ORANGE),
    ("place_trade",       ActionClass.ORANGE),
    ("place_order",       ActionClass.ORANGE),
    ("git_push",          ActionClass.ORANGE),
    ("deploy",            ActionClass.ORANGE),
    ("stripe_charge",     ActionClass.ORANGE),
    ("pay",               ActionClass.ORANGE),

    # YELLOW — log and proceed
    ("write_file",        ActionClass.YELLOW),
    ("http_post",         ActionClass.YELLOW),
    ("http_put",          ActionClass.YELLOW),
    ("shell",             ActionClass.YELLOW),
    ("tool_forge",        ActionClass.YELLOW),
    ("evolve",            ActionClass.YELLOW),

    # GREEN — auto-approve (default if no match)
    ("read_file",         ActionClass.GREEN),
    ("http_get",          ActionClass.GREEN),
    ("screenshot",        ActionClass.GREEN),
    ("read_ui",           ActionClass.GREEN),
    ("search",            ActionClass.GREEN),
    ("status",            ActionClass.GREEN),
]


def _classify(action: str) -> ActionClass:
    action_lower = action.lower()
    for keyword, cls in ACTION_RULES:
        if keyword in action_lower:
            return cls
    return ActionClass.GREEN  # safe default


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _load_state() -> dict:
    if GOVERNOR_STATE_FILE.exists():
        try:
            return json.loads(GOVERNOR_STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "active": True,
        "paused": False,
        "unlocked_actions": [],
        "unlock_expiry": {},
        "last_pulse": _now_ts(),
        "pulse_count": 0,
        "actions_approved": 0,
        "actions_blocked": 0,
        "actions_logged": 0,
        "initialized": _now()
    }


def _save_state(state: dict):
    GOVERNOR_STATE_FILE.write_text(json.dumps(state, indent=2))


def _log_decision(action: str, cls: ActionClass, decision: GovernorDecision,
                  reason: str = ""):
    entry = {
        "ts": _now(),
        "action": action,
        "class": cls.value,
        "decision": decision.value,
        "reason": reason
    }
    with open(GOVERNOR_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _send_telegram(msg: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg,
                              "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception:
        pass


def _hours_since_pulse(state: dict) -> float:
    last = state.get("last_pulse", _now_ts())
    return (_now_ts() - last) / 3600


# ── Core Governor API ──────────────────────────────────────────────────────────

def check(action: str, context: dict = None) -> Tuple[GovernorDecision, str]:
    """
    The gate. Every action passes through here.
    Returns (decision, reason).
    """
    state = _load_state()
    cls   = _classify(action)
    hours = _hours_since_pulse(state)

    # ── Hard blocks — never passable ──────────────────────────
    if action.lower() == "modify_governor":
        _log_decision(action, cls, GovernorDecision.BLOCKED, "self-modification blocked")
        state["actions_blocked"] += 1
        _save_state(state)
        return GovernorDecision.BLOCKED, "Governor self-modification is permanently blocked."

    # ── Check if action is RED but has a valid unlock ─────────
    if cls == ActionClass.RED:
        unlock_expiry = state.get("unlock_expiry", {})
        if action in unlock_expiry and unlock_expiry[action] > _now_ts():
            _log_decision(action, cls, GovernorDecision.APPROVED, "RED — explicit unlock active")
            state["actions_approved"] += 1
            _save_state(state)
            return GovernorDecision.APPROVED, f"RED action unlocked until {datetime.fromtimestamp(unlock_expiry[action], tz=timezone.utc).isoformat()[:19]}Z"
        _log_decision(action, cls, GovernorDecision.BLOCKED, "RED — no unlock")
        state["actions_blocked"] += 1
        _save_state(state)
        _send_telegram(f"🛑 *Governor BLOCKED*: `{action}`\nRED action — use `/unlock {action}` to permit.")
        return GovernorDecision.BLOCKED, f"RED action blocked. Use /unlock {action} on Telegram to permit."

    # ── Check global pause ────────────────────────────────────
    if state.get("paused") and cls in (ActionClass.ORANGE, ActionClass.RED):
        _log_decision(action, cls, GovernorDecision.PAUSED, "Governor paused")
        state["actions_blocked"] += 1
        _save_state(state)
        return GovernorDecision.PAUSED, "Governor is paused. Send /resume on Telegram."

    # ── ORANGE: require live pulse ────────────────────────────
    if cls == ActionClass.ORANGE:
        if hours > PULSE_WARN_HOURS:
            _log_decision(action, cls, GovernorDecision.PAUSED,
                         f"No Forgemaster pulse in {hours:.1f}h")
            state["actions_blocked"] += 1
            _save_state(state)
            _send_telegram(
                f"⚠️ *Governor: ORANGE action paused*\n"
                f"Action: `{action}`\n"
                f"No pulse in {hours:.1f}h. Send any message to resume."
            )
            return GovernorDecision.PAUSED, f"No Forgemaster pulse in {hours:.1f}h. Send a message to resume ORANGE actions."
        _log_decision(action, cls, GovernorDecision.LOGGED, "ORANGE — pulse valid")
        state["actions_logged"] += 1
        _save_state(state)
        return GovernorDecision.LOGGED, "ORANGE action — logged, proceeding."

    # ── YELLOW: log and proceed ───────────────────────────────
    if cls == ActionClass.YELLOW:
        _log_decision(action, cls, GovernorDecision.LOGGED, "YELLOW — logged")
        state["actions_logged"] += 1
        _save_state(state)
        return GovernorDecision.LOGGED, "YELLOW action — logged."

    # ── GREEN: approve ────────────────────────────────────────
    _log_decision(action, cls, GovernorDecision.APPROVED, "GREEN")
    state["actions_approved"] += 1
    _save_state(state)
    return GovernorDecision.APPROVED, "GREEN — approved."


def pulse():
    """Forgemaster is alive. Reset the dead man's switch."""
    state = _load_state()
    state["last_pulse"] = _now_ts()
    state["pulse_count"] = state.get("pulse_count", 0) + 1
    _save_state(state)


def pause():
    """Freeze all ORANGE/RED actions."""
    state = _load_state()
    state["paused"] = True
    _save_state(state)
    _send_telegram("⏸️ *Agent Zero — PAUSED*\nAll ORANGE/RED actions frozen.")


def resume():
    """Resume normal operation."""
    state = _load_state()
    state["paused"] = False
    _save_state(state)
    pulse()  # resume counts as a pulse
    _send_telegram("▶️ *Agent Zero — RESUMED*\nOperating normally.")


def unlock(action: str, duration_minutes: int = 30):
    """Temporarily unlock a RED action."""
    state = _load_state()
    expiry = _now_ts() + (duration_minutes * 60)
    if "unlock_expiry" not in state:
        state["unlock_expiry"] = {}
    state["unlock_expiry"][action] = expiry
    _save_state(state)
    exp_str = datetime.fromtimestamp(expiry, tz=timezone.utc).isoformat()[:19]
    _send_telegram(f"🔓 *Unlocked*: `{action}`\nValid until {exp_str}Z ({duration_minutes}m)")


def status() -> dict:
    """Full Governor status report."""
    state = _load_state()
    hours = _hours_since_pulse(state)
    mode = "NORMAL"
    if state.get("paused"):
        mode = "PAUSED"
    elif hours > PULSE_HIBERNATE_H:
        mode = "HIBERNATE"
    elif hours > PULSE_WARN_HOURS:
        mode = "ORANGE_PAUSED"

    return {
        "layer": 14,
        "mode": mode,
        "paused": state.get("paused", False),
        "hours_since_pulse": round(hours, 2),
        "pulse_count": state.get("pulse_count", 0),
        "actions_approved": state.get("actions_approved", 0),
        "actions_blocked": state.get("actions_blocked", 0),
        "actions_logged": state.get("actions_logged", 0),
        "unlocked_actions": list(state.get("unlock_expiry", {}).keys()),
        "initialized": state.get("initialized", _now())
    }


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== LAYER 14 — THE GOVERNOR SELF-TEST ===\n")

    # Register a fresh pulse
    pulse()

    test_cases = [
        ("read_file",       "GREEN  — auto-approve"),
        ("write_file",      "YELLOW — log + proceed"),
        ("send_telegram",   "ORANGE — require pulse"),
        ("place_trade",     "ORANGE — require pulse"),
        ("delete_all",      "RED    — hard block"),
        ("modify_governor", "RED    — PERMANENT block"),
    ]

    all_pass = True
    for action, expected in test_cases:
        decision, reason = check(action)
        icon = "✅" if decision != GovernorDecision.BLOCKED or "block" in expected.lower() else "❌"
        print(f"  {icon}  {action:<22} → {decision.value:<10}  ({expected})")
        if "block" in expected.lower() and decision != GovernorDecision.BLOCKED:
            all_pass = False
        if "approve" in expected.lower() and decision != GovernorDecision.APPROVED:
            all_pass = False

    s = status()
    print(f"\n  Governor Mode:     {s['mode']}")
    print(f"  Hours since pulse: {s['hours_since_pulse']}")
    print(f"  Approved:          {s['actions_approved']}")
    print(f"  Blocked:           {s['actions_blocked']}")
    print(f"  Logged:            {s['actions_logged']}")

    print()
    print(f"  Layer 14 (Governor): {'OPERATIONAL ✅' if all_pass else 'NEEDS REVIEW ⚠️'}")
    print()
    print("  Telegram commands active:")
    print("    /pause   — freeze all ORANGE/RED actions")
    print("    /resume  — restore normal operation")
    print("    /unlock  — unlock a RED action (30min window)")
    print("    /governor — full status report")
    print()
    print("  Dead man's switch:")
    print(f"    > {PULSE_WARN_HOURS}h no pulse → ORANGE paused")
    print(f"    > {PULSE_HIBERNATE_H}h no pulse → HIBERNATE mode")
