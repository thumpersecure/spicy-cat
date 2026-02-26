#!/usr/bin/env python3
"""
chaos.py - Chaotic Randomization Engine for spicy-cat

"Cats are connoisseurs of chaos." - This module proves it.

Uses deterministic chaos (logistic map, Lorenz attractor) to generate
unpredictable but reproducible sequences that look organic, not algorithmic.
"""

import math
import struct
import hashlib
from typing import Generator, List, Tuple, Optional


class LogisticMap:
    """
    Logistic map: x[n+1] = r * x[n] * (1 - x[n])

    At r ≈ 3.9999, exhibits chaotic behavior - deterministic but unpredictable.
    Perfect for generating "random-looking" values from a seed.
    """

    def __init__(self, seed: Optional[str] = None, r: float = 3.9999):
        self.r = r
        self.x = self._seed_to_x(seed) if seed else 0.5
        # Warm up the system to get past transient behavior
        for _ in range(100):
            self._step()

    def _seed_to_x(self, seed: str) -> float:
        """Convert string seed to initial x value in (0, 1)."""
        h = hashlib.sha256(seed.encode()).digest()
        # Use first 8 bytes as float seed
        val = struct.unpack('>Q', h[:8])[0]
        # Map to (0.1, 0.9) to avoid fixed points
        return 0.1 + (val / (2**64)) * 0.8

    def _step(self) -> float:
        """Single iteration of the logistic map."""
        self.x = self.r * self.x * (1 - self.x)
        return self.x

    def next(self) -> float:
        """Get next chaotic value in [0, 1)."""
        return self._step()

    def next_int(self, min_val: int, max_val: int) -> int:
        """Get next chaotic integer in [min_val, max_val]."""
        return min_val + int(self.next() * (max_val - min_val + 1))

    def next_choice(self, items: list):
        """Choose item from list using chaotic selection."""
        if not items:
            return None
        return items[self.next_int(0, len(items) - 1)]

    def next_gaussian(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Generate Gaussian-distributed value using Box-Muller transform."""
        u1 = max(self.next(), 1e-10)  # Avoid log(0)
        u2 = self.next()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        return mu + sigma * z


class LorenzAttractor:
    """
    Lorenz attractor for generating organic behavioral noise.

    The butterfly effect in code - small changes cascade into
    completely different trajectories. Cats understand this intuitively
    when they knock things off tables.
    """

    def __init__(self, seed: Optional[str] = None,
                 sigma: float = 10.0, rho: float = 28.0, beta: float = 8/3):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta

        # Initialize state from seed
        if seed:
            lm = LogisticMap(seed)
            self.x = (lm.next() - 0.5) * 30
            self.y = (lm.next() - 0.5) * 30
            self.z = lm.next() * 50
        else:
            self.x, self.y, self.z = 1.0, 1.0, 1.0

        self.dt = 0.01
        # Warm up
        for _ in range(1000):
            self._step()

    def _step(self) -> Tuple[float, float, float]:
        """Single Runge-Kutta 4 step."""
        def derivatives(x, y, z):
            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z
            return dx, dy, dz

        # RK4 integration
        k1 = derivatives(self.x, self.y, self.z)
        k2 = derivatives(
            self.x + k1[0]*self.dt/2,
            self.y + k1[1]*self.dt/2,
            self.z + k1[2]*self.dt/2
        )
        k3 = derivatives(
            self.x + k2[0]*self.dt/2,
            self.y + k2[1]*self.dt/2,
            self.z + k2[2]*self.dt/2
        )
        k4 = derivatives(
            self.x + k3[0]*self.dt,
            self.y + k3[1]*self.dt,
            self.z + k3[2]*self.dt
        )

        self.x += (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * self.dt / 6
        self.y += (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * self.dt / 6
        self.z += (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]) * self.dt / 6

        return self.x, self.y, self.z

    def next(self) -> Tuple[float, float, float]:
        """Get next point on the attractor."""
        return self._step()

    def next_normalized(self) -> Tuple[float, float, float]:
        """Get next point normalized to roughly [-1, 1] range."""
        x, y, z = self._step()
        # Typical Lorenz ranges: x,y in [-20,20], z in [0,50]
        return (x / 20.0, y / 20.0, (z - 25) / 25.0)

    def generate_noise(self, n: int) -> List[float]:
        """Generate n noise values from attractor trajectory."""
        noise = []
        for _ in range(n):
            x, y, z = self.next_normalized()
            # Combine dimensions for single noise value
            noise.append((x + y + z) / 3.0)
        return noise


class ChaoticTimer:
    """
    Generate organic-looking time intervals using chaos.

    Because cats never do anything on a predictable schedule.
    """

    def __init__(self, seed: str, base_interval: float = 60.0):
        self.lorenz = LorenzAttractor(seed)
        self.logistic = LogisticMap(seed + "_timer")
        self.base_interval = base_interval

    def next_interval(self, min_factor: float = 0.5, max_factor: float = 2.0) -> float:
        """
        Get next time interval with chaotic variation.
        Returns seconds.
        """
        # Use Lorenz for organic variation
        noise = self.lorenz.next_normalized()
        variation = (noise[0] + 1) / 2  # Map to [0, 1]

        # Scale to factor range
        factor = min_factor + variation * (max_factor - min_factor)

        return self.base_interval * factor

    def generate_schedule(
        self,
        hours: int = 24,
        min_factor: float = 0.17,
        max_factor: float = 2.0
    ) -> List[float]:
        """
        Generate a day's worth of activity timestamps.
        Returns list of hour offsets (0.0 to hours).
        """
        timestamps = []
        current = 0.0

        while current < hours:
            # next_interval returns seconds; convert to hour offsets for schedule output.
            interval_seconds = self.next_interval(min_factor, max_factor)
            current += interval_seconds / 3600.0
            if current < hours:
                timestamps.append(current)

        return timestamps


class IdentityDrift:
    """
    Subtle, natural-seeming mutations to identity over time.

    Like how cats slowly take over more and more of the bed.
    """

    def __init__(self, seed: str):
        self.lorenz = LorenzAttractor(seed + "_drift")
        self.logistic = LogisticMap(seed + "_drift_select")
        self.drift_accumulator = 0.0

    def should_drift(self, threshold: float = 0.7) -> bool:
        """Check if a drift event should occur."""
        self.drift_accumulator += abs(self.lorenz.next_normalized()[0]) * 0.1
        if self.drift_accumulator > threshold:
            self.drift_accumulator = 0.0
            return True
        return False

    def drift_interest(self, interests: List[str], available: List[str]) -> List[str]:
        """
        Drift interests slightly - maybe drop one, add one.
        Returns modified interest list.
        """
        if not self.should_drift():
            return interests.copy()

        new_interests = interests.copy()

        # Maybe drop one interest
        if len(new_interests) > 2 and self.logistic.next() > 0.6:
            idx = self.logistic.next_int(0, len(new_interests) - 1)
            new_interests.pop(idx)

        # Maybe add one interest
        if self.logistic.next() > 0.5:
            candidates = [i for i in available if i not in new_interests]
            if candidates:
                new_interests.append(self.logistic.next_choice(candidates))

        return new_interests

    def drift_location(self, current_city: str, nearby_cities: List[str]) -> str:
        """Maybe move to a nearby city."""
        if not self.should_drift(threshold=0.9):  # Moves are rare
            return current_city
        return self.logistic.next_choice(nearby_cities) or current_city


# Convenience function for seeded chaos
def create_chaos_engine(seed: str) -> Tuple[LogisticMap, LorenzAttractor]:
    """Create a paired chaos engine from a single seed."""
    return LogisticMap(seed), LorenzAttractor(seed)


if __name__ == "__main__":
    # Demo
    print("=== Logistic Map Demo ===")
    lm = LogisticMap("test_seed")
    print("Values:", [f"{lm.next():.4f}" for _ in range(5)])
    print("Integers [1-100]:", [lm.next_int(1, 100) for _ in range(5)])

    print("\n=== Lorenz Attractor Demo ===")
    la = LorenzAttractor("test_seed")
    print("Trajectory points:")
    for _ in range(3):
        x, y, z = la.next_normalized()
        print(f"  ({x:.3f}, {y:.3f}, {z:.3f})")

    print("\n=== Chaotic Timer Demo ===")
    ct = ChaoticTimer("test_seed", base_interval=60)
    print("Next 5 intervals (seconds):", [f"{ct.next_interval():.1f}" for _ in range(5)])
