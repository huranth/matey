# Timing tests

import unittest

from game import timing


# Fresh
def pace():

    return timing.Pace()


class BoundsTest(unittest.TestCase):

    def test_inside_bounds(self):

        player = pace()

        for _ in range(200):
            wait = player.target(600)

            self.assertGreaterEqual(wait, timing.FLOOR)
            self.assertLessEqual(wait, timing.CEIL)


class AdaptTest(unittest.TestCase):

    def test_bullet_is_quicker(self):

        fast = pace()
        slow = pace()

        bullet = sum(fast.target(60) for _ in range(200))
        rapid = sum(slow.target(600) for _ in range(200))

        self.assertLess(bullet, rapid)

    def test_clock_drain_shrinks(self):

        fresh = pace()
        low = pace()

        full = sum(fresh.target(600) for _ in range(200))
        tight = sum(low.target(30) for _ in range(200))

        self.assertLess(tight, full)


class BoardTest(unittest.TestCase):

    def test_busy_board_is_slower(self):

        quiet = pace()
        busy = pace()

        quick = sum(quiet.target(300, 5) for _ in range(200))
        slow = sum(busy.target(300, 40) for _ in range(200))

        self.assertLess(quick, slow)


class MoodTest(unittest.TestCase):

    def test_fresh_player(self):

        self.assertEqual(pace().tempo, 1.0)

    def test_tempo_stays_sane(self):

        player = pace()

        for _ in range(500):
            player.target(300)

        self.assertGreaterEqual(player.tempo, 0.55)
        self.assertLessEqual(player.tempo, 2.0)


class PatternTest(unittest.TestCase):

    def test_values_vary(self):

        player = pace()
        values = {player.target(180) for _ in range(50)}

        self.assertGreater(len(values), 5)


class EdgeTest(unittest.TestCase):

    def test_no_clock(self):

        player = pace()

        self.assertGreaterEqual(player.target(0), timing.FLOOR)
        self.assertLessEqual(player.target(0), timing.CEIL)

    def test_low_clock_is_capped(self):

        player = pace()

        for _ in range(100):
            self.assertLessEqual(player.target(10), 0.6)


if __name__ == '__main__':
    unittest.main()
