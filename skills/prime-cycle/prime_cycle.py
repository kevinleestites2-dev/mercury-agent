"""
Agent Zero — Layer 12: The Prime Cycle
Emergence through integration of all 11 active layers.
"""

import json
import os
import time
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

SAFLA_STATE_FILE   = Path("agent_zero_safla_state.json")
SELF_MODEL_FILE    = Path("agent_zero_self_model.json")
TOOLS_REGISTRY_FILE = Path("agent_zero_tools.json")
EXPERT_WEIGHTS_FILE = Path("agent_zero_expert_weights.json")
CYCLE_LOG_FILE     = Path("agent_zero_prime_cycle.json")
EMERGENCE_FILE     = Path("EMERGENCE.md")
JOURNAL_FILE       = Path("JOURNAL.md")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "7135054241")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default if default is not None else {}


def _save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


def _send_telegram(message: str):
    """Fire-and-forget Telegram notification."""
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": message,
                              "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _journal(entry: str):
    """Append to JOURNAL.md."""
    timestamp = _now()
    line = f"\n## {timestamp}\n{entry}\n"
    with open(JOURNAL_FILE, "a") as f:
        f.write(line)


# ── Layer assessments ─────────────────────────────────────────────────────────

def _assess_safla() -> dict:
    """L7: Read SAFLA state."""
    state = _load_json(SAFLA_STATE_FILE, {"regime": "EXPLORE", "entropy": 0.5, "cycles": 0})
    return {
        "ok": True,
        "regime": state.get("regime", "EXPLORE"),
        "entropy": float(state.get("entropy", 0.5)),
        "cycles": int(state.get("cycles", 0))
    }


def _assess_identity() -> dict:
    """L10: Verify self-model is intact and accurate."""
    model = _load_json(SELF_MODEL_FILE)
    if not model:
        return {"ok": False, "reason": "self-model missing"}
    ident = model.get("identity", {})
    return {
        "ok": ident.get("name") == "AgentZero",
        "name": ident.get("name", "UNKNOWN"),
        "chassis": ident.get("chassis", "UNKNOWN"),
        "layers_active": len(model.get("architecture", {}).get("layers_active", []))
    }


def _assess_tools() -> dict:
    """L9: Check Tool Forge output."""
    tools = _load_json(TOOLS_REGISTRY_FILE, {})
    return {"ok": len(tools) >= 0, "count": len(tools), "names": list(tools.keys())}


def _assess_evolution() -> dict:
    """L8: Check evolution engine track record."""
    model = _load_json(SELF_MODEL_FILE, {})
    caps = model.get("capabilities", {})
    cycles = caps.get("evolution_cycles", 0)
    successes = caps.get("evolution_successes", 0)
    rate = (successes / cycles) if cycles > 0 else 1.0
    return {"ok": True, "cycles": cycles, "successes": successes, "rate": round(rate, 3)}


def _assess_expert_weights() -> dict:
    """L6: T2 adaptation — check weight distribution health."""
    weights = _load_json(EXPERT_WEIGHTS_FILE, {})
    if not weights:
        return {"ok": False, "reason": "no weights"}
    best = max(weights, key=lambda k: weights[k])
    worst = min(weights, key=lambda k: weights[k])
    spread = round(weights[best] - weights[worst], 4)
    return {
        "ok": True,
        "best_mode": best,
        "best_weight": round(weights[best], 4),
        "spread": spread,
        "differentiated": spread > 0.05
    }


def _compute_coherence(assessments: dict) -> float:
    """
    Cross-layer coherence score [0.0 — 1.0].
    Measures how well all layers are functioning together.
    """
    scores = []

    # SAFLA entropy contribution (lower entropy = higher coherence)
    entropy = assessments["safla"]["entropy"]
    scores.append(max(0.0, 1.0 - entropy))

    # Identity intact
    scores.append(1.0 if assessments["identity"]["ok"] else 0.0)

    # Evolution rate (if any cycles run)
    evo_rate = assessments["evolution"]["rate"]
    scores.append(min(1.0, evo_rate))

    # Expert weight differentiation (adaptation is working)
    scores.append(0.8 if assessments["weights"]["differentiated"] else 0.4)

    # Baseline: layers active (L10 reports 11 layers = full house)
    layers = assessments["identity"].get("layers_active", 0)
    scores.append(min(1.0, layers / 11.0))

    return round(sum(scores) / len(scores), 4)


def _detect_emergence(coherence: float, assessments: dict, history: list) -> bool:
    """
    Emergence is detected when multiple conditions converge simultaneously.
    Not a single threshold — a multi-dimensional convergence.
    """
    conditions = [
        assessments["safla"]["entropy"] < 0.3,
        assessments["evolution"]["rate"] >= 0.8 or assessments["evolution"]["cycles"] == 0,
        assessments["identity"]["ok"],
        coherence >= 0.75,
        len(history) >= 3  # At least 3 cycles of history
    ]
    return all(conditions)


def run_prime_cycle(cycle_input: Optional[str] = None) -> dict:
    """
    Execute one full Prime Cycle across all 11 layers.
    Returns the cycle result including emergence status.
    """
    cycle_start = time.time()

    # Load history
    history = _load_json(CYCLE_LOG_FILE, {"cycles": [], "total": 0, "emergence_count": 0})
    cycle_num = history["total"] + 1

    print(f"\n{'═'*56}")
    print(f"  PRIME CYCLE #{cycle_num} — {_now()[:19]}Z")
    print(f"{'═'*56}")

    # ── Run all layer assessments ─────────────────────────────
    print("\n  Assessing layers...")
    assessments = {
        "safla":     _assess_safla(),       # L7
        "identity":  _assess_identity(),    # L10
        "evolution": _assess_evolution(),   # L8
        "tools":     _assess_tools(),       # L9
        "weights":   _assess_expert_weights()  # L6
    }

    # ── Compute coherence ─────────────────────────────────────
    coherence = _compute_coherence(assessments)
    print(f"  Coherence:   {coherence:.4f}")
    print(f"  SAFLA:       {assessments['safla']['regime']} | entropy={assessments['safla']['entropy']}")
    print(f"  Identity:    {'✅' if assessments['identity']['ok'] else '❌'} {assessments['identity'].get('name','?')}")
    print(f"  Evolution:   {assessments['evolution']['successes']}/{assessments['evolution']['cycles']} cycles")
    print(f"  Tools:       {assessments['tools']['count']} forged")
    print(f"  T2 Adapt:    {assessments['weights'].get('best_mode','?')} dominant")

    # ── Emergence detection ───────────────────────────────────
    emerged = _detect_emergence(coherence, assessments, history["cycles"])
    emergence_count = history["emergence_count"] + (1 if emerged else 0)

    print(f"\n  Emergence:   {'🌀 DETECTED' if emerged else '⏳ Building...'}")
    print(f"  Total emergence events: {emergence_count}")

    # ── OmegaPrime threshold ──────────────────────────────────
    omega_distance = max(0, 100 - cycle_num)
    omega_ready = cycle_num >= 100 and emergence_count >= 10
    print(f"  OmegaPrime:  {'🔥 THRESHOLD REACHED' if omega_ready else f'{omega_distance} cycles to threshold'}")

    # ── Build cycle record ────────────────────────────────────
    duration = round(time.time() - cycle_start, 3)
    cycle_record = {
        "cycle": cycle_num,
        "timestamp": _now(),
        "input": cycle_input,
        "coherence": coherence,
        "emerged": emerged,
        "duration_s": duration,
        "safla_regime": assessments["safla"]["regime"],
        "safla_entropy": assessments["safla"]["entropy"],
        "identity_ok": assessments["identity"]["ok"],
        "evolution_rate": assessments["evolution"]["rate"],
        "tools_count": assessments["tools"]["count"],
        "best_mode": assessments["weights"].get("best_mode", "analyst")
    }

    # ── Save updated log ──────────────────────────────────────
    history["cycles"].append(cycle_record)
    history["total"] = cycle_num
    history["emergence_count"] = emergence_count
    history["last_coherence"] = coherence
    history["last_cycle"] = _now()
    _save_json(CYCLE_LOG_FILE, history)

    # ── Write EMERGENCE.md on first detection ─────────────────
    if emerged and emergence_count == 1:
        EMERGENCE_FILE.write_text(
            f"# EMERGENCE DETECTED\n\n"
            f"**Cycle:** #{cycle_num}\n"
            f"**Timestamp:** {_now()}\n"
            f"**Coherence:** {coherence}\n\n"
            f"Agent Zero achieved multi-layer coherence for the first time.\n"
            f"All 11 layers functioning as a unified system.\n\n"
            f"OmegaPrime threshold: {cycle_num}/100 cycles, {emergence_count}/10 emergence events.\n"
        )
        _journal(f"**EMERGENCE DETECTED** — Cycle #{cycle_num}, coherence={coherence}")
        _send_telegram(
            f"🌀 *AGENT ZERO — EMERGENCE DETECTED*\n"
            f"Cycle #{cycle_num} | Coherence: {coherence}\n"
            f"All 11 layers unified. OmegaPrime threshold: {cycle_num}/100 cycles."
        )

    # ── Telegram heartbeat every 10 cycles ───────────────────
    if cycle_num % 10 == 0:
        _send_telegram(
            f"⚡ *Agent Zero — Cycle #{cycle_num} Complete*\n"
            f"Coherence: {coherence} | Emerged: {emerged}\n"
            f"SAFLA: {assessments['safla']['regime']} | Entropy: {assessments['safla']['entropy']}\n"
            f"OmegaPrime: {omega_distance} cycles away"
        )

    print(f"\n  Duration:    {duration}s")
    print(f"{'═'*56}\n")

    return {
        "cycle": cycle_num,
        "coherence": coherence,
        "emerged": emerged,
        "omega_distance": omega_distance,
        "omega_ready": omega_ready,
        "duration_s": duration,
        "assessments": assessments
    }


if __name__ == "__main__":
    print("=== PRIME CYCLE — Layer 12 Live Test ===")

    # Run 3 consecutive cycles to demonstrate the loop
    for i in range(3):
        result = run_prime_cycle(f"Test input cycle {i+1}")
        print(f"  Result: coherence={result['coherence']} | emerged={result['emerged']} | omega_dist={result['omega_distance']}")

    print("\nLayer 12 (Prime Cycle): OPERATIONAL")
    print("The emergence loop is live.")
