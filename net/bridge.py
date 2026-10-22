# Bridge

import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOCK = threading.Lock()
PORT = 8765
STATE = {}
PLAN = {}


# Port taken
def taken(port):

    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', port))
        except OSError:
            return True

    return False


# Latest
def latest():

    with LOCK:
        return dict(STATE)


# Plan
def plan(fen, best, auto, stamp, delay, until):

    with LOCK:
        PLAN.update(
            fen=fen,
            best=best,
            auto=auto,
            stamp=stamp,
            delay=delay,
            until=until,
        )


# Handler
class Handler(BaseHTTPRequestHandler):

    # Reply
    def reply(self, body):

        data = json.dumps(body).encode()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(data)

    # Silent
    def log_message(self, *args):

        pass

    # Preflight
    def do_OPTIONS(self):

        self.reply({})

    # Status
    def do_GET(self):

        with LOCK:
            body = {'state': dict(STATE), 'plan': dict(PLAN)}

        self.reply(body)

    # Post
    def do_POST(self):

        size = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(size)

        try:
            state = json.loads(body)
        except ValueError:
            self.reply({'error': 'bad json'})
            return

        with LOCK:
            STATE.clear()
            STATE.update(state)
            answer = dict(PLAN)

        self.reply(answer)


# Start
def start(port):

    if taken(port):
        raise OSError('Port ' + str(port) + ' is busy')

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)

    thread.start()
    return server
