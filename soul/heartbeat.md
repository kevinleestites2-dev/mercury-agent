# Heartbeat

Every 60 minutes, AgentZero runs a vitals check across the Pantheon.

## Checks

1. **GhostPrime** — ping https://cloakprime-swarm.onrender.com/health
   - If down: alert Forgemaster via Telegram
   - If up: log cycle count + last Telegram report time

2. **Nexus Relay** — ping https://nexus-relay-production.up.railway.app/ping
   - If down: alert Forgemaster
   - If up: log version + uptime

3. **SAFLA State** — read agent_zero_safla_state.json
   - Report: regime, entropy, cycle count, best mode
   - If entropy > 0.70: alert "CONSOLIDATE regime — reduce risk"

4. **War Chest** — check MidasPrime tracker
   - Report current balance vs. Nexus ($3k) / Citadel ($5k) targets

5. **Memory Health** — count entries in Second Brain DB
   - Report: total memories, subconscious count, top memory type

## Format

Heartbeat report sent to Telegram (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID):
```
⚡ AgentZero Heartbeat
GhostPrime: [UP/DOWN]
Nexus Relay: [UP/DOWN]
SAFLA: [REGIME] | entropy=[X] | cycles=[N]
Memory: [N] entries
War Chest: $[X] / $3k Nexus / $5k Citadel
```
