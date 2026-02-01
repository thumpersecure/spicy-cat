#!/usr/bin/env python3
"""
traffic.py - Traffic Issue Simulator for spicy-cat

"A cat always lands on its feet. Your fake traffic should too."

Generates decoy network traffic that mimics common system issues.
Creates noise to mask real activity and confuse traffic analysis.

9 Issue Types:
1. DNS resolution failures
2. Connection timeouts
3. SSL/TLS handshake errors
4. 503 Service Unavailable
5. Packet loss / retransmits
6. Bandwidth throttling
7. Authentication loops
8. API rate limiting
9. Proxy/gateway errors
"""

import os
import sys
import time
import random
import socket
import threading
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Import our chaos engine
try:
    from .chaos import LogisticMap, LorenzAttractor
except ImportError:
    # Allow standalone testing
    from chaos import LogisticMap, LorenzAttractor


class IssueType(Enum):
    """The 9 types of traffic issues we can simulate."""
    DNS_FAILURE = "dns_failure"
    CONNECTION_TIMEOUT = "connection_timeout"
    SSL_ERROR = "ssl_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    PACKET_LOSS = "packet_loss"
    BANDWIDTH_THROTTLE = "bandwidth_throttle"
    AUTH_LOOP = "auth_loop"
    RATE_LIMITED = "rate_limited"
    PROXY_ERROR = "proxy_error"


@dataclass
class TrafficEvent:
    """A single traffic event."""
    timestamp: datetime
    issue_type: IssueType
    target: str
    details: Dict
    success: bool = False


# Decoy targets - benign sites for generating traffic
DECOY_TARGETS = {
    'dns': [
        "nonexistent-{rand}.example.com",
        "fake-server-{rand}.internal.local",
        "missing-{rand}.test.invalid",
        "down-{rand}.localhost.localdomain",
    ],
    'http': [
        "http://httpstat.us/503",
        "http://httpstat.us/504",
        "http://httpstat.us/429",
        "http://httpstat.us/408",
        "http://httpbin.org/delay/30",
        "http://httpbin.org/status/502",
    ],
    'ssl': [
        "https://expired.badssl.com/",
        "https://wrong.host.badssl.com/",
        "https://self-signed.badssl.com/",
        "https://untrusted-root.badssl.com/",
    ],
    'auth': [
        "http://httpbin.org/basic-auth/user/pass",
        "http://httpbin.org/digest-auth/auth/user/pass",
        "http://httpbin.org/bearer",
    ],
}


class TrafficIssueSimulator:
    """
    Generates fake network traffic that looks like system issues.

    Like a cat knocking things off tables, but for network packets.
    """

    def __init__(self, seed: str = None):
        self.seed = seed or f"traffic_{int(time.time())}"
        self.chaos = LogisticMap(self.seed)
        self.lorenz = LorenzAttractor(self.seed)
        self.running = False
        self.events: List[TrafficEvent] = []
        self.thread: Optional[threading.Thread] = None

        # Issue generators
        self.generators: Dict[IssueType, Callable] = {
            IssueType.DNS_FAILURE: self._generate_dns_failure,
            IssueType.CONNECTION_TIMEOUT: self._generate_connection_timeout,
            IssueType.SSL_ERROR: self._generate_ssl_error,
            IssueType.SERVICE_UNAVAILABLE: self._generate_503,
            IssueType.PACKET_LOSS: self._generate_packet_loss,
            IssueType.BANDWIDTH_THROTTLE: self._generate_throttle,
            IssueType.AUTH_LOOP: self._generate_auth_loop,
            IssueType.RATE_LIMITED: self._generate_rate_limit,
            IssueType.PROXY_ERROR: self._generate_proxy_error,
        }

        # Statistics
        self.stats = {issue: 0 for issue in IssueType}

    def _random_string(self, length: int = 8) -> str:
        """Generate random string for domains."""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(self.chaos.next_choice(list(chars)) for _ in range(length))

    def _log_event(self, event: TrafficEvent):
        """Log a traffic event."""
        self.events.append(event)
        self.stats[event.issue_type] += 1
        # Keep last 1000 events only
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

    def _generate_dns_failure(self) -> TrafficEvent:
        """
        Issue 1: DNS Resolution Failures

        Simulate repeated failed DNS queries - looks like
        network configuration issues or unreachable servers.
        """
        template = self.chaos.next_choice(DECOY_TARGETS['dns'])
        target = template.format(rand=self._random_string())

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.DNS_FAILURE,
            target=target,
            details={'query_type': 'A', 'error': 'NXDOMAIN'},
        )

        try:
            # Actually try to resolve (will fail for fake domains)
            socket.gethostbyname(target)
        except socket.gaierror:
            event.details['error'] = 'NXDOMAIN'
        except socket.timeout:
            event.details['error'] = 'TIMEOUT'
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def _generate_connection_timeout(self) -> TrafficEvent:
        """
        Issue 2: Connection Timeouts

        Create half-open TCP connections that timeout.
        Looks like network congestion or unreachable hosts.
        """
        # Use a non-routable IP that will timeout
        targets = [
            ("10.255.255.1", 80),
            ("192.0.2.1", 443),  # TEST-NET
            ("198.51.100.1", 8080),  # TEST-NET-2
        ]
        target_ip, target_port = self.chaos.next_choice(targets)

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.CONNECTION_TIMEOUT,
            target=f"{target_ip}:{target_port}",
            details={'timeout_seconds': 2},
        )

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # Short timeout
            sock.connect((target_ip, target_port))
            sock.close()
        except socket.timeout:
            event.details['error'] = 'Connection timed out'
        except OSError as e:
            event.details['error'] = str(e)
        finally:
            try:
                sock.close()
            except:
                pass

        self._log_event(event)
        return event

    def _generate_ssl_error(self) -> TrafficEvent:
        """
        Issue 3: SSL/TLS Handshake Errors

        Hit known-bad SSL endpoints to generate certificate errors.
        """
        target = self.chaos.next_choice(DECOY_TARGETS['ssl'])

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.SSL_ERROR,
            target=target,
            details={'error_type': 'CERTIFICATE_VERIFY_FAILED'},
        )

        try:
            req = urllib.request.Request(target)
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.URLError as e:
            event.details['error'] = str(e.reason)
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def _generate_503(self) -> TrafficEvent:
        """
        Issue 4: 503 Service Unavailable

        Generate requests that return 503/504 errors.
        Looks like backend service issues.
        """
        codes = ['503', '504', '502']
        code = self.chaos.next_choice(codes)
        target = f"http://httpstat.us/{code}"

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.SERVICE_UNAVAILABLE,
            target=target,
            details={'http_code': int(code)},
        )

        try:
            req = urllib.request.Request(target)
            urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            event.details['response'] = e.code
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def _generate_packet_loss(self) -> TrafficEvent:
        """
        Issue 5: Packet Loss / Retransmits

        Simulate fragmented/partial connections.
        Uses UDP to unreachable ports.
        """
        # Send UDP packets to a non-listening port
        target_ip = "127.0.0.1"
        target_port = self.chaos.next_int(49152, 65535)  # Ephemeral range

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.PACKET_LOSS,
            target=f"{target_ip}:{target_port}/udp",
            details={'packets_sent': 0, 'packets_lost': 0},
        )

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.1)

            # Send a few packets
            for i in range(self.chaos.next_int(3, 10)):
                data = f"probe_{i}_{self._random_string()}".encode()
                sock.sendto(data, (target_ip, target_port))
                event.details['packets_sent'] += 1
                time.sleep(0.01)

            # Try to receive (will fail)
            try:
                sock.recvfrom(1024)
            except socket.timeout:
                event.details['packets_lost'] = event.details['packets_sent']

            sock.close()
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def _generate_throttle(self) -> TrafficEvent:
        """
        Issue 6: Bandwidth Throttling

        Simulate slow/stalled downloads.
        Request data but read very slowly.
        """
        target = "http://httpbin.org/drip?duration=2&numbytes=100&code=200"

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.BANDWIDTH_THROTTLE,
            target=target,
            details={'bytes_received': 0, 'duration_ms': 0},
        )

        start = time.time()
        try:
            req = urllib.request.Request(target)
            with urllib.request.urlopen(req, timeout=5) as response:
                # Read byte by byte with delays (simulates throttling)
                chunk_size = 1
                total = 0
                for _ in range(10):  # Read only a few bytes
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    total += len(chunk)
                    time.sleep(0.1)  # Artificial slowdown
                event.details['bytes_received'] = total
        except Exception as e:
            event.details['error'] = str(e)

        event.details['duration_ms'] = int((time.time() - start) * 1000)
        self._log_event(event)
        return event

    def _generate_auth_loop(self) -> TrafficEvent:
        """
        Issue 7: Authentication Loops

        Generate failed auth attempts - looks like
        OAuth/session problems.
        """
        target = self.chaos.next_choice(DECOY_TARGETS['auth'])

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.AUTH_LOOP,
            target=target,
            details={'attempts': 0, 'last_code': 0},
        )

        # Try a few times with wrong credentials
        for attempt in range(self.chaos.next_int(2, 5)):
            event.details['attempts'] += 1
            try:
                req = urllib.request.Request(target)
                urllib.request.urlopen(req, timeout=5)
            except urllib.error.HTTPError as e:
                event.details['last_code'] = e.code
            except Exception as e:
                event.details['error'] = str(e)
                break
            time.sleep(0.5)  # Delay between attempts

        self._log_event(event)
        return event

    def _generate_rate_limit(self) -> TrafficEvent:
        """
        Issue 8: API Rate Limiting

        Hit endpoints that return 429 Too Many Requests.
        """
        target = "http://httpstat.us/429"

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.RATE_LIMITED,
            target=target,
            details={'retry_after': 0},
        )

        try:
            req = urllib.request.Request(target)
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.HTTPError as e:
            event.details['http_code'] = e.code
            # Parse Retry-After header if present
            retry_after = e.headers.get('Retry-After', '60')
            event.details['retry_after'] = int(retry_after) if retry_after.isdigit() else 60
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def _generate_proxy_error(self) -> TrafficEvent:
        """
        Issue 9: Proxy/Gateway Errors

        Simulate 502 Bad Gateway and 504 Gateway Timeout.
        """
        codes = ['502', '504']
        code = self.chaos.next_choice(codes)
        target = f"http://httpstat.us/{code}"

        event = TrafficEvent(
            timestamp=datetime.now(),
            issue_type=IssueType.PROXY_ERROR,
            target=target,
            details={'gateway_error': code},
        )

        try:
            req = urllib.request.Request(target)
            req.add_header('Via', '1.1 fake-proxy.internal:8080')
            urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            event.details['response'] = e.code
        except Exception as e:
            event.details['error'] = str(e)

        self._log_event(event)
        return event

    def generate_single(self, issue_type: IssueType = None) -> TrafficEvent:
        """
        Generate a single traffic event.

        Args:
            issue_type: Specific issue type, or None for random.
        """
        if issue_type is None:
            issue_type = self.chaos.next_choice(list(IssueType))

        generator = self.generators.get(issue_type)
        if generator:
            return generator()
        return None

    def generate_burst(self, count: int = 10, issue_type: IssueType = None) -> List[TrafficEvent]:
        """
        Generate a burst of traffic events.

        Args:
            count: Number of events to generate.
            issue_type: Specific issue type, or None for mixed.
        """
        events = []
        for _ in range(count):
            event = self.generate_single(issue_type)
            if event:
                events.append(event)

            # Random delay between events (organic timing)
            delay = abs(self.lorenz.next_normalized()[0]) * 0.5
            time.sleep(delay)

        return events

    def start_background(self,
                         interval: float = 5.0,
                         issue_types: List[IssueType] = None):
        """
        Start generating traffic in background thread.

        Args:
            interval: Base interval between events (randomized).
            issue_types: List of issue types to generate, or None for all.
        """
        if self.running:
            return

        self.running = True
        allowed_types = issue_types or list(IssueType)

        def _worker():
            while self.running:
                issue_type = self.chaos.next_choice(allowed_types)
                self.generate_single(issue_type)

                # Randomized interval using Lorenz for organic timing
                jitter = abs(self.lorenz.next_normalized()[0]) * interval
                actual_interval = interval + jitter
                time.sleep(actual_interval)

        self.thread = threading.Thread(target=_worker, daemon=True)
        self.thread.start()

    def stop_background(self):
        """Stop background traffic generation."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def get_stats(self) -> Dict:
        """Get traffic generation statistics."""
        return {
            'total_events': len(self.events),
            'by_type': {k.value: v for k, v in self.stats.items()},
            'running': self.running,
        }

    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """Get recent events as dicts."""
        recent = self.events[-count:]
        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'type': e.issue_type.value,
                'target': e.target,
                'details': e.details,
            }
            for e in recent
        ]


# Issue type descriptions for CLI
ISSUE_DESCRIPTIONS = {
    IssueType.DNS_FAILURE: "DNS resolution failures (NXDOMAIN, timeouts)",
    IssueType.CONNECTION_TIMEOUT: "TCP connection timeouts to unreachable hosts",
    IssueType.SSL_ERROR: "SSL/TLS certificate and handshake errors",
    IssueType.SERVICE_UNAVAILABLE: "HTTP 503 Service Unavailable responses",
    IssueType.PACKET_LOSS: "UDP packet loss and retransmission patterns",
    IssueType.BANDWIDTH_THROTTLE: "Slow/stalled downloads, bandwidth throttling",
    IssueType.AUTH_LOOP: "Failed authentication attempts, OAuth loops",
    IssueType.RATE_LIMITED: "HTTP 429 Too Many Requests (API rate limiting)",
    IssueType.PROXY_ERROR: "HTTP 502/504 gateway and proxy errors",
}


# =============================================================================
# MALWARE BEHAVIOR SIMULATION (Educational/Testing Purposes)
# =============================================================================
#
# WARNING: This module simulates malware-like network patterns for:
# - Security training and education
# - Honeypot and deception technology testing
# - IDS/IPS detection rule validation
# - Incident response training
# - CTF challenges
#
# All traffic goes to safe/controlled endpoints. No actual malicious
# payloads are delivered or executed.
# =============================================================================


class MalwareType(Enum):
    """
    9 types of malware-like behavior patterns for educational simulation.

    These simulate the NETWORK PATTERNS of malware, not actual malware.
    Useful for testing detection systems and security training.
    """
    C2_BEACON = "c2_beacon"              # Command & Control beaconing
    DATA_EXFIL = "data_exfil"            # Data exfiltration patterns
    CRYPTOMINER = "cryptominer"          # Cryptocurrency mining traffic
    RANSOMWARE = "ransomware"            # Ransomware-like behavior
    BOTNET = "botnet"                    # Botnet communication
    KEYLOGGER = "keylogger"              # Keylogger/spyware uploads
    TROJAN_DL = "trojan_downloader"      # Trojan downloader patterns
    WORM_SCAN = "worm_scan"              # Worm propagation scanning
    ADWARE = "adware"                    # Adware/PUP traffic


@dataclass
class MalwareEvent:
    """A simulated malware traffic event."""
    timestamp: datetime
    malware_type: MalwareType
    target: str
    details: Dict
    ioc_indicators: List[str]  # Indicators of Compromise for training


# Simulated malicious infrastructure (all safe/non-existent targets)
MALWARE_TARGETS = {
    'c2_domains': [
        "update-service-{rand}.xyz",
        "cdn-static-{rand}.top",
        "api-gateway-{rand}.cc",
        "cloud-sync-{rand}.ru",
        "secure-portal-{rand}.cn",
    ],
    'exfil_endpoints': [
        "https://httpbin.org/post",  # Safe endpoint that accepts POST
        "https://httpbin.org/put",
    ],
    'mining_pools': [
        "stratum+tcp://pool.fake-{rand}.com:3333",
        "stratum+tcp://mine.fake-{rand}.net:4444",
    ],
    'botnet_irc': [
        "irc.fake-botnet-{rand}.net:6667",
        "chat.fake-c2-{rand}.org:6697",
    ],
    'malware_urls': [
        "http://httpbin.org/bytes/1024",  # Returns random bytes (safe)
        "http://httpbin.org/stream-bytes/2048",
    ],
}


# Malware behavior descriptions
MALWARE_DESCRIPTIONS = {
    MalwareType.C2_BEACON: "C2 beaconing (regular heartbeat to command server)",
    MalwareType.DATA_EXFIL: "Data exfiltration (large outbound transfers, DNS tunneling)",
    MalwareType.CRYPTOMINER: "Cryptominer activity (mining pool connections)",
    MalwareType.RANSOMWARE: "Ransomware patterns (key exchange, .onion lookups)",
    MalwareType.BOTNET: "Botnet communication (IRC/P2P command channels)",
    MalwareType.KEYLOGGER: "Keylogger/spyware (small frequent uploads)",
    MalwareType.TROJAN_DL: "Trojan downloader (fetching payloads)",
    MalwareType.WORM_SCAN: "Worm scanning (port scans, lateral movement)",
    MalwareType.ADWARE: "Adware/PUP (excessive ad network connections)",
}


class MalwareSimulator:
    """
    Simulates malware-like network behavior for educational purposes.

    "Know thy enemy" - Sun Tzu

    This generates traffic PATTERNS that look like malware behavior,
    without any actual malicious functionality. Useful for:
    - Training security analysts
    - Testing IDS/IPS rules
    - Honeypot realism
    - CTF challenges
    - Incident response drills
    """

    def __init__(self, seed: str = None):
        self.seed = seed or f"malware_{int(time.time())}"
        self.chaos = LogisticMap(self.seed)
        self.lorenz = LorenzAttractor(self.seed)
        self.running = False
        self.events: List[MalwareEvent] = []
        self.thread: Optional[threading.Thread] = None

        # Behavior generators
        self.generators: Dict[MalwareType, Callable] = {
            MalwareType.C2_BEACON: self._generate_c2_beacon,
            MalwareType.DATA_EXFIL: self._generate_data_exfil,
            MalwareType.CRYPTOMINER: self._generate_cryptominer,
            MalwareType.RANSOMWARE: self._generate_ransomware,
            MalwareType.BOTNET: self._generate_botnet,
            MalwareType.KEYLOGGER: self._generate_keylogger,
            MalwareType.TROJAN_DL: self._generate_trojan_dl,
            MalwareType.WORM_SCAN: self._generate_worm_scan,
            MalwareType.ADWARE: self._generate_adware,
        }

        self.stats = {mtype: 0 for mtype in MalwareType}

    def _random_string(self, length: int = 8) -> str:
        """Generate random string."""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(self.chaos.next_choice(list(chars)) for _ in range(length))

    def _log_event(self, event: MalwareEvent):
        """Log a malware event."""
        self.events.append(event)
        self.stats[event.malware_type] += 1
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

    def _generate_c2_beacon(self) -> MalwareEvent:
        """
        Malware Type 1: C2 Beaconing

        Simulates regular heartbeat connections to a command & control server.
        Characteristics:
        - Regular intervals (with jitter)
        - Small payloads
        - Encoded/obfuscated data
        - Unusual user agents
        """
        template = self.chaos.next_choice(MALWARE_TARGETS['c2_domains'])
        domain = template.format(rand=self._random_string(6))

        # Generate fake beacon data (base64-like)
        beacon_data = self._random_string(32)

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.C2_BEACON,
            target=f"https://{domain}/api/v1/check",
            details={
                'method': 'POST',
                'interval_seconds': self.chaos.next_int(30, 300),
                'jitter_percent': self.chaos.next_int(10, 30),
                'payload_size': len(beacon_data),
                'user_agent': f"Mozilla/5.0 (compatible; update-agent/{self._random_string(4)})",
                'encoded_payload': beacon_data[:16] + "...",
            },
            ioc_indicators=[
                f"domain:{domain}",
                "pattern:regular_interval_beaconing",
                "pattern:encoded_post_data",
                "pattern:unusual_user_agent",
            ],
        )

        # Attempt DNS resolution (will fail for fake domain)
        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            event.details['dns_status'] = 'NXDOMAIN'

        self._log_event(event)
        return event

    def _generate_data_exfil(self) -> MalwareEvent:
        """
        Malware Type 2: Data Exfiltration

        Simulates data theft patterns:
        - Large outbound transfers
        - DNS tunneling (long subdomain queries)
        - Chunked uploads
        - Off-hours activity
        """
        exfil_method = self.chaos.next_choice(['https', 'dns_tunnel'])

        if exfil_method == 'dns_tunnel':
            # DNS tunneling - encode data in subdomain
            encoded_data = self._random_string(60)
            domain = f"{encoded_data}.tunnel.fake-exfil-{self._random_string(4)}.com"
            target = f"dns://{domain}"
            details = {
                'method': 'dns_tunneling',
                'encoded_length': len(encoded_data),
                'query_type': 'TXT',
            }
            try:
                socket.gethostbyname(domain)
            except socket.gaierror:
                details['status'] = 'query_sent'
        else:
            # HTTPS exfil
            target = self.chaos.next_choice(MALWARE_TARGETS['exfil_endpoints'])
            chunk_size = self.chaos.next_int(1024, 65536)
            details = {
                'method': 'https_post',
                'chunk_size': chunk_size,
                'total_chunks': self.chaos.next_int(5, 50),
                'compression': 'gzip',
                'encryption': 'aes256',
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.DATA_EXFIL,
            target=target,
            details=details,
            ioc_indicators=[
                "pattern:large_outbound_transfer",
                "pattern:off_hours_activity",
                f"method:{exfil_method}",
                "pattern:chunked_upload",
            ],
        )

        self._log_event(event)
        return event

    def _generate_cryptominer(self) -> MalwareEvent:
        """
        Malware Type 3: Cryptominer Activity

        Simulates cryptocurrency mining traffic:
        - Stratum protocol connections
        - Mining pool communication
        - Share submissions
        """
        template = self.chaos.next_choice(MALWARE_TARGETS['mining_pools'])
        pool = template.format(rand=self._random_string(4))

        # Fake wallet address
        wallet = "0x" + self._random_string(40)

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.CRYPTOMINER,
            target=pool,
            details={
                'protocol': 'stratum',
                'algorithm': self.chaos.next_choice(['ethash', 'randomx', 'kawpow']),
                'wallet': wallet[:20] + "...",
                'worker': f"worker_{self._random_string(4)}",
                'hashrate': f"{self.chaos.next_int(10, 500)} MH/s",
                'shares_submitted': self.chaos.next_int(1, 100),
            },
            ioc_indicators=[
                "protocol:stratum",
                "pattern:mining_pool_connection",
                f"port:{pool.split(':')[-1] if ':' in pool else '3333'}",
                "pattern:continuous_connection",
            ],
        )

        self._log_event(event)
        return event

    def _generate_ransomware(self) -> MalwareEvent:
        """
        Malware Type 4: Ransomware Behavior

        Simulates ransomware network patterns:
        - Key exchange with C2
        - .onion domain lookups (Tor)
        - Ransom note hosting checks
        """
        behaviors = ['key_exchange', 'onion_lookup', 'payment_check']
        behavior = self.chaos.next_choice(behaviors)

        if behavior == 'key_exchange':
            domain = f"key-escrow-{self._random_string(8)}.xyz"
            target = f"https://{domain}/api/keys"
            details = {
                'operation': 'rsa_key_exchange',
                'key_size': 4096,
                'victim_id': self._random_string(16),
            }
        elif behavior == 'onion_lookup':
            onion = self._random_string(56)
            target = f"http://{onion}.onion"
            details = {
                'operation': 'tor_hidden_service_lookup',
                'purpose': 'ransom_payment_portal',
            }
        else:
            target = f"https://payment-{self._random_string(6)}.top/check"
            details = {
                'operation': 'payment_status_check',
                'bitcoin_address': f"bc1q{self._random_string(38)}",
                'demanded_btc': round(self.chaos.next() * 5 + 0.5, 4),
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.RANSOMWARE,
            target=target,
            details=details,
            ioc_indicators=[
                f"behavior:{behavior}",
                "pattern:crypto_key_exchange",
                "pattern:tor_communication",
                "pattern:bitcoin_address",
            ],
        )

        # DNS attempt
        try:
            if '.onion' not in target:
                domain = target.split('/')[2]
                socket.gethostbyname(domain)
        except (socket.gaierror, IndexError):
            event.details['dns_status'] = 'failed'

        self._log_event(event)
        return event

    def _generate_botnet(self) -> MalwareEvent:
        """
        Malware Type 5: Botnet Communication

        Simulates botnet C2 channels:
        - IRC-based command channels
        - P2P communication
        - DGA (Domain Generation Algorithm) lookups
        """
        comm_type = self.chaos.next_choice(['irc', 'p2p', 'dga'])

        if comm_type == 'irc':
            template = self.chaos.next_choice(MALWARE_TARGETS['botnet_irc'])
            target = template.format(rand=self._random_string(4))
            details = {
                'protocol': 'irc',
                'channel': f"#bot_{self._random_string(6)}",
                'nickname': f"bot_{self._random_string(8)}",
            }
        elif comm_type == 'p2p':
            # Fake P2P peer
            peer_ip = f"{self.chaos.next_int(1,255)}.{self.chaos.next_int(0,255)}.{self.chaos.next_int(0,255)}.{self.chaos.next_int(1,254)}"
            target = f"p2p://{peer_ip}:{self.chaos.next_int(10000, 60000)}"
            details = {
                'protocol': 'p2p_custom',
                'peer_count': self.chaos.next_int(5, 50),
                'message_type': 'heartbeat',
            }
        else:
            # DGA domain
            dga_domain = self._random_string(12) + self.chaos.next_choice(['.com', '.net', '.xyz', '.top'])
            target = f"https://{dga_domain}"
            details = {
                'protocol': 'https',
                'dga_seed': datetime.now().strftime("%Y%m%d"),
                'domain_index': self.chaos.next_int(0, 1000),
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.BOTNET,
            target=target,
            details=details,
            ioc_indicators=[
                f"protocol:{comm_type}",
                "pattern:botnet_communication",
                "pattern:command_channel",
            ],
        )

        self._log_event(event)
        return event

    def _generate_keylogger(self) -> MalwareEvent:
        """
        Malware Type 6: Keylogger/Spyware

        Simulates keylogger upload patterns:
        - Small, frequent uploads
        - Credential harvesting
        - Screenshot/clipboard uploads
        """
        upload_type = self.chaos.next_choice(['keystrokes', 'credentials', 'screenshot', 'clipboard'])

        domain = f"telemetry-{self._random_string(6)}.xyz"
        target = f"https://{domain}/collect"

        if upload_type == 'keystrokes':
            details = {
                'type': 'keystroke_log',
                'buffer_size': self.chaos.next_int(100, 1000),
                'window_title': f"[REDACTED] - {self.chaos.next_choice(['Chrome', 'Firefox', 'Outlook', 'Word'])}",
            }
        elif upload_type == 'credentials':
            details = {
                'type': 'credential_harvest',
                'source': self.chaos.next_choice(['browser', 'email_client', 'ftp_client']),
                'entry_count': self.chaos.next_int(1, 20),
            }
        elif upload_type == 'screenshot':
            details = {
                'type': 'screenshot_capture',
                'resolution': '1920x1080',
                'compression': 'jpeg_quality_30',
                'size_kb': self.chaos.next_int(50, 200),
            }
        else:
            details = {
                'type': 'clipboard_monitor',
                'content_type': self.chaos.next_choice(['text', 'password', 'crypto_wallet']),
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.KEYLOGGER,
            target=target,
            details=details,
            ioc_indicators=[
                f"exfil_type:{upload_type}",
                "pattern:small_frequent_uploads",
                "pattern:sensitive_data_collection",
            ],
        )

        self._log_event(event)
        return event

    def _generate_trojan_dl(self) -> MalwareEvent:
        """
        Malware Type 7: Trojan Downloader

        Simulates malware download patterns:
        - Payload fetching
        - Stage loading
        - Dynamic imports
        """
        stage = self.chaos.next_choice(['initial', 'stage2', 'plugin', 'update'])

        target = self.chaos.next_choice(MALWARE_TARGETS['malware_urls'])

        payload_name = self.chaos.next_choice([
            f"update_{self._random_string(8)}.exe",
            f"plugin_{self._random_string(6)}.dll",
            f"config_{self._random_string(4)}.dat",
            f"module_{self._random_string(5)}.bin",
        ])

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.TROJAN_DL,
            target=target,
            details={
                'stage': stage,
                'payload_name': payload_name,
                'expected_size': self.chaos.next_int(10000, 500000),
                'hash_type': 'sha256',
                'obfuscation': self.chaos.next_choice(['xor', 'rc4', 'aes', 'none']),
            },
            ioc_indicators=[
                f"stage:{stage}",
                "pattern:executable_download",
                "pattern:obfuscated_payload",
                f"file_extension:{payload_name.split('.')[-1]}",
            ],
        )

        # Actually fetch some bytes (safe endpoint)
        try:
            req = urllib.request.Request(target)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read(1024)
                event.details['bytes_received'] = len(data)
        except Exception as e:
            event.details['download_error'] = str(e)

        self._log_event(event)
        return event

    def _generate_worm_scan(self) -> MalwareEvent:
        """
        Malware Type 8: Worm Scanning

        Simulates worm propagation patterns:
        - Port scanning
        - Service enumeration
        - Vulnerability probing
        """
        scan_type = self.chaos.next_choice(['port_scan', 'smb_enum', 'ssh_brute', 'vuln_probe'])

        # Generate target in private IP range (won't actually connect)
        target_ip = self.chaos.next_choice([
            f"10.{self.chaos.next_int(0,255)}.{self.chaos.next_int(0,255)}.{self.chaos.next_int(1,254)}",
            f"192.168.{self.chaos.next_int(0,255)}.{self.chaos.next_int(1,254)}",
            f"172.{self.chaos.next_int(16,31)}.{self.chaos.next_int(0,255)}.{self.chaos.next_int(1,254)}",
        ])

        if scan_type == 'port_scan':
            ports = [22, 23, 80, 443, 445, 3389, 8080]
            target = f"{target_ip}:{self.chaos.next_choice(ports)}"
            details = {
                'scan_type': 'tcp_syn',
                'ports_scanned': self.chaos.next_int(10, 1000),
                'open_ports_found': self.chaos.next_int(0, 5),
            }
        elif scan_type == 'smb_enum':
            target = f"smb://{target_ip}:445"
            details = {
                'scan_type': 'smb_enumeration',
                'shares_found': self.chaos.next_int(0, 10),
                'null_session': self.chaos.next_choice([True, False]),
            }
        elif scan_type == 'ssh_brute':
            target = f"ssh://{target_ip}:22"
            details = {
                'scan_type': 'ssh_bruteforce',
                'attempts': self.chaos.next_int(10, 1000),
                'usernames_tried': ['root', 'admin', 'user', 'test'],
            }
        else:
            cve = f"CVE-{self.chaos.next_int(2018,2024)}-{self.chaos.next_int(1000,9999)}"
            target = f"exploit://{target_ip}"
            details = {
                'scan_type': 'vulnerability_probe',
                'cve': cve,
                'exploit_type': self.chaos.next_choice(['rce', 'lfi', 'sqli', 'overflow']),
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.WORM_SCAN,
            target=target,
            details=details,
            ioc_indicators=[
                f"scan_type:{scan_type}",
                "pattern:lateral_movement",
                "pattern:network_reconnaissance",
                f"target_network:{target_ip.rsplit('.', 1)[0]}.0/24",
            ],
        )

        self._log_event(event)
        return event

    def _generate_adware(self) -> MalwareEvent:
        """
        Malware Type 9: Adware/PUP

        Simulates adware traffic patterns:
        - Excessive ad network connections
        - Tracking beacon floods
        - Affiliate fraud clicks
        """
        ad_type = self.chaos.next_choice(['ad_fetch', 'tracking', 'click_fraud', 'popup'])

        ad_networks = [
            f"ads.{self._random_string(6)}-network.com",
            f"track.{self._random_string(5)}-analytics.net",
            f"pixel.{self._random_string(4)}-metrics.io",
        ]

        domain = self.chaos.next_choice(ad_networks)
        target = f"https://{domain}/serve"

        if ad_type == 'ad_fetch':
            details = {
                'type': 'ad_request',
                'ad_unit': self._random_string(12),
                'frequency': f"{self.chaos.next_int(10, 100)}/minute",
            }
        elif ad_type == 'tracking':
            details = {
                'type': 'tracking_beacon',
                'user_id': self._random_string(24),
                'events_per_session': self.chaos.next_int(50, 500),
            }
        elif ad_type == 'click_fraud':
            details = {
                'type': 'fraudulent_click',
                'affiliate_id': self._random_string(8),
                'fake_referrer': f"https://legitimate-site-{self._random_string(4)}.com",
            }
        else:
            details = {
                'type': 'popup_injection',
                'popups_per_hour': self.chaos.next_int(5, 50),
                'redirect_chain_length': self.chaos.next_int(2, 8),
            }

        event = MalwareEvent(
            timestamp=datetime.now(),
            malware_type=MalwareType.ADWARE,
            target=target,
            details=details,
            ioc_indicators=[
                f"ad_behavior:{ad_type}",
                "pattern:excessive_ad_traffic",
                "pattern:tracking_abuse",
                f"network:{domain}",
            ],
        )

        self._log_event(event)
        return event

    def generate_single(self, malware_type: MalwareType = None) -> MalwareEvent:
        """Generate a single malware behavior event."""
        if malware_type is None:
            malware_type = self.chaos.next_choice(list(MalwareType))

        generator = self.generators.get(malware_type)
        if generator:
            return generator()
        return None

    def generate_burst(self, count: int = 10, malware_type: MalwareType = None) -> List[MalwareEvent]:
        """Generate a burst of malware behavior events."""
        events = []
        for _ in range(count):
            event = self.generate_single(malware_type)
            if event:
                events.append(event)
            delay = abs(self.lorenz.next_normalized()[0]) * 0.3
            time.sleep(delay)
        return events

    def start_background(self,
                         interval: float = 5.0,
                         malware_types: List[MalwareType] = None):
        """Start generating malware-like traffic in background."""
        if self.running:
            return

        self.running = True
        allowed_types = malware_types or list(MalwareType)

        def _worker():
            while self.running:
                mtype = self.chaos.next_choice(allowed_types)
                self.generate_single(mtype)
                jitter = abs(self.lorenz.next_normalized()[0]) * interval
                time.sleep(interval + jitter)

        self.thread = threading.Thread(target=_worker, daemon=True)
        self.thread.start()

    def stop_background(self):
        """Stop background generation."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def get_stats(self) -> Dict:
        """Get generation statistics."""
        return {
            'total_events': len(self.events),
            'by_type': {k.value: v for k, v in self.stats.items()},
            'running': self.running,
        }

    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """Get recent events as dicts."""
        recent = self.events[-count:]
        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'type': e.malware_type.value,
                'target': e.target,
                'details': e.details,
                'iocs': e.ioc_indicators,
            }
            for e in recent
        ]


def list_malware_types() -> Dict[int, MalwareType]:
    """List all malware types with numeric keys."""
    return {i+1: mtype for i, mtype in enumerate(MalwareType)}


def get_malware_by_number(num: int) -> Optional[MalwareType]:
    """Get malware type by 1-indexed number."""
    types = list(MalwareType)
    if 1 <= num <= len(types):
        return types[num - 1]
    return None


def list_issue_types() -> Dict[int, IssueType]:
    """List all issue types with numeric keys."""
    return {i+1: issue for i, issue in enumerate(IssueType)}


def get_issue_by_number(num: int) -> Optional[IssueType]:
    """Get issue type by 1-indexed number."""
    types = list(IssueType)
    if 1 <= num <= len(types):
        return types[num - 1]
    return None


if __name__ == "__main__":
    # Demo
    print("Traffic Issue Simulator - 9 Issue Types")
    print("=" * 50)

    for i, issue in enumerate(IssueType, 1):
        print(f"  [{i}] {issue.value:25} - {ISSUE_DESCRIPTIONS[issue]}")

    print("\nGenerating sample events...\n")

    sim = TrafficIssueSimulator("demo_seed")

    # Generate one of each type
    for issue_type in IssueType:
        print(f"Generating: {issue_type.value}...")
        event = sim.generate_single(issue_type)
        print(f"  Target: {event.target}")
        print(f"  Details: {event.details}")
        print()

    print("\nStatistics:")
    print(sim.get_stats())
