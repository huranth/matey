# matey

Draws the best move over a live chess.com game with Stockfish.
The board is read from the page, so screen size and pixels do not matter.

## Setup

1. `pip install -r requirements.txt`
2. Download Stockfish and put the exe path in `config.cfg`.
3. Open `chrome://extensions`, turn on Developer mode, click Load unpacked
   and pick the `ext` folder.
4. Open chess.com and start a game.
5. Run `python main.py`.

Reload the extension and refresh the tab after changing anything in `ext`.
Steps 4 and 5 can happen in either order.

Auto play clicks through Chrome DevTools, so Chrome shows its
"started debugging this browser" bar while it is on.

## Config

`config.cfg` holds `autoPlay` (1 turns it on), `engine`, `threads`, `elo`
(1320-3190, 2000 plays like a strong club player) and `moveTime` in milliseconds.
Port 8765 is fixed in `net/bridge.py` and `ext/back.js`. Change both together.

## Limits

Live and bot games only, not puzzles or daily games. Board flips are handled.
Promotions auto-pick a queen.

Engine help in rated games against people is a ban. Play bots.
