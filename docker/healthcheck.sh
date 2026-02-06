#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
#  spicy-cat Docker Health Check
#
#  Verifies that privacy protections are active and functioning.
# ══════════════════════════════════════════════════════════════════════════

ERRORS=0

# Check 1: Protection agent is running
if [ -f /tmp/spicy-cat/agent.pid ]; then
    AGENT_PID=$(cat /tmp/spicy-cat/agent.pid)
    if kill -0 "$AGENT_PID" 2>/dev/null; then
        echo "OK: Protection agent running (PID: $AGENT_PID)"
    else
        echo "WARN: Protection agent not running"
        ERRORS=$((ERRORS + 1))
    fi
else
    if [ "${SPICY_CAT_AGENT}" = "true" ]; then
        echo "WARN: Agent PID file not found"
        ERRORS=$((ERRORS + 1))
    else
        echo "OK: Agent disabled by configuration"
    fi
fi

# Check 2: iptables TTL normalization
if iptables -t mangle -L POSTROUTING 2>/dev/null | grep -q "TTL"; then
    echo "OK: TTL normalization active"
else
    echo "WARN: TTL normalization not detected"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: WebRTC STUN blocking
if iptables -L OUTPUT -n 2>/dev/null | grep -q "3478"; then
    echo "OK: WebRTC STUN blocked"
else
    echo "WARN: WebRTC STUN not blocked"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Agent status file exists and is recent
if [ -f /tmp/spicy-cat/agent_status.json ]; then
    AGE=$(( $(date +%s) - $(stat -c %Y /tmp/spicy-cat/agent_status.json 2>/dev/null || echo 0) ))
    if [ "$AGE" -lt 300 ]; then
        echo "OK: Agent status fresh (${AGE}s old)"
    else
        echo "WARN: Agent status stale (${AGE}s old)"
    fi
else
    echo "INFO: No agent status file"
fi

# Check 5: Python environment works
if python3 -c "from lib.fingerprint import FingerprintGenerator; print('OK')" 2>/dev/null; then
    echo "OK: Python modules loaded"
else
    echo "FAIL: Cannot load Python modules"
    ERRORS=$((ERRORS + 1))
fi

# Exit with appropriate code
if [ "$ERRORS" -gt 2 ]; then
    echo "UNHEALTHY: $ERRORS critical issues"
    exit 1
else
    echo "HEALTHY: $ERRORS warnings"
    exit 0
fi
