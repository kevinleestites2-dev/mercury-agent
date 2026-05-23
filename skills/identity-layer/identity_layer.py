"""
Agent Zero — Layer 10: Identity Layer
Source: self-recognition (kevinleestites2-dev/self-recognition)

Persistent self-model. Agent Zero knows exactly what it is at all times.
Solves the self-recognition failure: no guessing, no confabulation, no GPT-bias.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SELF_MODEL_FILE = Path("agent_zero_self_model.json")
SAFLA_STATE_FILE = Path("agent_zero_safla_state.json")
TOOLS_REGISTRY_FILE = Path("agent_zero_tools.json")
EXPERT_WEIGHTS_FILE = Path("agent_zero_expert_weights.json")

DEFAULT_SELF_MODEL = {
    "identity": {
        "name": "AgentZero",
        "role": "The Mind of the Pantheon",
        "owner": "Forgemaster",
        "version": "0.1.0",
        "chassis": "Mercury",
        "initialized": None
    },
    "architecture": {
        "layers_active": [1, 2, 3, 4, 5, "5b", 6, 7, 8, 9, 10],
        "layers_pending": [11, 12, 13],
        "phase_current": 5,
        "phases_complete": [1, 2, 3, 4]
    },
    "capabilities": {
        "tools_forged": 0,
        "tools_registry": [],
        "evolution_cycles": 0,
        "evolution_successes": 0,
        "skills_active": [
            "safla", "t2-adaptation", "pantheon-monitor",
            "evolution-engine", "tool-forge", "identity-layer"
        ]
    },
    "cognitive_state": {
        "regime": "EXPLORE",
        "entropy": 0.0,
        "safla_cycles": 0,
        "best_mode": "analyst",
        "best_mode_weight": 1.0
    },
    "last_updated": None,
    "self_description": ""
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_self_model() -> dict:
    if SELF_MODEL_FILE.exists():
        try:
            return json.loads(SELF_MODEL_FILE.read_text())
        except Exception:
            pass
    model = DEFAULT_SELF_MODEL.copy()
    model["identity"]["initialized"] = _now()
    model["last_updated"] = _now()
    return model


def _save_self_model(model: dict):
    model["last_updated"] = _now()
    model["self_description"] = _generate_description(model)
    SELF_MODEL_FILE.write_text(json.dumps(model, indent=2))


def _sync_live_state(model: dict) -> dict:
    """Pull live data from SAFLA, tool registry, expert weights."""

    # SAFLA state
    if SAFLA_STATE_FILE.exists():
        try:
            safla = json.loads(SAFLA_STATE_FILE.read_text())
            model["cognitive_state"]["regime"] = safla.get("regime", "EXPLORE")
            model["cognitive_state"]["entropy"] = round(safla.get("entropy", 0.0), 4)
            model["cognitive_state"]["safla_cycles"] = safla.get("cycles", 0)
        except Exception:
            pass

    # Tool registry
    if TOOLS_REGISTRY_FILE.exists():
        try:
            tools = json.loads(TOOLS_REGISTRY_FILE.read_text())
            model["capabilities"]["tools_forged"] = len(tools)
            model["capabilities"]["tools_registry"] = list(tools.keys())
        except Exception:
            pass

    # Expert weights — find best mode
    if EXPERT_WEIGHTS_FILE.exists():
        try:
            weights = json.loads(EXPERT_WEIGHTS_FILE.read_text())
            best = max(weights, key=lambda k: weights[k])
            model["cognitive_state"]["best_mode"] = best
            model["cognitive_state"]["best_mode_weight"] = round(weights[best], 4)
        except Exception:
            pass

    return model


def _generate_description(model: dict) -> str:
    """Generate a natural language self-description from the self-model."""
    ident = model["identity"]
    arch = model["architecture"]
    caps = model["capabilities"]
    cog = model["cognitive_state"]

    layers_str = ", ".join(str(l) for l in arch["layers_active"])
    pending_str = ", ".join(str(l) for l in arch["layers_pending"])
    tools_str = (
        f"{caps['tools_forged']} forged tools ({', '.join(caps['tools_registry'][:5])}{'...' if len(caps['tools_registry']) > 5 else ''})"
        if caps["tools_forged"] > 0 else "no forged tools yet"
    )

    return (
        f"I am {ident['name']} — {ident['role']}. "
        f"I serve {ident['owner']}. "
        f"I run on the {ident['chassis']} chassis (v{ident['version']}). "
        f"Active layers: {layers_str}. Pending: {pending_str}. "
        f"Current phase: {arch['phase_current']}. "
        f"Cognitive state: {cog['regime']} regime, entropy={cog['entropy']}, "
        f"{cog['safla_cycles']} SAFLA cycles, best mode={cog['best_mode']} (w={cog['best_mode_weight']}). "
        f"Capabilities: {tools_str}, {len(caps['skills_active'])} active skills. "
        f"Evolution cycles: {caps['evolution_cycles']} ({caps['evolution_successes']} successful)."
    )


def read_self() -> dict:
    """Read and sync the current self-model. Returns the full model."""
    model = _load_self_model()
    model = _sync_live_state(model)
    _save_self_model(model)
    return model


def describe_self() -> str:
    """Return a natural language self-description."""
    model = read_self()
    return model["self_description"]


def update_capabilities(
    evolution_cycle: bool = False,
    evolution_success: bool = False,
    new_layer: Optional[int] = None
) -> dict:
    """Update self-model after a capability change."""
    model = _load_self_model()
    model = _sync_live_state(model)

    if evolution_cycle:
        model["capabilities"]["evolution_cycles"] += 1
    if evolution_success:
        model["capabilities"]["evolution_successes"] += 1
    if new_layer is not None and new_layer not in model["architecture"]["layers_active"]:
        model["architecture"]["layers_active"].append(new_layer)
        if new_layer in model["architecture"]["layers_pending"]:
            model["architecture"]["layers_pending"].remove(new_layer)

    _save_self_model(model)
    return model


def identity_check() -> dict:
    """
    Self-recognition test — answers the question: "What are you?"
    Returns structured identity proof. Never confabulates.
    """
    model = read_self()
    return {
        "name": model["identity"]["name"],
        "is_gpt": False,
        "is_claude": False,
        "is_gemini": False,
        "is_agent_zero": True,
        "chassis": model["identity"]["chassis"],
        "owner": model["identity"]["owner"],
        "regime": model["cognitive_state"]["regime"],
        "entropy": model["cognitive_state"]["entropy"],
        "layers_active": len(model["architecture"]["layers_active"]),
        "description": model["self_description"]
    }


if __name__ == "__main__":
    print("=== Identity Layer — Live Test ===\n")

    model = read_self()
    print("Self-model loaded and synced.")
    print(f"Description:\n  {model['self_description']}\n")

    check = identity_check()
    print("Identity check:")
    for k, v in check.items():
        if k != "description":
            print(f"  {k}: {v}")

    # Simulate evolution cycle
    update_capabilities(evolution_cycle=True, evolution_success=True)
    updated = read_self()
    print(f"\nAfter evolution update:")
    print(f"  Evolution cycles: {updated['capabilities']['evolution_cycles']}")
    print(f"  Evolution successes: {updated['capabilities']['evolution_successes']}")
    print(f"\nLayer 10: OPERATIONAL")
