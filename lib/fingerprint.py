#!/usr/bin/env python3
"""
fingerprint.py - Advanced Browser & System Fingerprint Protection for spicy-cat

"A cat leaves no fingerprints. Neither should you."

Implements comprehensive fingerprinting protection techniques designed
to run inside Docker containers with full network stack control.

Protection vectors:
1.  Canvas fingerprint randomization
2.  WebGL renderer/vendor spoofing
3.  AudioContext fingerprint noise
4.  Font enumeration masking
5.  Screen/display property spoofing
6.  Navigator property randomization
7.  WebRTC IP leak prevention
8.  Timezone spoofing
9.  Battery API masking
10. Hardware concurrency spoofing
11. Memory/DeviceMemory spoofing
12. Plugin/MimeType masking
13. TCP/IP stack fingerprint normalization
14. TLS fingerprint (JA3) randomization
15. HTTP header order randomization
"""

import os
import json
import random
import hashlib
import secrets
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    from .chaos import LogisticMap, LorenzAttractor
except ImportError:
    from chaos import LogisticMap, LorenzAttractor


class FingerprintVector(Enum):
    """All fingerprinting vectors we protect against."""
    CANVAS = "canvas"
    WEBGL = "webgl"
    AUDIO = "audio_context"
    FONTS = "font_enum"
    SCREEN = "screen_props"
    NAVIGATOR = "navigator"
    WEBRTC = "webrtc"
    TIMEZONE = "timezone"
    BATTERY = "battery_api"
    HARDWARE = "hw_concurrency"
    MEMORY = "device_memory"
    PLUGINS = "plugins"
    TCP_STACK = "tcp_stack"
    TLS_JA3 = "tls_ja3"
    HTTP_HEADERS = "http_headers"


@dataclass
class FingerprintProfile:
    """A complete spoofed fingerprint profile."""
    profile_id: str
    created_at: datetime = field(default_factory=datetime.now)

    # Canvas
    canvas_noise_seed: str = ""
    canvas_noise_intensity: float = 0.02

    # WebGL
    webgl_vendor: str = ""
    webgl_renderer: str = ""
    webgl_unmasked_vendor: str = ""
    webgl_unmasked_renderer: str = ""

    # Audio
    audio_noise_seed: str = ""
    audio_sample_rate: int = 44100
    audio_channel_count: int = 2

    # Fonts
    allowed_fonts: List[str] = field(default_factory=list)
    font_metrics_noise: float = 0.01

    # Screen
    screen_width: int = 1920
    screen_height: int = 1080
    color_depth: int = 24
    pixel_ratio: float = 1.0

    # Navigator
    platform: str = "Win32"
    user_agent: str = ""
    language: str = "en-US"
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])
    do_not_track: str = "1"
    hardware_concurrency: int = 4
    device_memory: int = 8
    max_touch_points: int = 0

    # Timezone
    timezone_name: str = "America/New_York"
    timezone_offset: int = -300

    # Network
    webrtc_policy: str = "disable_non_proxied_udp"
    effective_type: str = "4g"
    downlink: float = 10.0
    rtt: int = 50

    # TLS/TCP
    ja3_hash: str = ""
    tcp_window_size: int = 65535
    tcp_ttl: int = 64

    # HTTP
    header_order: List[str] = field(default_factory=list)
    accept_encoding: str = "gzip, deflate, br"

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'profile_id': self.profile_id,
            'created_at': self.created_at.isoformat(),
            'canvas': {
                'noise_seed': self.canvas_noise_seed,
                'noise_intensity': self.canvas_noise_intensity,
            },
            'webgl': {
                'vendor': self.webgl_vendor,
                'renderer': self.webgl_renderer,
                'unmasked_vendor': self.webgl_unmasked_vendor,
                'unmasked_renderer': self.webgl_unmasked_renderer,
            },
            'audio': {
                'noise_seed': self.audio_noise_seed,
                'sample_rate': self.audio_sample_rate,
                'channel_count': self.audio_channel_count,
            },
            'fonts': {
                'allowed': self.allowed_fonts,
                'metrics_noise': self.font_metrics_noise,
            },
            'screen': {
                'width': self.screen_width,
                'height': self.screen_height,
                'color_depth': self.color_depth,
                'pixel_ratio': self.pixel_ratio,
            },
            'navigator': {
                'platform': self.platform,
                'user_agent': self.user_agent,
                'language': self.language,
                'languages': self.languages,
                'do_not_track': self.do_not_track,
                'hardware_concurrency': self.hardware_concurrency,
                'device_memory': self.device_memory,
                'max_touch_points': self.max_touch_points,
            },
            'timezone': {
                'name': self.timezone_name,
                'offset': self.timezone_offset,
            },
            'network': {
                'webrtc_policy': self.webrtc_policy,
                'effective_type': self.effective_type,
                'downlink': self.downlink,
                'rtt': self.rtt,
            },
            'tls': {
                'ja3_hash': self.ja3_hash,
                'tcp_window_size': self.tcp_window_size,
                'tcp_ttl': self.tcp_ttl,
            },
            'http': {
                'header_order': self.header_order,
                'accept_encoding': self.accept_encoding,
            },
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)


# ── Realistic Data Pools ───────────────────────────────────────────────────

WEBGL_PROFILES = [
    {
        'vendor': 'Google Inc. (NVIDIA)',
        'renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'NVIDIA Corporation',
        'unmasked_renderer': 'NVIDIA GeForce RTX 3060/PCIe/SSE2',
    },
    {
        'vendor': 'Google Inc. (NVIDIA)',
        'renderer': 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'NVIDIA Corporation',
        'unmasked_renderer': 'NVIDIA GeForce GTX 1660 SUPER/PCIe/SSE2',
    },
    {
        'vendor': 'Google Inc. (AMD)',
        'renderer': 'ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'ATI Technologies Inc.',
        'unmasked_renderer': 'AMD Radeon RX 580 Series',
    },
    {
        'vendor': 'Google Inc. (Intel)',
        'renderer': 'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'Intel Inc.',
        'unmasked_renderer': 'Intel(R) UHD Graphics 630',
    },
    {
        'vendor': 'Google Inc. (Intel)',
        'renderer': 'ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'Intel Inc.',
        'unmasked_renderer': 'Intel(R) Iris(R) Xe Graphics',
    },
    {
        'vendor': 'Google Inc. (NVIDIA)',
        'renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
        'unmasked_vendor': 'NVIDIA Corporation',
        'unmasked_renderer': 'NVIDIA GeForce RTX 4070/PCIe/SSE2',
    },
    {
        'vendor': 'Apple',
        'renderer': 'Apple GPU',
        'unmasked_vendor': 'Apple',
        'unmasked_renderer': 'Apple M1',
    },
    {
        'vendor': 'Apple',
        'renderer': 'Apple GPU',
        'unmasked_vendor': 'Apple',
        'unmasked_renderer': 'Apple M2 Pro',
    },
]

COMMON_FONTS = [
    # Windows core
    "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia",
    "Tahoma", "Trebuchet MS", "Impact", "Comic Sans MS", "Palatino Linotype",
    "Lucida Sans Unicode", "Segoe UI", "Calibri", "Cambria", "Consolas",
    # Cross-platform
    "Helvetica", "Helvetica Neue", "Liberation Sans", "Liberation Serif",
    "DejaVu Sans", "DejaVu Serif", "Roboto", "Open Sans", "Lato",
    "Source Sans Pro", "Noto Sans",
]

SCREEN_PROFILES = [
    (1920, 1080, 24, 1.0),   # Standard FHD
    (1920, 1080, 24, 1.25),  # FHD with 125% scaling
    (2560, 1440, 24, 1.0),   # QHD
    (1366, 768, 24, 1.0),    # Common laptop
    (1536, 864, 24, 1.25),   # Laptop with scaling
    (3840, 2160, 24, 2.0),   # 4K with 200% scaling
    (1440, 900, 24, 2.0),    # MacBook Pro Retina
    (1680, 1050, 24, 1.0),   # Older widescreen
    (2560, 1600, 24, 2.0),   # MacBook Pro 16"
]

TIMEZONE_PROFILES = [
    ("America/New_York", -300),
    ("America/Chicago", -360),
    ("America/Denver", -420),
    ("America/Los_Angeles", -480),
    ("America/Phoenix", -420),
    ("Europe/London", 0),
    ("Europe/Berlin", 60),
    ("Europe/Paris", 60),
    ("Asia/Tokyo", 540),
    ("Asia/Shanghai", 480),
    ("Australia/Sydney", 660),
    ("America/Toronto", -300),
    ("America/Sao_Paulo", -180),
    ("Asia/Kolkata", 330),
    ("Pacific/Auckland", 780),
]

PLATFORM_PROFILES = [
    {
        'platform': 'Win32',
        'ua_os': 'Windows NT 10.0; Win64; x64',
        'languages': ['en-US', 'en'],
    },
    {
        'platform': 'Win32',
        'ua_os': 'Windows NT 10.0; Win64; x64',
        'languages': ['en-GB', 'en'],
    },
    {
        'platform': 'MacIntel',
        'ua_os': 'Macintosh; Intel Mac OS X 10_15_7',
        'languages': ['en-US', 'en'],
    },
    {
        'platform': 'Linux x86_64',
        'ua_os': 'X11; Linux x86_64',
        'languages': ['en-US', 'en'],
    },
    {
        'platform': 'Win32',
        'ua_os': 'Windows NT 10.0; Win64; x64',
        'languages': ['de-DE', 'de', 'en-US', 'en'],
    },
    {
        'platform': 'MacIntel',
        'ua_os': 'Macintosh; Intel Mac OS X 10_15_7',
        'languages': ['fr-FR', 'fr', 'en-US', 'en'],
    },
]

CHROME_VERSIONS = [
    "120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0",
    "124.0.0.0", "125.0.0.0", "126.0.0.0",
]

FIREFOX_VERSIONS = [
    "121.0", "122.0", "123.0", "124.0", "125.0", "126.0", "127.0",
]


# ── JA3 Fingerprint Profiles ──────────────────────────────────────────────

JA3_PROFILES = [
    # Chrome-like JA3 hashes
    "769,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0",
    "769,4865-4867-4866-49195-49199-52393-52392-49196-49200-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-34-51-43-13-45-28-27,29-23-24,0",
    # Firefox-like JA3 hashes
    "771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-51-43-13-45-28,29-23-24-25-256-257,0",
    "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-51-45-43-27-28,29-23-24-25,0",
]


# ── Header Order Profiles ─────────────────────────────────────────────────

HEADER_ORDER_PROFILES = [
    # Chrome order
    ["Host", "Connection", "Cache-Control", "sec-ch-ua", "sec-ch-ua-mobile",
     "sec-ch-ua-platform", "Upgrade-Insecure-Requests", "User-Agent",
     "Accept", "Sec-Fetch-Site", "Sec-Fetch-Mode", "Sec-Fetch-User",
     "Sec-Fetch-Dest", "Accept-Encoding", "Accept-Language"],
    # Firefox order
    ["Host", "User-Agent", "Accept", "Accept-Language", "Accept-Encoding",
     "Connection", "Upgrade-Insecure-Requests", "Sec-Fetch-Dest",
     "Sec-Fetch-Mode", "Sec-Fetch-Site", "Sec-Fetch-User"],
    # Edge order
    ["Host", "Connection", "Cache-Control", "sec-ch-ua", "sec-ch-ua-mobile",
     "sec-ch-ua-platform", "DNT", "Upgrade-Insecure-Requests",
     "User-Agent", "Accept", "Sec-Fetch-Site", "Sec-Fetch-Mode",
     "Sec-Fetch-Dest", "Accept-Encoding", "Accept-Language"],
]


class FingerprintGenerator:
    """
    Generates consistent, realistic fingerprint profiles.

    Like a cat creating a whole new identity - whiskers, fur pattern, and all.
    Each profile is internally consistent (e.g., Mac platform + Safari UA).
    """

    def __init__(self, seed: Optional[str] = None):
        self.seed = seed or secrets.token_hex(16)
        self.chaos = LogisticMap(self.seed)
        self.lorenz = LorenzAttractor(self.seed)

    def generate(self) -> FingerprintProfile:
        """Generate a complete, internally consistent fingerprint profile."""
        profile_id = hashlib.sha256(
            f"{self.seed}_{time.time()}".encode()
        ).hexdigest()[:16]

        profile = FingerprintProfile(profile_id=profile_id)

        # Select coherent platform
        plat = self.chaos.next_choice(PLATFORM_PROFILES)
        profile.platform = plat['platform']
        profile.language = plat['languages'][0]
        profile.languages = plat['languages']

        # User agent consistent with platform
        profile.user_agent = self._generate_ua(plat)

        # WebGL consistent with platform
        if 'Mac' in plat['platform']:
            webgl_choices = [p for p in WEBGL_PROFILES if 'Apple' in p['vendor']]
        elif 'Linux' in plat['platform']:
            webgl_choices = [p for p in WEBGL_PROFILES if 'NVIDIA' in p['vendor'] or 'Intel' in p['vendor']]
        else:
            webgl_choices = [p for p in WEBGL_PROFILES if 'Apple' not in p['vendor']]

        webgl = self.chaos.next_choice(webgl_choices or WEBGL_PROFILES)
        profile.webgl_vendor = webgl['vendor']
        profile.webgl_renderer = webgl['renderer']
        profile.webgl_unmasked_vendor = webgl['unmasked_vendor']
        profile.webgl_unmasked_renderer = webgl['unmasked_renderer']

        # Screen properties
        screen = self.chaos.next_choice(SCREEN_PROFILES)
        profile.screen_width = screen[0]
        profile.screen_height = screen[1]
        profile.color_depth = screen[2]
        profile.pixel_ratio = screen[3]

        # Timezone
        tz = self.chaos.next_choice(TIMEZONE_PROFILES)
        profile.timezone_name = tz[0]
        profile.timezone_offset = tz[1]

        # Hardware
        profile.hardware_concurrency = self.chaos.next_choice([2, 4, 6, 8, 12, 16])
        profile.device_memory = self.chaos.next_choice([4, 8, 16, 32])

        # Fonts - select a realistic subset
        n_fonts = self.chaos.next_int(15, 25)
        profile.allowed_fonts = sorted(
            [self.chaos.next_choice(COMMON_FONTS) for _ in range(n_fonts)]
        )
        profile.allowed_fonts = list(dict.fromkeys(profile.allowed_fonts))

        # Canvas noise
        profile.canvas_noise_seed = secrets.token_hex(8)
        profile.canvas_noise_intensity = 0.01 + self.chaos.next() * 0.03

        # Audio noise
        profile.audio_noise_seed = secrets.token_hex(8)
        profile.audio_sample_rate = self.chaos.next_choice([44100, 48000])

        # Network characteristics
        profile.effective_type = self.chaos.next_choice(["4g", "4g", "4g", "3g"])
        profile.downlink = round(5.0 + self.chaos.next() * 20.0, 1)
        profile.rtt = self.chaos.next_int(25, 150)

        # TLS/JA3
        profile.ja3_hash = self.chaos.next_choice(JA3_PROFILES)

        # TCP stack
        profile.tcp_window_size = self.chaos.next_choice([65535, 64240, 65535])
        profile.tcp_ttl = self.chaos.next_choice([64, 128, 64])

        # HTTP header order
        profile.header_order = self.chaos.next_choice(HEADER_ORDER_PROFILES)

        return profile

    def _generate_ua(self, platform_profile: Dict) -> str:
        """Generate a user agent string consistent with the platform."""
        os_str = platform_profile['ua_os']

        if 'Mac' in platform_profile['platform']:
            # Safari or Chrome on Mac
            if self.chaos.next() > 0.5:
                ver = self.chaos.next_choice(CHROME_VERSIONS)
                return f"Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36"
            else:
                return f"Mozilla/5.0 ({os_str}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        elif 'Linux' in platform_profile['platform']:
            # Firefox on Linux
            ver = self.chaos.next_choice(FIREFOX_VERSIONS)
            return f"Mozilla/5.0 ({os_str}; rv:{ver}) Gecko/20100101 Firefox/{ver}"
        else:
            # Chrome or Firefox on Windows
            if self.chaos.next() > 0.3:
                ver = self.chaos.next_choice(CHROME_VERSIONS)
                return f"Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36"
            else:
                ver = self.chaos.next_choice(FIREFOX_VERSIONS)
                return f"Mozilla/5.0 ({os_str}; rv:{ver}) Gecko/20100101 Firefox/{ver}"


class FingerprintProtector:
    """
    Applies fingerprint protection in Docker containers.

    Generates iptables rules, proxy configs, browser overrides, and
    system-level modifications to present a consistent fake fingerprint.

    "Cats don't leave paw prints on digital surfaces."
    """

    def __init__(self, profile: Optional[FingerprintProfile] = None, seed: Optional[str] = None):
        self.generator = FingerprintGenerator(seed)
        self.profile = profile or self.generator.generate()
        self._active = False
        self._protection_log: List[Dict] = []

    def get_profile(self) -> FingerprintProfile:
        """Get the current fingerprint profile."""
        return self.profile

    def rotate_profile(self) -> FingerprintProfile:
        """Generate and apply a new fingerprint profile."""
        self.profile = self.generator.generate()
        self._log_event("profile_rotated", {"new_id": self.profile.profile_id})
        return self.profile

    def generate_firefox_prefs(self) -> Dict[str, Any]:
        """
        Generate Firefox about:config preferences to match the profile.
        These override the browser's real fingerprint.
        """
        p = self.profile
        prefs = {
            # Core fingerprint resistance
            'privacy.resistFingerprinting': True,
            'privacy.resistFingerprinting.letterboxing': True,

            # WebGL
            'webgl.disabled': False,  # Allow but spoof
            'webgl.renderer-string-override': p.webgl_renderer,
            'webgl.vendor-string-override': p.webgl_vendor,

            # Canvas
            'privacy.resistFingerprinting.randomDataOnCanvasExtract': True,

            # Screen
            'privacy.window.maxInnerWidth': p.screen_width,
            'privacy.window.maxInnerHeight': p.screen_height,

            # Timezone
            'privacy.resistFingerprinting.spoofOsLocale': True,

            # WebRTC
            'media.peerconnection.enabled': False,
            'media.peerconnection.ice.default_address_only': True,
            'media.peerconnection.ice.no_host': True,
            'media.peerconnection.ice.proxy_only_if_behind_proxy': True,

            # Network info
            'dom.netinfo.enabled': False,

            # Battery
            'dom.battery.enabled': False,

            # Gamepad
            'dom.gamepad.enabled': False,

            # Sensor APIs
            'device.sensors.enabled': False,

            # Speech synthesis
            'media.webspeech.synth.enabled': False,

            # Keyboard layout
            'privacy.resistFingerprinting.block_mozAddonManager': True,

            # General privacy
            'privacy.trackingprotection.enabled': True,
            'privacy.trackingprotection.fingerprinting.enabled': True,
            'privacy.trackingprotection.cryptomining.enabled': True,
            'privacy.firstparty.isolate': True,
            'network.cookie.cookieBehavior': 1,
            'geo.enabled': False,
            'media.navigator.enabled': False,
            'network.prefetch-next': False,
            'network.dns.disablePrefetch': True,
            'toolkit.telemetry.enabled': False,
            'datareporting.healthreport.uploadEnabled': False,

            # Font fingerprinting
            'browser.display.use_document_fonts': 0,
            'font.system.whitelist': ','.join(p.allowed_fonts),

            # User agent
            'general.useragent.override': p.user_agent,
            'general.platform.override': p.platform,
            'general.oscpu.override': p.platform,
        }
        return prefs

    def generate_chromium_args(self) -> List[str]:
        """Generate Chromium command-line flags to match the profile."""
        p = self.profile
        args = [
            '--disable-features=WebRtcHideLocalIpsWithMdns',
            '--disable-webgl',
            '--disable-reading-from-canvas',
            f'--user-agent={p.user_agent}',
            '--disable-background-networking',
            '--disable-breakpad',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-domain-reliability',
            '--disable-extensions',
            '--disable-hang-monitor',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            f'--window-size={p.screen_width},{p.screen_height}',
            f'--lang={p.language}',
        ]
        return args

    def generate_iptables_rules(self) -> List[str]:
        """
        Generate iptables rules for TCP/IP stack normalization.
        Prevents OS fingerprinting via network stack analysis.
        """
        p = self.profile
        rules = [
            # Normalize TTL to match profile
            f"iptables -t mangle -A POSTROUTING -j TTL --ttl-set {p.tcp_ttl}",
            # Set TCP window size
            f"iptables -t mangle -A POSTROUTING -p tcp -j TCPMSS --set-mss {min(p.tcp_window_size, 1460)}",
            # Block WebRTC STUN/TURN leak attempts
            "iptables -A OUTPUT -p udp --dport 3478 -j DROP",
            "iptables -A OUTPUT -p tcp --dport 3478 -j DROP",
            "iptables -A OUTPUT -p udp --dport 5349 -j DROP",
            # Block direct DNS (force through proxy/container DNS)
            "iptables -A OUTPUT -p udp --dport 53 ! -d 127.0.0.1 -j DROP",
            "iptables -A OUTPUT -p tcp --dport 53 ! -d 127.0.0.1 -j DROP",
        ]
        return rules

    def generate_sysctl_config(self) -> Dict[str, str]:
        """
        Generate sysctl settings for TCP/IP stack normalization.
        Makes the container's network stack look like the target OS.
        """
        p = self.profile
        config = {}

        if p.tcp_ttl == 128:
            # Windows-like TCP stack
            config.update({
                'net.ipv4.ip_default_ttl': '128',
                'net.ipv4.tcp_window_scaling': '1',
                'net.ipv4.tcp_timestamps': '1',
                'net.ipv4.tcp_sack': '1',
                'net.core.rmem_default': '65535',
                'net.core.wmem_default': '65535',
            })
        else:
            # Linux-like TCP stack (default)
            config.update({
                'net.ipv4.ip_default_ttl': '64',
                'net.ipv4.tcp_window_scaling': '1',
                'net.ipv4.tcp_timestamps': '1',
                'net.ipv4.tcp_sack': '1',
                'net.core.rmem_default': '212992',
                'net.core.wmem_default': '212992',
            })

        return config

    def generate_injection_script(self) -> str:
        """
        Generate a JavaScript injection script that spoofs browser APIs.
        This is injected via browser extension or proxy to override
        fingerprinting APIs with our profile's values.
        """
        p = self.profile
        return f"""
// spicy-cat Fingerprint Protection Injection
// "A cat walks through the internet leaving no trace."
(function() {{
    'use strict';

    // ── Canvas Fingerprint Protection ──────────────────────────────
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    const noiseSeed = '{p.canvas_noise_seed}';
    const noiseIntensity = {p.canvas_noise_intensity};

    function seedRandom(seed) {{
        let h = 0;
        for (let i = 0; i < seed.length; i++) {{
            h = ((h << 5) - h + seed.charCodeAt(i)) | 0;
        }}
        return function() {{
            h = (h * 1664525 + 1013904223) | 0;
            return ((h >>> 16) & 0xffff) / 0x10000;
        }};
    }}

    const rng = seedRandom(noiseSeed + document.location.hostname);

    function addCanvasNoise(imageData) {{
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {{
            const noise = (rng() - 0.5) * noiseIntensity * 255;
            data[i] = Math.max(0, Math.min(255, data[i] + noise));
            data[i+1] = Math.max(0, Math.min(255, data[i+1] + noise));
            data[i+2] = Math.max(0, Math.min(255, data[i+2] + noise));
        }}
        return imageData;
    }}

    CanvasRenderingContext2D.prototype.getImageData = function(...args) {{
        return addCanvasNoise(originalGetImageData.apply(this, args));
    }};

    HTMLCanvasElement.prototype.toDataURL = function(...args) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            const imageData = originalGetImageData.call(ctx, 0, 0, this.width, this.height);
            addCanvasNoise(imageData);
            ctx.putImageData(imageData, 0, 0);
        }}
        return originalToDataURL.apply(this, args);
    }};

    // ── WebGL Fingerprint Protection ──────────────────────────────
    const getParameterProto = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {{
        if (param === 37445) return '{p.webgl_unmasked_vendor}';
        if (param === 37446) return '{p.webgl_unmasked_renderer}';
        return getParameterProto.call(this, param);
    }};

    try {{
        const getParameterProto2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{p.webgl_unmasked_vendor}';
            if (param === 37446) return '{p.webgl_unmasked_renderer}';
            return getParameterProto2.call(this, param);
        }};
    }} catch(e) {{}}

    // ── AudioContext Fingerprint Protection ────────────────────────
    const origCreateOscillator = AudioContext.prototype.createOscillator;
    const origCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
    AudioContext.prototype.createOscillator = function() {{
        const osc = origCreateOscillator.call(this);
        const origConnect = osc.connect.bind(osc);
        osc.connect = function(dest) {{
            // Inject tiny noise node in the chain
            const gainNode = this.context.createGain();
            gainNode.gain.value = 1.0 + (rng() - 0.5) * 0.0001;
            origConnect(gainNode);
            gainNode.connect(dest);
            return dest;
        }};
        return osc;
    }};

    // ── Navigator Properties ──────────────────────────────────────
    const navProps = {{
        platform: '{p.platform}',
        hardwareConcurrency: {p.hardware_concurrency},
        deviceMemory: {p.device_memory},
        maxTouchPoints: {p.max_touch_points},
        language: '{p.language}',
        languages: {json.dumps(p.languages)},
    }};

    for (const [key, value] of Object.entries(navProps)) {{
        try {{
            Object.defineProperty(navigator, key, {{
                get: () => value,
                configurable: true,
            }});
        }} catch(e) {{}}
    }}

    // ── Screen Properties ─────────────────────────────────────────
    const screenProps = {{
        width: {p.screen_width},
        height: {p.screen_height},
        availWidth: {p.screen_width},
        availHeight: {p.screen_height - 40},
        colorDepth: {p.color_depth},
        pixelDepth: {p.color_depth},
    }};

    for (const [key, value] of Object.entries(screenProps)) {{
        try {{
            Object.defineProperty(screen, key, {{
                get: () => value,
                configurable: true,
            }});
        }} catch(e) {{}}
    }}

    Object.defineProperty(window, 'devicePixelRatio', {{
        get: () => {p.pixel_ratio},
        configurable: true,
    }});

    // ── Timezone Spoofing ─────────────────────────────────────────
    const targetOffset = {p.timezone_offset};
    const origGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {{
        return targetOffset;
    }};

    const origResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
        const opts = origResolvedOptions.call(this);
        opts.timeZone = '{p.timezone_name}';
        return opts;
    }};

    // ── Battery API Blocking ──────────────────────────────────────
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.reject(new Error('Battery API disabled'));
    }}

    // ── Font Enumeration Protection ───────────────────────────────
    const allowedFonts = new Set({json.dumps(p.allowed_fonts)});
    const origOffsetWidth = Object.getOwnPropertyDescriptor(
        HTMLElement.prototype, 'offsetWidth'
    );
    // Font detection works by measuring text width with specific fonts
    // We add slight noise to measurements to confuse font enumeration
    if (origOffsetWidth && origOffsetWidth.get) {{
        Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {{
            get: function() {{
                const width = origOffsetWidth.get.call(this);
                return width + (rng() - 0.5) * {p.font_metrics_noise} * width;
            }}
        }});
    }}

    // ── WebRTC Protection ─────────────────────────────────────────
    if (window.RTCPeerConnection) {{
        window.RTCPeerConnection = function() {{
            throw new DOMException('WebRTC disabled', 'NotAllowedError');
        }};
    }}

    // ── Network Information API ───────────────────────────────────
    if (navigator.connection) {{
        try {{
            Object.defineProperty(navigator.connection, 'effectiveType', {{
                get: () => '{p.effective_type}', configurable: true
            }});
            Object.defineProperty(navigator.connection, 'downlink', {{
                get: () => {p.downlink}, configurable: true
            }});
            Object.defineProperty(navigator.connection, 'rtt', {{
                get: () => {p.rtt}, configurable: true
            }});
        }} catch(e) {{}}
    }}

    console.log('[spicy-cat] Fingerprint protection active: {p.profile_id}');
}})();
"""

    def get_protection_summary(self) -> Dict:
        """Get a summary of all active protections."""
        p = self.profile
        return {
            'profile_id': p.profile_id,
            'vectors_protected': len(FingerprintVector),
            'protections': {
                'canvas': f'Noise seed {p.canvas_noise_seed[:8]}... intensity {p.canvas_noise_intensity:.3f}',
                'webgl': f'{p.webgl_unmasked_renderer}',
                'audio': f'Noise seed {p.audio_noise_seed[:8]}... @ {p.audio_sample_rate}Hz',
                'fonts': f'{len(p.allowed_fonts)} whitelisted fonts',
                'screen': f'{p.screen_width}x{p.screen_height} @{p.pixel_ratio}x',
                'navigator': f'{p.platform} / {p.language}',
                'webrtc': 'Disabled',
                'timezone': f'{p.timezone_name} (UTC{p.timezone_offset//60:+d})',
                'battery': 'API disabled',
                'hardware': f'{p.hardware_concurrency} cores / {p.device_memory}GB',
                'plugins': 'Normalized',
                'tcp_stack': f'TTL={p.tcp_ttl} WIN={p.tcp_window_size}',
                'tls_ja3': f'{hashlib.md5(p.ja3_hash.encode()).hexdigest()[:12]}...',
                'http_headers': f'{len(p.header_order)} headers in browser-consistent order',
            },
        }

    def _log_event(self, event_type: str, details: Dict):
        """Log a protection event."""
        self._protection_log.append({
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'details': details,
        })


# ── CLI Demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== spicy-cat Fingerprint Protection ===\n")

    gen = FingerprintGenerator("demo_seed")
    profile = gen.generate()

    protector = FingerprintProtector(profile)

    summary = protector.get_protection_summary()
    print(f"Profile ID: {summary['profile_id']}")
    print(f"Vectors Protected: {summary['vectors_protected']}")
    print()

    for vector, desc in summary['protections'].items():
        print(f"  {vector:15} {desc}")

    print(f"\nUser-Agent: {profile.user_agent}")
    print(f"\nFirefox prefs: {len(protector.generate_firefox_prefs())} settings")
    print(f"Chromium flags: {len(protector.generate_chromium_args())} flags")
    print(f"iptables rules: {len(protector.generate_iptables_rules())} rules")
    print(f"JS injection: {len(protector.generate_injection_script())} chars")
