# Stockfish

import random
import warnings

import chess
from stockfish import Stockfish, StockfishException

OPENING = 8
CHOICES = 3


# Engine
class Engine:

    def __init__(self, path, threads, elo, time):

        options = {
            'Hash': 16,
            'Threads': threads,
            'UCI_LimitStrength': True,
            'UCI_Elo': elo,
        }

        self.time = time
        self.engine = Stockfish(path, parameters=options)

    # Stop
    def stop(self):

        try:
            self.engine.send_quit_command()
        except (OSError, StockfishException):
            pass

    # Pick
    def pick(self):

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            moves = self.engine.get_top_moves(CHOICES)

        if not moves:
            return ''

        return random.choice(moves)['Move']

    # Best
    def best(self, fen, ply=0, time=None):

        try:
            board = chess.Board(fen)
        except ValueError:
            return ''

        # Illegal board
        if not board.is_valid():
            return ''

        self.engine.set_fen_position(fen)

        # Opening
        if ply < OPENING:
            return self.pick()

        wait = min(self.time, time) if time else self.time

        return self.engine.get_best_move_time(wait) or ''
