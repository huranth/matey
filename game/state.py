# State

import chess


# Board
def place(pieces):

    board = chess.Board(None)

    for item in pieces:
        square = chess.parse_square(item['square'])
        piece = chess.Piece.from_symbol(item['piece'])

        board.set_piece_at(square, piece)

    return board


# Replay
def replay(moves):

    board = chess.Board()

    for move in moves:
        try:
            board.push_san(move)
        except ValueError:
            return None

    return board


# Side
def side(state):

    if state.get('turn'):
        return state['turn']

    return 'w' if len(state['moves']) % 2 == 0 else 'b'


# Rights
def rights(board):

    flags = ''

    for color, text in ((chess.WHITE, 'KQ'), (chess.BLACK, 'kq')):
        rank = '1' if color == chess.WHITE else '8'
        king = chess.Piece(chess.KING, color)
        rook = chess.Piece(chess.ROOK, color)

        if board.piece_at(chess.parse_square('e' + rank)) != king:
            continue

        if board.piece_at(chess.parse_square('h' + rank)) == rook:
            flags += text[0]

        if board.piece_at(chess.parse_square('a' + rank)) == rook:
            flags += text[1]

    return flags or '-'


# Loose
def loose(state):

    board = place(state['pieces'])
    parts = [board.board_fen(), side(state), rights(board), '-', '0', '1']

    return ' '.join(parts)


# FEN
def fen(state):

    board = replay(state.get('moves', []))

    if board and board.board_fen() == place(state['pieces']).board_fen():
        return board.fen()

    return loose(state)
