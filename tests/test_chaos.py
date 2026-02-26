#!/usr/bin/env python3
"""Tests for the chaos engine (lib/chaos.py)."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.chaos import LogisticMap, LorenzAttractor, ChaoticTimer, IdentityDrift


class TestLogisticMap:
    """Tests for LogisticMap chaos generator."""

    def test_deterministic_output(self):
        """Same seed should produce same sequence."""
        lm1 = LogisticMap("test_seed")
        lm2 = LogisticMap("test_seed")

        values1 = [lm1.next() for _ in range(10)]
        values2 = [lm2.next() for _ in range(10)]

        assert values1 == values2, "Same seed should produce identical sequences"

    def test_different_seeds_differ(self):
        """Different seeds should produce different sequences."""
        lm1 = LogisticMap("seed_a")
        lm2 = LogisticMap("seed_b")

        values1 = [lm1.next() for _ in range(10)]
        values2 = [lm2.next() for _ in range(10)]

        assert values1 != values2, "Different seeds should produce different sequences"

    def test_output_range(self):
        """Output should be in [0, 1) range."""
        lm = LogisticMap("range_test")

        for _ in range(100):
            value = lm.next()
            assert 0 <= value < 1, f"Value {value} outside [0, 1) range"

    def test_next_int_range(self):
        """next_int should return values within specified range."""
        lm = LogisticMap("int_test")

        for _ in range(100):
            value = lm.next_int(5, 15)
            assert 5 <= value <= 15, f"Value {value} outside [5, 15] range"

    def test_next_choice_returns_from_list(self):
        """next_choice should return an item from the provided list."""
        lm = LogisticMap("choice_test")
        items = ["a", "b", "c", "d"]

        for _ in range(20):
            choice = lm.next_choice(items)
            assert choice in items, f"Choice {choice} not in original list"

    def test_next_choice_empty_list(self):
        """next_choice should handle empty list."""
        lm = LogisticMap("empty_test")
        assert lm.next_choice([]) is None

    def test_gaussian_distribution(self):
        """next_gaussian should produce values roughly centered on mu."""
        lm = LogisticMap("gaussian_test")
        mu, sigma = 10.0, 2.0

        values = [lm.next_gaussian(mu, sigma) for _ in range(1000)]
        mean = sum(values) / len(values)

        # Mean should be within 1.0 of mu for 1000 samples (chaotic source has higher variance)
        assert abs(mean - mu) < 1.0, f"Mean {mean} too far from expected {mu}"


class TestLorenzAttractor:
    """Tests for Lorenz attractor chaos generator."""

    def test_deterministic_output(self):
        """Same seed should produce same trajectory."""
        la1 = LorenzAttractor("lorenz_seed")
        la2 = LorenzAttractor("lorenz_seed")

        points1 = [la1.next() for _ in range(10)]
        points2 = [la2.next() for _ in range(10)]

        assert points1 == points2, "Same seed should produce identical trajectories"

    def test_normalized_range(self):
        """Normalized output should be roughly in [-1, 1] range."""
        la = LorenzAttractor("normalized_test")

        for _ in range(100):
            x, y, z = la.next_normalized()
            # Allow some overshoot due to chaotic nature
            assert -2 <= x <= 2, f"x={x} outside expected range"
            assert -2 <= y <= 2, f"y={y} outside expected range"
            assert -2 <= z <= 2, f"z={z} outside expected range"

    def test_generate_noise(self):
        """generate_noise should return correct number of values."""
        la = LorenzAttractor("noise_test")
        noise = la.generate_noise(50)

        assert len(noise) == 50, f"Expected 50 noise values, got {len(noise)}"


class TestChaoticTimer:
    """Tests for ChaoticTimer."""

    def test_interval_positive(self):
        """Intervals should always be positive."""
        ct = ChaoticTimer("timer_test", base_interval=60.0)

        for _ in range(50):
            interval = ct.next_interval()
            assert interval > 0, f"Interval {interval} should be positive"

    def test_interval_within_bounds(self):
        """Intervals should respect min/max factors."""
        ct = ChaoticTimer("bounds_test", base_interval=100.0)

        for _ in range(50):
            interval = ct.next_interval(min_factor=0.5, max_factor=2.0)
            assert 50.0 <= interval <= 200.0, f"Interval {interval} outside expected bounds"

    def test_generate_schedule_increasing_and_bounded(self):
        """Generated schedule should be sorted and stay within requested hours."""
        ct = ChaoticTimer("schedule_test", base_interval=60.0)
        schedule = ct.generate_schedule(hours=2)

        assert len(schedule) > 0, "Schedule should include at least one timestamp"
        assert schedule == sorted(schedule), "Schedule timestamps should be increasing"
        assert all(0.0 < ts < 2.0 for ts in schedule), "Timestamps should be hour offsets in range"

    def test_generate_schedule_deterministic(self):
        """Schedules should be deterministic for the same seed."""
        ct1 = ChaoticTimer("deterministic_schedule", base_interval=60.0)
        ct2 = ChaoticTimer("deterministic_schedule", base_interval=60.0)

        schedule1 = ct1.generate_schedule(hours=1)
        schedule2 = ct2.generate_schedule(hours=1)
        assert schedule1 == schedule2


class TestIdentityDrift:
    """Tests for IdentityDrift."""

    def test_drift_interest_preserves_type(self):
        """Drifted interests should still be a list of strings."""
        drift = IdentityDrift("drift_test")
        interests = ["hiking", "reading", "cooking"]
        available = ["gaming", "music", "travel", "hiking", "reading", "cooking"]

        # Run multiple times to trigger drift
        for _ in range(20):
            result = drift.drift_interest(interests, available)
            assert isinstance(result, list)
            for item in result:
                assert isinstance(item, str)

    def test_drift_location_returns_string(self):
        """Drifted location should be a string."""
        drift = IdentityDrift("location_drift_test")
        cities = ["New York", "Los Angeles", "Chicago"]

        for _ in range(20):
            result = drift.drift_location("Boston", cities)
            assert isinstance(result, str)


def run_tests():
    """Simple test runner for standalone execution."""
    import traceback

    test_classes = [
        TestLogisticMap,
        TestLorenzAttractor,
        TestChaoticTimer,
        TestIdentityDrift,
    ]

    passed = 0
    failed = 0

    for cls in test_classes:
        print(f"\n{cls.__name__}")
        print("-" * 40)

        instance = cls()
        for name in dir(instance):
            if name.startswith("test_"):
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

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
