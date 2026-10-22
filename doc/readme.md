# chess.com moves

Draws the best move over a live chess.com game with Stockfish.
The board is read from the page, so pixels and screen size no longer matter.

## Setup

1. `pip install -r requirements.txt`
2. Download Stockfish and put the exe path in `config.cfg`.
3. Open `chrome://extensions`, turn on Developer mode, click Load unpacked
   and pick the `ext` folder. After reloading the extension, refresh the
   chess.com tab.
4. Open chess.com and start a game.
5. Run `python main.py`.

`main.py` serves the local bridge on `127.0.0.1:8765` and waits for the page.
Steps 4 and 5 can happen in either order.

## How it works

The page script sends the board and clocks to the bridge. `game/state.py`
turns that into a FEN, Stockfish answers, and the page draws blue boxes on
the best move.

Think time drifts from move to move: a mood that carries between moves,
faster on simple boards, the odd long think. The plan carries a wall-clock
deadline, so the click lands when the clock says, not after another round
trip. Only your own moves are planned.

Auto play clicks through Chrome DevTools, so Chrome shows its
"started debugging this browser" bar while it is on.

## Config

`config.cfg` holds `autoPlay` (1 turns it on), `engine`, `threads`, `elo`
(1320-3190, 2000 plays like a strong club player) and `moveTime` in milliseconds.
Port 8765 is fixed in `net/bridge.py` and `ext/back.js`. Change both together.

## Limits

Live and bot games only, not puzzles or daily games. Board flips are handled.
Promotions auto-pick a queen.

The chess.com tab can stay in the background. Add the site to Chrome's
"always keep these sites active" list so Memory Saver does not discard it.

Engine help in rated games against people is a ban. Play bots.
