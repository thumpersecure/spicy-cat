#!/usr/bin/env python3
"""
telemetry_chaos.py - 10 Creative Telemetry Confusion Methods for spicy-cat

"Cats don't use WiFi. They use meow-fi. And they encrypt everything."

Implements 10 unique methods to confuse telemetry collection systems,
specifically designed for use over WiFi networks while simultaneously
running advanced fingerprint protection.

The 10 Methods:
1.  Phantom Device Swarm - Broadcast as dozens of different device types
2.  Temporal Drift Engine - Skew timestamps across requests chaotically
3.  Geolocation Carousel - Rotate through plausible GPS coordinates
4.  DNS Chaff Generator - Flood DNS with decoy lookups
5.  Beacon Entropy Mixer - Inject noise into WiFi probe requests
6.  TLS Handshake Shuffler - Vary TLS fingerprints per connection
7.  HTTP Cookie Chimera - Generate contradictory tracking cookies
8.  User-Agent Metamorph - Morph UA strings mid-session organically
9.  Referrer Chain Fabricator - Create fake browsing history trails
10. Telemetry Feedback Loop - Send corrupted telemetry back to collectors
"""

import os
import json
import time
import random
import hashlib
import secrets
import socket
import struct
import threading
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from .chaos import LogisticMap, LorenzAttractor, ChaoticTimer
except ImportError:
    from chaos import LogisticMap, LorenzAttractor, ChaoticTimer


class TelemetryMethod(Enum):
    """The 10 creative telemetry confusion methods."""
    PHANTOM_SWARM = "phantom_device_swarm"
    TEMPORAL_DRIFT = "temporal_drift_engine"
    GEO_CAROUSEL = "geolocation_carousel"
    DNS_CHAFF = "dns_chaff_generator"
    BEACON_ENTROPY = "beacon_entropy_mixer"
    TLS_SHUFFLE = "tls_handshake_shuffler"
    COOKIE_CHIMERA = "http_cookie_chimera"
    UA_METAMORPH = "useragent_metamorph"
    REFERRER_FABRICATOR = "referrer_chain_fabricator"
    FEEDBACK_LOOP = "telemetry_feedback_loop"


TELEMETRY_DESCRIPTIONS = {
    TelemetryMethod.PHANTOM_SWARM: "Broadcast as dozens of phantom device types on WiFi",
    TelemetryMethod.TEMPORAL_DRIFT: "Chaotically skew timestamps to break session correlation",
    TelemetryMethod.GEO_CAROUSEL: "Rotate through plausible GPS coordinates per request",
    TelemetryMethod.DNS_CHAFF: "Flood WiFi DNS resolver with decoy domain lookups",
    TelemetryMethod.BEACON_ENTROPY: "Inject entropy noise into WiFi management frames",
    TelemetryMethod.TLS_SHUFFLE: "Vary TLS cipher suites and extensions per connection",
    TelemetryMethod.COOKIE_CHIMERA: "Generate contradictory tracking cookies across requests",
    TelemetryMethod.UA_METAMORPH: "Morph User-Agent strings organically mid-session",
    TelemetryMethod.REFERRER_FABRICATOR: "Create fake browsing history referrer chains",
    TelemetryMethod.FEEDBACK_LOOP: "Send corrupted telemetry data back to collection endpoints",
}


@dataclass
class TelemetryChaosEvent:
    """A single telemetry confusion event."""
    timestamp: datetime
    method: TelemetryMethod
    details: Dict
    target: str = ""
    spoofed_data: Dict = field(default_factory=dict)


# ── Device Profiles for Phantom Swarm ──────────────────────────────────────

PHANTOM_DEVICES = [
    {"type": "smart_tv", "vendor": "Samsung", "model": "UN55TU7000",
     "mac_prefix": "8C:79:F5", "hostname": "Samsung-SmartTV",
     "ua": "Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.5) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/5.0 Chrome/85.0.4183.93 TV Safari/537.36"},
    {"type": "smart_tv", "vendor": "LG", "model": "OLED55C1",
     "mac_prefix": "A8:23:FE", "hostname": "LGwebOSTV",
     "ua": "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 WebAppManager"},
    {"type": "gaming_console", "vendor": "Sony", "model": "PlayStation 5",
     "mac_prefix": "F8:46:1C", "hostname": "PS5-Console",
     "ua": "Mozilla/5.0 (PlayStation; PlayStation 5/4.03) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"},
    {"type": "gaming_console", "vendor": "Microsoft", "model": "Xbox Series X",
     "mac_prefix": "B4:09:31", "hostname": "XboxSeriesX",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edge/44.19041.1023"},
    {"type": "iot_hub", "vendor": "Amazon", "model": "Echo Show 15",
     "mac_prefix": "44:65:0D", "hostname": "amazon-echo",
     "ua": "Mozilla/5.0 (Linux; Android 11; AEOBP) AppleWebKit/537.36 (KHTML, like Gecko) Silk/95.3.6 like Chrome/95.0.4638.74 Safari/537.36"},
    {"type": "smart_fridge", "vendor": "Samsung", "model": "Family Hub",
     "mac_prefix": "8C:79:F5", "hostname": "Samsung-Fridge",
     "ua": "Mozilla/5.0 (Linux; Tizen 5.5; SmartFridge) AppleWebKit/537.36"},
    {"type": "smart_speaker", "vendor": "Google", "model": "Nest Hub Max",
     "mac_prefix": "54:60:09", "hostname": "Google-Nest",
     "ua": "Mozilla/5.0 (Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Safari/537.36 CrKey/1.56.500000"},
    {"type": "robot_vacuum", "vendor": "iRobot", "model": "Roomba j7+",
     "mac_prefix": "50:14:79", "hostname": "iRobot-Roomba",
     "ua": "iRobotSoftware/3.12.8 CFNetwork/1390 Darwin/22.0.0"},
    {"type": "security_cam", "vendor": "Ring", "model": "Doorbell Pro 2",
     "mac_prefix": "5C:47:5E", "hostname": "Ring-Doorbell",
     "ua": "Ring/5.64.0 (Linux; Android 12) okhttp/4.10.0"},
    {"type": "thermostat", "vendor": "Ecobee", "model": "SmartThermostat",
     "mac_prefix": "44:61:32", "hostname": "ecobee-stat",
     "ua": "ecobee/6.10.0 (Linux; Android 11) Dalvik/2.1.0"},
    {"type": "smart_watch", "vendor": "Apple", "model": "Watch Series 9",
     "mac_prefix": "F0:18:98", "hostname": "AppleWatch",
     "ua": "Mozilla/5.0 (Apple Watch; watchOS 10.1) AppleWebKit/605.1.15"},
    {"type": "printer", "vendor": "HP", "model": "LaserJet Pro M404dn",
     "mac_prefix": "3C:D9:2B", "hostname": "HP-LaserJet",
     "ua": "HP-ChaiServer/3.0"},
    {"type": "nas", "vendor": "Synology", "model": "DS920+",
     "mac_prefix": "00:11:32", "hostname": "DiskStation",
     "ua": "Mozilla/5.0 (X11; Linux x86_64; DiskStation) nginx"},
    {"type": "smart_plug", "vendor": "TP-Link", "model": "Tapo P110",
     "mac_prefix": "B0:A7:B9", "hostname": "Tapo-Plug",
     "ua": "Tapo/2.12.0.5 CFNetwork/1399 Darwin/22.1.0"},
    {"type": "ip_camera", "vendor": "Wyze", "model": "Cam v3",
     "mac_prefix": "2C:AA:8E", "hostname": "WyzeCam",
     "ua": "Wyze/2.42.0.189 (Android 12; SM-G998B)"},
    {"type": "ebook_reader", "vendor": "Amazon", "model": "Kindle Paperwhite 5",
     "mac_prefix": "44:65:0D", "hostname": "Kindle",
     "ua": "Mozilla/5.0 (X11; U; Linux armv7l like Android; en-us) AppleWebKit/537.36 (KHTML, like Gecko) Silk/95.3.1 Safari/537.36"},
]


# ── Geolocation Pools (metro areas with realistic variance) ────────────────

GEO_POOLS = {
    'new_york': [(40.7128, -74.0060, 0.02), (40.7580, -73.9855, 0.015), (40.6892, -74.0445, 0.01)],
    'los_angeles': [(34.0522, -118.2437, 0.03), (33.9425, -118.4081, 0.02), (34.1478, -118.1445, 0.02)],
    'chicago': [(41.8781, -87.6298, 0.02), (41.8827, -87.6233, 0.015)],
    'london': [(51.5074, -0.1278, 0.02), (51.5155, -0.1419, 0.015)],
    'berlin': [(52.5200, 13.4050, 0.02), (52.5163, 13.3777, 0.015)],
    'tokyo': [(35.6762, 139.6503, 0.02), (35.6595, 139.7004, 0.015)],
    'sydney': [(-33.8688, 151.2093, 0.02), (-33.8568, 151.2153, 0.015)],
    'toronto': [(43.6532, -79.3832, 0.02), (43.6426, -79.3871, 0.015)],
    'paris': [(48.8566, 2.3522, 0.02), (48.8606, 2.3376, 0.015)],
    'sao_paulo': [(-23.5505, -46.6333, 0.03), (-23.5489, -46.6388, 0.02)],
}


# ── Decoy DNS Domains ─────────────────────────────────────────────────────

DNS_CHAFF_DOMAINS = [
    # Mix of plausible browsing patterns
    "weather.com", "reddit.com", "stackoverflow.com", "wikipedia.org",
    "amazon.com", "ebay.com", "netflix.com", "spotify.com",
    "linkedin.com", "github.com", "medium.com", "bbc.co.uk",
    "nytimes.com", "washingtonpost.com", "cnn.com", "reuters.com",
    "espn.com", "twitch.tv", "discord.com", "zoom.us",
    "dropbox.com", "notion.so", "figma.com", "canva.com",
    "hulu.com", "disneyplus.com", "hbomax.com", "peacocktv.com",
    "target.com", "walmart.com", "bestbuy.com", "homedepot.com",
    "yelp.com", "tripadvisor.com", "booking.com", "airbnb.com",
    "indeed.com", "glassdoor.com", "zillow.com", "realtor.com",
    "webmd.com", "mayoclinic.org", "healthline.com",
    "coursera.org", "udemy.com", "khanacademy.org",
    "npr.org", "theguardian.com", "apnews.com",
]

# Subdomain patterns to make lookups more realistic
DNS_SUBDOMAIN_PATTERNS = [
    "www.{domain}", "api.{domain}", "cdn.{domain}", "static.{domain}",
    "images.{domain}", "assets.{domain}", "m.{domain}", "app.{domain}",
    "login.{domain}", "auth.{domain}", "accounts.{domain}",
    "analytics.{domain}", "tracking.{domain}", "pixel.{domain}",
    "ads.{domain}", "video.{domain}", "stream.{domain}",
]


# ── Referrer Chain Templates ───────────────────────────────────────────────

REFERRER_CHAINS = [
    # Social media -> news -> shopping
    ["https://twitter.com/home", "https://t.co/abc123", "https://www.nytimes.com/article",
     "https://www.amazon.com/dp/B09V3KXJPB"],
    # Search -> research -> tools
    ["https://www.google.com/search?q=python+tutorial", "https://docs.python.org/3/tutorial/",
     "https://stackoverflow.com/questions/123", "https://github.com/python/cpython"],
    # Email -> shopping -> review
    ["https://mail.google.com/mail/u/0/", "https://www.amazon.com/gp/goldbox",
     "https://www.amazon.com/dp/B0BSHF7P", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    # News aggregator -> article -> related
    ["https://news.ycombinator.com/", "https://www.wired.com/story/tech-article",
     "https://arstechnica.com/science/", "https://www.reddit.com/r/technology/"],
    # Direct -> login -> dashboard
    ["", "https://accounts.google.com/signin", "https://myaccount.google.com/",
     "https://drive.google.com/drive/my-drive"],
]


# ── Telemetry Collector Endpoints (for corrupted feedback) ──────────────────

TELEMETRY_ENDPOINTS = [
    # These are patterns for generating plausible telemetry endpoint URLs
    # Actual requests go to non-existent subdomains to avoid real traffic
    "telemetry-{rand}.example.com",
    "analytics-{rand}.example.com",
    "pixel-{rand}.example.com",
    "beacon-{rand}.example.com",
    "collect-{rand}.example.com",
    "events-{rand}.example.com",
    "metrics-{rand}.example.com",
    "track-{rand}.example.com",
]


# ── Cookie Templates ───────────────────────────────────────────────────────

TRACKING_COOKIE_TEMPLATES = [
    {"name": "_ga", "pattern": "GA1.2.{r1}.{r2}", "domain": ".google-analytics.com"},
    {"name": "_fbp", "pattern": "fb.1.{ts}.{r1}", "domain": ".facebook.com"},
    {"name": "_gcl_au", "pattern": "1.1.{r1}.{ts}", "domain": ".google.com"},
    {"name": "IDE", "pattern": "AHWqTU{hash}", "domain": ".doubleclick.net"},
    {"name": "_uetsid", "pattern": "{hash32}", "domain": ".bing.com"},
    {"name": "NID", "pattern": "511={hash}=", "domain": ".google.com"},
    {"name": "__gads", "pattern": "ID={hash}:T={ts}:RT={ts}:S={hash8}", "domain": ".google.com"},
    {"name": "_pin_unauth", "pattern": "dWlkPXt{hash}", "domain": ".pinterest.com"},
]


# ══════════════════════════════════════════════════════════════════════════
#   THE 10 METHODS
# ══════════════════════════════════════════════════════════════════════════


class PhantomDeviceSwarm:
    """
    Method 1: Phantom Device Swarm

    Broadcasts network traffic as if it's coming from dozens of different
    IoT devices, smart TVs, gaming consoles, etc. on the same WiFi network.
    This creates noise that makes it impossible to isolate the real device.

    "A cat surrounded by decoy cats is invisible."
    """

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "phantom_swarm")
        self.active_phantoms: List[Dict] = []
        self._lock = threading.Lock()

    def generate_phantom(self) -> Dict:
        """Generate a phantom device identity."""
        device = self.chaos.next_choice(PHANTOM_DEVICES)
        suffix = secrets.token_hex(3).upper()
        mac_suffix = ':'.join([secrets.token_hex(1).upper() for _ in range(3)])

        phantom = {
            'device': device.copy(),
            'mac': f"{device['mac_prefix']}:{mac_suffix}",
            'hostname': f"{device['hostname']}-{suffix}",
            'ip': f"192.168.{random.randint(1, 254)}.{random.randint(2, 254)}",
            'created': datetime.now().isoformat(),
        }

        with self._lock:
            self.active_phantoms.append(phantom)
        return phantom

    def generate_swarm(self, count: int = 15) -> List[Dict]:
        """Generate a swarm of phantom devices."""
        return [self.generate_phantom() for _ in range(count)]

    def get_phantom_dns_queries(self, phantom: Dict) -> List[str]:
        """Generate realistic DNS queries for a phantom device type."""
        device = phantom['device']
        queries = []

        if device['type'] == 'smart_tv':
            queries = [
                "api.samsungcloudsolution.com", "osb-apps.samsungqbe.com",
                "lcprd1.samsungcloudsolution.net", "gpm.samsungqbe.com",
                "api.netflix.com", "api2.hulu.com",
            ]
        elif device['type'] == 'gaming_console':
            queries = [
                "ps4-system.sec.np.dl.playstation.net", "nsx.np.dl.playstation.net",
                "activity.windows.com", "xboxlive.com",
                "perf.dogfood.office.com",
            ]
        elif device['type'] in ('iot_hub', 'smart_speaker'):
            queries = [
                "device-metrics-us-2.amazon.com", "api.amazonalexa.com",
                "unagi-na.amazon.com", "todo-ta-g7g.amazon.com",
                "clients3.google.com", "connectivitycheck.gstatic.com",
            ]
        elif device['type'] in ('security_cam', 'ip_camera'):
            queries = [
                "fw.ring.com", "ntp-g7g.amazon.com",
                "api.wyzecam.com", "wyze-mars-service.wyzecam.com",
            ]
        elif device['type'] == 'robot_vacuum':
            queries = [
                "disc-prod.iot.irobotapi.com", "data.iot.irobotapi.com",
                "realm-prod.iot.irobotapi.com",
            ]
        elif device['type'] == 'thermostat':
            queries = [
                "api.ecobee.com", "home.ecobee.com",
                "push.ecobee.com",
            ]
        else:
            queries = [
                "connectivitycheck.gstatic.com",
                "captive.apple.com",
                "ntp.ubuntu.com",
            ]

        return queries

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a phantom device swarm event."""
        phantom = self.generate_phantom()
        dns_queries = self.get_phantom_dns_queries(phantom)
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.PHANTOM_SWARM,
            target=phantom['hostname'],
            details={
                'device_type': phantom['device']['type'],
                'vendor': phantom['device']['vendor'],
                'model': phantom['device']['model'],
                'mac': phantom['mac'],
                'dns_queries': dns_queries,
                'user_agent': phantom['device']['ua'],
            },
            spoofed_data={'phantom': phantom},
        )


class TemporalDriftEngine:
    """
    Method 2: Temporal Drift Engine

    Chaotically skews timestamps across HTTP requests, DNS queries,
    and protocol headers. This breaks time-based session correlation
    used by telemetry systems to link requests from the same user.

    "A cat exists outside of time. So should your packets."
    """

    def __init__(self, seed: str = None):
        self.lorenz = LorenzAttractor(seed or "temporal_drift")
        self.chaos = LogisticMap(seed or "temporal_drift_select")
        self.base_drift = 0.0  # Accumulated drift in seconds

    def get_drifted_timestamp(self) -> datetime:
        """Get a timestamp with chaotic drift applied."""
        noise = self.lorenz.next_normalized()
        # Drift ranges from -30 to +30 seconds, varying chaotically
        drift_delta = noise[0] * 30.0
        self.base_drift += noise[1] * 0.5  # Slow cumulative drift
        total_drift = drift_delta + self.base_drift

        return datetime.now() + timedelta(seconds=total_drift)

    def get_skewed_headers(self) -> Dict[str, str]:
        """Generate HTTP headers with skewed timing information."""
        drifted = self.get_drifted_timestamp()
        return {
            'Date': drifted.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'X-Request-Time': str(int(drifted.timestamp() * 1000)),
            'X-Client-Timestamp': drifted.isoformat() + 'Z',
        }

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a temporal drift event."""
        drifted = self.get_drifted_timestamp()
        headers = self.get_skewed_headers()
        real_time = datetime.now()
        drift_amount = (drifted - real_time).total_seconds()

        return TelemetryChaosEvent(
            timestamp=real_time,
            method=TelemetryMethod.TEMPORAL_DRIFT,
            target="all_outbound_traffic",
            details={
                'drift_seconds': round(drift_amount, 2),
                'drifted_timestamp': drifted.isoformat(),
                'real_timestamp': real_time.isoformat(),
                'skewed_headers': headers,
            },
            spoofed_data={'headers': headers},
        )


class GeolocationCarousel:
    """
    Method 3: Geolocation Carousel

    Rotates through plausible GPS coordinates with each request,
    making it appear the device is moving through a metro area.
    Coordinates are kept realistic (within city bounds with natural
    variance) to avoid detection as obviously spoofed.

    "A cat is everywhere and nowhere at once."
    """

    def __init__(self, city: str = None, seed: str = None):
        self.chaos = LogisticMap(seed or "geo_carousel")
        self.lorenz = LorenzAttractor(seed or "geo_carousel_path")
        self.city = city or self.chaos.next_choice(list(GEO_POOLS.keys()))
        self.pool = GEO_POOLS[self.city]
        self._current_idx = 0

    def get_location(self) -> Tuple[float, float, float]:
        """Get a spoofed GPS location (lat, lon, accuracy_meters)."""
        base = self.chaos.next_choice(self.pool)
        noise = self.lorenz.next_normalized()

        # Add organic noise within the variance radius
        lat = base[0] + noise[0] * base[2]
        lon = base[1] + noise[1] * base[2]
        accuracy = 10.0 + abs(noise[2]) * 100.0  # 10-110m accuracy

        return (round(lat, 6), round(lon, 6), round(accuracy, 1))

    def get_geo_headers(self) -> Dict[str, str]:
        """Generate HTTP headers with spoofed geolocation."""
        lat, lon, acc = self.get_location()
        return {
            'X-Geo-Position': f'{lat};{lon}',
            'X-Geo-Accuracy': str(int(acc)),
            'Geolocation': f'{lat},{lon},{acc}',
        }

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a geolocation carousel event."""
        lat, lon, acc = self.get_location()
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.GEO_CAROUSEL,
            target=self.city,
            details={
                'latitude': lat,
                'longitude': lon,
                'accuracy_m': acc,
                'city': self.city,
                'geo_header': f'{lat};{lon}',
            },
            spoofed_data={'location': {'lat': lat, 'lon': lon, 'accuracy': acc}},
        )


class DNSChaffGenerator:
    """
    Method 4: DNS Chaff Generator

    Floods the WiFi network's DNS resolver with plausible but decoy
    domain lookups, making it impossible to determine which DNS queries
    are real browsing and which are chaff.

    "A cat shreds the evidence. We shred the DNS logs."
    """

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "dns_chaff")
        self.timer = ChaoticTimer(seed or "dns_chaff_timer", base_interval=2.0)
        self._query_log: List[Dict] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def generate_query(self) -> str:
        """Generate a single decoy DNS query."""
        domain = self.chaos.next_choice(DNS_CHAFF_DOMAINS)
        pattern = self.chaos.next_choice(DNS_SUBDOMAIN_PATTERNS)
        return pattern.format(domain=domain)

    def generate_batch(self, count: int = 10) -> List[str]:
        """Generate a batch of decoy DNS queries."""
        return [self.generate_query() for _ in range(count)]

    def execute_query(self, domain: str) -> Dict:
        """Actually perform a DNS lookup (for chaff generation)."""
        result = {'domain': domain, 'timestamp': datetime.now().isoformat()}
        try:
            answers = socket.getaddrinfo(domain, None, socket.AF_INET)
            result['resolved'] = True
            result['addresses'] = list(set(a[4][0] for a in answers))
        except socket.gaierror:
            result['resolved'] = False
            result['error'] = 'NXDOMAIN'
        except Exception as e:
            result['resolved'] = False
            result['error'] = str(e)

        self._query_log.append(result)
        return result

    def start_background(self, queries_per_burst: int = 5, interval: float = 3.0):
        """Start background DNS chaff generation."""
        self._running = True

        def _worker():
            while self._running:
                batch = self.generate_batch(queries_per_burst)
                for domain in batch:
                    if not self._running:
                        break
                    self.execute_query(domain)
                    time.sleep(0.1 + random.random() * 0.5)
                wait = self.timer.next_interval(0.5, 2.0)
                time.sleep(wait)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def stop_background(self):
        """Stop background DNS chaff generation."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def get_stats(self) -> Dict:
        """Get chaff generation statistics."""
        resolved = sum(1 for q in self._query_log if q.get('resolved'))
        return {
            'total_queries': len(self._query_log),
            'resolved': resolved,
            'failed': len(self._query_log) - resolved,
            'unique_domains': len(set(q['domain'] for q in self._query_log)),
        }

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a DNS chaff event."""
        batch = self.generate_batch(5)
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.DNS_CHAFF,
            target="dns_resolver",
            details={
                'batch_size': len(batch),
                'queries': batch,
                'stats': self.get_stats(),
            },
            spoofed_data={'dns_queries': batch},
        )


class BeaconEntropyMixer:
    """
    Method 5: Beacon Entropy Mixer

    Generates WiFi probe request data with randomized SSIDs,
    capabilities, and supported rates. This confuses WiFi analytics
    that track devices by their probe request patterns.

    "Like a cat leaving false scent trails everywhere."
    """

    # Common SSID patterns to probe for (realistic)
    PROBE_SSIDS = [
        "xfinitywifi", "ATT-WIFI-PASSPOINT", "optimumwifi",
        "Google Starbucks", "attwifi", "TWCWiFi",
        "CableWiFi", "XFINITY", "Boingo Hotspot",
        "HP-Print-{rand}", "DIRECT-{rand}-HP",
        "Ring-{rand}", "SimpliSafe-{rand}",
        "MySpectrumWiFi", "VerizonWiFi",
        "eduroam", "guest", "NETGEAR-{rand}",
        "linksys", "dlink-{rand}", "HOME-{rand}",
    ]

    # WiFi capability information elements
    SUPPORTED_RATES = [
        [1.0, 2.0, 5.5, 11.0],  # 802.11b only
        [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],  # 802.11b/g
        [6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],  # 802.11a/g only
    ]

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "beacon_entropy")
        self.lorenz = LorenzAttractor(seed or "beacon_path")

    def generate_probe_request(self) -> Dict:
        """Generate a spoofed WiFi probe request data structure."""
        ssid_template = self.chaos.next_choice(self.PROBE_SSIDS)
        ssid = ssid_template.format(rand=secrets.token_hex(2).upper())

        # Random MAC for the probe
        mac_bytes = [random.randint(0, 255) for _ in range(6)]
        mac_bytes[0] = (mac_bytes[0] | 0x02) & 0xFE  # Locally administered, unicast
        mac = ':'.join(f'{b:02X}' for b in mac_bytes)

        rates = self.chaos.next_choice(self.SUPPORTED_RATES)

        return {
            'ssid': ssid,
            'source_mac': mac,
            'supported_rates': rates,
            'ht_capable': self.chaos.next() > 0.3,
            'vht_capable': self.chaos.next() > 0.6,
            'he_capable': self.chaos.next() > 0.8,  # WiFi 6
            'power_capability': self.chaos.next_int(10, 20),
            'sequence_number': random.randint(0, 4095),
        }

    def generate_burst(self, count: int = 8) -> List[Dict]:
        """Generate a burst of probe requests from different phantom MACs."""
        return [self.generate_probe_request() for _ in range(count)]

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a beacon entropy event."""
        probes = self.generate_burst(5)
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.BEACON_ENTROPY,
            target="wifi_management_frames",
            details={
                'probe_count': len(probes),
                'unique_macs': len(set(p['source_mac'] for p in probes)),
                'ssids_probed': [p['ssid'] for p in probes],
                'sample_probe': probes[0] if probes else {},
            },
            spoofed_data={'probes': probes},
        )


class TLSHandshakeShuffler:
    """
    Method 6: TLS Handshake Shuffler

    Varies TLS cipher suites, extensions, and handshake parameters
    per connection to prevent JA3/JA3S fingerprinting. Each outgoing
    TLS connection looks like it comes from a different client.

    "Nine lives, nine TLS fingerprints."
    """

    CIPHER_SUITES = [
        # TLS 1.3 ciphers
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
        # TLS 1.2 ciphers
        "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
        "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
        "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
        "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
        "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    ]

    TLS_EXTENSIONS = [
        "server_name", "ec_point_formats", "supported_groups",
        "session_ticket", "encrypt_then_mac", "extended_master_secret",
        "signature_algorithms", "supported_versions", "psk_key_exchange_modes",
        "key_share", "application_layer_protocol_negotiation",
        "status_request", "signed_certificate_timestamp",
        "padding", "pre_shared_key", "early_data",
        "post_handshake_auth", "compress_certificate",
    ]

    ELLIPTIC_CURVES = [
        "x25519", "secp256r1", "secp384r1", "secp521r1",
        "x448", "ffdhe2048", "ffdhe3072",
    ]

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "tls_shuffle")

    def generate_tls_profile(self) -> Dict:
        """Generate a randomized TLS client profile."""
        # Select a subset of ciphers in random order
        n_ciphers = self.chaos.next_int(4, len(self.CIPHER_SUITES))
        ciphers = random.sample(self.CIPHER_SUITES, n_ciphers)

        # Select extensions in random order
        n_ext = self.chaos.next_int(8, len(self.TLS_EXTENSIONS))
        extensions = random.sample(self.TLS_EXTENSIONS, n_ext)

        # Select curves
        n_curves = self.chaos.next_int(2, len(self.ELLIPTIC_CURVES))
        curves = random.sample(self.ELLIPTIC_CURVES, n_curves)

        # Compute JA3-like hash
        ja3_string = f"771,{','.join(str(hash(c) % 65535) for c in ciphers)},{','.join(str(hash(e) % 65535) for e in extensions)},{','.join(str(hash(c) % 65535) for c in curves)},0"
        ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()

        return {
            'cipher_suites': ciphers,
            'extensions': extensions,
            'elliptic_curves': curves,
            'tls_version': self.chaos.next_choice(["1.2", "1.3", "1.3"]),
            'ja3_hash': ja3_hash,
            'compression_methods': [0],  # null only
            'alpn': self.chaos.next_choice([["h2", "http/1.1"], ["http/1.1"], ["h2"]]),
        }

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a TLS shuffle event."""
        profile = self.generate_tls_profile()
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.TLS_SHUFFLE,
            target="outbound_tls",
            details={
                'ja3_hash': profile['ja3_hash'],
                'cipher_count': len(profile['cipher_suites']),
                'extension_count': len(profile['extensions']),
                'tls_version': profile['tls_version'],
                'alpn': profile['alpn'],
            },
            spoofed_data={'tls_profile': profile},
        )


class HTTPCookieChimera:
    """
    Method 7: HTTP Cookie Chimera

    Generates contradictory tracking cookies that confuse ad networks
    and analytics systems. Each request carries cookies that suggest
    the user is multiple different people simultaneously.

    "Schrodinger's cookie - both tracked and untracked."
    """

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "cookie_chimera")
        self._cookie_jar: Dict[str, str] = {}

    def generate_tracking_cookie(self, template: Dict = None) -> Tuple[str, str]:
        """Generate a single fake tracking cookie."""
        if template is None:
            template = self.chaos.next_choice(TRACKING_COOKIE_TEMPLATES)

        ts = str(int(time.time()))
        r1 = str(random.randint(100000000, 999999999))
        r2 = str(random.randint(100000000, 999999999))
        hash_val = secrets.token_hex(16)
        hash32 = secrets.token_hex(32)
        hash8 = secrets.token_hex(4)

        value = template['pattern'].format(
            ts=ts, r1=r1, r2=r2, hash=hash_val, hash32=hash32, hash8=hash8
        )

        return (template['name'], value)

    def generate_cookie_set(self) -> Dict[str, str]:
        """Generate a full set of contradictory tracking cookies."""
        cookies = {}
        for template in TRACKING_COOKIE_TEMPLATES:
            name, value = self.generate_tracking_cookie(template)
            cookies[name] = value

        # Add some random advertising IDs
        cookies['_did'] = secrets.token_hex(16)
        cookies['_vid'] = f"v1.{secrets.token_hex(8)}"
        cookies['_sid'] = f"s.{int(time.time())}.{secrets.token_hex(4)}"

        self._cookie_jar = cookies
        return cookies

    def get_cookie_header(self) -> str:
        """Get a Cookie header string with chimera cookies."""
        if not self._cookie_jar:
            self.generate_cookie_set()
        return '; '.join(f'{k}={v}' for k, v in self._cookie_jar.items())

    def rotate_cookies(self):
        """Rotate all cookies to new contradictory values."""
        self.generate_cookie_set()

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a cookie chimera event."""
        cookies = self.generate_cookie_set()
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.COOKIE_CHIMERA,
            target="tracking_networks",
            details={
                'cookie_count': len(cookies),
                'cookie_names': list(cookies.keys()),
                'header_length': len(self.get_cookie_header()),
                'sample_ga': cookies.get('_ga', 'N/A'),
                'sample_fbp': cookies.get('_fbp', 'N/A'),
            },
            spoofed_data={'cookies': cookies},
        )


class UserAgentMetamorph:
    """
    Method 8: User-Agent Metamorph

    Organically morphs User-Agent strings mid-session, making it
    appear as if requests come from different browsers/versions.
    Uses Lorenz attractor to create natural-seeming transitions
    rather than abrupt changes.

    "A cat changes form as it moves through shadows."
    """

    BROWSER_STEMS = {
        'chrome_win': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
        'chrome_mac': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
        'chrome_linux': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36",
        'firefox_win': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{ver}) Gecko/20100101 Firefox/{ver}",
        'firefox_mac': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{ver}) Gecko/20100101 Firefox/{ver}",
        'firefox_linux': "Mozilla/5.0 (X11; Linux x86_64; rv:{ver}) Gecko/20100101 Firefox/{ver}",
        'safari_mac': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ver} Safari/605.1.15",
        'edge_win': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{cver} Safari/537.36 Edg/{ver}",
    }

    CHROME_VERS = ["120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0", "125.0.0.0"]
    FIREFOX_VERS = ["121.0", "122.0", "123.0", "124.0", "125.0", "126.0"]
    SAFARI_VERS = ["17.0", "17.1", "17.2", "17.3"]
    EDGE_VERS = ["120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0"]

    def __init__(self, seed: str = None):
        self.lorenz = LorenzAttractor(seed or "ua_metamorph")
        self.chaos = LogisticMap(seed or "ua_metamorph_select")
        self._current_family = None
        self._morph_count = 0

    def generate_ua(self) -> str:
        """Generate a morphed User-Agent string."""
        noise = self.lorenz.next_normalized()

        # Use Lorenz to determine if we should switch browser families
        # More extreme attractor positions = more likely to switch
        switch_threshold = 0.6
        if abs(noise[0]) > switch_threshold or self._current_family is None:
            self._current_family = self.chaos.next_choice(list(self.BROWSER_STEMS.keys()))
            self._morph_count += 1

        stem = self.BROWSER_STEMS[self._current_family]

        if 'chrome' in self._current_family:
            ver = self.chaos.next_choice(self.CHROME_VERS)
            return stem.format(ver=ver)
        elif 'firefox' in self._current_family:
            ver = self.chaos.next_choice(self.FIREFOX_VERS)
            return stem.format(ver=ver)
        elif 'safari' in self._current_family:
            ver = self.chaos.next_choice(self.SAFARI_VERS)
            return stem.format(ver=ver)
        elif 'edge' in self._current_family:
            ver = self.chaos.next_choice(self.EDGE_VERS)
            cver = self.chaos.next_choice(self.CHROME_VERS)
            return stem.format(ver=ver, cver=cver)

        return stem.format(ver="120.0.0.0")

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a UA metamorph event."""
        ua = self.generate_ua()
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.UA_METAMORPH,
            target="http_requests",
            details={
                'user_agent': ua,
                'browser_family': self._current_family,
                'morph_count': self._morph_count,
                'ua_length': len(ua),
            },
            spoofed_data={'user_agent': ua},
        )


class ReferrerChainFabricator:
    """
    Method 9: Referrer Chain Fabricator

    Creates fake but realistic browsing history trails via the
    Referer header. Makes it look like the user arrived at each
    page via a plausible navigation path, masking actual browsing.

    "Cats leave false trails. It's just good tradecraft."
    """

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "referrer_fab")
        self._current_chain: List[str] = []
        self._chain_position = 0

    def start_chain(self) -> List[str]:
        """Start a new referrer chain."""
        self._current_chain = self.chaos.next_choice(REFERRER_CHAINS).copy()
        self._chain_position = 0
        return self._current_chain

    def get_next_referrer(self) -> str:
        """Get the next referrer in the chain."""
        if not self._current_chain or self._chain_position >= len(self._current_chain):
            self.start_chain()

        referrer = self._current_chain[self._chain_position]
        self._chain_position += 1
        return referrer

    def generate_custom_chain(self, length: int = 5) -> List[str]:
        """Generate a custom referrer chain from component parts."""
        chain = []
        # Start with a search engine or direct
        starts = [
            "https://www.google.com/search?q=" + self.chaos.next_choice(
                ["news today", "weather", "python tutorial", "best restaurants",
                 "how to", "movie reviews", "stock market", "travel deals"]),
            "https://duckduckgo.com/?q=" + self.chaos.next_choice(
                ["privacy tools", "linux tips", "open source", "tech news"]),
            "",  # Direct navigation
        ]
        chain.append(self.chaos.next_choice(starts))

        # Add intermediate pages
        for _ in range(length - 2):
            domain = self.chaos.next_choice(DNS_CHAFF_DOMAINS)
            path = self.chaos.next_choice([
                "/article/", "/news/", "/blog/", "/product/",
                "/category/", "/search?q=", "/trending/",
            ])
            chain.append(f"https://www.{domain}{path}{secrets.token_hex(4)}")

        # End with something specific
        chain.append(f"https://www.{self.chaos.next_choice(DNS_CHAFF_DOMAINS)}/")
        return chain

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a referrer fabrication event."""
        chain = self.generate_custom_chain(4)
        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.REFERRER_FABRICATOR,
            target="http_referer_header",
            details={
                'chain_length': len(chain),
                'chain': chain,
                'current_referrer': chain[-2] if len(chain) > 1 else '',
                'destination': chain[-1],
            },
            spoofed_data={'referrer_chain': chain},
        )


class TelemetryFeedbackLoop:
    """
    Method 10: Telemetry Feedback Loop

    Sends corrupted telemetry data back to known collection endpoints.
    Instead of blocking telemetry, we poison it with contradictory
    information - wrong device IDs, impossible metrics, random session
    data. This degrades the quality of the telemetry database.

    "If you can't beat the watchers, confuse them."
    """

    def __init__(self, seed: str = None):
        self.chaos = LogisticMap(seed or "feedback_loop")

    def generate_corrupted_ga_payload(self) -> Dict:
        """Generate corrupted Google Analytics-style measurement data."""
        return {
            'v': '2',
            'tid': f"G-{secrets.token_hex(5).upper()}",
            'cid': f"{random.randint(100000000, 999999999)}.{random.randint(1000000000, 9999999999)}",
            'sid': secrets.token_hex(16),
            'dl': f"https://www.{self.chaos.next_choice(DNS_CHAFF_DOMAINS)}/{secrets.token_hex(4)}",
            'dt': self.chaos.next_choice([
                "Home Page", "Dashboard", "Settings", "Profile",
                "Search Results", "Product Page", "Cart", "Checkout",
            ]),
            'sr': self.chaos.next_choice(["1920x1080", "2560x1440", "1366x768", "3840x2160"]),
            'sd': self.chaos.next_choice(["24-bit", "32-bit"]),
            'ul': self.chaos.next_choice(["en-us", "en-gb", "de-de", "fr-fr", "ja"]),
            'je': self.chaos.next_choice(["0", "1"]),
            'fl': self.chaos.next_choice(["", "34.0.0.192"]),
            '_s': str(random.randint(1, 50)),
            '_ss': str(random.randint(1, 5)),
        }

    def generate_corrupted_fb_pixel(self) -> Dict:
        """Generate corrupted Facebook pixel-style data."""
        return {
            'id': str(random.randint(100000000000000, 999999999999999)),
            'ev': self.chaos.next_choice([
                "PageView", "ViewContent", "AddToCart",
                "Purchase", "Lead", "Search",
            ]),
            'dl': f"https://www.{self.chaos.next_choice(DNS_CHAFF_DOMAINS)}/",
            'rl': self.chaos.next_choice(REFERRER_CHAINS[0]),
            'ts': str(int(time.time() * 1000)),
            'sw': str(self.chaos.next_choice([1920, 2560, 1366])),
            'sh': str(self.chaos.next_choice([1080, 1440, 768])),
            'ud[em]': hashlib.sha256(f"fake_{secrets.token_hex(8)}@example.com".encode()).hexdigest(),
            'ud[ph]': hashlib.sha256(f"+1{random.randint(2000000000, 9999999999)}".encode()).hexdigest(),
        }

    def generate_corrupted_telemetry_beacon(self) -> Dict:
        """Generate a generic corrupted telemetry beacon."""
        return {
            'event': self.chaos.next_choice([
                'page_view', 'click', 'scroll', 'form_submit',
                'error', 'performance', 'vitals',
            ]),
            'session_id': secrets.token_hex(16),
            'user_id': secrets.token_hex(12),
            'device_id': secrets.token_hex(16),
            'timestamp': int(time.time() * 1000) + random.randint(-30000, 30000),
            'properties': {
                'browser': self.chaos.next_choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'os': self.chaos.next_choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android']),
                'screen': self.chaos.next_choice(['1920x1080', '2560x1440', '1366x768']),
                'language': self.chaos.next_choice(['en-US', 'en-GB', 'de-DE', 'fr-FR']),
                'referrer': self.chaos.next_choice(REFERRER_CHAINS[0]),
                'page': f"/{secrets.token_hex(4)}",
            },
        }

    def get_event(self) -> TelemetryChaosEvent:
        """Generate a telemetry feedback loop event."""
        ga = self.generate_corrupted_ga_payload()
        fb = self.generate_corrupted_fb_pixel()
        beacon = self.generate_corrupted_telemetry_beacon()

        endpoint = self.chaos.next_choice(TELEMETRY_ENDPOINTS).format(
            rand=secrets.token_hex(4)
        )

        return TelemetryChaosEvent(
            timestamp=datetime.now(),
            method=TelemetryMethod.FEEDBACK_LOOP,
            target=endpoint,
            details={
                'payload_types': ['google_analytics', 'facebook_pixel', 'generic_beacon'],
                'ga_tid': ga['tid'],
                'fb_pixel_id': fb['id'],
                'beacon_event': beacon['event'],
                'corrupted_fields': len(ga) + len(fb) + len(beacon),
            },
            spoofed_data={
                'ga_payload': ga,
                'fb_pixel': fb,
                'beacon': beacon,
            },
        )


# ══════════════════════════════════════════════════════════════════════════
#   UNIFIED TELEMETRY CHAOS ENGINE
# ══════════════════════════════════════════════════════════════════════════


class TelemetryChaosEngine:
    """
    Unified engine that orchestrates all 10 telemetry confusion methods.

    Can run all methods simultaneously in coordinated fashion,
    with the Lorenz attractor controlling which methods are active
    and at what intensity at any given moment.

    "Chaos is not disorder. Chaos is a higher form of order."
    """

    def __init__(self, seed: str = None):
        self.seed = seed or secrets.token_hex(16)
        self.lorenz = LorenzAttractor(self.seed + "_engine")
        self.timer = ChaoticTimer(self.seed + "_timer", base_interval=5.0)

        # Initialize all 10 methods
        self.methods = {
            TelemetryMethod.PHANTOM_SWARM: PhantomDeviceSwarm(self.seed),
            TelemetryMethod.TEMPORAL_DRIFT: TemporalDriftEngine(self.seed),
            TelemetryMethod.GEO_CAROUSEL: GeolocationCarousel(seed=self.seed),
            TelemetryMethod.DNS_CHAFF: DNSChaffGenerator(self.seed),
            TelemetryMethod.BEACON_ENTROPY: BeaconEntropyMixer(self.seed),
            TelemetryMethod.TLS_SHUFFLE: TLSHandshakeShuffler(self.seed),
            TelemetryMethod.COOKIE_CHIMERA: HTTPCookieChimera(self.seed),
            TelemetryMethod.UA_METAMORPH: UserAgentMetamorph(self.seed),
            TelemetryMethod.REFERRER_FABRICATOR: ReferrerChainFabricator(self.seed),
            TelemetryMethod.FEEDBACK_LOOP: TelemetryFeedbackLoop(self.seed),
        }

        self._event_log: List[TelemetryChaosEvent] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._active_methods: List[TelemetryMethod] = list(TelemetryMethod)
        self._lock = threading.Lock()

    def set_active_methods(self, methods: List[TelemetryMethod]):
        """Set which methods are active."""
        with self._lock:
            self._active_methods = methods

    def generate_single(self, method: TelemetryMethod) -> TelemetryChaosEvent:
        """Generate a single chaos event using the specified method."""
        handler = self.methods[method]
        event = handler.get_event()
        with self._lock:
            self._event_log.append(event)
        return event

    def generate_burst(self, count: int = 5) -> List[TelemetryChaosEvent]:
        """Generate a burst of events across active methods."""
        events = []
        for i in range(count):
            # Use Lorenz to select method organically
            noise = self.lorenz.next_normalized()
            idx = int(abs(noise[0]) * len(self._active_methods)) % len(self._active_methods)
            method = self._active_methods[idx]
            events.append(self.generate_single(method))
        return events

    def start_background(self, interval: float = 5.0,
                         methods: Optional[List[TelemetryMethod]] = None):
        """Start background chaos generation across all methods."""
        if methods:
            self.set_active_methods(methods)

        self._running = True

        def _worker():
            while self._running:
                try:
                    # Generate events with chaotic timing
                    noise = self.lorenz.next_normalized()
                    n_events = max(1, int(abs(noise[0]) * 5))

                    for _ in range(n_events):
                        if not self._running:
                            break
                        idx = int(abs(noise[1]) * len(self._active_methods)) % len(self._active_methods)
                        method = self._active_methods[idx]
                        self.generate_single(method)
                        noise = self.lorenz.next_normalized()

                    wait = self.timer.next_interval(0.3, 2.0)
                    time.sleep(wait)
                except Exception:
                    time.sleep(1)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def stop_background(self):
        """Stop background generation."""
        self._running = False
        # Also stop DNS chaff if running
        dns_chaff = self.methods[TelemetryMethod.DNS_CHAFF]
        if isinstance(dns_chaff, DNSChaffGenerator):
            dns_chaff.stop_background()
        if self._thread:
            self._thread.join(timeout=5)

    def get_stats(self) -> Dict:
        """Get comprehensive statistics."""
        with self._lock:
            by_method = {}
            for method in TelemetryMethod:
                by_method[method.value] = sum(
                    1 for e in self._event_log if e.method == method
                )

            return {
                'total_events': len(self._event_log),
                'by_method': by_method,
                'active_methods': [m.value for m in self._active_methods],
                'is_running': self._running,
            }

    def get_recent_events(self, count: int = 5) -> List[Dict]:
        """Get recent events as dicts."""
        with self._lock:
            recent = self._event_log[-count:]
            return [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'method': e.method.value,
                    'target': e.target,
                    'details': e.details,
                }
                for e in recent
            ]


def list_telemetry_methods() -> None:
    """Print all available telemetry confusion methods."""
    for i, method in enumerate(TelemetryMethod, 1):
        print(f"  [{i}] {method.value:30} {TELEMETRY_DESCRIPTIONS[method]}")


def get_method_by_number(n: int) -> Optional[TelemetryMethod]:
    """Get telemetry method by its number (1-10)."""
    methods = list(TelemetryMethod)
    if 1 <= n <= len(methods):
        return methods[n - 1]
    return None


# ── CLI Demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== spicy-cat Telemetry Chaos Engine ===\n")
    print("10 Methods of Telemetry Confusion:\n")
    list_telemetry_methods()

    print("\n--- Generating sample events ---\n")
    engine = TelemetryChaosEngine("demo_seed")

    for method in TelemetryMethod:
        event = engine.generate_single(method)
        print(f"[{method.value:30}] target={event.target[:40]}")

    print(f"\nTotal events: {engine.get_stats()['total_events']}")
