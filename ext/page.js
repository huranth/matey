// Chess reader

const POLL = 200;
const GAP = 50;
const STALL = 5000;
const MOVE_GAP = 140;
const PROMO_DELAY = 450;
const NEXT_DELAY = 1500;

const PAD = 5;
const LINE = 5;
const BOX = '#0000ff';

const FILES = 'abcdefgh';
const NEXT = /^new\s+\d+/i;
const PIECE = /^[wb][pnbrqk]$/;
const SQUARE = /^square-(\d)(\d)$/;
const END = '.game-over-controls-topControls, .live-game-buttons-game-over';
const SAN = new RegExp(
    '(O-O-O|O-O|' +
    '[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8]' +
    '(?:=[QRBN])?[+#]?)',
    'g'
);


// State
let warned = false;
let mark = '';
let seen = 0;
let played = '';
let asked = '';
let busy = false;
let queued = false;


// Canvas
const canvas = document.createElement('canvas');

canvas.style.position = 'fixed';
canvas.style.display = 'none';
canvas.style.zIndex = '2147483000';
canvas.style.pointerEvents = 'none';
canvas.style.padding = '0';
canvas.style.margin = '0';
document.body.appendChild(canvas);


// Alive
function alive() {

    return Boolean(chrome.runtime && chrome.runtime.id);
}


// Warn
function warn(text) {

    if (warned) return;

    warned = true;
    console.warn(text);
}


// Board
function board() {

    return document.querySelector('wc-chess-board');
}


// Square
function squareOf(node) {

    for (const name of node.classList) {
        const hit = name.match(SQUARE);

        if (hit) {
            return FILES[Number(hit[1]) - 1] + hit[2];
        }
    }

    return '';
}


// Piece
function pieceOf(node) {

    for (const name of node.classList) {
        if (PIECE.test(name)) {
            return name[0] === 'w' ? name[1].toUpperCase() : name[1];
        }
    }

    return '';
}


// Pieces
function pieces(node) {

    const list = [...node.querySelectorAll('.piece')];

    return list.map(item => ({
        square: squareOf(item),
        piece: pieceOf(item),
    })).filter(item => item.square && item.piece);
}


// Moves
function moves() {

    const list = [];

    for (const node of document.querySelectorAll('.node')) {
        for (const move of node.textContent.match(SAN) || []) {
            list.push(move);
        }
    }

    return list;
}


// Turn
function turn(list) {

    const clock = document.querySelector('.clock-player-turn');

    if (clock) {
        if (clock.classList.contains('clock-white')) return 'w';
        if (clock.classList.contains('clock-black')) return 'b';
    }

    return list.length % 2 === 0 ? 'w' : 'b';
}


// Clock
function seconds() {

    const node = document.querySelector('.clock-player-turn');

    if (!node) return 0;

    const parts = node.textContent.replace(/\s+/g, '').split(':');

    if (parts.length !== 2) return 0;

    return Number(parts[0]) * 60 + Number(parts[1]) || 0;
}


// Over
function over(node) {

    if (!node) return true;
    if (document.querySelector(END)) return true;

    return Boolean(nextButton());
}


// Stamp
function stamp(items, list, side) {

    const text = [...items]
        .sort((a, b) => a.square.localeCompare(b.square))
        .map(item => item.square + item.piece)
        .join('');

    return text + '|' + list.length + '|' + side;
}


// Read
function read() {

    const node = board();
    const items = node ? pieces(node) : [];
    const list = moves();
    const side = turn(list);
    const key = stamp(items, list, side);

    if (key !== mark) {
        mark = key;
        seen = Date.now();
    }

    return {
        active: Boolean(node),
        stamp: key,
        flipped: node ? node.classList.contains('flipped') : false,
        pieces: items,
        moves: list,
        turn: side,
        seen: seen,
        clock: seconds(),
        over: over(node),
    };
}


// Our side
function ourColor(state) {

    return state.flipped ? 'b' : 'w';
}


// Clear
function clear() {

    canvas.style.display = 'none';
}


// Size
function size(rect) {

    return Math.min(rect.width, rect.height) / 8;
}


// Offset
function offset(square, flipped, size) {

    const file = FILES.indexOf(square[0]);
    const rank = Number(square[1]) - 1;

    const x = flipped ? 7 - file : file;
    const y = flipped ? rank : 7 - rank;

    return [x * size, y * size];
}


// Box
function box(ctx, square, flipped, size) {

    const [x, y] = offset(square, flipped, size);

    ctx.strokeStyle = BOX;
    ctx.lineWidth = LINE;
    ctx.strokeRect(x + PAD, y + PAD, size - PAD * 2, size - PAD * 2);
}


// Centre
function centre(square, flipped) {

    const node = board();
    if (!node) return null;

    const rect = node.getBoundingClientRect();
    const side = size(rect);

    const [x, y] = offset(square, flipped, side);

    return [rect.left + x + side / 2, rect.top + y + side / 2];
}


// Click
function click(x, y) {

    chrome.runtime.sendMessage({ type: 'click', x, y });
}


// Jitter
function jitter(base) {

    return base * (0.6 + Math.random() * 0.8);
}


// Draw
function draw(state, plan) {

    const node = board();

    if (!node || !plan || !plan.best) return clear();
    if (plan.stamp !== state.stamp) return clear();
    if (state.turn !== ourColor(state)) return clear();
    if (state.over) return clear();

    const rect = node.getBoundingClientRect();
    const scale = window.devicePixelRatio || 1;
    const side = size(rect);

    canvas.style.display = 'block';
    canvas.style.left = rect.left + 'px';
    canvas.style.top = rect.top + 'px';
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';

    canvas.width = Math.round(rect.width * scale);
    canvas.height = Math.round(rect.height * scale);

    const ctx = canvas.getContext('2d');
    ctx.setTransform(scale, 0, 0, scale, 0, 0);

    const move = plan.best;
    box(ctx, move.slice(0, 2), state.flipped, side);
    box(ctx, move.slice(2, 4), state.flipped, side);
}


// Play
function play(state, plan) {

    if (!plan || !plan.auto) return;
    if (!plan.best || plan.stamp !== state.stamp) return;
    if (state.turn !== ourColor(state)) return;
    if (state.over || played === state.stamp) return;

    played = state.stamp;

    const move = plan.best;
    const gap = jitter(MOVE_GAP);

    let wait = (Number(plan.delay) || 0) * 1000;

    // Deadline
    if (plan.until) {
        wait = Math.max(0, plan.until - Date.now() - gap);
    }

    setTimeout(() => {

        const now = read();

        if (now.stamp !== state.stamp) return;

        const from = centre(move.slice(0, 2), now.flipped);
        const to = centre(move.slice(2, 4), now.flipped);

        if (!from || !to) return;

        click(...from);

        setTimeout(() => {

            click(...to);

            if (move.length !== 5) return;

            setTimeout(() => {
                const again = centre(move.slice(2, 4), now.flipped);
                if (again) click(...again);
            }, jitter(PROMO_DELAY));

        }, gap);

    }, wait);
}


// Next
function nextButton() {

    const nodes = document.querySelectorAll('button, [role="button"], a');

    for (const node of nodes) {
        const text = node.textContent.replace(/\s+/g, ' ').trim();

        if (!NEXT.test(text)) continue;
        if (!node.getBoundingClientRect().width) continue;

        return node;
    }

    return null;
}


// Restart
function restart(state, plan) {

    if (!state.over) {
        asked = '';
        return;
    }

    if (!plan || !plan.auto) return;
    if (asked === state.stamp) return;

    const node = nextButton();
    if (!node) return;

    asked = state.stamp;

    setTimeout(() => {

        const rect = node.getBoundingClientRect();

        if (!rect.width) return;

        click(rect.left + rect.width / 2, rect.top + rect.height / 2);

    }, jitter(NEXT_DELAY));
}


// Stop
function stop() {

    watcher.disconnect();
    clearInterval(timer);

    canvas.remove();
}


// Tick
function tick() {

    if (busy) return;
    if (!alive()) return stop();

    busy = true;

    // Stall guard
    setTimeout(() => { busy = false; }, STALL);

    const state = read();

    try {
        chrome.runtime.sendMessage({ type: 'state', state }, plan => {

            busy = false;

            if (!alive()) return;

            if (chrome.runtime.lastError) {
                warn('Extension reloaded. Refresh this tab.');
                return;
            }

            if (!plan) warn('Bridge is down. Start main.py.');

            draw(state, plan);
            play(state, plan);
            restart(state, plan);

        });
    } catch (error) {
        busy = false;
        return stop();
    }
}


// Ping
function ping() {

    if (queued) return;

    queued = true;

    setTimeout(() => {
        queued = false;
        tick();
    }, GAP);
}


// Watch
const watcher = new MutationObserver(ping);

watcher.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
});


// Poll
const timer = setInterval(tick, POLL);

tick();
