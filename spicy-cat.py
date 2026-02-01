#!/usr/bin/env python3
"""
spicy-cat - Create and manage alternate digital identities

    /\\_____/\\
   /  o   o  \\
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

"In a world of digital surveillance, be a cat:
 mysterious, independent, and impossible to track."

Usage:
    spicy-cat new [--name NAME] [--locale LOCALE] [--temp]
    spicy-cat show [NAME]
    spicy-cat list
    spicy-cat delete NAME
    spicy-cat rotate
    spicy-cat browse [NAME] [--tor] [--url URL]
    spicy-cat dashboard [NAME]
    spicy-cat daemon [start|stop|status]
    spicy-cat export NAME [--format FORMAT]
    spicy-cat --help

Commands:
    new         Generate a new identity
    show        Display current or named identity
    list        List all saved identities
    delete      Remove an identity
    rotate      Switch to a different identity
    browse      Launch Firefox with identity profile
    dashboard   Show live identity dashboard
    daemon      Manage background service
    export      Export identity data

Options:
    --name      Custom name for the identity
    --locale    Locale for generating names (default: en_US)
    --temp      Create ephemeral identity (not saved)
    --tor       Route through Tor (requires Tor running)
    --url       URL to open in browser
    --format    Export format: json, csv, minimal (default: json)

Examples:
    spicy-cat new
    spicy-cat new --locale de_DE --name "german_alias"
    spicy-cat browse german_alias --tor
    spicy-cat dashboard
    spicy-cat daemon start

The purrfect tool for digital anonymity.
"""

import os
import sys
import json
import argparse
import secrets
from pathlib import Path
from datetime import datetime

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.identity import Identity, IdentityVault, quick_identity, generate_seed, FAKER_AVAILABLE
from lib.dashboard import Dashboard, CompactDisplay, print_identity_card, Colors, SPICY_CAT_LOGO, SPICY_CAT_SMALL
from lib.browser import BrowserManager, FirefoxProfile, check_tor_available, get_browser_fingerprint_info
from lib.daemon import SpicyCatDaemon, DaemonClient, daemon_status, start_daemon, stop_daemon
from lib.traffic import (TrafficIssueSimulator, IssueType, ISSUE_DESCRIPTIONS,
                          list_issue_types, get_issue_by_number,
                          MalwareSimulator, MalwareType, MALWARE_DESCRIPTIONS,
                          list_malware_types, get_malware_by_number)


# Version and metadata
__version__ = "1.0.0"
__codename__ = "Curious Whiskers"


def print_banner():
    """Print the spicy-cat banner."""
    print(f"{Colors.BRIGHT_MAGENTA}{SPICY_CAT_SMALL}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}spicy-cat{Colors.RESET} {Colors.DIM}v{__version__} \"{__codename__}\"{Colors.RESET}")
    print(f"{Colors.DIM}The purrfect anonymity tool{Colors.RESET}")
    print()


def cmd_new(args):
    """Generate a new identity."""
    print_banner()

    seed = generate_seed()
    locale = args.locale or 'en_US'

    print(f"{Colors.YELLOW}Generating identity...{Colors.RESET}")
    identity = Identity(seed, locale)

    if args.temp:
        print(f"{Colors.BRIGHT_BLACK}(Ephemeral - not saved){Colors.RESET}")
    else:
        vault = IdentityVault()
        name = args.name or identity.username
        vault.save(identity, name)
        print(f"{Colors.GREEN}Saved as:{Colors.RESET} {name}")

    print()
    print(print_identity_card(identity))

    # Show behavior hints
    behavior = identity.behavior.get_current_state()
    print(f"{Colors.DIM}Writing style: {behavior['writing_style']} | Activity: {behavior['activity_state']}{Colors.RESET}")

    return identity


def cmd_show(args):
    """Show an identity."""
    print_banner()

    vault = IdentityVault()

    if args.name:
        identity = vault.load(args.name)
        if not identity:
            print(f"{Colors.RED}Identity not found:{Colors.RESET} {args.name}")
            return None
    else:
        # Show most recent or first available
        identities = vault.list_identities()
        if not identities:
            print(f"{Colors.YELLOW}No identities found. Use 'spicy-cat new' to create one.{Colors.RESET}")
            return None
        identity = vault.load(identities[0])

    print(print_identity_card(identity))

    # Extended info
    if identity.bio:
        print(f"{Colors.DIM}Bio: {identity.bio[:100]}...{Colors.RESET}")

    print(f"\n{Colors.BRIGHT_BLACK}Backstory:{Colors.RESET}")
    for key, value in identity.backstory.items():
        if isinstance(value, list):
            value = ', '.join(value)
        print(f"  {Colors.DIM}{key}:{Colors.RESET} {value}")

    return identity


def cmd_list(args):
    """List all identities."""
    print_banner()

    vault = IdentityVault()
    identities = vault.list_identities()

    if not identities:
        print(f"{Colors.YELLOW}No identities found.{Colors.RESET}")
        print(f"{Colors.DIM}Use 'spicy-cat new' to create one.{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Saved Identities ({len(identities)}){Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 50}{Colors.RESET}")

    for name in identities:
        identity = vault.load(name)
        if identity:
            age_days = (datetime.now() - identity.created_at).days
            age_str = f"{age_days}d" if age_days > 0 else "new"

            print(f"  {Colors.CYAN}{name:20}{Colors.RESET} "
                  f"{Colors.WHITE}{identity.full_name:25}{Colors.RESET} "
                  f"{Colors.DIM}({age_str}){Colors.RESET}")


def cmd_delete(args):
    """Delete an identity."""
    if not args.name:
        print(f"{Colors.RED}Please specify identity name to delete.{Colors.RESET}")
        return False

    vault = IdentityVault()

    if args.name not in vault.list_identities():
        print(f"{Colors.RED}Identity not found:{Colors.RESET} {args.name}")
        return False

    # Confirm
    print(f"{Colors.YELLOW}Delete identity '{args.name}'? [y/N]{Colors.RESET} ", end='')
    confirm = input().strip().lower()

    if confirm != 'y':
        print("Cancelled.")
        return False

    if vault.delete(args.name):
        print(f"{Colors.GREEN}Deleted:{Colors.RESET} {args.name}")

        # Also cleanup browser profile
        browser_mgr = BrowserManager()
        browser_mgr.cleanup_profile(f"spicy-{args.name}")

        return True

    return False


def cmd_rotate(args):
    """Rotate to a different identity."""
    print_banner()

    vault = IdentityVault()
    identities = vault.list_identities()

    if len(identities) < 2:
        print(f"{Colors.YELLOW}Not enough identities to rotate.{Colors.RESET}")
        print(f"{Colors.DIM}Create more with 'spicy-cat new'{Colors.RESET}")
        return None

    # Simple rotation - just pick the next one
    # In a real scenario, you'd track "current" identity
    print(f"{Colors.YELLOW}Available identities:{Colors.RESET}")
    for i, name in enumerate(identities):
        print(f"  [{i+1}] {name}")

    print(f"\n{Colors.CYAN}Select identity number:{Colors.RESET} ", end='')
    try:
        choice = int(input().strip()) - 1
        if 0 <= choice < len(identities):
            identity = vault.load(identities[choice])
            print(f"\n{Colors.GREEN}Switched to:{Colors.RESET} {identity.full_name}")
            print(print_identity_card(identity))
            return identity
        else:
            print(f"{Colors.RED}Invalid choice{Colors.RESET}")
    except ValueError:
        print(f"{Colors.RED}Invalid input{Colors.RESET}")

    return None


def cmd_browse(args):
    """Launch browser with identity profile."""
    print_banner()

    vault = IdentityVault()
    browser_mgr = BrowserManager()

    # Get identity
    if args.name:
        identity = vault.load(args.name)
        if not identity:
            print(f"{Colors.RED}Identity not found:{Colors.RESET} {args.name}")
            return False
    else:
        identities = vault.list_identities()
        if not identities:
            print(f"{Colors.YELLOW}No identities. Creating temporary one...{Colors.RESET}")
            identity = quick_identity()
        else:
            identity = vault.load(identities[0])

    # Tor check
    if args.tor:
        if check_tor_available():
            print(f"{Colors.GREEN}Tor detected{Colors.RESET} (127.0.0.1:9050)")
        else:
            print(f"{Colors.YELLOW}Warning: Tor not detected on port 9050{Colors.RESET}")
            print(f"{Colors.DIM}Install and start Tor, or traffic won't be routed through it.{Colors.RESET}")

    print(f"{Colors.CYAN}Launching browser as:{Colors.RESET} {identity.full_name}")
    print(f"{Colors.DIM}Username: @{identity.username} | {identity.location}{Colors.RESET}")

    # Show fingerprinting warning
    info = get_browser_fingerprint_info()
    print(f"\n{Colors.BRIGHT_BLACK}{info['warning']}{Colors.RESET}")

    # Launch
    url = args.url or 'about:blank'
    process = browser_mgr.launch_for_identity(identity, url=url, tor=args.tor)

    if process:
        print(f"\n{Colors.GREEN}Browser launched!{Colors.RESET}")
        print(f"{Colors.DIM}Profile will persist for this identity.{Colors.RESET}")
        return True

    return False


def cmd_dashboard(args):
    """Show live dashboard."""
    vault = IdentityVault()

    # Get identity
    if args.name:
        identity = vault.load(args.name)
    else:
        identities = vault.list_identities()
        identity = vault.load(identities[0]) if identities else None

    dashboard = Dashboard(identity)

    try:
        dashboard.run()
    except KeyboardInterrupt:
        pass

    print(f"{Colors.DIM}Dashboard closed.{Colors.RESET}")


def cmd_daemon(args):
    """Manage daemon."""
    action = args.action or 'status'

    if action == 'start':
        print(f"{Colors.CYAN}Starting spicy-cat daemon...{Colors.RESET}")

        # Check if already running
        status = daemon_status()
        if status:
            print(f"{Colors.YELLOW}Daemon already running{Colors.RESET}")
            print(f"  Uptime: {int(status.get('uptime_seconds', 0))}s")
            return True

        # Fork to background
        if '--foreground' in sys.argv or '-f' in sys.argv:
            start_daemon(foreground=True)
        else:
            # Start in background via fork
            pid = os.fork()
            if pid == 0:
                # Child process
                start_daemon(foreground=True)
                sys.exit(0)
            else:
                # Parent
                import time
                time.sleep(0.5)
                print(f"{Colors.GREEN}Daemon started{Colors.RESET} (PID: {pid})")

    elif action == 'stop':
        print(f"{Colors.CYAN}Stopping spicy-cat daemon...{Colors.RESET}")
        if stop_daemon():
            print(f"{Colors.GREEN}Daemon stopped{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Daemon was not running{Colors.RESET}")

    elif action == 'status':
        status = daemon_status()
        if status:
            print(f"{Colors.GREEN}Daemon running{Colors.RESET}")
            print(f"  Uptime: {int(status.get('uptime_seconds', 0))}s")
            print(f"  Current identity: {status.get('current_identity') or 'None'}")
            if status.get('next_rotation'):
                print(f"  Next rotation: {status.get('next_rotation')}")
        else:
            print(f"{Colors.YELLOW}Daemon not running{Colors.RESET}")
            print(f"{Colors.DIM}Start with: spicy-cat daemon start{Colors.RESET}")


def cmd_export(args):
    """Export identity data."""
    if not args.name:
        print(f"{Colors.RED}Please specify identity name to export.{Colors.RESET}")
        return False

    vault = IdentityVault()
    identity = vault.load(args.name)

    if not identity:
        print(f"{Colors.RED}Identity not found:{Colors.RESET} {args.name}")
        return False

    format_type = args.format or 'json'

    if format_type == 'json':
        print(identity.to_json())

    elif format_type == 'minimal':
        print(f"Name: {identity.full_name}")
        print(f"Age: {identity.age}")
        print(f"Location: {identity.location}, {identity.country}")
        print(f"Occupation: {identity.occupation}")
        print(f"Email: {identity.email}")
        print(f"Username: @{identity.username}")
        print(f"Phone: {identity.phone}")

    elif format_type == 'csv':
        # Header
        print("name,age,location,country,occupation,email,username,phone")
        # Data
        print(f'"{identity.full_name}",{identity.age},"{identity.location}","{identity.country}",'
              f'"{identity.occupation}","{identity.email}","@{identity.username}","{identity.phone}"')

    else:
        print(f"{Colors.RED}Unknown format:{Colors.RESET} {format_type}")
        return False

    return True


def cmd_traffic(args):
    """Generate decoy traffic that mimics system issues or malware behavior."""
    print_banner()

    # Check if malware mode
    is_malware_mode = args.malware

    if is_malware_mode:
        print(f"{Colors.BOLD}{Colors.BRIGHT_RED}Malware Behavior Simulator{Colors.RESET}")
        print(f"{Colors.DIM}Educational/testing - simulates malware network patterns{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}(No actual malicious functionality){Colors.RESET}")
    else:
        print(f"{Colors.BOLD}Traffic Issue Simulator{Colors.RESET}")
        print(f"{Colors.DIM}Generate decoy traffic to mask real activity{Colors.RESET}")
    print()

    # List available types
    if args.list_types:
        if is_malware_mode:
            print(f"{Colors.BOLD}Available Malware Behavior Types (9):{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLACK}{'─' * 65}{Colors.RESET}")
            for i, mtype in enumerate(MalwareType, 1):
                print(f"  {Colors.RED}[{i}]{Colors.RESET} {mtype.value:20} {Colors.DIM}{MALWARE_DESCRIPTIONS[mtype]}{Colors.RESET}")
        else:
            print(f"{Colors.BOLD}Available Issue Types (9):{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLACK}{'─' * 60}{Colors.RESET}")
            for i, issue in enumerate(IssueType, 1):
                print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {issue.value:25} {Colors.DIM}{ISSUE_DESCRIPTIONS[issue]}{Colors.RESET}")
        return

    # Determine which types to use
    selected_types = []
    if args.type:
        for t in args.type:
            if t.isdigit():
                if is_malware_mode:
                    mtype = get_malware_by_number(int(t))
                    if mtype:
                        selected_types.append(mtype)
                else:
                    issue = get_issue_by_number(int(t))
                    if issue:
                        selected_types.append(issue)
            else:
                try:
                    if is_malware_mode:
                        mtype = MalwareType(t)
                        selected_types.append(mtype)
                    else:
                        issue = IssueType(t)
                        selected_types.append(issue)
                except ValueError:
                    print(f"{Colors.RED}Unknown type:{Colors.RESET} {t}")
                    return

    if not selected_types:
        selected_types = list(MalwareType) if is_malware_mode else list(IssueType)

    # Create simulator
    if is_malware_mode:
        sim = MalwareSimulator()
        type_attr = 'malware_type'
    else:
        sim = TrafficIssueSimulator()
        type_attr = 'issue_type'

    print(f"{Colors.YELLOW}Selected types:{Colors.RESET}")
    for t in selected_types:
        color = Colors.RED if is_malware_mode else Colors.CYAN
        print(f"  {color}•{Colors.RESET} {t.value}")
    print()

    # Run mode
    if args.background:
        interval = args.interval or 5.0
        print(f"{Colors.GREEN}Starting background generation...{Colors.RESET}")
        print(f"{Colors.DIM}Interval: ~{interval}s (with jitter){Colors.RESET}")
        print(f"{Colors.DIM}Press Ctrl+C to stop{Colors.RESET}")
        print()

        if is_malware_mode:
            sim.start_background(interval=interval, malware_types=selected_types)
        else:
            sim.start_background(interval=interval, issue_types=selected_types)

        try:
            import time
            while True:
                time.sleep(5)
                stats = sim.get_stats()
                recent = sim.get_recent_events(3)

                print(f"\r{Colors.BRIGHT_BLACK}Events: {stats['total_events']} | ", end='')
                if recent:
                    latest = recent[-1]
                    print(f"Last: {latest['type']} -> {latest['target'][:30]}...{Colors.RESET}", end='')
                sys.stdout.flush()

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stopping...{Colors.RESET}")
            sim.stop_background()

    else:
        # Burst mode
        count = args.count or 5
        mode_name = "malware behavior" if is_malware_mode else "traffic"
        print(f"{Colors.CYAN}Generating {count} {mode_name} events...{Colors.RESET}")
        print()

        for i in range(count):
            selected_type = selected_types[i % len(selected_types)]
            event = sim.generate_single(selected_type)

            status_color = Colors.RED if is_malware_mode else Colors.YELLOW
            event_type = getattr(event, type_attr)
            print(f"  {status_color}◆{Colors.RESET} [{event_type.value:20}] {event.target[:40]}")

            if args.verbose:
                for k, v in event.details.items():
                    print(f"      {Colors.DIM}{k}: {v}{Colors.RESET}")
                if is_malware_mode and hasattr(event, 'ioc_indicators'):
                    print(f"      {Colors.BRIGHT_RED}IOCs: {', '.join(event.ioc_indicators[:3])}{Colors.RESET}")

        print()
        print(f"{Colors.GREEN}Generated {count} {mode_name} events.{Colors.RESET}")

    # Show stats
    stats = sim.get_stats()
    print()
    print(f"{Colors.BOLD}Statistics:{Colors.RESET}")
    for issue_type, count in stats['by_type'].items():
        if count > 0:
            print(f"  {issue_type}: {count}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='spicy-cat - Digital identity management for the privacy-conscious',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spicy-cat new                    Generate new identity
  spicy-cat new --locale de_DE     German identity
  spicy-cat show                   Show current identity
  spicy-cat list                   List all identities
  spicy-cat browse --tor           Browse with Tor
  spicy-cat dashboard              Live status display
  spicy-cat daemon start           Start background service

"Curiosity killed the cat, but anonymity kept it safe."
        """
    )

    parser.add_argument('--version', action='version', version=f'spicy-cat {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # new
    new_parser = subparsers.add_parser('new', help='Generate new identity')
    new_parser.add_argument('--name', '-n', help='Custom name for identity')
    new_parser.add_argument('--locale', '-l', default='en_US', help='Locale (default: en_US)')
    new_parser.add_argument('--temp', '-t', action='store_true', help='Ephemeral identity')

    # show
    show_parser = subparsers.add_parser('show', help='Show identity details')
    show_parser.add_argument('name', nargs='?', help='Identity name')

    # list
    subparsers.add_parser('list', help='List all identities')

    # delete
    delete_parser = subparsers.add_parser('delete', help='Delete identity')
    delete_parser.add_argument('name', help='Identity name')

    # rotate
    subparsers.add_parser('rotate', help='Switch identity')

    # browse
    browse_parser = subparsers.add_parser('browse', help='Launch browser')
    browse_parser.add_argument('name', nargs='?', help='Identity name')
    browse_parser.add_argument('--tor', action='store_true', help='Route through Tor')
    browse_parser.add_argument('--url', '-u', help='URL to open')

    # dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Live dashboard')
    dashboard_parser.add_argument('name', nargs='?', help='Identity name')

    # daemon
    daemon_parser = subparsers.add_parser('daemon', help='Background service')
    daemon_parser.add_argument('action', nargs='?', choices=['start', 'stop', 'status'],
                               default='status', help='Daemon action')

    # export
    export_parser = subparsers.add_parser('export', help='Export identity')
    export_parser.add_argument('name', help='Identity name')
    export_parser.add_argument('--format', '-f', choices=['json', 'csv', 'minimal'],
                               default='json', help='Export format')

    # traffic
    traffic_parser = subparsers.add_parser('traffic', help='Generate decoy traffic')
    traffic_parser.add_argument('--type', '-t', action='append',
                                help='Issue type (1-9 or name). Can repeat for multiple types.')
    traffic_parser.add_argument('--list-types', '-l', action='store_true',
                                help='List available issue/malware types')
    traffic_parser.add_argument('--count', '-c', type=int, default=5,
                                help='Number of events to generate (default: 5)')
    traffic_parser.add_argument('--background', '-b', action='store_true',
                                help='Run continuously in background')
    traffic_parser.add_argument('--interval', '-i', type=float, default=5.0,
                                help='Interval between events in background mode (default: 5.0s)')
    traffic_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Show detailed event information')
    traffic_parser.add_argument('--malware', '-m', action='store_true',
                                help='Simulate malware behavior (educational/testing)')

    args = parser.parse_args()

    # No command - show help
    if not args.command:
        print_banner()
        print(f"{Colors.DIM}Usage: spicy-cat <command> [options]{Colors.RESET}")
        print()
        print(f"{Colors.BOLD}Commands:{Colors.RESET}")
        print(f"  {Colors.CYAN}new{Colors.RESET}        Generate new identity")
        print(f"  {Colors.CYAN}show{Colors.RESET}       Display identity details")
        print(f"  {Colors.CYAN}list{Colors.RESET}       List saved identities")
        print(f"  {Colors.CYAN}delete{Colors.RESET}     Remove identity")
        print(f"  {Colors.CYAN}rotate{Colors.RESET}     Switch identities")
        print(f"  {Colors.CYAN}browse{Colors.RESET}     Launch Firefox with identity")
        print(f"  {Colors.CYAN}dashboard{Colors.RESET}  Live status display")
        print(f"  {Colors.CYAN}daemon{Colors.RESET}     Background service")
        print(f"  {Colors.CYAN}export{Colors.RESET}     Export identity data")
        print(f"  {Colors.CYAN}traffic{Colors.RESET}    Generate decoy traffic (9 issue types)")
        print()
        print(f"{Colors.DIM}Use 'spicy-cat <command> --help' for more info{Colors.RESET}")
        print()
        print(f"Faker: {Colors.GREEN if FAKER_AVAILABLE else Colors.YELLOW}{'installed' if FAKER_AVAILABLE else 'not installed'}{Colors.RESET}")
        if not FAKER_AVAILABLE:
            print(f"{Colors.DIM}Install with: pip install faker{Colors.RESET}")
        return

    # Dispatch
    commands = {
        'new': cmd_new,
        'show': cmd_show,
        'list': cmd_list,
        'delete': cmd_delete,
        'rotate': cmd_rotate,
        'browse': cmd_browse,
        'dashboard': cmd_dashboard,
        'daemon': cmd_daemon,
        'export': cmd_export,
        'traffic': cmd_traffic,
    }

    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            print(f"\n{Colors.DIM}Interrupted.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error:{Colors.RESET} {e}")
            if os.environ.get('DEBUG'):
                raise
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
