#!/usr/bin/env python3
"""
markov.py - Behavioral Markov Models for spicy-cat

"Cats are mysterious beings... you never know what they're thinking."
This module makes your digital behavior equally mysterious.

Generates:
- Writing style variations (anti-stylometry)
- Activity timing patterns (realistic online presence)
- Behavioral state machines (organic interaction patterns)
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Import our chaos engine
from .chaos import LogisticMap, LorenzAttractor


class WritingStyleMarkov:
    """
    Markov chain for generating writing style variations.

    Helps defeat stylometry by introducing controlled variation
    in how text is transformed/suggested.
    """

    # Predefined style profiles (9 styles for maximum anti-stylometry)
    STYLES = {
        'formal': {
            'contractions': False,
            'punctuation_density': 1.2,
            'avg_sentence_length': 18,
            'vocabulary_tier': 'elevated',
            'emoji_probability': 0.0,
            'capitalization': 'proper',
            'filler_words': ['indeed', 'therefore', 'consequently', 'furthermore'],
        },
        'casual': {
            'contractions': True,
            'punctuation_density': 0.8,
            'avg_sentence_length': 12,
            'vocabulary_tier': 'common',
            'emoji_probability': 0.1,
            'capitalization': 'relaxed',
            'filler_words': ['like', 'you know', 'basically', 'honestly'],
        },
        'terse': {
            'contractions': True,
            'punctuation_density': 0.6,
            'avg_sentence_length': 6,
            'vocabulary_tier': 'minimal',
            'emoji_probability': 0.0,
            'capitalization': 'lowercase',
            'filler_words': [],
        },
        'verbose': {
            'contractions': False,
            'punctuation_density': 1.4,
            'avg_sentence_length': 25,
            'vocabulary_tier': 'elaborate',
            'emoji_probability': 0.02,
            'capitalization': 'proper',
            'filler_words': ['essentially', 'in other words', 'to be specific', 'as it were'],
        },
        'gen_z': {
            'contractions': True,
            'punctuation_density': 0.5,
            'avg_sentence_length': 8,
            'vocabulary_tier': 'slang',
            'emoji_probability': 0.3,
            'capitalization': 'lowercase',
            'filler_words': ['lowkey', 'ngl', 'fr', 'tbh', 'literally'],
        },
        'academic': {
            'contractions': False,
            'punctuation_density': 1.3,
            'avg_sentence_length': 22,
            'vocabulary_tier': 'scholarly',
            'emoji_probability': 0.0,
            'capitalization': 'proper',
            'filler_words': ['notably', 'it should be noted', 'the literature suggests', 'arguably'],
            'passive_voice': True,
            'hedging': ['may', 'might', 'appears to', 'suggests that', 'it is possible'],
        },
        'technical': {
            'contractions': False,
            'punctuation_density': 1.0,
            'avg_sentence_length': 14,
            'vocabulary_tier': 'jargon',
            'emoji_probability': 0.0,
            'capitalization': 'proper',
            'filler_words': ['i.e.', 'e.g.', 'cf.', 'viz.', 'N.B.'],
            'abbreviations': True,
            'precision': 'high',
        },
        'friendly': {
            'contractions': True,
            'punctuation_density': 1.1,
            'avg_sentence_length': 10,
            'vocabulary_tier': 'warm',
            'emoji_probability': 0.15,
            'capitalization': 'relaxed',
            'filler_words': ['hey', 'so', 'just wanted to', 'hope you\'re well'],
            'exclamations': True,
            'personal_pronouns': 'heavy',
        },
        'sarcastic': {
            'contractions': True,
            'punctuation_density': 0.9,
            'avg_sentence_length': 11,
            'vocabulary_tier': 'ironic',
            'emoji_probability': 0.05,
            'capitalization': 'dramatic',
            'filler_words': ['obviously', 'clearly', 'sure', 'wow', 'shocking'],
            'rhetorical_questions': True,
            'air_quotes': True,
        },
    }

    # Transition probabilities between styles (for drift)
    # Nine lives, nine styles - each can drift to related styles
    TRANSITIONS = {
        'formal': {'formal': 0.5, 'academic': 0.2, 'verbose': 0.15, 'technical': 0.1, 'casual': 0.05},
        'casual': {'casual': 0.4, 'friendly': 0.2, 'terse': 0.15, 'gen_z': 0.15, 'sarcastic': 0.1},
        'terse': {'terse': 0.5, 'casual': 0.2, 'technical': 0.15, 'sarcastic': 0.1, 'formal': 0.05},
        'verbose': {'verbose': 0.5, 'academic': 0.2, 'formal': 0.15, 'friendly': 0.1, 'casual': 0.05},
        'gen_z': {'gen_z': 0.5, 'casual': 0.2, 'sarcastic': 0.15, 'terse': 0.1, 'friendly': 0.05},
        'academic': {'academic': 0.5, 'formal': 0.2, 'verbose': 0.15, 'technical': 0.1, 'terse': 0.05},
        'technical': {'technical': 0.5, 'terse': 0.2, 'academic': 0.15, 'formal': 0.1, 'casual': 0.05},
        'friendly': {'friendly': 0.5, 'casual': 0.2, 'verbose': 0.15, 'gen_z': 0.1, 'sarcastic': 0.05},
        'sarcastic': {'sarcastic': 0.5, 'casual': 0.2, 'terse': 0.15, 'gen_z': 0.1, 'friendly': 0.05},
    }

    def __init__(self, seed: str, initial_style: str = 'casual'):
        self.chaos = LogisticMap(seed + "_writing")
        self.current_style = initial_style
        self.style_params = self.STYLES.get(initial_style, self.STYLES['casual']).copy()
        self.message_count = 0

    def get_current_style(self) -> Dict:
        """Get current style parameters."""
        return self.style_params.copy()

    def transition(self) -> str:
        """
        Maybe transition to a different style.
        Returns new style name.
        """
        self.message_count += 1

        # Only consider transition every ~10 messages
        if self.message_count % 10 != 0:
            return self.current_style

        transitions = self.TRANSITIONS.get(self.current_style, {})
        roll = self.chaos.next()

        cumulative = 0.0
        for style, prob in transitions.items():
            cumulative += prob
            if roll <= cumulative:
                if style != self.current_style:
                    self.current_style = style
                    self.style_params = self.STYLES[style].copy()
                break

        return self.current_style

    def apply_style_hints(self, text: str) -> Dict:
        """
        Generate style hints for a piece of text.
        Returns suggestions, doesn't modify text directly.
        """
        self.transition()  # Maybe change style

        hints = {
            'style': self.current_style,
            'suggestions': [],
        }

        params = self.style_params

        # Contraction hints
        if params['contractions']:
            hints['suggestions'].append("Use contractions (don't, can't, won't)")
        else:
            hints['suggestions'].append("Avoid contractions (do not, cannot)")

        # Sentence length hints
        avg_len = params['avg_sentence_length']
        hints['suggestions'].append(f"Target ~{avg_len} words per sentence")

        # Add filler word suggestions
        if params['filler_words']:
            hints['suggestions'].append(f"Sprinkle in: {', '.join(params['filler_words'][:2])}")

        return hints


class ActivityPatternMarkov:
    """
    Generates realistic online activity patterns.

    Like a cat, your digital presence should have natural
    rhythms of activity and rest.
    """

    # States: represents different activity modes
    STATES = ['sleeping', 'active', 'browsing', 'focused', 'idle']

    # Time-of-day modifiers (24-hour format)
    TIME_PROFILES = {
        'early_bird': {
            'wake_hour': 5,
            'sleep_hour': 21,
            'peak_hours': [6, 7, 8, 9, 10],
        },
        'night_owl': {
            'wake_hour': 10,
            'sleep_hour': 2,
            'peak_hours': [20, 21, 22, 23, 0, 1],
        },
        'nine_to_five': {
            'wake_hour': 7,
            'sleep_hour': 23,
            'peak_hours': [9, 10, 11, 14, 15, 16],
        },
        'erratic': {
            'wake_hour': None,  # Random
            'sleep_hour': None,
            'peak_hours': [],  # All hours equally likely
        },
    }

    # State transition matrix
    TRANSITIONS = {
        'sleeping': {'sleeping': 0.9, 'active': 0.08, 'idle': 0.02},
        'active': {'active': 0.4, 'browsing': 0.25, 'focused': 0.2, 'idle': 0.1, 'sleeping': 0.05},
        'browsing': {'browsing': 0.5, 'active': 0.2, 'focused': 0.15, 'idle': 0.15},
        'focused': {'focused': 0.6, 'browsing': 0.15, 'active': 0.1, 'idle': 0.15},
        'idle': {'idle': 0.3, 'active': 0.25, 'browsing': 0.2, 'sleeping': 0.15, 'focused': 0.1},
    }

    def __init__(self, seed: str, profile: str = 'nine_to_five'):
        self.chaos = LogisticMap(seed + "_activity")
        self.lorenz = LorenzAttractor(seed + "_activity_noise")
        self.profile_name = profile
        self.profile = self.TIME_PROFILES.get(profile, self.TIME_PROFILES['nine_to_five'])
        self.current_state = 'idle'
        self.state_duration = 0  # Minutes in current state

    def _is_sleep_time(self, hour: int) -> bool:
        """Check if current hour is during sleep time."""
        wake = self.profile.get('wake_hour')
        sleep = self.profile.get('sleep_hour')

        if wake is None or sleep is None:
            return self.chaos.next() < 0.3  # 30% chance for erratic

        if sleep < wake:  # Crosses midnight (night owl)
            return hour >= sleep and hour < wake
        else:
            return hour >= sleep or hour < wake

    def _get_time_modifier(self, hour: int) -> float:
        """Get activity probability modifier based on time."""
        if self._is_sleep_time(hour):
            return 0.1  # Low activity during sleep

        if hour in self.profile.get('peak_hours', []):
            return 1.5  # High activity during peak

        return 1.0

    def step(self, current_hour: int = 12) -> Tuple[str, int]:
        """
        Advance one time step (1 minute).
        Returns (new_state, suggested_duration_minutes).
        """
        self.state_duration += 1

        # Force sleep state during sleep hours
        if self._is_sleep_time(current_hour) and self.current_state != 'sleeping':
            if self.chaos.next() < 0.1:  # 10% chance per minute to fall asleep
                self.current_state = 'sleeping'
                self.state_duration = 0

        # Get base transitions for current state
        transitions = self.TRANSITIONS.get(self.current_state, {})

        # Modify based on time
        time_mod = self._get_time_modifier(current_hour)

        # Roll for transition
        roll = self.chaos.next()

        # Add some Lorenz noise for organic feel
        noise = self.lorenz.next_normalized()[0] * 0.1
        roll = max(0, min(1, roll + noise))

        cumulative = 0.0
        for state, prob in transitions.items():
            # Modify transition probability based on time
            if state == 'sleeping':
                adj_prob = prob * (1.5 if self._is_sleep_time(current_hour) else 0.5)
            elif state in ['active', 'focused']:
                adj_prob = prob * time_mod
            else:
                adj_prob = prob

            cumulative += adj_prob
            if roll <= cumulative:
                if state != self.current_state:
                    self.current_state = state
                    self.state_duration = 0
                break

        # Generate suggested duration for current state
        base_durations = {
            'sleeping': 360,  # 6 hours
            'active': 45,
            'browsing': 30,
            'focused': 90,
            'idle': 15,
        }

        base = base_durations.get(self.current_state, 30)
        duration = int(base * (0.5 + self.chaos.next()))

        return self.current_state, duration

    def generate_day_schedule(self) -> List[Dict]:
        """
        Generate a full day's activity schedule.
        Returns list of {hour, minute, state, duration} dicts.
        """
        schedule = []
        minute = 0  # Start at midnight

        while minute < 1440:  # Full day in minutes
            hour = minute // 60
            state, duration = self.step(hour)

            schedule.append({
                'hour': hour,
                'minute': minute % 60,
                'state': state,
                'duration': min(duration, 1440 - minute),  # Don't exceed day
            })

            minute += max(duration, 1)  # At least 1 minute per step

        return schedule

    def get_online_probability(self, hour: int) -> float:
        """Get probability of being online at given hour."""
        if self._is_sleep_time(hour):
            return 0.05

        base = 0.5
        if hour in self.profile.get('peak_hours', []):
            base = 0.85

        # Add chaos variation
        noise = self.lorenz.next_normalized()[0] * 0.15
        return max(0, min(1, base + noise))


class BehaviorStateMachine:
    """
    Higher-level behavioral state machine combining writing and activity.

    This is the cat's whole personality, not just one aspect.
    """

    def __init__(self, seed: str,
                 writing_style: str = 'casual',
                 activity_profile: str = 'nine_to_five'):
        self.seed = seed
        self.writing = WritingStyleMarkov(seed, writing_style)
        self.activity = ActivityPatternMarkov(seed, activity_profile)
        self.chaos = LogisticMap(seed + "_behavior")

        # Track behavioral metrics
        self.session_start = None
        self.interactions = 0
        self.current_mood = 'neutral'  # neutral, engaged, distracted, tired

    def get_current_state(self) -> Dict:
        """Get complete current behavioral state."""
        return {
            'writing_style': self.writing.current_style,
            'activity_state': self.activity.current_state,
            'mood': self.current_mood,
            'interactions': self.interactions,
        }

    def interact(self, hour: int = 12) -> Dict:
        """
        Register an interaction and get behavioral guidance.
        """
        self.interactions += 1

        # Update activity state
        activity_state, duration = self.activity.step(hour)

        # Maybe transition writing style
        writing_style = self.writing.transition()

        # Update mood based on activity
        if activity_state == 'focused':
            self.current_mood = 'engaged'
        elif activity_state == 'idle':
            self.current_mood = self.chaos.next_choice(['distracted', 'tired', 'neutral'])
        elif activity_state == 'sleeping':
            self.current_mood = 'tired'
        else:
            self.current_mood = 'neutral'

        return {
            'state': self.get_current_state(),
            'writing_hints': self.writing.get_current_style(),
            'suggested_break': duration if activity_state == 'idle' else None,
            'online_probability': self.activity.get_online_probability(hour),
        }

    def serialize(self) -> Dict:
        """Serialize state for persistence."""
        return {
            'seed': self.seed,
            'writing_style': self.writing.current_style,
            'activity_state': self.activity.current_state,
            'mood': self.current_mood,
            'interactions': self.interactions,
        }

    @classmethod
    def deserialize(cls, data: Dict) -> 'BehaviorStateMachine':
        """Restore from serialized state."""
        machine = cls(data['seed'])
        machine.writing.current_style = data.get('writing_style', 'casual')
        machine.activity.current_state = data.get('activity_state', 'idle')
        machine.current_mood = data.get('mood', 'neutral')
        machine.interactions = data.get('interactions', 0)
        return machine


if __name__ == "__main__":
    # Demo
    print("=== Writing Style Demo ===")
    ws = WritingStyleMarkov("test_seed", "casual")
    for i in range(3):
        hints = ws.apply_style_hints("Sample text")
        print(f"Message {i+1}: Style={hints['style']}")
        for s in hints['suggestions']:
            print(f"  - {s}")

    print("\n=== Activity Pattern Demo ===")
    ap = ActivityPatternMarkov("test_seed", "night_owl")
    print(f"Profile: {ap.profile_name}")
    print("Sample activity states throughout the day:")
    for hour in [6, 12, 18, 23, 2]:
        state, duration = ap.step(hour)
        online = ap.get_online_probability(hour)
        print(f"  {hour:02d}:00 - State: {state:10s} | Online prob: {online:.2f}")

    print("\n=== Behavior State Machine Demo ===")
    bsm = BehaviorStateMachine("test_seed", "formal", "early_bird")
    for hour in [7, 12, 20]:
        result = bsm.interact(hour)
        print(f"Hour {hour:02d}: {result['state']}")
