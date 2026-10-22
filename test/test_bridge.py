# Bridge tests

import json
import socket
import unittest
from urllib.request import Request, urlopen

from net import bridge


# Call
def call(port, path, body=None):

    data = json.dumps(body).encode() if body is not None else None
    request = Request('http://127.0.0.1:%d%s' % (port, path), data=data)
    request.add_header('Content-Type', 'application/json')

    with urlopen(request) as answer:
        return json.loads(answer.read())


# Raw
def raw(port, path, text):

    request = Request('http://127.0.0.1:%d%s' % (port, path), data=text.encode())
    request.add_header('Content-Type', 'application/json')

    with urlopen(request) as answer:
        return json.loads(answer.read())


class BridgeTest(unittest.TestCase):

    # Fresh
    def setUp(self):

        bridge.STATE.clear()
        bridge.PLAN.clear()

        self.server = bridge.start(0)
        self.port = self.server.server_address[1]

        self.state = {
            'active': True,
            'stamp': 'abc',
            'flipped': False,
            'pieces': [{'square': 'e2', 'piece': 'P'}],
            'moves': ['e4'],
            'turn': 'b',
            'over': False,
        }

    def tearDown(self):

        self.server.shutdown()
        self.server.server_close()

    # State
    def test_state_round_trip(self):

        answer = call(self.port, '/state', self.state)

        self.assertEqual(answer, {})
        self.assertEqual(bridge.latest(), self.state)

    # Plan
    def test_plan_in_reply(self):

        bridge.plan('fen text', 'e2e4', True, 'abc', 2.4, 1760000000000)
        answer = call(self.port, '/state', self.state)

        self.assertEqual(answer['fen'], 'fen text')
        self.assertEqual(answer['best'], 'e2e4')
        self.assertTrue(answer['auto'])
        self.assertEqual(answer['stamp'], 'abc')
        self.assertEqual(answer['delay'], 2.4)
        self.assertEqual(answer['until'], 1760000000000)

    # Bad JSON
    def test_bad_json(self):

        call(self.port, '/state', self.state)
        answer = raw(self.port, '/state', '{oops')

        self.assertEqual(answer, {'error': 'bad json'})
        self.assertEqual(bridge.latest(), self.state)

    # GET
    def test_get(self):

        call(self.port, '/state', self.state)
        bridge.plan('fen text', 'e2e4', False, 'abc', 1.1, 1760000000000)
        answer = call(self.port, '/')

        self.assertEqual(answer['state'], self.state)
        self.assertEqual(answer['plan']['best'], 'e2e4')
        self.assertEqual(answer['plan']['delay'], 1.1)
        self.assertEqual(answer['plan']['until'], 1760000000000)
        self.assertFalse(answer['plan']['auto'])


class PortTest(unittest.TestCase):

    # Busy port
    def test_listening_port(self):

        server = bridge.start(0)
        port = server.server_address[1]

        try:
            self.assertTrue(bridge.taken(port))
        finally:
            server.shutdown()
            server.server_close()

    # Free port
    def test_free_port(self):

        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]

        self.assertFalse(bridge.taken(port))

    # Refused
    def test_second_bridge(self):

        server = bridge.start(0)
        port = server.server_address[1]

        try:
            self.assertRaises(OSError, bridge.start, port)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
