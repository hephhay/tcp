import configparser
import logging
import pathlib
import sys
import unittest
import asyncio
import tracemalloc

# third party libraries
import serial_asyncio

PACKAGE_PATH = str(pathlib.Path(sys.argv[0]).absolute().parent.parent)
sys.path.append(PACKAGE_PATH)
__package__ = PACKAGE_PATH

# Project Modules
from as_tcp import (
    FOUND_MESSAGE,
    NOT_FOUND_MESSAGE,
    ServerProtocol,
    REREAD,
    hash_file,
    load_file,
    OVERFLOW_MESSAGE
)

[found_str, not_found_str, b'ab'*513]
[FOUND_MESSAGE, NOT_FOUND_MESSAGE, OVERFLOW_MESSAGE]

# track memory allocaton
tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

config = configparser.ConfigParser()
config.read('config.ini')

TEST_FILE_PATH = config['TEST'].get('filepath')
IP_ADRESS = config['TEST'].get('IP_ADDRESS')
PORT = config['TEST'].getint('PORT')

CONN_STRING = 'socket://{}:{}'.format(IP_ADRESS, str(PORT))

logging.basicConfig(level=logging.DEBUG)

done = found_str = not_found_str = received = actions = None

class TestClientProtocol(asyncio.Protocol):
    def __init__(self):
        super().__init__()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

        # Send data to server
        for data in self.send_data():
            transport.write(data)
            logging.debug('Data sent: {!r}'.format(data))

        # sets the current action to opened connection
        actions.append('open')

    def send_data(self):
        return [found_str, not_found_str, b'ab'*513]

    def data_received(self, data):
        logging.debug('Data received: {!r}'.format(data.decode()))
        received.append(data)

    def connection_lost(self, exc):
        logging.debug('The server closed the connection')

        # sets the current action to closed
        actions.append('close')

        # 
        done.set()

class TestServerProtocol(ServerProtocol):
    def get_bytes(self):
        return load_file(TEST_FILE_PATH)

    def data_received(self, data):
        super().data_received(data)

        logging.debug('Close the client socket')
        self.transport.close()

class IntegrationTestCases(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.get_event_loop()

        # Set global variables
        global done, found_str, not_found_str, received, actions
        done = asyncio.Event()
        found_str = b'7;0;21;28;0;24;5;0;'
        not_found_str = b'algorithmic'
        received = []
        actions = []

        # File Operation
        if not REREAD:
            hash_file(load_file(TEST_FILE_PATH))

        return super().setUp()

    def tearDown(self):
        self.loop.close()

        # Unset Global Variables
        global done, found_str, not_found_str, received, actions
        done = found_str = not_found_str = received = actions = None

        return super().tearDown()

    def run_connection(self):
        # Setting up server
        coro = self.loop.create_server(TestServerProtocol, IP_ADRESS, PORT)
        self.loop.run_until_complete(coro)

        # Setting up client
        client = serial_asyncio.create_serial_connection(
            self.loop,
            TestClientProtocol,
            CONN_STRING)

        # Start event Loop and wait till all event is done
        self.loop.run_until_complete(client)
        self.loop.run_until_complete(done.wait())
        pending = asyncio.all_tasks(self.loop)
        self.loop.run_until_complete(asyncio.gather(*pending))

        # expected results
        self.expected = map(
            lambda val: val.encode(),
            [FOUND_MESSAGE, NOT_FOUND_MESSAGE, OVERFLOW_MESSAGE]
        )

    def test_connection(self):
        self.run_connection()

        # Test that all recieved data matches expected output
        for output, expected in zip(received, self.expected):
            self.assertIn(expected, output)

        # Test that actions occur in the correct order
        self.assertEqual(actions, ['open', 'close'])

snapshot2 = tracemalloc.take_snapshot()

# compare memory difference between the two snapshopts
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

# Top 10 diffrences
for stat in top_stats[:10]:
    logging.warning(stat)

if __name__ == '__main__':
    unittest.main()