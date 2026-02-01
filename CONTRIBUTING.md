# Contributing to spicy-cat

## Code of Conduct

Be respectful. This is a project about privacy tools, not a platform for harassment or malicious activity.

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Setup

```bash
git clone https://github.com/yourrepo/spicy-cat.git
cd spicy-cat

# Optional but recommended
pip install faker cryptography

# Run directly (no install needed)
python3 spicy-cat.py --help
```

### Running Tests

```bash
python3 -m pytest tests/ -v
```

Or run individual test files:

```bash
python3 tests/test_chaos.py
python3 tests/test_identity.py
```

## Coding Style

### General Guidelines

- **Python version**: Target Python 3.8+ (use type hints where helpful)
- **Line length**: 100 characters soft limit
- **Imports**: Standard library first, then third-party, then local
- **Docstrings**: Required for public functions and classes

### Naming Conventions

```python
# Functions and variables: snake_case
def generate_identity():
    user_name = "test"

# Classes: PascalCase
class IdentityVault:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_LOCALE = "en_US"
```

### Error Handling

```python
# Preferred: specific exceptions with context
try:
    identity = vault.load(name)
except FileNotFoundError:
    print(f"Identity '{name}' not found")
    return None

# Avoid: bare except or overly broad catching
try:
    ...
except:  # Don't do this
    pass
```

### Comments

- Write self-documenting code when possible
- Add comments for non-obvious logic
- Cat puns are permitted but not required

## Submitting Changes

### Issues

Before starting work:

1. Check existing issues for duplicates
2. For bugs: include reproduction steps, Python version, OS
3. For features: describe the use case, not just the solution

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add or update tests if applicable
5. Run existing tests to ensure nothing breaks
6. Commit with a clear message
7. Push and open a PR

### Commit Messages

```
Short summary (50 chars or less)

Longer description if needed. Explain what and why,
not how (the code shows how).

Fixes #123
```

## Areas of Interest

Contributions welcome in these areas:

- **Locales**: Adding more locale support for identity generation
- **Browser support**: Chromium/Chrome profile management
- **Tests**: Expanding test coverage
- **Documentation**: Improving examples and explanations
- **Fingerprint resistance**: Better browser fingerprinting countermeasures

## What We Won't Accept

- Features that enable harassment or stalking
- Code that contacts external services without user consent
- Backdoors or data exfiltration
- Obfuscated or intentionally unclear code
- Changes that break Python 3.8 compatibility without discussion

## Questions?

Open an issue with the "question" label.
