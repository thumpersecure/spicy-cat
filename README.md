# 🐱 spicy-cat

```
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

"On the internet, nobody knows you're a cat."
```

<div align="center">

**Create and manage alternate digital identities for privacy protection, OSINT defense, and reducing your digital footprint.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange?logo=linux&logoColor=white)](#installation)
[![Meow](https://img.shields.io/badge/Cats-Approved-ff69b4)](#)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage](#-usage) • [How It Works](#-how-it-works) • [FAQ](#-faq)

</div>

---

## 🎯 What Is This?

**spicy-cat** is a privacy tool that helps you:

- **Generate complete fake identities** with realistic details
- **Defeat people search engines** and data brokers
- **Protect against stylometry** (writing style fingerprinting)
- **Create convincing online personas** for OSINT defense
- **Reduce your digital footprint** while browsing
- **Safely conduct research** without exposing your real identity

> *"Curiosity killed the cat, but anonymity brought it back."*

---

## ✨ Features

### 🎭 **Identity Generation**
- Full personas: name, age, location, occupation, backstory
- Email patterns and username styles
- Localized data (US, UK, Germany, etc.) via [Faker](https://faker.readthedocs.io/)
- Chaotic randomization for organic, non-patterned output

### 🧠 **Behavioral Camouflage**
- **Markov-based writing styles** to defeat stylometry
- **Activity patterns** that mimic real human behavior
- **Identity drift** - subtle, natural evolution over time
- Multiple personality modes: formal, casual, terse, verbose, gen-z

### 🔮 **Chaos Engine**
- Built on **Lorenz attractors** and **logistic maps**
- Generates unpredictable but reproducible patterns
- Creates organic-looking behavioral noise
- Avoids algorithmic fingerprints

### 🦊 **Browser Integration**
- Automatic Firefox profile creation
- Privacy-hardened settings pre-configured
- Optional Tor routing
- Isolated browsing per identity

### 📊 **Dashboard**
- Live terminal UI showing "who you are"
- Identity age and rotation suggestions
- Behavioral state monitoring
- Compact mode for shell prompts

### 😈 **Daemon Mode**
- Background service for persistent identity
- Scheduled rotation
- Unix socket for IPC
- Set it and forget it

---

## 📦 Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/yourrepo/spicy-cat.git
cd spicy-cat
./spicy-cat.sh install
```

### Manual Install

```bash
# Clone
git clone https://github.com/yourrepo/spicy-cat.git
cd spicy-cat

# Install dependencies
pip install faker cryptography  # Optional but recommended

# Run directly
python3 spicy-cat.py --help
```

### Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| Python 3.8+ | ✅ Yes | Core runtime |
| faker | ⭐ Recommended | Rich, localized identity data |
| cryptography | 💡 Optional | Secure identity storage |
| Firefox | 💡 Optional | Browser profile feature |
| Tor | 💡 Optional | Anonymous browsing |

Install everything on Debian/Ubuntu:

```bash
./spicy-cat.sh deps
# Or manually:
sudo apt install python3 python3-pip firefox tor
pip install faker cryptography
```

---

## 🚀 Quick Start

```bash
# Generate your first identity
spicy-cat new

# See who you are
spicy-cat show

# Launch anonymous browser
spicy-cat browse --tor

# Live dashboard
spicy-cat dashboard
```

That's it. You're now someone else. =^.^=

---

## 📖 Usage

### Core Commands

```
 /\_/\
( o.o )  spicy-cat v1.0.0 "Curious Whiskers"
 > ^ <   The purrfect anonymity tool

Commands:
  new        Generate new identity
  show       Display identity details
  list       List saved identities
  delete     Remove identity
  rotate     Switch identities
  browse     Launch Firefox with identity
  dashboard  Live status display
  daemon     Background service
  export     Export identity data
```

### Generate Identity

```bash
# Basic (uses en_US locale)
spicy-cat new

# German identity
spicy-cat new --locale de_DE

# Custom name, temporary (not saved)
spicy-cat new --name "work_alias" --temp

# French Canadian
spicy-cat new --locale fr_CA --name "montreal_persona"
```

### View Identities

```bash
# Show current/default identity
spicy-cat show

# Show specific identity
spicy-cat show work_alias

# List all saved identities
spicy-cat list
```

### Browser with Identity

```bash
# Launch Firefox with identity profile
spicy-cat browse

# Use specific identity
spicy-cat browse work_alias

# Route through Tor
spicy-cat browse --tor

# Open specific URL
spicy-cat browse --url "https://example.com"
```

### Dashboard

```bash
# Interactive dashboard
spicy-cat dashboard

# Specific identity
spicy-cat dashboard work_alias
```

**Dashboard Controls:**
| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Rotate identity |
| `n` | New identity |
| `?` | Help |

### Background Daemon

```bash
# Start daemon
spicy-cat daemon start

# Check status
spicy-cat daemon status

# Stop daemon
spicy-cat daemon stop
```

### Export Identity

```bash
# Full JSON export
spicy-cat export work_alias

# Minimal text format
spicy-cat export work_alias --format minimal

# CSV (for spreadsheets)
spicy-cat export work_alias --format csv
```

---

## 🔬 How It Works

### The Chaos Engine

Unlike typical random generators, spicy-cat uses **deterministic chaos**:

```
┌─────────────────────────────────────────────────────┐
│                  LOGISTIC MAP                       │
│                                                     │
│  x[n+1] = r × x[n] × (1 - x[n])   where r ≈ 3.9999 │
│                                                     │
│  Deterministic but unpredictable. Same seed =      │
│  same identity, but no discernible pattern.        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                LORENZ ATTRACTOR                     │
│                                                     │
│        dx/dt = σ(y - x)                            │
│        dy/dt = x(ρ - z) - y                        │
│        dz/dt = xy - βz                             │
│                                                     │
│  The butterfly effect. Creates organic noise that  │
│  looks human, not algorithmic.                     │
└─────────────────────────────────────────────────────┘
```

### Markov Behavioral Models

```
Writing Styles:
┌──────────┐     ┌──────────┐     ┌──────────┐
│  FORMAL  │◄───►│  CASUAL  │◄───►│  TERSE   │
└──────────┘     └──────────┘     └──────────┘
     ▲               ▲               ▲
     │               │               │
     ▼               ▼               ▼
┌──────────┐     ┌──────────┐
│ VERBOSE  │◄───►│  GEN_Z   │
└──────────┘     └──────────┘

Each style has:
- Contraction preferences
- Sentence length targets
- Vocabulary tier
- Filler word patterns
- Punctuation density
```

### Activity Patterns

```
Night Owl Profile:
                    ▂▄▆█████▆▄▂
    ░░░░░░░░░░░░████████████████████░░░░░░░
    00:00     06:00     12:00     18:00     24:00

Early Bird Profile:
    ████████████▆▄▂░░░░░░░░░░░░░░░░░░░░░░░░
    00:00     06:00     12:00     18:00     24:00
```

### Identity Storage

```
~/.spicy-cat/
├── identities/           # Encrypted identity files
│   ├── work_alias.json
│   └── travel_persona.json
├── browsers/             # Browser profile registry
│   └── profiles.json
├── daemon.pid            # Background service PID
├── daemon.sock           # Unix socket for IPC
└── state.json            # Current state
```

---

## 🛡️ Security Considerations

### What spicy-cat DOES protect against:
- ✅ People search engines and data brokers
- ✅ Casual social media correlation
- ✅ Basic stylometry (writing fingerprinting)
- ✅ Session tracking across sites

### What spicy-cat does NOT fully protect against:
- ⚠️ Advanced browser fingerprinting (use Tor Browser for that)
- ⚠️ Network-level surveillance (use VPN/Tor)
- ⚠️ Sophisticated adversaries (nation-states, etc.)
- ⚠️ You accidentally revealing your real info

### Best Practices

```
    /\_/\
   ( ^.^ )  Pro Tips from a Paranoid Cat:
    > ~ <

1. Use Tor Browser for high-stakes anonymity
2. Never mix real and fake identities
3. Keep persona details consistent
4. Rotate identities periodically
5. Don't access personal accounts while in persona
6. Use different devices/VMs for different identities
7. Remember: the tool is only as good as your opsec
```

---

## ❓ FAQ

<details>
<summary><strong>Why "spicy-cat"?</strong></summary>

Cats are mysterious, independent, and notoriously hard to track. They have nine lives - you can have nine identities. Also, spicy things are hard to handle. Like your new personas.

</details>

<details>
<summary><strong>Is this legal?</strong></summary>

Creating fictional personas for privacy is legal. Using them for fraud, impersonation, or illegal activities is not. Don't be evil.

</details>

<details>
<summary><strong>Why Faker as default?</strong></summary>

Faker provides rich, localized data across many countries. A German identity should have German-sounding names and German cities. The builtin fallback works but is US-centric.

</details>

<details>
<summary><strong>Why chaos mathematics?</strong></summary>

Standard PRNGs produce patterns that can potentially be reverse-engineered. Chaotic systems are deterministic (reproducible from seed) but practically unpredictable. They also produce more "organic" looking patterns.

</details>

<details>
<summary><strong>Can I contribute?</strong></summary>

Yes! Pull requests welcome. Areas of interest:
- More locales
- Browser fingerprint resistance
- Additional browser support
- Mobile companion app

</details>

---

## 🗺️ Roadmap

- [ ] **v1.1** - Chromium/Chrome profile support
- [ ] **v1.2** - Social media persona templates
- [ ] **v1.3** - Profile photo generation (AI)
- [ ] **v1.4** - Keyboard timing simulation
- [ ] **v2.0** - GUI application

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

Built with:
- [Faker](https://faker.readthedocs.io/) - Fake data generation
- Python standard library - Keeping it minimal
- Lorenz, Rössler, and other chaos theory pioneers
- Cats everywhere - For inspiration

---

<div align="center">

```
    /\_____/\
   /  o   o  \    "Stay curious. Stay anonymous."
  ( ==  ^  == )
   )  ~~~  (
  (         )
   \       /
    \_____/

        =^.^=
```

**[Back to Top](#-spicy-cat)**

</div>
