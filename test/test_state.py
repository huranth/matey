# State tests

import chess
import unittest

from game.state import place, replay, side, rights, loose, fen

START = chess.Board().fen()
START_BOARD = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'


# Pieces
def pieces_from(fen_text):

    board = chess.Board(fen_text)

    return [
        {'square': chess.square_name(square), 'piece': piece.symbol()}
        for square, piece in board.piece_map().items()
    ]


# Page state
def state_from(fen_text, moves=None):

    board = chess.Board(fen_text)

    return {
        'pieces': pieces_from(fen_text),
        'moves': moves or [],
        'turn': 'w' if board.turn else 'b',
    }


class PlaceTest(unittest.TestCase):

    def test_start_pieces(self):

        state = state_from(START)

        self.assertEqual(place(state['pieces']).board_fen(), START_BOARD)


class ReplayTest(unittest.TestCase):

    def test_castling_after_four_moves(self):

        board = chess.Board()
        moves = ['e4', 'e5', 'Nf3', 'Nc6']

        for move in moves:
            board.push_san(move)

        state = state_from(board.fen(), moves)

        self.assertEqual(fen(state), board.fen())
        self.assertIn(' KQkq ', fen(state))

    def test_bad_move_returns_none(self):

        self.assertIsNone(replay(['e4', 'not a move']))


class LooseTest(unittest.TestCase):

    def test_mismatch_falls_back(self):

        state = state_from(START, ['e4'])
        state['turn'] = 'b'

        self.assertEqual(fen(state), START_BOARD + ' b KQkq - 0 1')

    def test_en_passant_is_empty(self):

        state = state_from(START)

        self.assertEqual(loose(state).split(' ')[3], '-')


class SideTest(unittest.TestCase):

    def test_clock_wins(self):

        state = {'pieces': [], 'moves': ['e4'], 'turn': 'w'}

        self.assertEqual(side(state), 'w')

    def test_parity_when_missing(self):

        state = {'pieces': [], 'moves': ['e4']}

        self.assertEqual(side(state), 'b')

    def test_parity_when_empty(self):

        state = {'pieces': [], 'moves': ['e4'], 'turn': ''}

        self.assertEqual(side(state), 'b')

    def test_even_count(self):

        state = {'pieces': [], 'moves': []}

        self.assertEqual(side(state), 'w')


class RightsTest(unittest.TestCase):

    def test_bare_board(self):

        self.assertEqual(rights(chess.Board(None)), '-')

    def test_start_board(self):

        self.assertEqual(rights(chess.Board()), 'KQkq')

    def test_lost_rook(self):

        board = chess.Board()
        board.remove_piece_at(chess.H1)

        self.assertEqual(rights(board), 'Qkq')


if __name__ == '__main__':
    unittest.main()
