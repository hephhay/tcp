import asyncio
from as_tcp.server import ServerProtocol

# third party libraries
import serial_asyncio

# package Modules
from as_tcp.server import timer
from as_tcp.setup import (
    FILEPATH,
    REREAD,
    TEST_STRING,
    logger,
    config,
)
from as_tcp.util import hash_file, load_file

IP_ADRESS = config['TEST'].get('IP_ADDRESS')
PORT = config['TEST'].getint('PORT')

# create event listener
DONE = asyncio.Event()

# holds time
START = 0.0


class ClientTestServerProtocol(ServerProtocol):
    """
    Client specific Server shuts down after every message
    """

    def get_bytes(self):
        return load_file(FILEPATH)

    def data_received(self, data):
        # start timer
        START = timer()

        super().data_received(data)

        logger.debug('Close the client socket')
        self.transport.close()
        
        logger.info('roundtrip takes {} ms'.format((timer() - START) * 1000))


class ClientProtocol(asyncio.Protocol):
    """
    Client specifcally made for benchmarking serverss
    """

    def __init__(self, message):
        self.message = message

    def connection_made(self, transport):
        transport.write(self.message)
        logger.debug('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        logger.debug('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        logger.debug('The server closed the connection')

        # Notify Event loop abount connection ended
        DONE.set()


if __name__ == '__main__':
    # Loading and hashing file
    if not REREAD:
        hash_file(load_file(FILEPATH))

    # get current event loop
    loop = asyncio.get_event_loop()

    # Setting up server
    coro = loop.create_server(ClientTestServerProtocol, IP_ADRESS, PORT)
    loop.run_until_complete(coro)

    # Setting up client
    client = serial_asyncio.create_serial_connection(
        loop,
        lambda: ClientProtocol(TEST_STRING),
        'socket://{}:{}'.format(IP_ADRESS, str(PORT)))

    # Start event Loop and wait till all event is done
    loop.run_until_complete(client)
    loop.run_until_complete(DONE.wait())
    pending = asyncio.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
