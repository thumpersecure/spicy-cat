#!/usr/bin/env python3
"""Tests for identity generation (lib/identity.py)."""

import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.identity import Identity, IdentityVault, generate_seed, quick_identity


class TestIdentity:
    """Tests for Identity class."""

    def test_deterministic_generation(self):
        """Same seed should produce same identity."""
        id1 = Identity("test_seed_123")
        id2 = Identity("test_seed_123")

        assert id1.full_name == id2.full_name
        assert id1.email == id2.email
        assert id1.username == id2.username

    def test_different_seeds_differ(self):
        """Different seeds should produce different identities."""
        id1 = Identity("seed_alpha")
        id2 = Identity("seed_beta")

        # Names should differ (statistically certain with different seeds)
        assert id1.full_name != id2.full_name or id1.email != id2.email

    def test_required_attributes_exist(self):
        """Identity should have all required attributes."""
        identity = Identity("attr_test")

        required = [
            "first_name", "last_name", "full_name",
            "city", "state", "country", "location",
            "age", "birth_date", "occupation",
            "email", "username", "phone",
            "interests", "backstory"
        ]

        for attr in required:
            assert hasattr(identity, attr), f"Missing attribute: {attr}"
            assert getattr(identity, attr) is not None, f"Attribute {attr} is None"

    def test_age_reasonable(self):
        """Age should be between 18 and 65."""
        for i in range(10):
            identity = Identity(f"age_test_{i}")
            assert 18 <= identity.age <= 65, f"Age {identity.age} outside expected range"

    def test_email_format(self):
        """Email should contain @ and domain."""
        identity = Identity("email_test")
        assert "@" in identity.email
        assert "." in identity.email.split("@")[1]

    def test_interests_is_list(self):
        """Interests should be a non-empty list."""
        identity = Identity("interests_test")
        assert isinstance(identity.interests, list)
        assert len(identity.interests) >= 3

    def test_to_dict_roundtrip(self):
        """Identity should survive dict serialization."""
        original = Identity("roundtrip_test")
        data = original.to_dict()
        restored = Identity.from_dict(data)

        assert original.full_name == restored.full_name
        assert original.email == restored.email
        assert original.username == restored.username
        assert original.occupation == restored.occupation

    def test_to_json_valid(self):
        """to_json should produce valid JSON."""
        identity = Identity("json_test")
        json_str = identity.to_json()

        # Should parse without error
        parsed = json.loads(json_str)
        assert "core" in parsed
        assert "digital" in parsed

    def test_summary_not_empty(self):
        """Summary should return non-empty string."""
        identity = Identity("summary_test")
        summary = identity.summary()
        assert len(summary.strip()) > 0


class TestIdentityVault:
    """Tests for IdentityVault storage."""

    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "identities"

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """Should save and load identity correctly."""
        vault = IdentityVault(str(self.vault_path))
        identity = Identity("vault_test")

        vault.save(identity, "test_id")
        loaded = vault.load("test_id")

        assert loaded is not None
        assert loaded.full_name == identity.full_name
        assert loaded.email == identity.email

    def test_list_identities(self):
        """Should list saved identities."""
        vault = IdentityVault(str(self.vault_path))

        vault.save(Identity("id1"), "alice")
        vault.save(Identity("id2"), "bob")
        vault.save(Identity("id3"), "carol")

        identities = vault.list_identities()
        assert len(identities) == 3
        assert "alice" in identities
        assert "bob" in identities
        assert "carol" in identities

    def test_delete_identity(self):
        """Should delete identity."""
        vault = IdentityVault(str(self.vault_path))
        vault.save(Identity("del_test"), "to_delete")

        assert "to_delete" in vault.list_identities()

        result = vault.delete("to_delete")
        assert result is True
        assert "to_delete" not in vault.list_identities()

    def test_load_nonexistent(self):
        """Loading nonexistent identity should return None."""
        vault = IdentityVault(str(self.vault_path))
        result = vault.load("does_not_exist")
        assert result is None

    def test_generate_new(self):
        """generate_new should create and save identity."""
        vault = IdentityVault(str(self.vault_path))
        identity = vault.generate_new("generated")

        assert identity is not None
        assert "generated" in vault.list_identities()


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_generate_seed_unique(self):
        """generate_seed should produce unique values."""
        seeds = [generate_seed() for _ in range(100)]
        unique_seeds = set(seeds)
        assert len(unique_seeds) == 100, "Seeds should be unique"

    def test_generate_seed_length(self):
        """generate_seed should produce 32-char hex string."""
        seed = generate_seed()
        assert len(seed) == 32
        assert all(c in "0123456789abcdef" for c in seed)

    def test_quick_identity_works(self):
        """quick_identity should return valid Identity."""
        identity = quick_identity()
        assert identity is not None
        assert hasattr(identity, "full_name")
        assert hasattr(identity, "email")

    def test_quick_identity_with_seed(self):
        """quick_identity with seed should be deterministic."""
        id1 = quick_identity("fixed_seed")
        id2 = quick_identity("fixed_seed")
        assert id1.full_name == id2.full_name


def run_tests():
    """Simple test runner for standalone execution."""
    import traceback

    test_classes = [
        TestIdentity,
        TestIdentityVault,
        TestHelperFunctions,
    ]

    passed = 0
    failed = 0

    for cls in test_classes:
        print(f"\n{cls.__name__}")
        print("-" * 40)

        instance = cls()

        for name in dir(instance):
            if name.startswith("test_"):
                # Run setup if exists
                if hasattr(instance, "setup_method"):
                    instance.setup_method()

                try:
                    getattr(instance, name)()
                    print(f"  [PASS] {name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  [FAIL] {name}: {e}")
                    failed += 1
                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")
                    traceback.print_exc()
                    failed += 1
                finally:
                    # Run teardown if exists
                    if hasattr(instance, "teardown_method"):
                        instance.teardown_method()

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
