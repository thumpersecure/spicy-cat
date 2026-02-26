#!/usr/bin/env python3
"""
identity.py - Identity Generation for spicy-cat

"A cat has absolute emotional honesty: human beings, for one reason
or another, may hide their feelings, but a cat does not."
- Ernest Hemingway

This module creates completely fabricated humans. The opposite of cats.
"""

import json
import os
import hashlib
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import our chaos engine and Markov models
from .chaos import LogisticMap, LorenzAttractor, IdentityDrift
from .markov import BehaviorStateMachine

# Try to import Faker (preferred), fall back to built-in data
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("[spicy-cat] Faker not installed, using built-in data. Install with: pip install faker")


class BuiltinDataProvider:
    """
    Fallback data provider when Faker isn't available.
    Less variety, but zero dependencies.
    """

    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Alex", "Jordan", "Taylor", "Morgan",
        "Casey", "Riley", "Avery", "Quinn", "Sage", "River", "Skylar", "Dakota",
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    ]

    CITIES = [
        ("New York", "NY", "USA"), ("Los Angeles", "CA", "USA"), ("Chicago", "IL", "USA"),
        ("Houston", "TX", "USA"), ("Phoenix", "AZ", "USA"), ("Philadelphia", "PA", "USA"),
        ("San Antonio", "TX", "USA"), ("San Diego", "CA", "USA"), ("Dallas", "TX", "USA"),
        ("Austin", "TX", "USA"), ("Seattle", "WA", "USA"), ("Denver", "CO", "USA"),
        ("Boston", "MA", "USA"), ("Portland", "OR", "USA"), ("Atlanta", "GA", "USA"),
        ("Miami", "FL", "USA"), ("Nashville", "TN", "USA"), ("Detroit", "MI", "USA"),
        ("Minneapolis", "MN", "USA"), ("Charlotte", "NC", "USA"),
        ("Toronto", "ON", "Canada"), ("Vancouver", "BC", "Canada"), ("Montreal", "QC", "Canada"),
        ("London", "", "UK"), ("Manchester", "", "UK"), ("Birmingham", "", "UK"),
        ("Sydney", "NSW", "Australia"), ("Melbourne", "VIC", "Australia"),
        ("Berlin", "", "Germany"), ("Munich", "", "Germany"),
    ]

    OCCUPATIONS = [
        "Software Developer", "Data Analyst", "Graphic Designer", "Marketing Manager",
        "Teacher", "Nurse", "Accountant", "Sales Representative", "Project Manager",
        "Customer Service Representative", "Administrative Assistant", "Consultant",
        "Writer", "Photographer", "Electrician", "Plumber", "Chef", "Librarian",
        "Research Scientist", "Financial Analyst", "UX Designer", "DevOps Engineer",
        "Product Manager", "Business Analyst", "HR Specialist", "Social Media Manager",
        "Content Creator", "Freelance Artist", "IT Support Specialist", "Entrepreneur",
    ]

    INTERESTS = [
        "hiking", "photography", "cooking", "gaming", "reading", "travel", "music",
        "fitness", "art", "movies", "technology", "gardening", "yoga", "cycling",
        "writing", "podcasts", "meditation", "coffee", "wine", "craft beer",
        "board games", "camping", "fishing", "woodworking", "knitting", "chess",
        "astronomy", "birdwatching", "volunteering", "languages", "history", "science",
    ]

    EMAIL_PROVIDERS = [
        "gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "icloud.com",
        "fastmail.com", "tutanota.com", "mail.com", "zoho.com", "aol.com",
    ]

    def __init__(self, chaos: LogisticMap):
        self.chaos = chaos

    def first_name(self) -> str:
        return self.chaos.next_choice(self.FIRST_NAMES)

    def last_name(self) -> str:
        return self.chaos.next_choice(self.LAST_NAMES)

    def city(self) -> Tuple[str, str, str]:
        return self.chaos.next_choice(self.CITIES)

    def job(self) -> str:
        return self.chaos.next_choice(self.OCCUPATIONS)

    def interests(self, count: int = 4) -> List[str]:
        selected = []
        available = self.INTERESTS.copy()
        for _ in range(min(count, len(available))):
            choice = self.chaos.next_choice(available)
            selected.append(choice)
            available.remove(choice)
        return selected

    def email_provider(self) -> str:
        return self.chaos.next_choice(self.EMAIL_PROVIDERS)

    def date_of_birth(self, min_age: int = 18, max_age: int = 65) -> datetime:
        age = self.chaos.next_int(min_age, max_age)
        days_offset = self.chaos.next_int(0, 364)
        return datetime.now() - timedelta(days=age*365 + days_offset)


class FakerProvider:
    """
    Faker-based data provider for rich, localized identity data.
    The cat's meow of fake data generation.
    """

    def __init__(self, chaos: LogisticMap, locale: str = 'en_US'):
        self.chaos = chaos
        self.faker = Faker(locale)
        # Seed Faker with our chaotic seed for reproducibility
        Faker.seed(int(chaos.next() * 2**31))

    def first_name(self) -> str:
        return self.faker.first_name()

    def last_name(self) -> str:
        return self.faker.last_name()

    def city(self) -> Tuple[str, str, str]:
        return (self.faker.city(), self.faker.state_abbr() if hasattr(self.faker, 'state_abbr') else "",
                self.faker.current_country())

    def job(self) -> str:
        return self.faker.job()

    def interests(self, count: int = 4) -> List[str]:
        # Faker doesn't have interests, use builtin
        builtin = BuiltinDataProvider(self.chaos)
        return builtin.interests(count)

    def email_provider(self) -> str:
        return self.faker.free_email_domain()

    def date_of_birth(self, min_age: int = 18, max_age: int = 65) -> datetime:
        return self.faker.date_of_birth(minimum_age=min_age, maximum_age=max_age)

    def phone_number(self) -> str:
        return self.faker.phone_number()

    def address(self) -> str:
        return self.faker.address()

    def company(self) -> str:
        return self.faker.company()

    def bio(self) -> str:
        return self.faker.paragraph(nb_sentences=3)


class Identity:
    """
    A complete fabricated identity.

    Nine lives, nine different people. That's the cat way.
    """

    def __init__(self, seed: str, locale: str = 'en_US'):
        self.seed = seed
        self.locale = locale
        self.created_at = datetime.now()
        self.chaos = LogisticMap(seed)
        self.lorenz = LorenzAttractor(seed)
        self.drift = IdentityDrift(seed)

        # Choose data provider
        if FAKER_AVAILABLE:
            self.provider = FakerProvider(self.chaos, locale)
        else:
            self.provider = BuiltinDataProvider(self.chaos)

        # Generate core identity
        self._generate()

    def _generate(self):
        """Generate all identity attributes."""
        p = self.provider

        # Core identity
        self.first_name = p.first_name()
        self.last_name = p.last_name()
        self.full_name = f"{self.first_name} {self.last_name}"

        # Location
        city_data = p.city()
        self.city = city_data[0]
        self.state = city_data[1]
        self.country = city_data[2]
        self.location = f"{self.city}, {self.state}" if self.state else self.city

        # Demographics
        dob = p.date_of_birth(min_age=18, max_age=65)
        # Ensure dob is a datetime (Faker returns date, builtin returns datetime)
        if hasattr(dob, 'hour'):
            self.birth_date = dob
        else:
            self.birth_date = datetime.combine(dob, datetime.min.time())
        self.age = (datetime.now() - self.birth_date).days // 365

        # Professional
        self.occupation = p.job()
        self.interests = p.interests(self.chaos.next_int(3, 6))

        # Digital presence
        self.email = self._generate_email()
        self.username = self._generate_username()

        # Extended info (Faker-only)
        if FAKER_AVAILABLE and isinstance(self.provider, FakerProvider):
            self.phone = self.provider.phone_number()
            self.address = self.provider.address()
            self.company = self.provider.company()
            self.bio = self.provider.bio()
        else:
            self.phone = self._generate_phone()
            self.address = f"{self.chaos.next_int(100, 9999)} {self.chaos.next_choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine', 'Elm'])} St"
            self.company = None
            self.bio = None

        # Behavioral profile
        writing_style = self.chaos.next_choice(['casual', 'formal', 'terse', 'verbose', 'gen_z'])
        activity_profile = self.chaos.next_choice(['early_bird', 'night_owl', 'nine_to_five', 'erratic'])
        self.behavior = BehaviorStateMachine(self.seed, writing_style, activity_profile)

        # Backstory elements
        self.backstory = self._generate_backstory()

    def _generate_email(self) -> str:
        """Generate realistic email based on name."""
        patterns = [
            lambda f, l: f"{f.lower()}.{l.lower()}",
            lambda f, l: f"{f.lower()}{l.lower()}",
            lambda f, l: f"{f[0].lower()}{l.lower()}",
            lambda f, l: f"{f.lower()}{l[0].lower()}",
            lambda f, l: f"{f.lower()}_{l.lower()}",
            lambda f, l: f"{l.lower()}.{f.lower()}",
        ]

        pattern = self.chaos.next_choice(patterns)
        base = pattern(self.first_name, self.last_name)

        # Maybe add numbers
        if self.chaos.next() > 0.6:
            base += str(self.chaos.next_int(1, 99))

        provider = self.provider.email_provider() if FAKER_AVAILABLE else self.chaos.next_choice(BuiltinDataProvider.EMAIL_PROVIDERS)
        return f"{base}@{provider}"

    def _generate_username(self) -> str:
        """Generate username for social platforms."""
        patterns = [
            lambda: f"{self.first_name.lower()}{self.chaos.next_int(10, 999)}",
            lambda: f"{self.first_name.lower()}_{self.last_name.lower()}",
            lambda: f"the_{self.first_name.lower()}",
            lambda: f"{self.interests[0].replace(' ', '')}{self.chaos.next_int(1, 99)}" if self.interests else "user",
            lambda: f"{self.first_name.lower()}{self.birth_date.strftime('%y')}",
            lambda: f"real_{self.first_name.lower()}",
        ]
        return self.chaos.next_choice(patterns)()

    def _generate_phone(self) -> str:
        """Generate phone number (fallback when Faker unavailable)."""
        area = self.chaos.next_int(200, 999)
        prefix = self.chaos.next_int(200, 999)
        line = self.chaos.next_int(1000, 9999)
        return f"({area}) {prefix}-{line}"

    def _generate_backstory(self) -> Dict:
        """Generate backstory elements."""
        backstory = {
            'grew_up_in': self.chaos.next_choice([
                'small town', 'suburbs', 'city', 'rural area', 'coast'
            ]),
            'education': self.chaos.next_choice([
                'high school', 'some college', 'bachelor\'s degree',
                'master\'s degree', 'self-taught', 'trade school'
            ]),
            'personality_traits': [
                self.chaos.next_choice(['introverted', 'extroverted', 'ambiverted']),
                self.chaos.next_choice(['analytical', 'creative', 'practical']),
                self.chaos.next_choice(['optimistic', 'realistic', 'cautious']),
            ],
        }
        return backstory

    def to_dict(self) -> Dict:
        """Export identity as dictionary."""
        return {
            'seed': self.seed,
            'locale': self.locale,
            'created_at': self.created_at.isoformat(),
            'core': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'full_name': self.full_name,
                'age': self.age,
                'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            },
            'location': {
                'city': self.city,
                'state': self.state,
                'country': self.country,
                'display': self.location,
            },
            'professional': {
                'occupation': self.occupation,
                'company': self.company,
                'interests': self.interests,
            },
            'digital': {
                'email': self.email,
                'username': self.username,
                'phone': self.phone,
            },
            'extended': {
                'address': self.address,
                'bio': self.bio,
                'backstory': self.backstory,
            },
            'behavior': self.behavior.serialize(),
        }

    def to_json(self, pretty: bool = True) -> str:
        """Export identity as JSON string."""
        return json.dumps(self.to_dict(), indent=2 if pretty else None)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Identity':
        """Restore identity from dictionary."""
        identity = cls(data['seed'], data.get('locale', 'en_US'))
        # Overwrite with saved data
        identity.first_name = data['core']['first_name']
        identity.last_name = data['core']['last_name']
        identity.full_name = data['core']['full_name']
        identity.age = data['core']['age']
        identity.birth_date = datetime.strptime(data['core']['birth_date'], '%Y-%m-%d')

        identity.city = data['location']['city']
        identity.state = data['location']['state']
        identity.country = data['location']['country']
        identity.location = data['location']['display']

        identity.occupation = data['professional']['occupation']
        identity.company = data['professional'].get('company')
        identity.interests = data['professional']['interests']

        identity.email = data['digital']['email']
        identity.username = data['digital']['username']
        identity.phone = data['digital']['phone']

        identity.address = data['extended'].get('address')
        identity.bio = data['extended'].get('bio')
        identity.backstory = data['extended'].get('backstory', {})

        if 'behavior' in data:
            identity.behavior = BehaviorStateMachine.deserialize(data['behavior'])

        identity.created_at = datetime.fromisoformat(data['created_at'])
        return identity

    def summary(self) -> str:
        """Get a brief summary of the identity."""
        return f"""
{self.full_name} ({self.age})
{self.occupation}
{self.location}, {self.country}
{self.email}
Interests: {', '.join(self.interests[:3])}
"""

    def apply_drift(self, available_interests: List[str] = None, nearby_cities: List[str] = None):
        """Apply natural drift to identity over time."""
        interest_pool = (
            available_interests
            if available_interests is not None
            else BuiltinDataProvider.INTERESTS
        )
        self.interests = self.drift.drift_interest(self.interests, interest_pool)
        if nearby_cities:
            old_city = self.city
            self.city = self.drift.drift_location(self.city, nearby_cities)
            if self.city != old_city:
                self.location = f"{self.city}, {self.state}" if self.state else self.city


class IdentityVault:
    """
    Secure storage for multiple identities.

    Like a cat's many hiding spots, but for personas.
    """

    def __init__(self, vault_path: str = None, passphrase: str = None):
        if vault_path is None:
            vault_path = os.path.expanduser("~/.spicy-cat/identities")
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.passphrase = passphrase
        self.identities: Dict[str, Identity] = {}

    def _get_identity_path(self, name: str) -> Path:
        """Get file path for an identity."""
        safe_name = "".join(c for c in name if c.isalnum() or c in '-_')
        return self.vault_path / f"{safe_name}.json"

    def _encrypt(self, data: str) -> str:
        """Simple obfuscation (use cryptography lib for real encryption)."""
        if not self.passphrase:
            return data

        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.passphrase.encode()).digest()
            )
            f = Fernet(key)
            return f.encrypt(data.encode()).decode()
        except ImportError:
            # Fallback: simple XOR obfuscation (NOT secure, just obscures)
            key = hashlib.sha256(self.passphrase.encode()).digest()
            result = bytearray()
            for i, char in enumerate(data.encode()):
                result.append(char ^ key[i % len(key)])
            return base64.b64encode(result).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt identity data."""
        if not self.passphrase:
            return data

        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.passphrase.encode()).digest()
            )
            f = Fernet(key)
            return f.decrypt(data.encode()).decode()
        except ImportError:
            # Fallback: simple XOR deobfuscation
            key = hashlib.sha256(self.passphrase.encode()).digest()
            data_bytes = base64.b64decode(data)
            result = bytearray()
            for i, byte in enumerate(data_bytes):
                result.append(byte ^ key[i % len(key)])
            return result.decode()

    def save(self, identity: Identity, name: str = None):
        """Save an identity to the vault."""
        if name is None:
            name = identity.username

        json_data = identity.to_json()
        encrypted = self._encrypt(json_data)

        path = self._get_identity_path(name)
        with open(path, 'w') as f:
            f.write(encrypted)

        self.identities[name] = identity

    def load(self, name: str) -> Optional[Identity]:
        """Load an identity from the vault."""
        path = self._get_identity_path(name)
        if not path.exists():
            return None

        with open(path, 'r') as f:
            encrypted = f.read()

        try:
            json_data = self._decrypt(encrypted)
            data = json.loads(json_data)
            identity = Identity.from_dict(data)
            self.identities[name] = identity
            return identity
        except Exception as e:
            print(f"[spicy-cat] Failed to load identity '{name}': {e}")
            return None

    def list_identities(self) -> List[str]:
        """List all saved identities."""
        identities = []
        for f in self.vault_path.glob("*.json"):
            identities.append(f.stem)
        return sorted(identities)

    def delete(self, name: str) -> bool:
        """Delete an identity from the vault."""
        path = self._get_identity_path(name)
        if path.exists():
            path.unlink()
            self.identities.pop(name, None)
            return True
        return False

    def generate_new(self, name: str = None, locale: str = 'en_US') -> Identity:
        """Generate and save a new identity."""
        import secrets
        seed = secrets.token_hex(16)
        identity = Identity(seed, locale)

        if name is None:
            name = identity.username

        self.save(identity, name)
        return identity


def generate_seed() -> str:
    """Generate a cryptographically random seed."""
    import secrets
    return secrets.token_hex(16)


def quick_identity(seed: str = None, locale: str = 'en_US') -> Identity:
    """Quickly generate a throwaway identity."""
    if seed is None:
        seed = generate_seed()
    return Identity(seed, locale)


if __name__ == "__main__":
    # Demo
    print("=== spicy-cat Identity Generator ===\n")
    print(f"Faker available: {FAKER_AVAILABLE}\n")

    identity = quick_identity("demo_seed_123")
    print("Generated Identity:")
    print(identity.summary())

    print("\nFull JSON export:")
    print(identity.to_json())
