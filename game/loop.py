# Loop

import time

import chess

from cfg.setting import auto_play
from game import timing
from game.state import fen
from net import bridge

GAP = 0.05


# Our turn
def our_turn(data):

    ours = 'b' if data.get('flipped') else 'w'

    return data.get('turn') == ours


# Clock text
def clock_text(seconds):

    if not seconds:
        return '--'

    return '%d:%02d' % (seconds // 60, seconds % 60)


# Main
def run(engine):

    last = ''
    joined = False
    pace = timing.Pace()

    while True:
        data = bridge.latest()

        if data and not joined:
            print('Page connected.', flush=True)
            joined = True

        position = ''

        if data and data.get('active') and not data.get('over'):
            try:
                position = fen(data)
            except (KeyError, ValueError):
                position = ''

        stamp = data.get('stamp', '') if data else ''
        key = (position, stamp)

        if position and key != last:
            last = key

            if our_turn(data):
                plan(engine, pace, data, position)

        time.sleep(GAP)


# One plan
def plan(engine, pace, data, position):

    print('Thinking...', flush=True)

    stamp = data.get('stamp', '')
    ply = len(data.get('moves') or [])
    moves = chess.Board(position).legal_moves.count()
    clock = data.get('clock') or 0

    saw = data.get('seen') or 0
    target = pace.target(clock, moves)
    limit = max(120, int(target * 550))

    best = engine.best(position, ply, limit)

    if not best:
        return

    base = saw / 1000 if saw else time.time()
    until = int((base + target) * 1000)
    now = time.time()

    # Search overran
    if until / 1000 < now:
        until = int((now + 0.15) * 1000)

    delay = max(round(until / 1000 - now, 2), 0)
    total = round(until / 1000 - base, 2)

    bridge.plan(position, best, auto_play(), stamp, delay, until)
    print('Move', best, 'in', total, 's at', clock_text(clock), flush=True)
