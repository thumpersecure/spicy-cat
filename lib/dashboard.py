#!/usr/bin/env python3
"""
dashboard.py - Terminal Dashboard for spicy-cat

"Curiosity killed the cat, but satisfaction brought it back."
This dashboard keeps you satisfied with quick identity status.

Minimal, clean, informative. Like a cat's judgment.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# ANSI color codes - because cats see in color (sort of)
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # Foreground
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


# Minimalist spicy-cat ASCII art
SPICY_CAT_LOGO = r"""
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)
"""

SPICY_CAT_SMALL = r"""
 /\_/\
( o.o )
 > ^ <
"""

SPICY_CAT_MINI = r"=^.^="

# ASCII cat animation frames for dashboard
CAT_FRAMES = [
    # Frame 1: Alert cat
    r"""
   /\_/\
  ( o.o )
   > ^ <
  /|   |\
 (_|   |_)
""",
    # Frame 2: Sleepy cat
    r"""
   /\_/\
  ( -.- )
   > ~ <
  /|   |\
 (_|   |_)
""",
    # Frame 3: Curious cat
    r"""
   /\_/\
  ( o.O )
   > ? <
  /|   |\
 (_|   |_)
""",
    # Frame 4: Happy cat
    r"""
   /\_/\
  ( ^.^ )
   > w <
  /|   |\
 (_|   |_)
""",
    # Frame 5: Stretching cat
    r"""
     /\_/\
    ( o.o )
  />  ^   \
 / |     | \
(__/     \__)
""",
    # Frame 6: Grooming cat
    r"""
   /\_/\
  ( >.< )
  _> _ <_
  \|   |/
   |   |
""",
    # Frame 7: Stalking cat
    r"""
  /\_____/\
 /  o   o  \
( ==  ^  == )
 \    ~    /
  \__   __/
""",
    # Frame 8: Loaf cat
    r"""
    /\_/\
   ( o.o )
  __|   |__
 |_________|
""",
    # Frame 9: Tail swish
    r"""
   /\_/\  ~
  ( o.o )/
   > ^ <
  /|   |\
 (_|   |_)
""",
]

# Cat GIF URLs (popular free cat gif services)
CAT_GIF_SOURCES = [
    "https://cataas.com/cat/gif",
    "https://thecatapi.com/api/images/get?format=src&type=gif",
    "https://edgecats.net/",
]

# Pre-rendered "ASCII GIFs" (multi-frame scenes)
CAT_SCENES = {
    'hunting': [
        "   /\\_/\\      ...      ~>))'>",
        "  ( o.o )    ....     ~>))'>",
        " ( ( > ^))  .....    ~>))'>",
        "   \\(_|_)/    ..    ~=))'>  POUNCE!",
    ],
    'sleeping': [
        "   /\\_/\\   z",
        "  ( -.- )  zZ",
        "   > ~ <  zZz",
        "  /|   |\\ zZzZ",
    ],
    'walking': [
        "      /\\_/\\",
        "     ( o.o )",
        " /\\__/    \\__/\\",
        "(_/          \\_)",
    ],
}


def get_random_cat_gif_url() -> str:
    """Get a URL for a random cat GIF."""
    import random
    return random.choice(CAT_GIF_SOURCES)


def get_cat_frame(frame_index: int) -> str:
    """Get a specific cat animation frame."""
    return CAT_FRAMES[frame_index % len(CAT_FRAMES)]


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def move_cursor(row: int, col: int):
    """Move cursor to position."""
    print(f'\033[{row};{col}H', end='')


def hide_cursor():
    """Hide the cursor."""
    print('\033[?25l', end='')


def show_cursor():
    """Show the cursor."""
    print('\033[?25h', end='')


def get_terminal_size() -> tuple:
    """Get terminal dimensions."""
    try:
        columns, rows = os.get_terminal_size()
        return rows, columns
    except OSError:
        return 24, 80  # Fallback


class StatusIndicator:
    """Compact status indicators."""

    @staticmethod
    def status(active: bool) -> str:
        if active:
            return f"{Colors.BRIGHT_GREEN}●{Colors.RESET}"
        return f"{Colors.BRIGHT_BLACK}○{Colors.RESET}"

    @staticmethod
    def level(value: float, width: int = 10) -> str:
        """Create a level bar."""
        filled = int(value * width)
        empty = width - filled
        bar = f"{Colors.BRIGHT_CYAN}{'█' * filled}{Colors.BRIGHT_BLACK}{'░' * empty}{Colors.RESET}"
        return bar

    @staticmethod
    def age_indicator(created: datetime) -> str:
        """Show identity age with color coding."""
        age = datetime.now() - created
        hours = age.total_seconds() / 3600

        if hours < 1:
            color = Colors.BRIGHT_GREEN
            text = f"{int(age.total_seconds() / 60)}m"
        elif hours < 24:
            color = Colors.BRIGHT_YELLOW
            text = f"{int(hours)}h"
        elif hours < 168:  # 7 days
            color = Colors.YELLOW
            text = f"{int(hours / 24)}d"
        else:
            color = Colors.BRIGHT_RED
            text = f"{int(hours / 168)}w"

        return f"{color}{text}{Colors.RESET}"


class Dashboard:
    """
    Main dashboard display.

    Cats are minimalists. So is this dashboard.
    """

    def __init__(self, identity=None, refresh_interval: float = 1.0, show_cat: bool = True):
        self.identity = identity
        self.refresh_interval = refresh_interval
        self.running = False
        self.start_time = datetime.now()
        self.show_cat = show_cat
        self.cat_frame_index = 0
        self.cat_gif_url = get_random_cat_gif_url()  # Cache one for session

    def set_identity(self, identity):
        """Set the current identity to display."""
        self.identity = identity

    def _format_header(self, width: int) -> List[str]:
        """Format the header section."""
        lines = []

        # Animated cat (cycles through frames)
        if self.show_cat:
            cat_frame = get_cat_frame(self.cat_frame_index)
            lines.append(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}")
            for line in cat_frame.strip().split('\n'):
                lines.append(line)
            lines.append(f"{Colors.RESET}")

        lines.append(f"{Colors.BRIGHT_CYAN}spicy-cat{Colors.RESET} {Colors.DIM}v1.0.0{Colors.RESET}")
        lines.append(f"{Colors.BRIGHT_BLACK}{'─' * min(40, width)}{Colors.RESET}")

        # Random cat GIF URL
        lines.append(f"{Colors.DIM}Cat GIF:{Colors.RESET} {Colors.CYAN}{self.cat_gif_url}{Colors.RESET}")
        lines.append("")

        return lines

    def _format_identity(self, width: int) -> List[str]:
        """Format the identity section."""
        lines = []

        if not self.identity:
            lines.append(f"{Colors.BRIGHT_BLACK}No identity loaded{Colors.RESET}")
            lines.append(f"{Colors.DIM}Use 'spicy-cat new' to generate one{Colors.RESET}")
            return lines

        i = self.identity

        # Identity header
        lines.append(f"{Colors.BOLD}{Colors.WHITE}WHO YOU ARE{Colors.RESET}")
        lines.append("")

        # Name and age
        lines.append(f"{Colors.BRIGHT_WHITE}{i.full_name}{Colors.RESET} {Colors.DIM}({i.age}){Colors.RESET}")

        # Occupation
        lines.append(f"{Colors.CYAN}{i.occupation}{Colors.RESET}")

        # Location
        lines.append(f"{Colors.YELLOW}📍 {i.location}, {i.country}{Colors.RESET}")

        lines.append("")

        # Digital footprint
        lines.append(f"{Colors.BRIGHT_BLACK}─── Digital ───{Colors.RESET}")
        lines.append(f"{Colors.DIM}Email:{Colors.RESET}    {Colors.WHITE}{i.email}{Colors.RESET}")
        lines.append(f"{Colors.DIM}Username:{Colors.RESET} {Colors.WHITE}@{i.username}{Colors.RESET}")
        lines.append(f"{Colors.DIM}Phone:{Colors.RESET}    {Colors.WHITE}{i.phone}{Colors.RESET}")

        lines.append("")

        # Interests (truncated)
        interests_str = ', '.join(i.interests[:3])
        if len(i.interests) > 3:
            interests_str += f" +{len(i.interests) - 3}"
        lines.append(f"{Colors.DIM}Interests:{Colors.RESET} {Colors.GREEN}{interests_str}{Colors.RESET}")

        return lines

    def _format_status(self, width: int) -> List[str]:
        """Format the status section."""
        lines = []
        lines.append("")
        lines.append(f"{Colors.BRIGHT_BLACK}{'─' * min(40, width)}{Colors.RESET}")

        if self.identity:
            # Identity age
            age_ind = StatusIndicator.age_indicator(self.identity.created_at)
            lines.append(f"{Colors.DIM}Identity age:{Colors.RESET} {age_ind}")

            # Behavior state
            behavior = self.identity.behavior.get_current_state()
            style = behavior['writing_style']
            activity = behavior['activity_state']
            mood = behavior['mood']

            style_color = {
                'formal': Colors.BLUE,
                'casual': Colors.GREEN,
                'terse': Colors.YELLOW,
                'verbose': Colors.MAGENTA,
                'gen_z': Colors.CYAN,
                'academic': Colors.BRIGHT_BLUE,
                'technical': Colors.BRIGHT_WHITE,
                'friendly': Colors.BRIGHT_GREEN,
                'sarcastic': Colors.BRIGHT_MAGENTA,
            }.get(style, Colors.WHITE)

            lines.append(f"{Colors.DIM}Style:{Colors.RESET} {style_color}{style}{Colors.RESET}")
            lines.append(f"{Colors.DIM}Activity:{Colors.RESET} {Colors.WHITE}{activity}{Colors.RESET}")
            lines.append(f"{Colors.DIM}Mood:{Colors.RESET} {Colors.WHITE}{mood}{Colors.RESET}")

        # Session info
        session_duration = datetime.now() - self.start_time
        session_str = str(session_duration).split('.')[0]  # Remove microseconds
        lines.append(f"{Colors.DIM}Session:{Colors.RESET} {Colors.BRIGHT_BLACK}{session_str}{Colors.RESET}")

        # Current time
        now = datetime.now().strftime("%H:%M:%S")
        lines.append(f"{Colors.DIM}Time:{Colors.RESET} {Colors.BRIGHT_BLACK}{now}{Colors.RESET}")

        return lines

    def _format_footer(self, width: int) -> List[str]:
        """Format the footer section."""
        lines = []
        lines.append("")
        lines.append(f"{Colors.BRIGHT_BLACK}{'─' * min(40, width)}{Colors.RESET}")
        lines.append(f"{Colors.DIM}[q]Quit [r]Rotate [n]New [c]Cat GIF [g]Toggle Cat [?]Help{Colors.RESET}")
        return lines

    def render(self) -> str:
        """Render the full dashboard."""
        rows, cols = get_terminal_size()
        width = min(cols, 50)

        all_lines = []
        all_lines.extend(self._format_header(width))
        all_lines.extend(self._format_identity(width))
        all_lines.extend(self._format_status(width))
        all_lines.extend(self._format_footer(width))

        return '\n'.join(all_lines)

    def display_once(self):
        """Display the dashboard once."""
        clear_screen()
        print(self.render())

    def run(self):
        """Run the interactive dashboard."""
        import select
        import termios
        import tty

        self.running = True

        # Save terminal settings
        try:
            old_settings = termios.tcgetattr(sys.stdin)
        except termios.error:
            # Not a TTY, just display once
            self.display_once()
            return

        try:
            # Set terminal to raw mode for key capture
            tty.setcbreak(sys.stdin.fileno())
            hide_cursor()

            while self.running:
                self.display_once()

                # Advance cat animation frame
                self.cat_frame_index = (self.cat_frame_index + 1) % len(CAT_FRAMES)

                # Wait for input or timeout
                readable, _, _ = select.select([sys.stdin], [], [], self.refresh_interval)

                if readable:
                    key = sys.stdin.read(1)

                    if key.lower() == 'q':
                        self.running = False
                    elif key.lower() == 'r':
                        # Signal rotation request
                        print(f"\n{Colors.YELLOW}Rotating identity...{Colors.RESET}")
                        time.sleep(0.5)
                    elif key.lower() == 'n':
                        # Signal new identity request
                        print(f"\n{Colors.CYAN}Generating new identity...{Colors.RESET}")
                        time.sleep(0.5)
                    elif key.lower() == 'c':
                        # New random cat GIF
                        self.cat_gif_url = get_random_cat_gif_url()
                    elif key.lower() == 'g':
                        # Toggle cat animation
                        self.show_cat = not self.show_cat
                    elif key == '?':
                        self._show_help()

        except KeyboardInterrupt:
            pass
        finally:
            # Restore terminal settings
            show_cursor()
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except termios.error:
                pass
            clear_screen()

    def _show_help(self):
        """Display help screen."""
        clear_screen()
        print(f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}spicy-cat Dashboard Help{Colors.RESET}

{Colors.BOLD}Navigation:{Colors.RESET}
  {Colors.YELLOW}q{Colors.RESET}  Quit dashboard
  {Colors.YELLOW}r{Colors.RESET}  Rotate to next saved identity
  {Colors.YELLOW}n{Colors.RESET}  Generate new identity
  {Colors.YELLOW}c{Colors.RESET}  Get new random cat GIF URL
  {Colors.YELLOW}g{Colors.RESET}  Toggle cat animation on/off
  {Colors.YELLOW}?{Colors.RESET}  Show this help

{Colors.BOLD}Status Indicators:{Colors.RESET}
  {Colors.BRIGHT_GREEN}●{Colors.RESET}  Active/Online
  {Colors.BRIGHT_BLACK}○{Colors.RESET}  Inactive/Offline

{Colors.BOLD}Identity Age Colors:{Colors.RESET}
  {Colors.BRIGHT_GREEN}Green{Colors.RESET}   Fresh (< 1 hour)
  {Colors.BRIGHT_YELLOW}Yellow{Colors.RESET}  Recent (< 24 hours)
  {Colors.YELLOW}Orange{Colors.RESET}  Aging (< 1 week)
  {Colors.BRIGHT_RED}Red{Colors.RESET}     Old (> 1 week, consider rotating)

{Colors.BOLD}Writing Styles (9 total):{Colors.RESET}
  formal, casual, terse, verbose, gen_z
  academic, technical, friendly, sarcastic

{Colors.DIM}Press any key to continue...{Colors.RESET}
""")
        sys.stdin.read(1)


class CompactDisplay:
    """
    One-line compact display for embedding in prompts/status bars.

    For cats who prefer the TL;DR version.
    """

    def __init__(self, identity=None):
        self.identity = identity

    def set_identity(self, identity):
        self.identity = identity

    def render(self) -> str:
        """Render compact one-liner."""
        if not self.identity:
            return f"{SPICY_CAT_MINI} {Colors.DIM}no identity{Colors.RESET}"

        i = self.identity
        age = StatusIndicator.age_indicator(i.created_at)

        return f"{SPICY_CAT_MINI} {Colors.BRIGHT_WHITE}{i.full_name}{Colors.RESET} | {Colors.CYAN}{i.occupation}{Colors.RESET} | {age}"


def print_identity_card(identity) -> str:
    """Print a formatted identity card."""
    i = identity
    card = f"""
{Colors.BRIGHT_BLACK}╭{'─' * 48}╮{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.BRIGHT_MAGENTA}{SPICY_CAT_MINI}{Colors.RESET}  {Colors.BOLD}{Colors.WHITE}{i.full_name}{Colors.RESET}{' ' * (48 - 7 - len(i.full_name))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}       {Colors.DIM}Age {i.age} • {i.location}{Colors.RESET}{' ' * max(0, 48 - 13 - len(str(i.age)) - len(i.location))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}├{'─' * 48}┤{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.CYAN}Occupation:{Colors.RESET} {i.occupation}{' ' * max(0, 36 - len(i.occupation))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.YELLOW}Email:{Colors.RESET}      {i.email}{' ' * max(0, 36 - len(i.email))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.GREEN}Username:{Colors.RESET}   @{i.username}{' ' * max(0, 35 - len(i.username))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.MAGENTA}Phone:{Colors.RESET}      {i.phone}{' ' * max(0, 36 - len(i.phone))}{Colors.BRIGHT_BLACK}│{Colors.RESET}
{Colors.BRIGHT_BLACK}╰{'─' * 48}╯{Colors.RESET}
"""
    return card


if __name__ == "__main__":
    # Demo
    print(f"{Colors.BRIGHT_MAGENTA}")
    print(SPICY_CAT_LOGO)
    print(f"{Colors.RESET}")

    print("Dashboard demo - press Ctrl+C to exit\n")

    # Create a mock identity for demo
    try:
        from .identity import quick_identity
        identity = quick_identity("demo_seed")
        dashboard = Dashboard(identity)
        dashboard.display_once()
    except ImportError:
        print("Run from main spicy-cat CLI to see full demo")
        dashboard = Dashboard()
        dashboard.display_once()
