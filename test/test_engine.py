# Engine tests

import unittest

import chess
from stockfish import StockfishException

from eng.engine import Engine

FEN = chess.Board().fen()


# Fake
class Fake:

    def __init__(self):

        self.time = None

    def set_fen_position(self, fen):
        pass

    def get_top_moves(self, count):

        moves = [
            {'Move': 'e2e4'},
            {'Move': 'd2d4'},
            {'Move': 'g1f3'},
        ]

        return moves[:count]

    def get_best_move_time(self, time):

        self.time = time

        return 'e2e4'


# Dead
class Dead:

    def send_quit_command(self):
        raise StockfishException('crashed')


# Bare
def bare():

    engine = Engine.__new__(Engine)

    engine.time = 800
    engine.engine = Fake()

    return engine


class OpeningTest(unittest.TestCase):

    def test_opening_varies(self):

        engine = bare()
        picks = {engine.best(FEN, 0) for _ in range(40)}

        self.assertEqual(picks, {'e2e4', 'd2d4', 'g1f3'})

    def test_opening_is_gated(self):

        self.assertEqual(bare().best(FEN, 8), 'e2e4')

    def test_bad_fen(self):

        self.assertEqual(bare().best('nonsense', 0), '')


class LimitTest(unittest.TestCase):

    def test_limit_is_used(self):

        engine = bare()
        engine.best(FEN, 20, 250)

        self.assertEqual(engine.engine.time, 250)

    def test_config_is_the_cap(self):

        engine = bare()
        engine.best(FEN, 20, 2000)

        self.assertEqual(engine.engine.time, 800)


class StopTest(unittest.TestCase):

    def test_dead_engine_is_quiet(self):

        engine = bare()
        engine.engine = Dead()

        engine.stop()


if __name__ == '__main__':
    unittest.main()
