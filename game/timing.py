# Timing

import math
import random

FLOOR = 0.4
CEIL = 15.0
SCALE = 0.055
SPIKE = 0.08
SNAP = 0.14
DRIFT = 0.16


# Player mood
class Pace:

    def __init__(self):

        self.tempo = 1.0

    # Mood drift
    def drift(self):

        self.tempo *= math.exp(random.uniform(-DRIFT, DRIFT))
        self.tempo = min(max(self.tempo, 0.55), 2.0)

    # Move target
    def target(self, clock, moves=20):

        self.drift()

        # Clock curve
        base = (clock or 180) ** 0.72 * SCALE

        # Busy board
        base *= 0.75 + min(moves, 40) / 80

        target = base * self.tempo * random.uniform(0.7, 1.35)

        # Snap move
        if random.random() < SNAP:
            target *= 0.25

        # Slow move
        if random.random() < SPIKE:
            target *= random.uniform(1.8, 3.0)

        # Clock safety
        if clock:
            target = min(target, max(clock * 0.06, FLOOR))

        return round(min(max(target, FLOOR), CEIL), 2)
