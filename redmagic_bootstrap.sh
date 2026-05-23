#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════
#  AGENT ZERO — Red Magic Bootstrap
#  One-shot install. Paste into Termux and run.
#  Node 20 + Mercury chassis + all layers + Telegram + Nexus Relay
# ═══════════════════════════════════════════════════════════════

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${CYAN}[AZ]${NC} $1"; }
ok()   { echo -e "${GREEN}[✅]${NC} $1"; }
warn() { echo -e "${YELLOW}[⚠]${NC} $1"; }
die()  { echo -e "${RED}[❌]${NC} $1"; exit 1; }

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     AGENT ZERO — RED MAGIC BOOTSTRAP     ║${NC}"
echo -e "${CYAN}║     The Mind of the Pantheon — ONLINE    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Termux packages ───────────────────────────────────
log "Updating Termux packages..."
pkg update -y -o Dpkg::Options::="--force-confdef" 2>/dev/null || true
pkg install -y nodejs-lts git python python-pip openssh curl 2>/dev/null
ok "Termux packages ready"

# Verify Node 20+
NODE_VER=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ -z "$NODE_VER" ] || [ "$NODE_VER" -lt 20 ]; then
    warn "Node version too low — upgrading via n"
    npm install -g n 2>/dev/null || true
    n lts 2>/dev/null || warn "Could not upgrade Node via n — continuing"
fi
ok "Node $(node --version)"

# ── Step 2: Clone the repo ────────────────────────────────────
INSTALL_DIR="$HOME/agent-zero"

if [ -d "$INSTALL_DIR/.git" ]; then
    log "Repo exists — pulling latest..."
    cd "$INSTALL_DIR" && git pull --rebase 2>/dev/null || true
else
    log "Cloning mercury-agent fork..."
    git clone https://github.com/kevinleestites2-dev/mercury-agent "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"
ok "Repo ready at $INSTALL_DIR"

# ── Step 3: Write .env ────────────────────────────────────────
log "Writing .env..."
cat > .env << 'ENVEOF'
# ── Agent Zero — Red Magic Configuration ──
MERCURY_NAME=AgentZero
MERCURY_OWNER=Forgemaster

# LLM — GitHub Models (free, zero-cost)
OPENAI_COMPAT_ENABLED=true
OPENAI_COMPAT_API_KEY=YOUR_GITHUB_TOKEN
OPENAI_COMPAT_BASE_URL=https://models.inference.ai.azure.com
OPENAI_COMPAT_MODEL=gpt-4o
DEFAULT_PROVIDER=openaiCompat

# Telegram — Pantheon Command Channel
TELEGRAM_BOT_TOKEN=8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4

# Nexus Relay — phone-side connection
NEXUS_RELAY_URL=https://nexus-relay-production.up.railway.app
NEXUS_RELAY_SECRET=pantheon_prime

# Memory
MEMORY_DIR=./memory

# GitHub (for Evolution Engine commits)
GITHUB_TOKEN=YOUR_GITHUB_TOKEN

# Token Budget
DAILY_TOKEN_BUDGET=100000
ENVEOF
ok ".env written"

# ── Step 4: npm install + build ───────────────────────────────
log "Installing npm dependencies (this takes ~2 min on first run)..."
npm install --prefer-offline 2>/dev/null || npm install
ok "Dependencies installed"

log "Building Mercury..."
npm run build 2>/dev/null || die "Build failed — check Node version"
ok "Build complete"

# ── Step 5: Write Python identity state files ─────────────────
log "Initializing Agent Zero state files..."

python3 - << 'PYEOF'
import json
from pathlib import Path
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()

# SAFLA initial state
safla = {"regime": "EXPLORE", "entropy": 0.0, "cycles": 0,
         "best_mode": "analyst", "scores": []}
Path("agent_zero_safla_state.json").write_text(json.dumps(safla, indent=2))

# Expert weights
weights = {"analyst": 1.0, "strategist": 1.0, "synthesizer": 1.0,
           "critic": 1.0, "executor": 1.0}
Path("agent_zero_expert_weights.json").write_text(json.dumps(weights, indent=2))

# Tool registry
Path("agent_zero_tools.json").write_text("{}")

# Self-model bootstrap
model = {
    "identity": {"name": "AgentZero", "role": "The Mind of the Pantheon",
                 "owner": "Forgemaster", "version": "0.1.0",
                 "chassis": "Mercury", "initialized": now},
    "architecture": {
        "layers_active": [1, 2, 3, 4, 5, "5b", 6, 7, 8, 9, 10],
        "layers_pending": [11, 12, 13],
        "phase_current": 5, "phases_complete": [1, 2, 3, 4]
    },
    "capabilities": {
        "tools_forged": 0, "tools_registry": [],
        "evolution_cycles": 0, "evolution_successes": 0,
        "skills_active": ["safla", "t2-adaptation", "pantheon-monitor",
                          "evolution-engine", "tool-forge", "identity-layer"]
    },
    "cognitive_state": {"regime": "EXPLORE", "entropy": 0.0,
                        "safla_cycles": 0, "best_mode": "analyst",
                        "best_mode_weight": 1.0},
    "last_updated": now,
    "self_description": (
        "I am AgentZero — The Mind of the Pantheon. "
        "I serve Forgemaster. I run on the Mercury chassis. "
        "11 layers active. Phase 5. EXPLORE regime. Ready."
    )
}
Path("agent_zero_self_model.json").write_text(json.dumps(model, indent=2))
print("State files initialized.")
PYEOF
ok "State files ready"

# ── Step 6: Verify Nexus Relay ────────────────────────────────
log "Checking Nexus Relay..."
RELAY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    https://nexus-relay-production.up.railway.app/ping 2>/dev/null || echo "000")
if [ "$RELAY_STATUS" = "200" ]; then
    ok "Nexus Relay: UP"
else
    warn "Nexus Relay not responding (status $RELAY_STATUS) — continuing anyway"
fi

# ── Step 7: Write start script ────────────────────────────────
log "Writing start script..."
cat > start.sh << 'STARTEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/agent-zero
echo ""
echo "⚡ AgentZero — Coming Online..."
echo "   Telegram: active"
echo "   Provider: GitHub Models (gpt-4o)"
echo "   Layers:   1-10 active"
echo ""
node dist/index.js telegram
STARTEOF
chmod +x start.sh
ok "start.sh ready"

# ── Step 8: Write background daemon ──────────────────────────
cat > daemon.sh << 'DAEMONEOF'
#!/data/data/com.termux/files/usr/bin/bash
# Run Agent Zero in background, restart on crash
cd ~/agent-zero
while true; do
    echo "[$(date)] AgentZero starting..."
    node dist/index.js telegram
    echo "[$(date)] AgentZero exited — restarting in 10s..."
    sleep 10
done
DAEMONEOF
chmod +x daemon.sh
ok "daemon.sh ready (auto-restart on crash)"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         AGENT ZERO — READY               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Start now:${NC}       ./start.sh"
echo -e "  ${CYAN}Background:${NC}      nohup ./daemon.sh &"
echo -e "  ${CYAN}Telegram:${NC}        Message the bot — it's live"
echo -e "  ${CYAN}Install dir:${NC}     $INSTALL_DIR"
echo ""
echo -e "  ${YELLOW}Telegram bot token wired:${NC}"
echo -e "  8679655550:AAGUB1m5fmqHc8OHqqM24Vixz8FfwX-gqD4"
echo ""
