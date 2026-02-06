#!/usr/bin/env python3
"""
spicy-wifi.py - WiFi AP Confusion Tool for spicy-cat

    /\\_____/\\
   /  o   o  \\
  ( ==  ^  == )  "Confuse the airwaves."
   )  ~WiFi~  (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

A privacy tool that generates WiFi traffic to confuse access point
analytics and WiFi-based tracking systems.

Three Operation Modes:
  1) NOWHERE   - Broadcast to random non-existent APs (noise generation)
  2) TARGETED  - Send crafted traffic to a specific AP
  3) MIMIC     - Send traffic as a spoofed device identity

Features:
  - Collects real news categories for realistic traffic content
  - Uses chaos engine for organic, non-patterned behavior
  - Integrates with spicy-cat fingerprint protection
  - Randomized timing to avoid detection patterns

Usage:
    python3 spicy-wifi.py                    # Interactive mode selector
    python3 spicy-wifi.py --mode nowhere     # Broadcast to nowhere
    python3 spicy-wifi.py --mode targeted    # Target specific AP
    python3 spicy-wifi.py --mode mimic       # Mimic a device
    python3 spicy-wifi.py --list-categories  # Show news categories
    python3 spicy-wifi.py --list-devices     # Show device profiles

Requirements:
    - Python 3.8+
    - Root/sudo for raw socket operations (optional, falls back to simulation)
    - scapy (optional, for real WiFi frame injection)

Note: This tool is for authorized security research and privacy protection only.
      Always ensure you have permission to transmit on WiFi networks.
"""

import os
import sys
import json
import time
import random
import struct
import socket
import hashlib
import secrets
import argparse
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Add parent dir for lib imports
sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), '..')))

try:
    from lib.chaos import LogisticMap, LorenzAttractor, ChaoticTimer
except ImportError:
    # Standalone fallback
    class LogisticMap:
        def __init__(self, seed=None, r=3.9999):
            self.r = r
            h = hashlib.sha256((seed or "default").encode()).digest()
            val = struct.unpack('>Q', h[:8])[0]
            self.x = 0.1 + (val / (2**64)) * 0.8
            for _ in range(100):
                self.x = self.r * self.x * (1 - self.x)
        def next(self):
            self.x = self.r * self.x * (1 - self.x)
            return self.x
        def next_int(self, min_val, max_val):
            return min_val + int(self.next() * (max_val - min_val + 1))
        def next_choice(self, items):
            if not items: return None
            return items[self.next_int(0, len(items) - 1)]

    class LorenzAttractor:
        def __init__(self, seed=None, sigma=10.0, rho=28.0, beta=8/3):
            self.sigma, self.rho, self.beta = sigma, rho, beta
            self.x, self.y, self.z, self.dt = 1.0, 1.0, 1.0, 0.01
            for _ in range(1000):
                dx = self.sigma * (self.y - self.x)
                dy = self.x * (self.rho - self.z) - self.y
                dz = self.x * self.y - self.beta * self.z
                self.x += dx * self.dt
                self.y += dy * self.dt
                self.z += dz * self.dt
        def next_normalized(self):
            dx = self.sigma * (self.y - self.x)
            dy = self.x * (self.rho - self.z) - self.y
            dz = self.x * self.y - self.beta * self.z
            self.x += dx * self.dt
            self.y += dy * self.dt
            self.z += dz * self.dt
            return (self.x/20, self.y/20, (self.z-25)/25)

    class ChaoticTimer:
        def __init__(self, seed, base_interval=5.0):
            self.lorenz = LorenzAttractor(seed)
            self.base = base_interval
        def next_interval(self, min_f=0.5, max_f=2.0):
            n = self.lorenz.next_normalized()
            v = (n[0]+1)/2
            return self.base * (min_f + v * (max_f - min_f))


# Try to import scapy for real WiFi operations
SCAPY_AVAILABLE = False
try:
    from scapy.all import (
        RadioTap, Dot11, Dot11ProbeReq, Dot11Elt,
        Dot11Beacon, Dot11Auth, Dot11AssoReq,
        sendp, sniff, conf
    )
    SCAPY_AVAILABLE = True
except ImportError:
    pass


# ══════════════════════════════════════════════════════════════════════════
#   CONSTANTS & DATA
# ══════════════════════════════════════════════════════════════════════════

class WiFiMode(Enum):
    """The three operation modes."""
    NOWHERE = "nowhere"
    TARGETED = "targeted"
    MIMIC = "mimic"


# ── Device Profiles for Mimicry ────────────────────────────────────────────

DEVICE_PROFILES = [
    {
        'name': 'iPhone 15 Pro',
        'vendor': 'Apple',
        'mac_prefix': 'F0:18:98',
        'hostname': 'iPhone',
        'oui': 'Apple, Inc.',
        'probe_ssids': ['eduroam', 'xfinitywifi', 'attwifi', 'Google Starbucks'],
        'capabilities': {'ht': True, 'vht': True, 'he': True},
        'supported_rates': [6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'Samsung Galaxy S24',
        'vendor': 'Samsung',
        'mac_prefix': '8C:79:F5',
        'hostname': 'Galaxy-S24',
        'oui': 'Samsung Electronics Co.,Ltd',
        'probe_ssids': ['HOME-WIFI', 'AndroidAP', 'DIRECT-xy', 'CableWiFi'],
        'capabilities': {'ht': True, 'vht': True, 'he': True},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'MacBook Pro M3',
        'vendor': 'Apple',
        'mac_prefix': '3C:22:FB',
        'hostname': 'MacBook-Pro',
        'oui': 'Apple, Inc.',
        'probe_ssids': ['eduroam', 'Starbucks WiFi', 'xfinitywifi'],
        'capabilities': {'ht': True, 'vht': True, 'he': True},
        'supported_rates': [6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'Dell XPS 15',
        'vendor': 'Dell',
        'mac_prefix': 'B0:A4:60',
        'hostname': 'DESKTOP-DELL',
        'oui': 'Dell Technologies',
        'probe_ssids': ['NETGEAR78', 'linksys', 'HOME-5G', 'TP-Link_5GHz'],
        'capabilities': {'ht': True, 'vht': True, 'he': False},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'Google Pixel 8',
        'vendor': 'Google',
        'mac_prefix': '54:60:09',
        'hostname': 'Pixel-8',
        'oui': 'Google, Inc.',
        'probe_ssids': ['GoogleGuest', 'Project Fi', 'xfinitywifi'],
        'capabilities': {'ht': True, 'vht': True, 'he': True},
        'supported_rates': [6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'Ring Doorbell',
        'vendor': 'Ring/Amazon',
        'mac_prefix': '5C:47:5E',
        'hostname': 'Ring-Doorbell',
        'oui': 'Amazon Technologies Inc.',
        'probe_ssids': ['Ring-Setup'],
        'capabilities': {'ht': True, 'vht': False, 'he': False},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0],
    },
    {
        'name': 'Nest Thermostat',
        'vendor': 'Google',
        'mac_prefix': '64:16:66',
        'hostname': 'Nest-Thermostat',
        'oui': 'Google, Inc.',
        'probe_ssids': ['Nest-Setup'],
        'capabilities': {'ht': True, 'vht': False, 'he': False},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0],
    },
    {
        'name': 'iPad Air M2',
        'vendor': 'Apple',
        'mac_prefix': 'A4:83:E7',
        'hostname': 'iPad',
        'oui': 'Apple, Inc.',
        'probe_ssids': ['eduroam', 'attwifi', 'xfinitywifi'],
        'capabilities': {'ht': True, 'vht': True, 'he': True},
        'supported_rates': [6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'ThinkPad X1 Carbon',
        'vendor': 'Lenovo',
        'mac_prefix': 'E8:6A:64',
        'hostname': 'LAPTOP-THINKPAD',
        'oui': 'Lenovo',
        'probe_ssids': ['CORP-WIFI', 'eduroam', 'Marriott_WIFI'],
        'capabilities': {'ht': True, 'vht': True, 'he': False},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
    {
        'name': 'Nintendo Switch',
        'vendor': 'Nintendo',
        'mac_prefix': '98:B6:E9',
        'hostname': 'NintendoSwitch',
        'oui': 'Nintendo Co.,Ltd',
        'probe_ssids': ['NintendoAP'],
        'capabilities': {'ht': True, 'vht': False, 'he': False},
        'supported_rates': [1.0, 2.0, 5.5, 11.0, 6.0, 9.0, 12.0, 18.0, 24.0, 36.0, 48.0, 54.0],
    },
]


# ── Fake SSID Pools for "Nowhere" Mode ─────────────────────────────────────

NOWHERE_SSIDS = [
    # Home-style SSIDs
    "NETGEAR{num}", "linksys-{hex4}", "TP-Link_{hex4}_{band}",
    "ASUS_RT_{hex4}", "Dlink-{hex4}", "HOME-{hex4}-{band}",
    "Verizon_{hex4}", "ATT{hex6}", "XFINITY-{hex4}",
    "MySpectrum_{hex4}", "CenturyLink{num}",
    # Business-style SSIDs
    "Guest_WiFi_{hex4}", "Corp-Wireless", "Office_{num}",
    "Conference_Room_{num}", "Visitor-{hex4}",
    # Public-style SSIDs
    "FreeWiFi", "Airport_WiFi", "Hotel_Guest_{num}",
    "Starbucks_WiFi_{hex4}", "McDonald's Free WiFi",
    "Library_Public", "CityWiFi_{hex4}",
]


# ══════════════════════════════════════════════════════════════════════════
#   NEWS COLLECTOR
# ══════════════════════════════════════════════════════════════════════════

class NewsCategory(Enum):
    """News categories for generating realistic WiFi traffic content."""
    WORLD = "world"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    POLITICS = "politics"
    ENVIRONMENT = "environment"
    EDUCATION = "education"


NEWS_DESCRIPTIONS = {
    NewsCategory.WORLD: "International news and global events",
    NewsCategory.TECHNOLOGY: "Tech industry, gadgets, and software",
    NewsCategory.SCIENCE: "Scientific discoveries and research",
    NewsCategory.BUSINESS: "Markets, economy, and corporate news",
    NewsCategory.SPORTS: "Sports scores, transfers, and events",
    NewsCategory.ENTERTAINMENT: "Movies, music, TV, and celebrity news",
    NewsCategory.HEALTH: "Medical research, wellness, and public health",
    NewsCategory.POLITICS: "Government, policy, and elections",
    NewsCategory.ENVIRONMENT: "Climate, conservation, and sustainability",
    NewsCategory.EDUCATION: "Schools, universities, and learning",
}


# ── Offline News Content Templates (fallback) ────────────────────────────

NEWS_TEMPLATES = {
    NewsCategory.WORLD: [
        "UN General Assembly discusses new climate framework agreement",
        "G20 summit concludes with joint statement on economic cooperation",
        "International trade negotiations enter final round in Geneva",
        "Humanitarian aid organizations expand relief operations",
        "Global migration patterns shift as new policies take effect",
        "International space station celebrates milestone anniversary",
        "World Health Organization updates global health guidelines",
        "Cross-border infrastructure project breaks ground",
    ],
    NewsCategory.TECHNOLOGY: [
        "New AI model achieves breakthrough in natural language understanding",
        "Major tech company announces next-generation processor architecture",
        "Open source community releases updated framework version",
        "Cybersecurity researchers discover novel vulnerability class",
        "Quantum computing startup demonstrates error correction milestone",
        "Self-driving vehicle technology passes new safety certification",
        "Cloud computing market grows as enterprises accelerate migration",
        "New programming language gains popularity among developers",
    ],
    NewsCategory.SCIENCE: [
        "Astronomers detect unusual signal from distant galaxy cluster",
        "New species discovered in deep-sea expedition findings",
        "Particle physics experiment yields unexpected measurement results",
        "Gene therapy clinical trial reports promising early outcomes",
        "Climate model predictions updated with new satellite data",
        "Archaeological discovery sheds light on ancient civilization",
        "Materials science team develops stronger lightweight composite",
        "Neuroscience study reveals new insights about memory formation",
    ],
    NewsCategory.BUSINESS: [
        "Stock markets reach new highs amid positive earnings reports",
        "Federal Reserve signals potential adjustment to interest rates",
        "Major merger announced in telecommunications sector",
        "Startup funding round breaks records for AI sector",
        "Retail sales data suggests strong consumer confidence",
        "International trade volume increases for third consecutive quarter",
        "New regulations impact fintech industry operating models",
        "Corporate sustainability reporting standards see wider adoption",
    ],
    NewsCategory.SPORTS: [
        "Championship final draws record global television audience",
        "Olympic committee announces changes to upcoming games format",
        "Transfer window sees major player moves across top leagues",
        "New world record set in track and field competition",
        "Esports tournament prize pool exceeds traditional sports events",
        "Youth athletics program expands to underserved communities",
        "Stadium renovation project approved for historic venue",
        "International cricket council updates tournament schedule",
    ],
    NewsCategory.ENTERTAINMENT: [
        "Blockbuster film surpasses box office expectations opening weekend",
        "Streaming platform announces new original content lineup",
        "Music festival lineup revealed for upcoming summer season",
        "Award nominations announced for annual ceremony",
        "Bestselling author reveals next novel in popular series",
        "Video game release breaks concurrent player records",
        "Documentary film raises awareness about social issues",
        "Theater production receives critical acclaim in new season",
    ],
    NewsCategory.HEALTH: [
        "Clinical trial results show promise for new treatment approach",
        "Public health guidelines updated for seasonal prevention",
        "Mental health awareness campaign gains widespread support",
        "Nutritional study reveals benefits of Mediterranean diet patterns",
        "Wearable health technology accuracy improves with new sensors",
        "Telemedicine adoption rates continue upward trend",
        "Vaccine research advances for emerging infectious diseases",
        "Hospital system implements new patient care protocols",
    ],
    NewsCategory.POLITICS: [
        "Legislative session begins with focus on infrastructure spending",
        "Election polling data shows shift in voter demographics",
        "Bipartisan committee reaches agreement on policy framework",
        "Local government implements new community engagement program",
        "Policy analysis highlights impacts of recent regulatory changes",
        "International diplomacy effort addresses regional stability",
        "Campaign finance reform legislation advances to committee vote",
        "Public forum discusses proposed changes to education policy",
    ],
    NewsCategory.ENVIRONMENT: [
        "Renewable energy installation capacity surpasses coal globally",
        "Conservation effort saves endangered species from habitat loss",
        "Carbon capture technology demonstrates improved efficiency",
        "Ocean cleanup initiative removes significant plastic waste",
        "New national park designation protects biodiversity corridor",
        "Electric vehicle adoption accelerates with infrastructure build",
        "Sustainable agriculture practices show yield improvements",
        "Climate resilience project protects coastal communities",
    ],
    NewsCategory.EDUCATION: [
        "University introduces innovative online learning platform",
        "STEM education funding increases in national budget proposal",
        "Student achievement data shows improvement in literacy rates",
        "Education technology startup launches adaptive learning tool",
        "Community college program bridges skills gap for local employers",
        "International student exchange programs see record enrollment",
        "Teacher training initiative focuses on inclusive classroom methods",
        "Research university opens new interdisciplinary research center",
    ],
}


# News source URLs for generating realistic HTTP traffic
NEWS_SOURCES = {
    NewsCategory.WORLD: [
        "https://www.bbc.com/news/world", "https://www.reuters.com/world/",
        "https://www.aljazeera.com/", "https://apnews.com/world-news",
    ],
    NewsCategory.TECHNOLOGY: [
        "https://www.theverge.com/tech", "https://arstechnica.com/",
        "https://www.wired.com/", "https://techcrunch.com/",
    ],
    NewsCategory.SCIENCE: [
        "https://www.nature.com/news", "https://www.sciencedaily.com/",
        "https://www.newscientist.com/", "https://phys.org/",
    ],
    NewsCategory.BUSINESS: [
        "https://www.bloomberg.com/", "https://www.ft.com/",
        "https://www.cnbc.com/", "https://www.wsj.com/",
    ],
    NewsCategory.SPORTS: [
        "https://www.espn.com/", "https://www.bbc.com/sport",
        "https://sports.yahoo.com/", "https://www.si.com/",
    ],
    NewsCategory.ENTERTAINMENT: [
        "https://www.ew.com/", "https://variety.com/",
        "https://www.hollywoodreporter.com/", "https://deadline.com/",
    ],
    NewsCategory.HEALTH: [
        "https://www.webmd.com/", "https://www.health.com/",
        "https://www.healthline.com/", "https://www.mayoclinic.org/",
    ],
    NewsCategory.POLITICS: [
        "https://www.politico.com/", "https://thehill.com/",
        "https://www.npr.org/sections/politics/", "https://apnews.com/politics",
    ],
    NewsCategory.ENVIRONMENT: [
        "https://www.nationalgeographic.com/environment/",
        "https://www.theguardian.com/environment",
        "https://earther.gizmodo.com/", "https://insideclimatenews.org/",
    ],
    NewsCategory.EDUCATION: [
        "https://www.edweek.org/", "https://www.insidehighered.com/",
        "https://www.edsurge.com/", "https://theconversation.com/education",
    ],
}


class NewsCollector:
    """
    Collects and generates news content for WiFi traffic simulation.

    Uses both online fetching (when available) and offline templates
    for generating realistic browsing-like content to transmit.

    "A well-informed cat is a dangerous cat."
    """

    def __init__(self, seed: str = None, categories: List[NewsCategory] = None):
        self.chaos = LogisticMap(seed or "news_collector")
        self.categories = categories or list(NewsCategory)
        self._cache: Dict[str, List[str]] = {}
        self._online = False

    def get_headline(self, category: NewsCategory = None) -> str:
        """Get a news headline (from template pool)."""
        if category is None:
            category = self.chaos.next_choice(self.categories)

        templates = NEWS_TEMPLATES.get(category, NEWS_TEMPLATES[NewsCategory.WORLD])
        return self.chaos.next_choice(templates)

    def get_headlines(self, count: int = 5,
                      categories: List[NewsCategory] = None) -> List[Dict]:
        """Get multiple headlines across categories."""
        cats = categories or self.categories
        headlines = []

        for _ in range(count):
            cat = self.chaos.next_choice(cats)
            headline = self.get_headline(cat)
            source = self.chaos.next_choice(NEWS_SOURCES.get(cat, ["https://news.example.com"]))
            headlines.append({
                'category': cat.value,
                'headline': headline,
                'source_url': source,
                'timestamp': datetime.now().isoformat(),
            })

        return headlines

    def get_browsing_urls(self, count: int = 10,
                          categories: List[NewsCategory] = None) -> List[str]:
        """Generate realistic news browsing URLs for traffic generation."""
        cats = categories or self.categories
        urls = []

        for _ in range(count):
            cat = self.chaos.next_choice(cats)
            sources = NEWS_SOURCES.get(cat, ["https://news.example.com/"])
            base_url = self.chaos.next_choice(sources)
            # Add a realistic-looking article path
            slug = "-".join(self.chaos.next_choice(
                self.get_headline(cat).lower().split()[:5]
            ).replace(',', '').replace('.', '') for _ in range(1))
            article_id = secrets.token_hex(4)
            urls.append(f"{base_url.rstrip('/')}/{slug}-{article_id}")

        return urls

    def fetch_online(self, category: NewsCategory) -> List[str]:
        """
        Attempt to fetch real headlines from RSS/API.
        Falls back to templates if network unavailable.
        """
        import urllib.request
        import urllib.error

        rss_feeds = {
            NewsCategory.WORLD: "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            NewsCategory.TECHNOLOGY: "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            NewsCategory.SCIENCE: "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
            NewsCategory.BUSINESS: "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            NewsCategory.SPORTS: "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
            NewsCategory.HEALTH: "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
        }

        feed_url = rss_feeds.get(category)
        if not feed_url:
            return [self.get_headline(category) for _ in range(5)]

        try:
            req = urllib.request.Request(feed_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode('utf-8', errors='ignore')

            # Simple XML title extraction
            headlines = []
            import re
            titles = re.findall(r'<title[^>]*>(.*?)</title>', content)
            for title in titles[2:12]:  # Skip feed title and description
                clean = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                if clean and len(clean) > 10:
                    headlines.append(clean)

            if headlines:
                self._online = True
                self._cache[category.value] = headlines
                return headlines

        except Exception:
            pass

        return [self.get_headline(category) for _ in range(5)]


# ══════════════════════════════════════════════════════════════════════════
#   WIFI FRAME GENERATION
# ══════════════════════════════════════════════════════════════════════════

def generate_random_mac() -> str:
    """Generate a random locally-administered MAC address."""
    mac_bytes = [random.randint(0, 255) for _ in range(6)]
    mac_bytes[0] = (mac_bytes[0] | 0x02) & 0xFE  # Local, unicast
    return ':'.join(f'{b:02X}' for b in mac_bytes)


def generate_mac_from_prefix(prefix: str) -> str:
    """Generate a MAC with a specific vendor prefix."""
    suffix = ':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))
    return f"{prefix}:{suffix}"


def generate_ssid(template: str) -> str:
    """Generate a realistic SSID from template."""
    return template.format(
        num=random.randint(1000, 9999),
        hex4=secrets.token_hex(2).upper(),
        hex6=secrets.token_hex(3).upper(),
        band=random.choice(['2G', '5G', '5GHz', '2.4GHz']),
    )


@dataclass
class WiFiFrame:
    """Represents a WiFi management/data frame (simulated or real)."""
    frame_type: str  # probe_request, probe_response, beacon, data, auth
    source_mac: str
    dest_mac: str
    bssid: str
    ssid: str = ""
    channel: int = 0
    signal_strength: int = -50
    payload: bytes = b""
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        """Human-readable summary."""
        return (f"[{self.frame_type:15}] "
                f"src={self.source_mac} dst={self.dest_mac} "
                f"ssid={self.ssid[:20]:20} ch={self.channel}")


# ══════════════════════════════════════════════════════════════════════════
#   MODE 1: NOWHERE - Broadcast to Non-Existent APs
# ══════════════════════════════════════════════════════════════════════════

class NowhereMode:
    """
    Mode 1: Send WiFi traffic to nowhere.

    Generates probe requests and data frames directed at randomly
    generated BSSIDs that don't correspond to any real access point.
    This creates noise in WiFi analytics systems that monitor the
    airspace for device tracking.

    "Broadcasting to the void. The cat disappears into thin air."
    """

    def __init__(self, seed: str = None, interface: str = None):
        self.chaos = LogisticMap(seed or "nowhere_mode")
        self.lorenz = LorenzAttractor(seed or "nowhere_path")
        self.timer = ChaoticTimer(seed or "nowhere_timer", base_interval=2.0)
        self.interface = interface
        self.news = NewsCollector(seed)
        self._frames_sent = 0
        self._running = False

    def generate_frame(self, categories: List[NewsCategory] = None) -> WiFiFrame:
        """Generate a frame directed at a non-existent AP."""
        # Random non-existent BSSID
        fake_bssid = generate_random_mac()
        # Our spoofed source MAC (changes each time)
        source_mac = generate_random_mac()
        # Random fake SSID
        ssid_template = self.chaos.next_choice(NOWHERE_SSIDS)
        ssid = generate_ssid(ssid_template)
        channel = self.chaos.next_int(1, 11)

        # Generate news-based payload
        if categories:
            headline = self.news.get_headline(self.chaos.next_choice(categories))
        else:
            headline = self.news.get_headline()

        # Create probe request or data frame
        frame_type = self.chaos.next_choice([
            'probe_request', 'probe_request', 'probe_request',
            'data', 'auth',
        ])

        frame = WiFiFrame(
            frame_type=frame_type,
            source_mac=source_mac,
            dest_mac=fake_bssid,
            bssid=fake_bssid,
            ssid=ssid,
            channel=channel,
            signal_strength=self.chaos.next_int(-80, -30),
            payload=headline.encode('utf-8')[:128],
            metadata={
                'mode': 'nowhere',
                'target_exists': False,
                'news_category': headline[:30],
            },
        )

        self._frames_sent += 1
        return frame

    def send_frame(self, frame: WiFiFrame) -> bool:
        """Send a frame (real with scapy, or simulated)."""
        if SCAPY_AVAILABLE and self.interface:
            try:
                if frame.frame_type == 'probe_request':
                    pkt = (
                        RadioTap() /
                        Dot11(
                            type=0, subtype=4,
                            addr1="ff:ff:ff:ff:ff:ff",
                            addr2=frame.source_mac,
                            addr3=frame.bssid,
                        ) /
                        Dot11ProbeReq() /
                        Dot11Elt(ID="SSID", info=frame.ssid.encode()) /
                        Dot11Elt(ID="Rates", info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')
                    )
                    sendp(pkt, iface=self.interface, count=1, verbose=False)
                    return True
            except Exception:
                pass
        # Simulation mode
        return True

    def generate_burst(self, count: int = 10,
                       categories: List[NewsCategory] = None) -> List[WiFiFrame]:
        """Generate a burst of nowhere-bound frames."""
        return [self.generate_frame(categories) for _ in range(count)]

    def start_continuous(self, categories: List[NewsCategory] = None,
                         callback=None):
        """Start continuous nowhere broadcasting."""
        self._running = True

        def _worker():
            while self._running:
                frame = self.generate_frame(categories)
                self.send_frame(frame)
                if callback:
                    callback(frame)
                wait = self.timer.next_interval(0.3, 1.5)
                time.sleep(wait)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Stop continuous broadcasting."""
        self._running = False

    def get_stats(self) -> Dict:
        return {
            'mode': 'nowhere',
            'frames_sent': self._frames_sent,
            'running': self._running,
        }


# ══════════════════════════════════════════════════════════════════════════
#   MODE 2: TARGETED - Send Traffic to Specific AP
# ══════════════════════════════════════════════════════════════════════════

class TargetedMode:
    """
    Mode 2: Send crafted traffic to a specific access point.

    Generates frames that target a specific BSSID/SSID, making it
    appear that many different devices are connecting to or probing
    for that specific network. Useful for testing AP analytics.

    "The cat knows exactly where to pounce."
    """

    def __init__(self, target_bssid: str, target_ssid: str = "",
                 target_channel: int = 6, seed: str = None,
                 interface: str = None):
        self.target_bssid = target_bssid
        self.target_ssid = target_ssid
        self.target_channel = target_channel
        self.chaos = LogisticMap(seed or "targeted_mode")
        self.timer = ChaoticTimer(seed or "targeted_timer", base_interval=3.0)
        self.interface = interface
        self.news = NewsCollector(seed)
        self._frames_sent = 0
        self._running = False

    def generate_frame(self, categories: List[NewsCategory] = None) -> WiFiFrame:
        """Generate a frame targeting the specific AP."""
        # Different spoofed source MACs each time
        device = self.chaos.next_choice(DEVICE_PROFILES)
        source_mac = generate_mac_from_prefix(device['mac_prefix'])

        # News content payload
        if categories:
            headline = self.news.get_headline(self.chaos.next_choice(categories))
        else:
            headline = self.news.get_headline()

        frame_type = self.chaos.next_choice([
            'probe_request', 'probe_request',
            'auth', 'data',
        ])

        frame = WiFiFrame(
            frame_type=frame_type,
            source_mac=source_mac,
            dest_mac=self.target_bssid,
            bssid=self.target_bssid,
            ssid=self.target_ssid,
            channel=self.target_channel,
            signal_strength=self.chaos.next_int(-75, -35),
            payload=headline.encode('utf-8')[:128],
            metadata={
                'mode': 'targeted',
                'device_profile': device['name'],
                'device_vendor': device['vendor'],
            },
        )

        self._frames_sent += 1
        return frame

    def send_frame(self, frame: WiFiFrame) -> bool:
        """Send a frame to the target AP."""
        if SCAPY_AVAILABLE and self.interface:
            try:
                if frame.frame_type == 'probe_request':
                    pkt = (
                        RadioTap() /
                        Dot11(
                            type=0, subtype=4,
                            addr1=self.target_bssid,
                            addr2=frame.source_mac,
                            addr3=self.target_bssid,
                        ) /
                        Dot11ProbeReq() /
                        Dot11Elt(ID="SSID", info=self.target_ssid.encode()) /
                        Dot11Elt(ID="Rates", info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')
                    )
                    sendp(pkt, iface=self.interface, count=1, verbose=False)
                    return True
            except Exception:
                pass
        return True

    def generate_burst(self, count: int = 10,
                       categories: List[NewsCategory] = None) -> List[WiFiFrame]:
        """Generate a burst of targeted frames."""
        return [self.generate_frame(categories) for _ in range(count)]

    def start_continuous(self, categories: List[NewsCategory] = None,
                         callback=None):
        """Start continuous targeted transmission."""
        self._running = True

        def _worker():
            while self._running:
                frame = self.generate_frame(categories)
                self.send_frame(frame)
                if callback:
                    callback(frame)
                wait = self.timer.next_interval(0.5, 2.0)
                time.sleep(wait)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def stop(self):
        self._running = False

    def get_stats(self) -> Dict:
        return {
            'mode': 'targeted',
            'target_bssid': self.target_bssid,
            'target_ssid': self.target_ssid,
            'frames_sent': self._frames_sent,
            'running': self._running,
        }


# ══════════════════════════════════════════════════════════════════════════
#   MODE 3: MIMIC - Send Traffic as a Specific Device
# ══════════════════════════════════════════════════════════════════════════

class MimicMode:
    """
    Mode 3: Send traffic as a specific device type.

    Generates WiFi frames that closely mimic a chosen device profile,
    including correct OUI prefix, probe SSIDs, capability bits, and
    timing patterns. Makes it appear that the spoofed device type
    is active on the network.

    "A cat in a dog costume is still a cat. But the trackers won't know."
    """

    def __init__(self, device_profile: Dict = None, seed: str = None,
                 interface: str = None):
        self.chaos = LogisticMap(seed or "mimic_mode")
        self.lorenz = LorenzAttractor(seed or "mimic_behavior")
        self.timer = ChaoticTimer(seed or "mimic_timer", base_interval=5.0)
        self.interface = interface
        self.news = NewsCollector(seed)
        self._frames_sent = 0
        self._running = False

        # Set device profile
        if device_profile:
            self.device = device_profile
        else:
            self.device = self.chaos.next_choice(DEVICE_PROFILES)

        # Generate a consistent MAC for this mimic session
        self.mac = generate_mac_from_prefix(self.device['mac_prefix'])

    def generate_frame(self, categories: List[NewsCategory] = None) -> WiFiFrame:
        """Generate a frame mimicking the device profile."""
        # Probe for SSIDs the device would know
        ssid = self.chaos.next_choice(self.device['probe_ssids'] + [''])
        bssid = generate_random_mac()  # Random AP to probe

        # News payload
        if categories:
            headline = self.news.get_headline(self.chaos.next_choice(categories))
        else:
            headline = self.news.get_headline()

        # Device-appropriate frame types
        noise = self.lorenz.next_normalized()
        if abs(noise[0]) > 0.5:
            frame_type = 'probe_request'
        elif abs(noise[1]) > 0.7:
            frame_type = 'auth'
        else:
            frame_type = 'data'

        frame = WiFiFrame(
            frame_type=frame_type,
            source_mac=self.mac,  # Consistent MAC for this device
            dest_mac='ff:ff:ff:ff:ff:ff' if frame_type == 'probe_request' else bssid,
            bssid=bssid,
            ssid=ssid,
            channel=self.chaos.next_int(1, 11),
            signal_strength=self.chaos.next_int(-70, -30),
            payload=headline.encode('utf-8')[:128],
            metadata={
                'mode': 'mimic',
                'device_name': self.device['name'],
                'device_vendor': self.device['vendor'],
                'hostname': self.device['hostname'],
                'ht_capable': self.device['capabilities']['ht'],
                'vht_capable': self.device['capabilities']['vht'],
                'he_capable': self.device['capabilities']['he'],
            },
        )

        self._frames_sent += 1
        return frame

    def send_frame(self, frame: WiFiFrame) -> bool:
        """Send a frame as the mimicked device."""
        if SCAPY_AVAILABLE and self.interface:
            try:
                if frame.frame_type == 'probe_request':
                    ssid_elt = Dot11Elt(ID="SSID", info=frame.ssid.encode()) if frame.ssid else Dot11Elt(ID="SSID", info=b"")
                    rates = bytes([int(r * 2) | (0x80 if r in [1.0, 2.0, 5.5, 11.0] else 0)
                                   for r in self.device['supported_rates'][:8]])

                    pkt = (
                        RadioTap() /
                        Dot11(
                            type=0, subtype=4,
                            addr1="ff:ff:ff:ff:ff:ff",
                            addr2=self.mac,
                            addr3="ff:ff:ff:ff:ff:ff",
                        ) /
                        Dot11ProbeReq() /
                        ssid_elt /
                        Dot11Elt(ID="Rates", info=rates)
                    )
                    sendp(pkt, iface=self.interface, count=1, verbose=False)
                    return True
            except Exception:
                pass
        return True

    def generate_burst(self, count: int = 10,
                       categories: List[NewsCategory] = None) -> List[WiFiFrame]:
        return [self.generate_frame(categories) for _ in range(count)]

    def start_continuous(self, categories: List[NewsCategory] = None,
                         callback=None):
        self._running = True

        def _worker():
            while self._running:
                frame = self.generate_frame(categories)
                self.send_frame(frame)
                if callback:
                    callback(frame)
                # Device-appropriate timing
                wait = self.timer.next_interval(0.5, 3.0)
                time.sleep(wait)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def stop(self):
        self._running = False

    def get_stats(self) -> Dict:
        return {
            'mode': 'mimic',
            'device': self.device['name'],
            'mac': self.mac,
            'frames_sent': self._frames_sent,
            'running': self._running,
        }


# ══════════════════════════════════════════════════════════════════════════
#   CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════

# ANSI Colors
class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


WIFI_BANNER = f"""{C.MAGENTA}
    /\\_____/\\
   /  o   o  \\
  ( ==  ^  == )  {C.CYAN}spicy-wifi{C.RESET}
{C.MAGENTA}   )  ~{C.YELLOW}WiFi{C.MAGENTA}~  (  {C.DIM}Confuse the airwaves{C.RESET}
{C.MAGENTA}  (           )
 ( (  )   (  ) )
(__(__)___(__)__){C.RESET}
"""


def print_banner():
    print(WIFI_BANNER)


def print_frame(frame: WiFiFrame, verbose: bool = False):
    """Pretty-print a WiFi frame."""
    type_colors = {
        'probe_request': C.CYAN,
        'data': C.GREEN,
        'auth': C.YELLOW,
        'beacon': C.MAGENTA,
    }
    color = type_colors.get(frame.frame_type, C.WHITE)

    print(f"  {color}*{C.RESET} [{frame.frame_type:15}] "
          f"src={C.WHITE}{frame.source_mac}{C.RESET} "
          f"ssid={C.CYAN}{frame.ssid[:20]:20}{C.RESET} "
          f"ch={frame.channel}")

    if verbose:
        print(f"      {C.DIM}dst={frame.dest_mac} bssid={frame.bssid} "
              f"rssi={frame.signal_strength}dBm{C.RESET}")
        if frame.payload:
            print(f"      {C.DIM}payload: {frame.payload.decode('utf-8', errors='ignore')[:60]}...{C.RESET}")
        for k, v in frame.metadata.items():
            print(f"      {C.DIM}{k}: {v}{C.RESET}")


def interactive_mode_select() -> WiFiMode:
    """Interactive mode selection."""
    print(f"\n{C.BOLD}Select Operation Mode:{C.RESET}\n")
    print(f"  {C.CYAN}[1]{C.RESET} {C.BOLD}NOWHERE{C.RESET}   - Broadcast to random non-existent APs")
    print(f"                {C.DIM}Creates WiFi noise by probing fake networks{C.RESET}")
    print(f"  {C.YELLOW}[2]{C.RESET} {C.BOLD}TARGETED{C.RESET}  - Send traffic to a specific AP")
    print(f"                {C.DIM}Flood a specific BSSID with spoofed device probes{C.RESET}")
    print(f"  {C.MAGENTA}[3]{C.RESET} {C.BOLD}MIMIC{C.RESET}     - Send traffic as a specific device")
    print(f"                {C.DIM}Impersonate an iPhone, Galaxy, IoT device, etc.{C.RESET}")
    print()

    while True:
        choice = input(f"  {C.GREEN}>{C.RESET} Enter choice (1-3): ").strip()
        if choice == '1':
            return WiFiMode.NOWHERE
        elif choice == '2':
            return WiFiMode.TARGETED
        elif choice == '3':
            return WiFiMode.MIMIC
        else:
            print(f"  {C.RED}Invalid choice. Enter 1, 2, or 3.{C.RESET}")


def select_categories() -> List[NewsCategory]:
    """Interactive news category selection."""
    print(f"\n{C.BOLD}Select News Categories for Traffic Content:{C.RESET}\n")

    cats = list(NewsCategory)
    for i, cat in enumerate(cats, 1):
        print(f"  {C.CYAN}[{i:2}]{C.RESET} {cat.value:15} {C.DIM}{NEWS_DESCRIPTIONS[cat]}{C.RESET}")
    print(f"  {C.GREEN}[{len(cats)+1:2}]{C.RESET} {C.BOLD}ALL{C.RESET}            {C.DIM}Use all categories{C.RESET}")
    print()

    selected = input(f"  {C.GREEN}>{C.RESET} Enter numbers (comma-separated, or 'all'): ").strip()

    if selected.lower() == 'all' or selected == str(len(cats) + 1):
        return list(NewsCategory)

    try:
        indices = [int(x.strip()) for x in selected.split(',')]
        return [cats[i - 1] for i in indices if 1 <= i <= len(cats)]
    except (ValueError, IndexError):
        print(f"  {C.YELLOW}Using all categories.{C.RESET}")
        return list(NewsCategory)


def select_device() -> Dict:
    """Interactive device profile selection."""
    print(f"\n{C.BOLD}Select Device to Mimic:{C.RESET}\n")

    for i, device in enumerate(DEVICE_PROFILES, 1):
        caps = []
        if device['capabilities']['ht']:
            caps.append('HT')
        if device['capabilities']['vht']:
            caps.append('VHT')
        if device['capabilities']['he']:
            caps.append('HE')
        cap_str = '/'.join(caps)

        print(f"  {C.CYAN}[{i:2}]{C.RESET} {device['name']:25} "
              f"{C.DIM}{device['vendor']:12} {device['mac_prefix']} {cap_str}{C.RESET}")
    print()

    while True:
        choice = input(f"  {C.GREEN}>{C.RESET} Enter device number: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(DEVICE_PROFILES):
                return DEVICE_PROFILES[idx]
        except ValueError:
            pass
        print(f"  {C.RED}Invalid choice.{C.RESET}")


def run_nowhere_mode(args):
    """Run Mode 1: Nowhere."""
    print(f"\n{C.BOLD}{C.CYAN}Mode: NOWHERE{C.RESET}")
    print(f"{C.DIM}Broadcasting to random non-existent APs...{C.RESET}\n")

    categories = None
    if not args.no_news:
        if args.categories:
            cats = list(NewsCategory)
            categories = [cats[int(c)-1] for c in args.categories.split(',') if c.strip().isdigit()]
        elif not args.batch:
            categories = select_categories()

    mode = NowhereMode(seed=args.seed, interface=args.interface)
    count = args.count or 10

    if args.continuous:
        print(f"{C.GREEN}Starting continuous broadcast...{C.RESET}")
        print(f"{C.DIM}Press Ctrl+C to stop{C.RESET}\n")

        def on_frame(frame):
            print_frame(frame, args.verbose)

        mode.start_continuous(categories=categories, callback=on_frame)
        try:
            while True:
                time.sleep(5)
                stats = mode.get_stats()
                print(f"\r{C.DIM}Frames sent: {stats['frames_sent']}{C.RESET}", end='')
                sys.stdout.flush()
        except KeyboardInterrupt:
            mode.stop()
            print(f"\n\n{C.YELLOW}Stopped.{C.RESET}")
    else:
        frames = mode.generate_burst(count, categories)
        for frame in frames:
            mode.send_frame(frame)
            print_frame(frame, args.verbose)

    stats = mode.get_stats()
    print(f"\n{C.GREEN}Total frames: {stats['frames_sent']}{C.RESET}")


def run_targeted_mode(args):
    """Run Mode 2: Targeted."""
    print(f"\n{C.BOLD}{C.YELLOW}Mode: TARGETED{C.RESET}\n")

    # Get target AP info
    if args.bssid:
        bssid = args.bssid
    else:
        bssid = input(f"  {C.GREEN}>{C.RESET} Target BSSID (MAC address): ").strip()

    ssid = args.ssid or input(f"  {C.GREEN}>{C.RESET} Target SSID (name, optional): ").strip()
    channel = args.channel or 6

    categories = None
    if not args.no_news:
        if args.categories:
            cats = list(NewsCategory)
            categories = [cats[int(c)-1] for c in args.categories.split(',') if c.strip().isdigit()]
        elif not args.batch:
            categories = select_categories()

    print(f"\n{C.DIM}Target: {bssid} ({ssid or 'any'}) ch={channel}{C.RESET}\n")

    mode = TargetedMode(
        target_bssid=bssid, target_ssid=ssid,
        target_channel=channel, seed=args.seed,
        interface=args.interface,
    )
    count = args.count or 10

    if args.continuous:
        print(f"{C.GREEN}Starting continuous targeted transmission...{C.RESET}")
        print(f"{C.DIM}Press Ctrl+C to stop{C.RESET}\n")

        def on_frame(frame):
            print_frame(frame, args.verbose)

        mode.start_continuous(categories=categories, callback=on_frame)
        try:
            while True:
                time.sleep(5)
                stats = mode.get_stats()
                print(f"\r{C.DIM}Frames sent: {stats['frames_sent']}{C.RESET}", end='')
                sys.stdout.flush()
        except KeyboardInterrupt:
            mode.stop()
            print(f"\n\n{C.YELLOW}Stopped.{C.RESET}")
    else:
        frames = mode.generate_burst(count, categories)
        for frame in frames:
            mode.send_frame(frame)
            print_frame(frame, args.verbose)

    stats = mode.get_stats()
    print(f"\n{C.GREEN}Total frames: {stats['frames_sent']}{C.RESET}")


def run_mimic_mode(args):
    """Run Mode 3: Mimic."""
    print(f"\n{C.BOLD}{C.MAGENTA}Mode: MIMIC{C.RESET}\n")

    # Select device
    if args.device:
        device = None
        for d in DEVICE_PROFILES:
            if args.device.lower() in d['name'].lower():
                device = d
                break
        if not device:
            print(f"{C.RED}Device not found: {args.device}{C.RESET}")
            print(f"{C.DIM}Use --list-devices to see options{C.RESET}")
            return
    else:
        device = select_device() if not args.batch else DEVICE_PROFILES[0]

    categories = None
    if not args.no_news:
        if args.categories:
            cats = list(NewsCategory)
            categories = [cats[int(c)-1] for c in args.categories.split(',') if c.strip().isdigit()]
        elif not args.batch:
            categories = select_categories()

    mode = MimicMode(device_profile=device, seed=args.seed, interface=args.interface)

    print(f"  {C.BOLD}Mimicking:{C.RESET} {device['name']} ({device['vendor']})")
    print(f"  {C.DIM}MAC: {mode.mac} | OUI: {device['oui']}{C.RESET}")
    print(f"  {C.DIM}Probing for: {', '.join(device['probe_ssids'])}{C.RESET}\n")

    count = args.count or 10

    if args.continuous:
        print(f"{C.GREEN}Starting continuous device mimicry...{C.RESET}")
        print(f"{C.DIM}Press Ctrl+C to stop{C.RESET}\n")

        def on_frame(frame):
            print_frame(frame, args.verbose)

        mode.start_continuous(categories=categories, callback=on_frame)
        try:
            while True:
                time.sleep(5)
                stats = mode.get_stats()
                print(f"\r{C.DIM}Frames sent: {stats['frames_sent']} as {stats['device']}{C.RESET}", end='')
                sys.stdout.flush()
        except KeyboardInterrupt:
            mode.stop()
            print(f"\n\n{C.YELLOW}Stopped.{C.RESET}")
    else:
        frames = mode.generate_burst(count, categories)
        for frame in frames:
            mode.send_frame(frame)
            print_frame(frame, args.verbose)

    stats = mode.get_stats()
    print(f"\n{C.GREEN}Total frames: {stats['frames_sent']} as {stats['device']}{C.RESET}")


def main():
    """Main entry point for spicy-wifi."""
    parser = argparse.ArgumentParser(
        description='spicy-wifi - WiFi AP Confusion Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spicy-wifi.py                                # Interactive mode
  spicy-wifi.py --mode nowhere --continuous     # Broadcast noise continuously
  spicy-wifi.py --mode targeted --bssid AA:BB:CC:DD:EE:FF
  spicy-wifi.py --mode mimic --device "iPhone"  # Mimic iPhone
  spicy-wifi.py --list-categories               # Show news categories
  spicy-wifi.py --list-devices                  # Show device profiles

"On WiFi, everybody knows you're a cat. Unless you confuse them."
        """
    )

    parser.add_argument('--mode', '-m', choices=['nowhere', 'targeted', 'mimic'],
                        help='Operation mode (1=nowhere, 2=targeted, 3=mimic)')
    parser.add_argument('--count', '-c', type=int, default=10,
                        help='Number of frames per burst (default: 10)')
    parser.add_argument('--continuous', action='store_true',
                        help='Run continuously until Ctrl+C')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed frame information')
    parser.add_argument('--interface', '-i',
                        help='WiFi interface in monitor mode (e.g., wlan0mon)')
    parser.add_argument('--seed', '-s',
                        help='Chaos engine seed for reproducibility')

    # Targeted mode options
    parser.add_argument('--bssid', help='Target BSSID for targeted mode')
    parser.add_argument('--ssid', help='Target SSID for targeted mode')
    parser.add_argument('--channel', type=int, default=6,
                        help='WiFi channel (default: 6)')

    # Mimic mode options
    parser.add_argument('--device', '-d',
                        help='Device name to mimic (partial match)')

    # News options
    parser.add_argument('--categories', help='News categories (comma-separated numbers)')
    parser.add_argument('--no-news', action='store_true',
                        help='Disable news-based payload content')
    parser.add_argument('--list-categories', action='store_true',
                        help='List available news categories')
    parser.add_argument('--list-devices', action='store_true',
                        help='List available device profiles')
    parser.add_argument('--batch', action='store_true',
                        help='Non-interactive batch mode')

    args = parser.parse_args()

    # Info display modes
    if args.list_categories:
        print_banner()
        print(f"{C.BOLD}Available News Categories:{C.RESET}\n")
        for i, cat in enumerate(NewsCategory, 1):
            print(f"  {C.CYAN}[{i:2}]{C.RESET} {cat.value:15} {C.DIM}{NEWS_DESCRIPTIONS[cat]}{C.RESET}")
        print()

        print(f"{C.BOLD}Sample Headlines:{C.RESET}\n")
        collector = NewsCollector()
        for cat in list(NewsCategory)[:5]:
            headline = collector.get_headline(cat)
            print(f"  {C.DIM}{cat.value:15}{C.RESET} {headline[:60]}...")
        return

    if args.list_devices:
        print_banner()
        print(f"{C.BOLD}Available Device Profiles ({len(DEVICE_PROFILES)}):{C.RESET}\n")
        for i, device in enumerate(DEVICE_PROFILES, 1):
            caps = []
            if device['capabilities']['ht']:
                caps.append('HT')
            if device['capabilities']['vht']:
                caps.append('VHT')
            if device['capabilities']['he']:
                caps.append('WiFi6')
            cap_str = '/'.join(caps)

            print(f"  {C.CYAN}[{i:2}]{C.RESET} {device['name']:25} "
                  f"{C.WHITE}{device['vendor']:12}{C.RESET} "
                  f"{C.DIM}{device['mac_prefix']} {cap_str}{C.RESET}")
            print(f"       {C.DIM}Probes: {', '.join(device['probe_ssids'][:3])}{C.RESET}")
        return

    # Main execution
    print_banner()

    if not SCAPY_AVAILABLE:
        print(f"{C.YELLOW}Note: scapy not installed - running in simulation mode{C.RESET}")
        print(f"{C.DIM}Install with: pip install scapy{C.RESET}")
        print(f"{C.DIM}Real WiFi injection requires monitor mode interface{C.RESET}\n")

    # Select mode
    if args.mode:
        mode = WiFiMode(args.mode)
    else:
        mode = interactive_mode_select()

    # Run selected mode
    if mode == WiFiMode.NOWHERE:
        run_nowhere_mode(args)
    elif mode == WiFiMode.TARGETED:
        run_targeted_mode(args)
    elif mode == WiFiMode.MIMIC:
        run_mimic_mode(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.DIM}Interrupted.{C.RESET}")
    except Exception as e:
        print(f"\n{C.RED}Error: {e}{C.RESET}")
        if os.environ.get('DEBUG'):
            raise
