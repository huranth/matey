# Main

from cfg.setting import engine_path, number
from eng.engine import Engine
from game.loop import run
from net.bridge import PORT, start


# Start
def main():

    try:
        start(PORT)
    except OSError:
        raise SystemExit('Port %d is busy. Close the other main.py.' % PORT)

    print('Bridge: http://127.0.0.1:' + str(PORT), flush=True)

    print('Starting stockfish...', flush=True)

    engine = Engine(
        engine_path(),
        number('threads'),
        number('elo'),
        number('moveTime'),
    )

    print('Waiting for chess.com. Press Ctrl+C to stop.', flush=True)

    try:
        run(engine)
    except KeyboardInterrupt:
        engine.stop()
        print('\nStopped.', flush=True)


if __name__ == '__main__':
    main()
