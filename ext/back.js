// Bridge

const BRIDGE = 'http://127.0.0.1:8765/state';
const ATTACHED = new Set();
const ATTACHING = new Map();
const QUEUE = new Map();


// Ask
async function ask(state) {

    try {
        const reply = await fetch(BRIDGE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state),
        });

        return await reply.json();
    } catch (error) {
        return null;
    }
}


// Messages
chrome.runtime.onMessage.addListener((message, sender, respond) => {

    if (message.type === 'state') {
        ask(message.state).then(respond);
        return true;
    }

    if (message.type === 'click' && sender.tab) {
        click(sender.tab.id, message.x, message.y).then(respond);
        return true;
    }
});


// Attach
async function attach(tabId) {

    if (ATTACHED.has(tabId)) {
        return true;
    }

    if (!ATTACHING.has(tabId)) {
        const task = chrome.debugger.attach({ tabId }, '1.3')
            .then(() => ATTACHED.add(tabId))
            .catch(() => {})
            .finally(() => ATTACHING.delete(tabId));

        ATTACHING.set(tabId, task);
    }

    await ATTACHING.get(tabId);

    return ATTACHED.has(tabId);
}


// Send
async function send(tabId, x, y) {

    if (!await attach(tabId)) {
        return false;
    }

    const press = { x, y, button: 'left', clickCount: 1 };
    const input = 'Input.dispatchMouseEvent';
    const target = { tabId };

    try {
        await chrome.debugger.sendCommand(
            target,
            input,
            { ...press, type: 'mousePressed' },
        );

        await chrome.debugger.sendCommand(
            target,
            input,
            { ...press, type: 'mouseReleased' },
        );

        return true;
    } catch (error) {
        console.warn('Click failed:', error.message);
        ATTACHED.delete(tabId);

        return false;
    }
}


// Click
function click(tabId, x, y) {

    const last = QUEUE.get(tabId) || Promise.resolve();
    const next = last.then(() => send(tabId, x, y));

    QUEUE.set(tabId, next);

    next.finally(() => {
        if (QUEUE.get(tabId) === next) QUEUE.delete(tabId);
    });

    return next;
}


// Cleanup
chrome.tabs.onRemoved.addListener((tabId) => {

    if (!ATTACHED.has(tabId)) {
        return;
    }

    chrome.debugger.detach({ tabId }).catch(() => {});
    ATTACHED.delete(tabId);
});
