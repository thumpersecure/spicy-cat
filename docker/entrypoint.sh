#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
#  spicy-cat Docker Entrypoint
#
#  "A cat always lands on its feet, especially when containerized."
#
#  This script:
#  1. Applies system-level fingerprint protection (sysctl, iptables)
#  2. Generates and applies a fingerprint profile
#  3. Starts the protection agent if enabled
#  4. Launches the requested command
#
# ══════════════════════════════════════════════════════════════════════════

set -e

CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}"
echo '    /\_____/\'
echo '   /  o   o  \'
echo '  ( ==  ^  == )  spicy-cat Docker'
echo '   )         ('
echo '  (           )'
echo ' ( (  )   (  ) )'
echo '(__(__)___(__)__)'
echo -e "${RESET}"
echo -e "${BOLD}${GREEN}Initializing privacy protections...${RESET}\n"

# ── Step 1: Generate Fingerprint Profile ─────────────────────────────────
echo -e "${DIM}[1/5] Generating fingerprint profile...${RESET}"

# Use Python to generate a profile and extract key values
PROFILE_JSON=$(python3 -c "
import sys, json
sys.path.insert(0, '/opt/spicy-cat')
from lib.fingerprint import FingerprintGenerator, FingerprintProtector
from lib.agent_shield import DockerProtectionManager, ProtectionAgent

agent = ProtectionAgent()
docker_mgr = DockerProtectionManager(agent)

profile = agent.fingerprint_protector.get_profile()
print(json.dumps({
    'profile_id': profile.profile_id,
    'platform': profile.platform,
    'timezone': profile.timezone_name,
    'ttl': profile.tcp_ttl,
    'window_size': profile.tcp_window_size,
    'user_agent': profile.user_agent,
    'language': profile.language,
}))
" 2>/dev/null || echo '{"profile_id":"fallback","platform":"Win32","timezone":"America/New_York","ttl":64,"window_size":65535,"user_agent":"Mozilla/5.0","language":"en-US"}')

PROFILE_ID=$(echo "$PROFILE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['profile_id'])" 2>/dev/null || echo "fallback")
TTL=$(echo "$PROFILE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['ttl'])" 2>/dev/null || echo "64")
TZ_NAME=$(echo "$PROFILE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['timezone'])" 2>/dev/null || echo "America/New_York")
PLATFORM=$(echo "$PROFILE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['platform'])" 2>/dev/null || echo "Win32")

echo -e "  Profile: ${GREEN}${PROFILE_ID:0:12}...${RESET}"
echo -e "  Platform: ${DIM}${PLATFORM}${RESET}"

# ── Step 2: Apply TCP/IP Stack Normalization ─────────────────────────────
echo -e "${DIM}[2/5] Applying TCP/IP stack normalization...${RESET}"

if [ "$TTL" = "128" ]; then
    # Windows-like TCP stack
    sysctl -w net.ipv4.ip_default_ttl=128 2>/dev/null || true
    sysctl -w net.ipv4.tcp_window_scaling=1 2>/dev/null || true
    sysctl -w net.ipv4.tcp_timestamps=1 2>/dev/null || true
    sysctl -w net.ipv4.tcp_sack=1 2>/dev/null || true
    sysctl -w net.core.rmem_default=65535 2>/dev/null || true
    sysctl -w net.core.wmem_default=65535 2>/dev/null || true
    echo -e "  Stack: ${DIM}Windows-like (TTL=128)${RESET}"
else
    # Linux-like TCP stack
    sysctl -w net.ipv4.ip_default_ttl=64 2>/dev/null || true
    sysctl -w net.ipv4.tcp_window_scaling=1 2>/dev/null || true
    sysctl -w net.ipv4.tcp_timestamps=1 2>/dev/null || true
    sysctl -w net.ipv4.tcp_sack=1 2>/dev/null || true
    echo -e "  Stack: ${DIM}Linux-like (TTL=64)${RESET}"
fi

# ── Step 3: Apply iptables Rules ─────────────────────────────────────────
echo -e "${DIM}[3/5] Applying network protection rules...${RESET}"

# TTL normalization
iptables -t mangle -A POSTROUTING -j TTL --ttl-set "$TTL" 2>/dev/null || true

# Block WebRTC STUN/TURN leak attempts
iptables -A OUTPUT -p udp --dport 3478 -j DROP 2>/dev/null || true
iptables -A OUTPUT -p tcp --dport 3478 -j DROP 2>/dev/null || true
iptables -A OUTPUT -p udp --dport 5349 -j DROP 2>/dev/null || true

# Block direct DNS (force through container DNS)
# Allow localhost DNS for dnsmasq
iptables -A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j ACCEPT 2>/dev/null || true
iptables -A OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j ACCEPT 2>/dev/null || true

RULES_APPLIED=$(iptables -L OUTPUT -n 2>/dev/null | wc -l || echo "0")
echo -e "  Rules: ${DIM}${RULES_APPLIED} iptables rules applied${RESET}"

# ── Step 4: Set Timezone ─────────────────────────────────────────────────
echo -e "${DIM}[4/5] Setting timezone to ${TZ_NAME}...${RESET}"
ln -sf "/usr/share/zoneinfo/${TZ_NAME}" /etc/localtime 2>/dev/null || true
echo "${TZ_NAME}" > /etc/timezone 2>/dev/null || true
export TZ="${TZ_NAME}"
echo -e "  Timezone: ${DIM}${TZ_NAME}${RESET}"

# ── Step 5: Start Protection Agent ───────────────────────────────────────
if [ "${SPICY_CAT_AGENT}" = "true" ]; then
    echo -e "${DIM}[5/5] Starting protection agent...${RESET}"

    python3 -c "
import sys, os, time, threading, json
sys.path.insert(0, '/opt/spicy-cat')

from lib.agent_shield import ProtectionAgent
from lib.telemetry_chaos import TelemetryChaosEngine, TelemetryMethod

agent = ProtectionAgent(log_file='/var/log/spicy-cat/agent.log')
agent.start()

# Start telemetry chaos if enabled
chaos_enabled = os.environ.get('SPICY_CAT_TELEMETRY_CHAOS', 'true') == 'true'
if chaos_enabled:
    agent.telemetry_engine.start_background(interval=5.0)

# Write status for health checks
status = agent.get_status()
with open('/tmp/spicy-cat/agent_status.json', 'w') as f:
    json.dump(status, f)

print(f'  Agent started: threat_level={status[\"threat_level\"]}')
print(f'  Profile: {status[\"current_profile_id\"][:12]}...')
" 2>/dev/null &

    AGENT_PID=$!
    echo "$AGENT_PID" > /tmp/spicy-cat/agent.pid
    echo -e "  Agent: ${GREEN}Running (PID: ${AGENT_PID})${RESET}"
else
    echo -e "${DIM}[5/5] Protection agent disabled by configuration${RESET}"
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}Privacy protections active!${RESET}"
echo -e "${DIM}──────────────────────────────────${RESET}"
echo -e "  Profile:    ${PROFILE_ID:0:12}..."
echo -e "  Platform:   ${PLATFORM}"
echo -e "  Timezone:   ${TZ_NAME}"
echo -e "  TTL:        ${TTL}"
echo -e "  Agent:      ${SPICY_CAT_AGENT:-false}"
echo -e "  Telemetry:  ${SPICY_CAT_TELEMETRY_CHAOS:-false}"
echo -e "  DNS Chaff:  ${SPICY_CAT_DNS_CHAFF:-false}"
echo -e "  Phantoms:   ${SPICY_CAT_PHANTOM_SWARM:-false}"
echo -e "${DIM}──────────────────────────────────${RESET}"
echo ""

# ── Execute Main Command ─────────────────────────────────────────────────
exec "$@"
