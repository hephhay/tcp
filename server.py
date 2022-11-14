import asyncio
import configparser
import logging
import mmap
from collections import defaultdict
from timeit import default_timer as timer

#third party libraries
from aiorun import run

logging.basicConfig(level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('./config.ini')

LINUXPATH = config['DEFAULT'].get('linuxpath')
REREAD = config['DEFAULT'].getboolean('REREAD_ON_QUERY')

HASHMAP = defaultdict(lambda : -1)
NEW_LINE = '\r\n'
ENCODING = 'utf-8'

NOT_FOUND_MESSAGE = 'STRING NOT FOUND'
FOUND_MESSAGE = 'STRING EXISTS'

logging.debug('linuxpath: {!r}'.format(LINUXPATH))
logging.debug('REREAD_ON_QUERY: {!r}'.format(REREAD))


def load_file(path):
    with open(path, "r+b") as f:
        logging.debug('file opened successfully')
        # memory-map the file, size 0 means whole file and return
        mfile = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        logging.debug('file mapped to memmory')
        return mfile

def hash_file(mfile):
    logging.debug('started hashing file')

    while True:
        line = mfile.readline()
        if line == b'':
            break
        HASHMAP[line.strip()] = 1

    logging.debug('file hashed successfully')

def get_message(value):
    if value < 0:
        logging.debug(NOT_FOUND_MESSAGE)
        return NOT_FOUND_MESSAGE

    logging.debug(FOUND_MESSAGE)
    return FOUND_MESSAGE

def add_new_line(word):
    return word + bytes(NEW_LINE, ENCODING)


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(self.peername))
        self.transport = transport

    def data_received(self, data):
        message = data.strip()
        logging.info('Data received: {!r}'.format(message.decode()))

        if REREAD:
            found_val = load_file(LINUXPATH).find(add_new_line(message))
        else:
            found_val = HASHMAP[message]

        res_message = get_message(found_val)

        logging.info('Sending: {!r}'.format(res_message))
        self.transport.write(add_new_line(bytes(res_message, ENCODING)))

        logging.info('Close the client socket')
        self.transport.close()

    def connection_lost(self, exc):
        logging.info('{} is disconnnected'.format(self.peername))
        return super().connection_lost(exc)

async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.

    if not REREAD:
        m_file = load_file(LINUXPATH)
        hash_file(m_file)

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

run(main())