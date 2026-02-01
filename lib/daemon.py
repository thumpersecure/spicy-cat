#!/usr/bin/env python3
"""
daemon.py - Background Service for spicy-cat

"Cats spend 70% of their lives sleeping."
This daemon runs while you sleep, keeping your identity fresh.

Handles:
- Identity rotation scheduling
- State persistence
- Dashboard status updates
- Unix socket for client communication
"""

import os
import sys
import json
import time
import signal
import socket
import threading
import atexit
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable
import selectors


class SpicyCatDaemon:
    """
    Background daemon for identity management.

    Like a cat, it's always watching, rarely seen.
    """

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.spicy-cat")
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.pid_file = self.config_dir / 'daemon.pid'
        self.socket_path = self.config_dir / 'daemon.sock'
        self.state_file = self.config_dir / 'state.json'

        self.running = False
        self.current_identity = None
        self.rotation_interval: Optional[timedelta] = None
        self.last_rotation: Optional[datetime] = None

        self.callbacks: Dict[str, Callable] = {}
        self.server_socket: Optional[socket.socket] = None

    def is_running(self) -> bool:
        """Check if daemon is already running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # Process doesn't exist or invalid PID
            self.pid_file.unlink(missing_ok=True)
            return False

    def _write_pid(self):
        """Write PID file."""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def _remove_pid(self):
        """Remove PID file."""
        self.pid_file.unlink(missing_ok=True)

    def _save_state(self):
        """Persist current state."""
        state = {
            'last_rotation': self.last_rotation.isoformat() if self.last_rotation else None,
            'rotation_interval_seconds': self.rotation_interval.total_seconds() if self.rotation_interval else None,
            'current_identity_name': getattr(self.current_identity, 'username', None),
            'updated_at': datetime.now().isoformat(),
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load persisted state."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            if state.get('last_rotation'):
                self.last_rotation = datetime.fromisoformat(state['last_rotation'])

            if state.get('rotation_interval_seconds'):
                self.rotation_interval = timedelta(seconds=state['rotation_interval_seconds'])

        except (json.JSONDecodeError, KeyError):
            pass

    def _setup_socket(self):
        """Setup Unix domain socket for IPC."""
        # Remove old socket if exists
        self.socket_path.unlink(missing_ok=True)

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(str(self.socket_path))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)

        # Set socket permissions
        os.chmod(self.socket_path, 0o600)

    def _handle_client(self, client_socket: socket.socket):
        """Handle a client connection."""
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return

            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                request = {'command': data.strip()}

            response = self._process_command(request)
            client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            error_response = {'status': 'error', 'message': str(e)}
            try:
                client_socket.send(json.dumps(error_response).encode('utf-8'))
            except Exception:
                pass
        finally:
            client_socket.close()

    def _process_command(self, request: Dict) -> Dict:
        """Process a command from a client."""
        command = request.get('command', '')

        if command == 'status':
            return {
                'status': 'ok',
                'running': True,
                'current_identity': getattr(self.current_identity, 'username', None),
                'last_rotation': self.last_rotation.isoformat() if self.last_rotation else None,
                'next_rotation': self._next_rotation_time(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            }

        elif command == 'rotate':
            if 'rotate' in self.callbacks:
                self.callbacks['rotate']()
                self.last_rotation = datetime.now()
                self._save_state()
                return {'status': 'ok', 'message': 'Identity rotated'}
            return {'status': 'error', 'message': 'Rotation callback not set'}

        elif command == 'set_interval':
            seconds = request.get('seconds')
            if seconds:
                self.rotation_interval = timedelta(seconds=seconds)
                self._save_state()
                return {'status': 'ok', 'message': f'Rotation interval set to {seconds}s'}
            return {'status': 'error', 'message': 'No interval specified'}

        elif command == 'get_identity':
            if self.current_identity:
                return {
                    'status': 'ok',
                    'identity': {
                        'name': self.current_identity.full_name,
                        'username': self.current_identity.username,
                        'occupation': self.current_identity.occupation,
                        'location': self.current_identity.location,
                    }
                }
            return {'status': 'ok', 'identity': None}

        elif command == 'stop':
            self.running = False
            return {'status': 'ok', 'message': 'Daemon stopping'}

        elif command == 'ping':
            return {'status': 'ok', 'message': 'pong', 'timestamp': datetime.now().isoformat()}

        else:
            return {'status': 'error', 'message': f'Unknown command: {command}'}

    def _next_rotation_time(self) -> Optional[str]:
        """Calculate next rotation time."""
        if not self.rotation_interval or not self.last_rotation:
            return None

        next_time = self.last_rotation + self.rotation_interval
        return next_time.isoformat()

    def _check_rotation(self):
        """Check if rotation is due."""
        if not self.rotation_interval:
            return False

        if not self.last_rotation:
            self.last_rotation = datetime.now()
            return False

        if datetime.now() >= self.last_rotation + self.rotation_interval:
            return True

        return False

    def set_rotation_callback(self, callback: Callable):
        """Set the function to call for identity rotation."""
        self.callbacks['rotate'] = callback

    def set_identity(self, identity):
        """Set current identity."""
        self.current_identity = identity
        self._save_state()

    def daemonize(self):
        """
        Fork to background (Unix double-fork).

        Not all cats are domesticated.
        """
        if sys.platform == 'win32':
            print("[spicy-cat] Daemon mode not supported on Windows")
            return False

        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                # Parent exits
                sys.exit(0)
        except OSError as e:
            print(f"[spicy-cat] Fork #1 failed: {e}")
            return False

        # Decouple from parent
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            print(f"[spicy-cat] Fork #2 failed: {e}")
            return False

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        null_fd = os.open('/dev/null', os.O_RDWR)
        os.dup2(null_fd, sys.stdin.fileno())
        os.dup2(null_fd, sys.stdout.fileno())
        os.dup2(null_fd, sys.stderr.fileno())

        return True

    def run(self, foreground: bool = False):
        """
        Run the daemon.

        Args:
            foreground: If True, don't daemonize (useful for debugging)
        """
        if self.is_running():
            print("[spicy-cat] Daemon already running")
            return False

        if not foreground:
            if not self.daemonize():
                return False

        # Setup
        self._write_pid()
        self._load_state()
        self._setup_socket()

        self.running = True
        self.start_time = datetime.now()

        # Register cleanup
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Create selector for non-blocking I/O
        sel = selectors.DefaultSelector()
        sel.register(self.server_socket, selectors.EVENT_READ)

        if foreground:
            print(f"[spicy-cat] Daemon running (PID: {os.getpid()})")
            print(f"[spicy-cat] Socket: {self.socket_path}")

        # Main loop
        while self.running:
            # Check for socket connections
            events = sel.select(timeout=1.0)

            for key, _ in events:
                if key.fileobj == self.server_socket:
                    try:
                        client, _ = self.server_socket.accept()
                        # Handle in thread to not block
                        thread = threading.Thread(target=self._handle_client, args=(client,))
                        thread.daemon = True
                        thread.start()
                    except BlockingIOError:
                        pass

            # Check for scheduled rotation
            if self._check_rotation():
                if 'rotate' in self.callbacks:
                    self.callbacks['rotate']()
                    self.last_rotation = datetime.now()
                    self._save_state()

        self._cleanup()
        return True

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.running = False

    def _cleanup(self):
        """Cleanup on exit."""
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

        self.socket_path.unlink(missing_ok=True)
        self._remove_pid()


class DaemonClient:
    """
    Client for communicating with the daemon.

    "Hey daemon, what's up?" - basically this.
    """

    def __init__(self, socket_path: str = None):
        if socket_path is None:
            socket_path = os.path.expanduser("~/.spicy-cat/daemon.sock")
        self.socket_path = Path(socket_path)

    def is_daemon_running(self) -> bool:
        """Check if daemon is responding."""
        try:
            response = self.send_command({'command': 'ping'})
            return response.get('status') == 'ok'
        except Exception:
            return False

    def send_command(self, command: Dict) -> Dict:
        """Send command to daemon and get response."""
        if not self.socket_path.exists():
            raise ConnectionError("Daemon socket not found. Is the daemon running?")

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(str(self.socket_path))
            sock.send(json.dumps(command).encode('utf-8'))

            response_data = sock.recv(4096).decode('utf-8')
            return json.loads(response_data)
        finally:
            sock.close()

    def status(self) -> Dict:
        """Get daemon status."""
        return self.send_command({'command': 'status'})

    def rotate(self) -> Dict:
        """Request identity rotation."""
        return self.send_command({'command': 'rotate'})

    def get_identity(self) -> Dict:
        """Get current identity info."""
        return self.send_command({'command': 'get_identity'})

    def set_rotation_interval(self, seconds: int) -> Dict:
        """Set rotation interval."""
        return self.send_command({'command': 'set_interval', 'seconds': seconds})

    def stop(self) -> Dict:
        """Request daemon shutdown."""
        return self.send_command({'command': 'stop'})


def start_daemon(foreground: bool = False) -> bool:
    """Start the spicy-cat daemon."""
    daemon = SpicyCatDaemon()
    return daemon.run(foreground=foreground)


def stop_daemon() -> bool:
    """Stop the spicy-cat daemon."""
    client = DaemonClient()
    try:
        response = client.stop()
        return response.get('status') == 'ok'
    except ConnectionError:
        print("[spicy-cat] Daemon not running")
        return False


def daemon_status() -> Optional[Dict]:
    """Get daemon status."""
    client = DaemonClient()
    try:
        return client.status()
    except ConnectionError:
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == 'start':
            foreground = '--foreground' in sys.argv or '-f' in sys.argv
            start_daemon(foreground=foreground)

        elif cmd == 'stop':
            stop_daemon()

        elif cmd == 'status':
            status = daemon_status()
            if status:
                print(json.dumps(status, indent=2))
            else:
                print("Daemon not running")

        else:
            print(f"Unknown command: {cmd}")
            print("Usage: daemon.py [start|stop|status] [--foreground]")
    else:
        print("spicy-cat daemon")
        print("Usage: daemon.py [start|stop|status] [--foreground]")
