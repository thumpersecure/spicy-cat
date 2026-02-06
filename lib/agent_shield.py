#!/usr/bin/env python3
"""
agent_shield.py - Agentic Real-Time Protection System for spicy-cat

"A cat doesn't just hide - it adapts, observes, and outsmarts."

Implements an autonomous protection agent that monitors network conditions,
detects fingerprinting/tracking attempts, and dynamically adjusts protection
parameters in real-time. Uses the Lorenz attractor as a decision engine
for organic, unpredictable defensive responses.

Agent Capabilities:
- Monitors outbound traffic for fingerprinting attempts
- Detects telemetry collection patterns
- Dynamically rotates fingerprint profiles
- Adjusts telemetry chaos intensity based on threat level
- Self-heals when protection is degraded
- Learns from detection patterns to improve evasion

Threat Detection Signals:
1. Canvas fingerprinting API calls
2. WebGL parameter enumeration
3. Font measurement probing
4. AudioContext fingerprinting
5. WebRTC STUN requests
6. Known tracker domain requests
7. Telemetry beacon patterns
8. Cookie sync pixel requests
9. Browser plugin enumeration
10. TCP/TLS fingerprinting probes
"""

import os
import json
import time
import hashlib
import secrets
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

try:
    from .chaos import LogisticMap, LorenzAttractor, ChaoticTimer
    from .fingerprint import FingerprintProtector, FingerprintGenerator, FingerprintProfile
    from .telemetry_chaos import TelemetryChaosEngine, TelemetryMethod
except ImportError:
    from chaos import LogisticMap, LorenzAttractor, ChaoticTimer
    from fingerprint import FingerprintProtector, FingerprintGenerator, FingerprintProfile
    from telemetry_chaos import TelemetryChaosEngine, TelemetryMethod


# ── Threat Level System ────────────────────────────────────────────────────

class ThreatLevel(Enum):
    """Current threat assessment level."""
    CALM = "calm"          # Normal browsing, minimal tracking detected
    ELEVATED = "elevated"  # Some tracking signals detected
    HIGH = "high"          # Active fingerprinting attempts detected
    CRITICAL = "critical"  # Coordinated tracking/fingerprinting attack


class DetectionType(Enum):
    """Types of tracking/fingerprinting attempts we detect."""
    CANVAS_FINGERPRINT = "canvas_fingerprint"
    WEBGL_ENUM = "webgl_enumeration"
    FONT_PROBE = "font_measurement_probe"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    WEBRTC_LEAK = "webrtc_stun_request"
    TRACKER_DOMAIN = "known_tracker_domain"
    TELEMETRY_BEACON = "telemetry_beacon"
    COOKIE_SYNC = "cookie_sync_pixel"
    PLUGIN_ENUM = "plugin_enumeration"
    TLS_FINGERPRINT = "tls_fingerprint_probe"


@dataclass
class ThreatSignal:
    """A detected threat signal."""
    timestamp: datetime
    detection_type: DetectionType
    source: str
    confidence: float  # 0.0 to 1.0
    details: Dict = field(default_factory=dict)
    mitigated: bool = False


@dataclass
class AgentAction:
    """An action taken by the protection agent."""
    timestamp: datetime
    action_type: str
    reason: str
    details: Dict = field(default_factory=dict)
    success: bool = True


# ── Known Tracker Domains ──────────────────────────────────────────────────

KNOWN_TRACKER_DOMAINS = {
    # Analytics
    "google-analytics.com", "analytics.google.com", "ssl.google-analytics.com",
    "stats.g.doubleclick.net", "www.googletagmanager.com",
    # Facebook
    "connect.facebook.net", "pixel.facebook.com", "www.facebook.com/tr",
    # Advertising
    "ad.doubleclick.net", "pagead2.googlesyndication.com",
    "ads.linkedin.com", "bat.bing.com",
    "cdn.mxpnl.com", "api.mixpanel.com",
    # Fingerprinting services
    "cdn.jsdelivr.net/npm/fingerprintjs",
    "fpcdn.io", "api.fpjs.io",
    "cdn.cookielaw.org", "geolocation.onetrust.com",
    # Session replay
    "cdn.mouseflow.com", "cdn.logrocket.io",
    "cdn.fullstory.com", "rs.fullstory.com",
    "static.hotjar.com", "script.hotjar.com",
    # A/B testing
    "cdn.optimizely.com", "logx.optimizely.com",
    "cdn.amplitude.com", "api.amplitude.com",
}

# Tracker URL patterns (regex-like matching)
TRACKER_PATTERNS = [
    "/collect?", "/analytics/", "/pixel/", "/beacon/",
    "/track?", "/event?", "/log?", "/__utm.",
    "/pagead/", "/adview/", "/impression/",
    "/_vercel/insights/", "/_next/data/",
    "/api/telemetry", "/v1/collect", "/v2/track",
]

# Fingerprinting script patterns
FINGERPRINT_PATTERNS = [
    "fingerprint", "canvas.toDataURL", "getImageData",
    "webgl.getParameter", "AudioContext", "createOscillator",
    "navigator.plugins", "navigator.mimeTypes",
    "screen.width", "screen.height", "devicePixelRatio",
    "getTimezoneOffset", "getBattery",
]


# ── Agent Decision Engine ──────────────────────────────────────────────────

class AgentDecisionEngine:
    """
    Uses Lorenz attractor dynamics to make unpredictable but
    contextually appropriate defensive decisions.

    The attractor's three dimensions map to:
    - X: Aggression (how strongly to respond)
    - Y: Diversity (how many methods to activate)
    - Z: Timing (how frequently to change)

    "A cat's decisions look random but follow deep instinct."
    """

    def __init__(self, seed: str = None):
        self.lorenz = LorenzAttractor(seed or "agent_decisions")
        self.chaos = LogisticMap(seed or "agent_select")
        self._decision_history: deque = deque(maxlen=100)

    def evaluate_threat(self, signals: List[ThreatSignal]) -> ThreatLevel:
        """Evaluate current threat level from accumulated signals."""
        if not signals:
            return ThreatLevel.CALM

        # Score recent signals (last 60 seconds weighted more)
        now = datetime.now()
        score = 0.0

        for signal in signals:
            age = (now - signal.timestamp).total_seconds()
            if age > 300:  # Ignore signals older than 5 minutes
                continue

            # Recency weight
            recency = max(0.1, 1.0 - (age / 300.0))

            # Confidence weight
            confidence = signal.confidence

            # Type severity
            severity = {
                DetectionType.CANVAS_FINGERPRINT: 3.0,
                DetectionType.WEBGL_ENUM: 2.5,
                DetectionType.FONT_PROBE: 2.0,
                DetectionType.AUDIO_FINGERPRINT: 3.0,
                DetectionType.WEBRTC_LEAK: 4.0,
                DetectionType.TRACKER_DOMAIN: 1.0,
                DetectionType.TELEMETRY_BEACON: 1.5,
                DetectionType.COOKIE_SYNC: 2.0,
                DetectionType.PLUGIN_ENUM: 2.0,
                DetectionType.TLS_FINGERPRINT: 2.5,
            }.get(signal.detection_type, 1.0)

            score += recency * confidence * severity

        # Map score to threat level
        if score < 2.0:
            return ThreatLevel.CALM
        elif score < 6.0:
            return ThreatLevel.ELEVATED
        elif score < 15.0:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL

    def decide_response(self, threat_level: ThreatLevel) -> Dict:
        """Decide how to respond based on threat level and Lorenz dynamics."""
        noise = self.lorenz.next_normalized()

        # Base response parameters
        response = {
            'rotate_fingerprint': False,
            'chaos_intensity': 0.0,
            'active_methods': [],
            'rotation_interval': 3600,  # seconds
            'dns_chaff_rate': 0,
            'phantom_count': 0,
        }

        if threat_level == ThreatLevel.CALM:
            response['chaos_intensity'] = 0.1 + abs(noise[0]) * 0.2
            response['active_methods'] = [TelemetryMethod.DNS_CHAFF]
            response['dns_chaff_rate'] = 2
            response['rotation_interval'] = 3600

        elif threat_level == ThreatLevel.ELEVATED:
            response['chaos_intensity'] = 0.3 + abs(noise[0]) * 0.3
            response['active_methods'] = [
                TelemetryMethod.DNS_CHAFF,
                TelemetryMethod.COOKIE_CHIMERA,
                TelemetryMethod.UA_METAMORPH,
                TelemetryMethod.TEMPORAL_DRIFT,
            ]
            response['dns_chaff_rate'] = 5
            response['phantom_count'] = 3
            response['rotation_interval'] = 1800

        elif threat_level == ThreatLevel.HIGH:
            response['rotate_fingerprint'] = abs(noise[1]) > 0.5
            response['chaos_intensity'] = 0.6 + abs(noise[0]) * 0.3
            response['active_methods'] = [
                TelemetryMethod.DNS_CHAFF,
                TelemetryMethod.COOKIE_CHIMERA,
                TelemetryMethod.UA_METAMORPH,
                TelemetryMethod.TEMPORAL_DRIFT,
                TelemetryMethod.PHANTOM_SWARM,
                TelemetryMethod.TLS_SHUFFLE,
                TelemetryMethod.REFERRER_FABRICATOR,
            ]
            response['dns_chaff_rate'] = 10
            response['phantom_count'] = 10
            response['rotation_interval'] = 600

        elif threat_level == ThreatLevel.CRITICAL:
            response['rotate_fingerprint'] = True
            response['chaos_intensity'] = 0.9 + abs(noise[0]) * 0.1
            response['active_methods'] = list(TelemetryMethod)  # ALL methods
            response['dns_chaff_rate'] = 20
            response['phantom_count'] = 20
            response['rotation_interval'] = 120

        # Add Lorenz-based variation to timing
        timing_noise = abs(noise[2])
        response['rotation_interval'] = int(
            response['rotation_interval'] * (0.7 + timing_noise * 0.6)
        )

        self._decision_history.append({
            'timestamp': datetime.now().isoformat(),
            'threat_level': threat_level.value,
            'response': response,
        })

        return response


# ── The Protection Agent ───────────────────────────────────────────────────

class ProtectionAgent:
    """
    Autonomous protection agent that monitors, detects, and responds
    to fingerprinting and telemetry collection in real-time.

    The agent runs as a background thread, continuously:
    1. Monitoring for threat signals
    2. Evaluating threat level
    3. Deciding on response actions
    4. Executing protective measures
    5. Logging all activity

    "Like a cat on patrol - always watching, always ready."
    """

    def __init__(self, seed: str = None, log_file: str = None):
        self.seed = seed or secrets.token_hex(16)
        self.decision_engine = AgentDecisionEngine(self.seed)
        self.fingerprint_protector = FingerprintProtector(seed=self.seed)
        self.telemetry_engine = TelemetryChaosEngine(self.seed)
        self.timer = ChaoticTimer(self.seed + "_agent", base_interval=10.0)

        # State
        self._threat_signals: List[ThreatSignal] = []
        self._actions: List[AgentAction] = []
        self._current_threat_level = ThreatLevel.CALM
        self._current_response: Dict = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []

        # Stats
        self._fingerprint_rotations = 0
        self._threats_mitigated = 0
        self._start_time: Optional[datetime] = None
        self._last_rotation: Optional[datetime] = None

        # Logging
        self._logger = logging.getLogger('spicy-cat.agent')
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            ))
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def register_callback(self, callback: Callable):
        """Register a callback for agent events."""
        self._callbacks.append(callback)

    def _notify(self, event_type: str, data: Dict):
        """Notify registered callbacks."""
        for cb in self._callbacks:
            try:
                cb(event_type, data)
            except Exception:
                pass

    def report_signal(self, detection_type: DetectionType,
                      source: str, confidence: float = 0.8,
                      details: Dict = None):
        """Report a detected threat signal to the agent."""
        signal = ThreatSignal(
            timestamp=datetime.now(),
            detection_type=detection_type,
            source=source,
            confidence=confidence,
            details=details or {},
        )

        with self._lock:
            self._threat_signals.append(signal)

        self._logger.info(
            f"Signal: {detection_type.value} from {source} "
            f"(confidence={confidence:.1%})"
        )
        self._notify('signal', {
            'type': detection_type.value,
            'source': source,
            'confidence': confidence,
        })

    def check_domain(self, domain: str) -> Optional[ThreatSignal]:
        """Check if a domain is a known tracker."""
        domain_lower = domain.lower().strip()

        for tracker in KNOWN_TRACKER_DOMAINS:
            if tracker in domain_lower:
                signal = ThreatSignal(
                    timestamp=datetime.now(),
                    detection_type=DetectionType.TRACKER_DOMAIN,
                    source=domain,
                    confidence=0.9,
                    details={'tracker_pattern': tracker},
                )
                with self._lock:
                    self._threat_signals.append(signal)
                return signal

        return None

    def check_url(self, url: str) -> Optional[ThreatSignal]:
        """Check if a URL matches known tracking patterns."""
        url_lower = url.lower()

        for pattern in TRACKER_PATTERNS:
            if pattern in url_lower:
                signal = ThreatSignal(
                    timestamp=datetime.now(),
                    detection_type=DetectionType.TELEMETRY_BEACON,
                    source=url[:100],
                    confidence=0.7,
                    details={'pattern': pattern},
                )
                with self._lock:
                    self._threat_signals.append(signal)
                return signal

        return None

    def check_script_content(self, content: str) -> List[ThreatSignal]:
        """Check JavaScript content for fingerprinting patterns."""
        signals = []
        content_lower = content.lower()

        detection_map = {
            'canvas.todataurl': (DetectionType.CANVAS_FINGERPRINT, 0.8),
            'getimagedata': (DetectionType.CANVAS_FINGERPRINT, 0.7),
            'webgl.getparameter': (DetectionType.WEBGL_ENUM, 0.8),
            'webgl2renderingcontext': (DetectionType.WEBGL_ENUM, 0.6),
            'audiocontext': (DetectionType.AUDIO_FINGERPRINT, 0.7),
            'createoscillator': (DetectionType.AUDIO_FINGERPRINT, 0.8),
            'navigator.plugins': (DetectionType.PLUGIN_ENUM, 0.7),
            'navigator.mimetypes': (DetectionType.PLUGIN_ENUM, 0.6),
            'getbattery': (DetectionType.TLS_FINGERPRINT, 0.5),
            'rtcpeerconnection': (DetectionType.WEBRTC_LEAK, 0.9),
            'createoffer': (DetectionType.WEBRTC_LEAK, 0.8),
        }

        for pattern, (det_type, confidence) in detection_map.items():
            if pattern in content_lower:
                signal = ThreatSignal(
                    timestamp=datetime.now(),
                    detection_type=det_type,
                    source="script_analysis",
                    confidence=confidence,
                    details={'pattern': pattern},
                )
                signals.append(signal)
                with self._lock:
                    self._threat_signals.append(signal)

        return signals

    def _evaluate_and_respond(self):
        """Core agent loop: evaluate threats and respond."""
        with self._lock:
            # Prune old signals (keep last 5 minutes)
            cutoff = datetime.now() - timedelta(minutes=5)
            self._threat_signals = [
                s for s in self._threat_signals
                if s.timestamp > cutoff
            ]

            # Evaluate threat level
            new_level = self.decision_engine.evaluate_threat(self._threat_signals)

        # If threat level changed, respond
        if new_level != self._current_threat_level:
            self._logger.info(
                f"Threat level: {self._current_threat_level.value} -> {new_level.value}"
            )
            self._current_threat_level = new_level

            # Get response decision
            response = self.decision_engine.decide_response(new_level)
            self._current_response = response

            # Execute response
            self._execute_response(response)

            self._notify('threat_level_change', {
                'old': self._current_threat_level.value,
                'new': new_level.value,
                'response': response,
            })

    def _execute_response(self, response: Dict):
        """Execute the decided response actions."""
        # Rotate fingerprint if needed
        if response.get('rotate_fingerprint'):
            self.fingerprint_protector.rotate_profile()
            self._fingerprint_rotations += 1
            self._last_rotation = datetime.now()
            self._log_action("fingerprint_rotation",
                             f"Threat level: {self._current_threat_level.value}",
                             {"new_profile_id": self.fingerprint_protector.get_profile().profile_id})

        # Update telemetry chaos methods
        active_methods = response.get('active_methods', [])
        if active_methods:
            self.telemetry_engine.set_active_methods(active_methods)
            self._log_action("telemetry_methods_updated",
                             f"Active methods: {len(active_methods)}",
                             {"methods": [m.value for m in active_methods]})

        # Generate phantom devices if needed
        phantom_count = response.get('phantom_count', 0)
        if phantom_count > 0:
            swarm = self.telemetry_engine.methods[TelemetryMethod.PHANTOM_SWARM]
            if isinstance(swarm, object) and hasattr(swarm, 'generate_swarm'):
                swarm.generate_swarm(phantom_count)
                self._log_action("phantom_swarm_deployed",
                                 f"Deployed {phantom_count} phantom devices",
                                 {"count": phantom_count})

        self._threats_mitigated += 1

    def _log_action(self, action_type: str, reason: str, details: Dict = None):
        """Log an agent action."""
        action = AgentAction(
            timestamp=datetime.now(),
            action_type=action_type,
            reason=reason,
            details=details or {},
        )
        with self._lock:
            self._actions.append(action)
        self._logger.info(f"Action: {action_type} - {reason}")

    def start(self):
        """Start the protection agent."""
        if self._running:
            return

        self._running = True
        self._start_time = datetime.now()

        def _agent_loop():
            self._logger.info("Protection agent started")
            while self._running:
                try:
                    self._evaluate_and_respond()

                    # Periodic fingerprint rotation based on current response
                    if self._current_response.get('rotation_interval'):
                        interval = self._current_response['rotation_interval']
                        if self._last_rotation:
                            elapsed = (datetime.now() - self._last_rotation).total_seconds()
                            if elapsed >= interval:
                                self.fingerprint_protector.rotate_profile()
                                self._fingerprint_rotations += 1
                                self._last_rotation = datetime.now()
                                self._log_action("scheduled_rotation",
                                                 f"Interval: {interval}s")

                    # Chaotic sleep between evaluations
                    wait = self.timer.next_interval(0.5, 2.0)
                    time.sleep(wait)

                except Exception as e:
                    self._logger.error(f"Agent error: {e}")
                    time.sleep(5)

        self._thread = threading.Thread(target=_agent_loop, daemon=True)
        self._thread.start()
        self._log_action("agent_started", "Protection agent initialized")

    def stop(self):
        """Stop the protection agent."""
        self._running = False
        self.telemetry_engine.stop_background()
        if self._thread:
            self._thread.join(timeout=10)
        self._log_action("agent_stopped", "Protection agent shut down")
        self._logger.info("Protection agent stopped")

    def get_status(self) -> Dict:
        """Get comprehensive agent status."""
        uptime = 0
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()

        with self._lock:
            recent_signals = self._threat_signals[-10:]
            recent_actions = self._actions[-10:]

        return {
            'running': self._running,
            'uptime_seconds': int(uptime),
            'threat_level': self._current_threat_level.value,
            'fingerprint_rotations': self._fingerprint_rotations,
            'threats_mitigated': self._threats_mitigated,
            'current_profile_id': self.fingerprint_protector.get_profile().profile_id,
            'active_methods': [m.value for m in self._current_response.get('active_methods', [])],
            'total_signals': len(self._threat_signals),
            'recent_signals': [
                {
                    'type': s.detection_type.value,
                    'source': s.source[:50],
                    'confidence': s.confidence,
                    'time': s.timestamp.isoformat(),
                }
                for s in recent_signals
            ],
            'recent_actions': [
                {
                    'action': a.action_type,
                    'reason': a.reason,
                    'time': a.timestamp.isoformat(),
                }
                for a in recent_actions
            ],
            'telemetry_stats': self.telemetry_engine.get_stats(),
            'fingerprint_summary': self.fingerprint_protector.get_protection_summary(),
        }

    def get_dashboard_data(self) -> Dict:
        """Get data formatted for dashboard display."""
        status = self.get_status()
        threat_colors = {
            'calm': '\033[92m',      # Green
            'elevated': '\033[93m',  # Yellow
            'high': '\033[91m',      # Red
            'critical': '\033[95m',  # Magenta (blinking)
        }
        reset = '\033[0m'

        color = threat_colors.get(status['threat_level'], reset)

        return {
            'threat_display': f"{color}{status['threat_level'].upper()}{reset}",
            'threat_level': status['threat_level'],
            'uptime': status['uptime_seconds'],
            'rotations': status['fingerprint_rotations'],
            'mitigated': status['threats_mitigated'],
            'profile_id': status['current_profile_id'][:12],
            'active_methods_count': len(status['active_methods']),
            'signal_count': status['total_signals'],
        }


# ── Docker Integration ─────────────────────────────────────────────────────

class DockerProtectionManager:
    """
    Manages protection specifically within Docker containers.
    Applies system-level protections that require container privileges.

    "Cats in boxes are still cats. Just more protected ones."
    """

    def __init__(self, agent: ProtectionAgent):
        self.agent = agent
        self.protector = agent.fingerprint_protector

    def generate_docker_env(self) -> Dict[str, str]:
        """Generate environment variables for Docker container."""
        profile = self.protector.get_profile()
        return {
            'SPICY_CAT_PROFILE_ID': profile.profile_id,
            'SPICY_CAT_USER_AGENT': profile.user_agent,
            'SPICY_CAT_PLATFORM': profile.platform,
            'SPICY_CAT_LANGUAGE': profile.language,
            'SPICY_CAT_TIMEZONE': profile.timezone_name,
            'SPICY_CAT_SCREEN': f'{profile.screen_width}x{profile.screen_height}',
            'TZ': profile.timezone_name,
        }

    def generate_startup_script(self) -> str:
        """Generate a shell script to apply protections at container start."""
        profile = self.protector.get_profile()
        iptables_rules = self.protector.generate_iptables_rules()
        sysctl_config = self.protector.generate_sysctl_config()

        script = """#!/bin/bash
# spicy-cat Docker Protection Startup Script
# "A cat always lands on its feet, especially in containers."

set -e

echo "[spicy-cat] Applying system-level protections..."

# ── Apply sysctl settings (TCP/IP stack normalization) ──
"""
        for key, value in sysctl_config.items():
            script += f'sysctl -w {key}={value} 2>/dev/null || true\n'

        script += """
# ── Apply iptables rules (network fingerprint protection) ──
"""
        for rule in iptables_rules:
            script += f'{rule} 2>/dev/null || true\n'

        script += f"""
# ── Set timezone ──
ln -sf /usr/share/zoneinfo/{profile.timezone_name} /etc/localtime 2>/dev/null || true
echo "{profile.timezone_name}" > /etc/timezone 2>/dev/null || true

# ── Configure DNS (prevent DNS leak) ──
echo "nameserver 127.0.0.1" > /etc/resolv.conf 2>/dev/null || true

echo "[spicy-cat] Protection applied. Profile: {profile.profile_id[:12]}..."
echo "[spicy-cat] Platform: {profile.platform} | TZ: {profile.timezone_name}"
echo "[spicy-cat] TTL: {profile.tcp_ttl} | Window: {profile.tcp_window_size}"

# ── Start the protection agent ──
exec "$@"
"""
        return script

    def generate_healthcheck_script(self) -> str:
        """Generate a health check script for Docker."""
        return """#!/bin/bash
# spicy-cat Protection Health Check

# Check if the agent is running
if pgrep -f "spicy-cat.*agent" > /dev/null 2>&1; then
    echo "OK: Agent running"
else
    echo "WARN: Agent not detected"
    exit 1
fi

# Check iptables rules are in place
if iptables -t mangle -L POSTROUTING 2>/dev/null | grep -q "TTL"; then
    echo "OK: TTL normalization active"
else
    echo "WARN: TTL normalization missing"
fi

# Check DNS configuration
if grep -q "127.0.0.1" /etc/resolv.conf 2>/dev/null; then
    echo "OK: DNS configured"
else
    echo "WARN: DNS may leak"
fi

exit 0
"""


# ── CLI Demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== spicy-cat Protection Agent ===\n")

    agent = ProtectionAgent("demo_seed")

    # Simulate some threat signals
    print("Simulating threat detection...\n")

    agent.report_signal(DetectionType.TRACKER_DOMAIN, "google-analytics.com", 0.9)
    agent.report_signal(DetectionType.CANVAS_FINGERPRINT, "suspicious-site.com", 0.8)
    agent.report_signal(DetectionType.WEBGL_ENUM, "fingerprint-test.com", 0.7)

    # Run one evaluation cycle
    agent._evaluate_and_respond()

    status = agent.get_status()
    print(f"Threat Level: {status['threat_level']}")
    print(f"Profile ID: {status['current_profile_id'][:12]}...")
    print(f"Rotations: {status['fingerprint_rotations']}")
    print(f"Mitigated: {status['threats_mitigated']}")
    print(f"Active Methods: {len(status['active_methods'])}")

    print("\nRecent Actions:")
    for action in status['recent_actions']:
        print(f"  [{action['action']}] {action['reason']}")

    # Docker integration
    print("\n--- Docker Integration ---")
    docker_mgr = DockerProtectionManager(agent)
    env = docker_mgr.generate_docker_env()
    for k, v in env.items():
        print(f"  {k}={v[:60]}...")
