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
