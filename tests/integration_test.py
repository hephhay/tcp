import configparser
import logging
import pathlib
import sys
import unittest
import asyncio
import tracemalloc
from timeit import default_timer as timer

# third party libraries
import serial_asyncio

# set package scope to as_tcp
# PACKAGE_PATH = str(pathlib.Path(sys.argv[0]).absolute().parent.parent)
# sys.path.append(PACKAGE_PATH)
# __package__ = PACKAGE_PATH

# Project Modules
from as_tcp import (
    FOUND_MESSAGE,
    NOT_FOUND_MESSAGE,
    ServerProtocol,
    REREAD,
    hash_file,
    load_file,
    logging
)

logging.basicConfig(level=logging.DEBUG)

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
    """
    Base TestClient to be used for testing
    """

    def __init__(self):
        super().__init__()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

        # Send data to server
        data = self.send_data()
        transport.write(data)
        logging.debug('Data sent: {!r}'.format(data))

        # sets the current action to opened connection
        actions.append('open')

    def send_data(self):
        """
        Called to get the string to be sent to server

        Returns:
        bytes: string to be sent to server

        """

        pass

    def data_received(self, data):
        logging.debug('Data received: {!r}'.format(data.decode()))
        global received
        received = data

    def connection_lost(self, exc):
        logging.debug('The server closed the connection')

        # sets the current action to closed
        actions.append('close')

        # Notify Event loop abount connection ended
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
        received = ''
        actions = []

        return super().setUp()

    def tearDown(self):
        # close the curent event loop
        self.loop.close()

        # create a new event loop and make it the current event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Unset Global Variables
        global done, found_str, not_found_str, received, actions
        done = found_str = not_found_str = received = actions = None

        return super().tearDown()

    def run_connection(self, output_client):
        """
        start both the TCP client and server when called

        Parameters:
        output_client (TestClientProtocol): client class for testing

        Returns:
        None

        """

        # Setting up server
        coro = self.loop.create_server(TestServerProtocol, IP_ADRESS, PORT)
        self.loop.run_until_complete(coro)

        # Loading and hashing file
        if not REREAD:
            hash_file(load_file(TEST_FILE_PATH))

        # Setting up client
        client = serial_asyncio.create_serial_connection(
            self.loop,
            output_client,
            CONN_STRING)

        # Start event Loop and wait till all event is done
        self.loop.run_until_complete(client)
        self.loop.run_until_complete(done.wait())
        pending = asyncio.all_tasks(self.loop)
        self.loop.run_until_complete(asyncio.gather(*pending))

    def get_output_client(self, input_data):
        """
        Called to get the client class for testing

        Parameters:
        input_data (bytes): bytes string to be sent to the server

        Returns:
        TestClientProtocol: clent class for testing

        """

        class OuputClient(TestClientProtocol):
            def send_data(self):
                return input_data

        return OuputClient

    def assert_order(self):
        global REREAD
        REREAD = True

        self.assertEqual(actions, ['open', 'close'])

    """
    test for success when REREAD is True and query not in file
    """
    def test_reread_not_found_success(self):
        self.run_connection(self.get_output_client(found_str))

        """Test that all recieved data matches expected output"""
        self.assertIn(FOUND_MESSAGE, received.decode())
        self.assert_order()

    """
    test for success when REREAD is True and query is in file
    """
    def test_reread_found_success(self):
        global REREAD
        REREAD = True

        self.run_connection(self.get_output_client(not_found_str))

        """Test that all recieved data matches expected output"""
        self.assertIn(NOT_FOUND_MESSAGE, received.decode())
        self.assert_order()

    """
    test for success when REREAD is True and query longer than 1024 bytes
    """
    def test_reread_overflow_success(self):
        global REREAD
        REREAD = True

        self.run_connection(self.get_output_client(b'ab'*513))

        """Test that all recieved data matches expected output"""
        self.assertIn('ab'*3, received.decode())
        self.assert_order()

    """
    test for success when REREAD is False and query not in file
    """
    def test_reread_false_found_success(self):
        global REREAD
        REREAD = False

        self.test_reread_found_success()

    """
    test for success when REREAD is False and query is in file
    """
    def test_reread_false_not_found_success(self):
        global REREAD
        REREAD = False

        self.test_reread_not_found_success()

    """
    test for success when REREAD is False and query longer than 1024 bytes
    """
    def test_reread_false_overflow_success(self):
        global REREAD
        REREAD = False

        self.test_reread_overflow_success()


snapshot2 = tracemalloc.take_snapshot()

# compare memory difference between the two snapshopts
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

# Top 10 diffrences
for stat in top_stats[:10]:
    logging.warning(stat)

if __name__ == '__main__':
    unittest.main()
