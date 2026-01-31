#!/usr/bin/env python3
"""
browser.py - Firefox Profile Management for spicy-cat

"A cat always lands on its feet, and Firefox always lands on privacy."

Manages Firefox profiles seeded with identity data for consistent
browsing under assumed identities.
"""

import os
import json
import shutil
import subprocess
import configparser
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class FirefoxProfile:
    """
    Firefox profile manager.

    Like herding cats, but with browser profiles.
    """

    # Firefox profile paths by platform
    FIREFOX_PATHS = {
        'linux': [
            Path.home() / '.mozilla' / 'firefox',
            Path.home() / 'snap' / 'firefox' / 'common' / '.mozilla' / 'firefox',
        ],
        'darwin': [
            Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles',
        ],
        'win32': [
            Path(os.environ.get('APPDATA', '')) / 'Mozilla' / 'Firefox' / 'Profiles',
        ],
    }

    # Privacy-focused prefs
    PRIVACY_PREFS = {
        # Disable telemetry
        'toolkit.telemetry.enabled': False,
        'toolkit.telemetry.unified': False,
        'datareporting.healthreport.uploadEnabled': False,
        'datareporting.policy.dataSubmissionEnabled': False,

        # Disable Pocket
        'extensions.pocket.enabled': False,

        # Enhanced tracking protection
        'privacy.trackingprotection.enabled': True,
        'privacy.trackingprotection.socialtracking.enabled': True,
        'privacy.trackingprotection.cryptomining.enabled': True,
        'privacy.trackingprotection.fingerprinting.enabled': True,

        # Cookies
        'network.cookie.cookieBehavior': 1,  # Block third-party cookies

        # WebRTC (prevents IP leak)
        'media.peerconnection.enabled': False,

        # Disable prefetching
        'network.prefetch-next': False,
        'network.dns.disablePrefetch': True,

        # Disable geolocation
        'geo.enabled': False,

        # Resist fingerprinting
        'privacy.resistFingerprinting': True,

        # First-party isolation
        'privacy.firstparty.isolate': True,

        # Disable WebGL (fingerprinting vector)
        'webgl.disabled': True,

        # Safe browsing (can be privacy issue but also protective)
        'browser.safebrowsing.malware.enabled': False,
        'browser.safebrowsing.phishing.enabled': False,
    }

    def __init__(self, identity=None, profile_name: str = None):
        self.identity = identity
        self.profile_name = profile_name or f"spicy-cat-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.profile_path: Optional[Path] = None
        self.firefox_dir = self._find_firefox_dir()

    def _find_firefox_dir(self) -> Optional[Path]:
        """Find the Firefox profiles directory."""
        import sys
        platform = sys.platform

        paths = self.FIREFOX_PATHS.get(platform, self.FIREFOX_PATHS['linux'])

        for path in paths:
            if path.exists():
                return path

        return None

    def _get_profiles_ini(self) -> Optional[Path]:
        """Get path to profiles.ini."""
        if not self.firefox_dir:
            return None

        # profiles.ini is usually one level up from Profiles folder on some systems
        candidates = [
            self.firefox_dir / 'profiles.ini',
            self.firefox_dir.parent / 'profiles.ini',
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def create_profile(self) -> Optional[Path]:
        """
        Create a new Firefox profile.

        Returns the profile path if successful.
        """
        if not self.firefox_dir:
            print("[spicy-cat] Firefox directory not found. Is Firefox installed?")
            return None

        # Create profile directory
        profile_dir = self.firefox_dir / self.profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = profile_dir

        # Create user.js with privacy settings
        self._write_user_prefs()

        # Register profile in profiles.ini
        self._register_profile()

        print(f"[spicy-cat] Created Firefox profile: {self.profile_name}")
        print(f"[spicy-cat] Profile path: {profile_dir}")

        return profile_dir

    def _write_user_prefs(self):
        """Write user.js with privacy settings and identity data."""
        if not self.profile_path:
            return

        user_js = self.profile_path / 'user.js'

        prefs = self.PRIVACY_PREFS.copy()

        # Add identity-specific preferences if available
        if self.identity:
            # Set timezone based on location (simplified)
            # In reality, you'd map city to timezone
            prefs['intl.accept_languages'] = 'en-US, en'

            # Set homepage to something generic
            prefs['browser.startup.homepage'] = 'about:blank'

        # Write prefs
        with open(user_js, 'w') as f:
            f.write('// spicy-cat Firefox profile\n')
            f.write(f'// Generated: {datetime.now().isoformat()}\n')
            f.write(f'// Identity: {self.identity.full_name if self.identity else "Anonymous"}\n\n')

            for key, value in prefs.items():
                if isinstance(value, bool):
                    js_value = 'true' if value else 'false'
                elif isinstance(value, int):
                    js_value = str(value)
                elif isinstance(value, str):
                    js_value = f'"{value}"'
                else:
                    continue

                f.write(f'user_pref("{key}", {js_value});\n')

    def _register_profile(self):
        """Register profile in Firefox's profiles.ini."""
        profiles_ini = self._get_profiles_ini()
        if not profiles_ini:
            # Create a new profiles.ini if it doesn't exist
            return

        config = configparser.ConfigParser()
        config.read(profiles_ini)

        # Find next profile number
        profile_num = 0
        while f'Profile{profile_num}' in config:
            profile_num += 1

        section = f'Profile{profile_num}'
        config[section] = {
            'Name': self.profile_name,
            'IsRelative': '1',
            'Path': self.profile_name,
        }

        with open(profiles_ini, 'w') as f:
            config.write(f)

    def get_launch_command(self, url: str = None) -> List[str]:
        """Get command to launch Firefox with this profile."""
        cmd = ['firefox', '-P', self.profile_name]

        if url:
            cmd.append(url)
        else:
            cmd.append('about:blank')

        return cmd

    def launch(self, url: str = None, tor: bool = False) -> Optional[subprocess.Popen]:
        """
        Launch Firefox with this profile.

        If tor=True, attempts to route through Tor (requires Tor to be running).
        """
        if not self.profile_path:
            self.create_profile()

        cmd = self.get_launch_command(url)

        env = os.environ.copy()

        if tor:
            # Try to use Tor SOCKS proxy
            # Assumes Tor is running on default port 9050
            env['all_proxy'] = 'socks5://127.0.0.1:9050'
            env['ALL_PROXY'] = 'socks5://127.0.0.1:9050'
            print("[spicy-cat] Attempting to route through Tor (127.0.0.1:9050)")

        try:
            # Launch in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                start_new_session=True,
            )
            print(f"[spicy-cat] Launched Firefox (PID: {process.pid})")
            return process
        except FileNotFoundError:
            print("[spicy-cat] Firefox not found. Please install Firefox.")
            return None
        except Exception as e:
            print(f"[spicy-cat] Failed to launch Firefox: {e}")
            return None

    def delete_profile(self) -> bool:
        """Delete this profile."""
        if not self.profile_path or not self.profile_path.exists():
            return False

        try:
            shutil.rmtree(self.profile_path)
            print(f"[spicy-cat] Deleted profile: {self.profile_name}")
            return True
        except Exception as e:
            print(f"[spicy-cat] Failed to delete profile: {e}")
            return False


class BrowserManager:
    """
    Manage multiple browser profiles for different identities.

    A cat cafe of browser profiles.
    """

    def __init__(self, vault_path: str = None):
        if vault_path is None:
            vault_path = os.path.expanduser("~/.spicy-cat/browsers")
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        self.profiles: Dict[str, FirefoxProfile] = {}
        self._load_profile_registry()

    def _registry_path(self) -> Path:
        return self.vault_path / 'profiles.json'

    def _load_profile_registry(self):
        """Load the profile registry."""
        registry_path = self._registry_path()
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.registry = json.load(f)
            except json.JSONDecodeError:
                self.registry = {}
        else:
            self.registry = {}

    def _save_profile_registry(self):
        """Save the profile registry."""
        with open(self._registry_path(), 'w') as f:
            json.dump(self.registry, f, indent=2)

    def create_for_identity(self, identity, name: str = None) -> FirefoxProfile:
        """Create a browser profile for an identity."""
        if name is None:
            name = f"spicy-{identity.username}"

        profile = FirefoxProfile(identity, name)
        profile_path = profile.create_profile()

        if profile_path:
            self.profiles[name] = profile
            self.registry[name] = {
                'identity_username': identity.username,
                'profile_name': name,
                'profile_path': str(profile_path),
                'created_at': datetime.now().isoformat(),
            }
            self._save_profile_registry()

        return profile

    def get_profile(self, name: str) -> Optional[FirefoxProfile]:
        """Get a profile by name."""
        if name in self.profiles:
            return self.profiles[name]

        if name in self.registry:
            profile = FirefoxProfile(profile_name=self.registry[name]['profile_name'])
            profile.profile_path = Path(self.registry[name]['profile_path'])
            self.profiles[name] = profile
            return profile

        return None

    def list_profiles(self) -> List[str]:
        """List all managed profiles."""
        return list(self.registry.keys())

    def launch_for_identity(self, identity, url: str = None, tor: bool = False) -> Optional[subprocess.Popen]:
        """Launch browser for an identity, creating profile if needed."""
        name = f"spicy-{identity.username}"

        profile = self.get_profile(name)
        if not profile:
            profile = self.create_for_identity(identity, name)

        return profile.launch(url, tor)

    def cleanup_profile(self, name: str) -> bool:
        """Remove a profile completely."""
        profile = self.get_profile(name)
        if profile:
            success = profile.delete_profile()
            if success:
                self.profiles.pop(name, None)
                self.registry.pop(name, None)
                self._save_profile_registry()
            return success
        return False

    def cleanup_all(self) -> int:
        """Remove all spicy-cat profiles. Returns count of removed profiles."""
        count = 0
        for name in list(self.registry.keys()):
            if self.cleanup_profile(name):
                count += 1
        return count


def check_tor_available() -> bool:
    """Check if Tor SOCKS proxy is available."""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        return result == 0
    except socket.error:
        return False


def get_browser_fingerprint_info() -> Dict:
    """
    Get information about browser fingerprinting risks.
    Educational output for the user.
    """
    return {
        'warning': 'Browser fingerprinting can still identify you even with a new profile',
        'mitigations': [
            'Use Tor Browser instead of Firefox for maximum anonymity',
            'The profile enables resistFingerprinting which helps but is not perfect',
            'Canvas, WebGL, and audio fingerprinting are reduced but not eliminated',
            'Your screen resolution and fonts can still be fingerprinting vectors',
        ],
        'recommendations': [
            'For high-stakes anonymity, use Tor Browser or Tails OS',
            'This profile is suitable for reducing casual tracking and data broker collection',
            'Combine with VPN or Tor for network-level anonymity',
        ],
    }


if __name__ == "__main__":
    print("=== Firefox Profile Manager Demo ===\n")

    print(f"Tor available: {check_tor_available()}")

    fp = FirefoxProfile(profile_name="spicy-cat-demo")

    if fp.firefox_dir:
        print(f"Firefox directory: {fp.firefox_dir}")
        print(f"Launch command: {' '.join(fp.get_launch_command('https://example.com'))}")
    else:
        print("Firefox not found on this system")

    print("\nFingerprinting info:")
    info = get_browser_fingerprint_info()
    print(f"  Warning: {info['warning']}")
    print("  Mitigations:")
    for m in info['mitigations'][:2]:
        print(f"    - {m}")
