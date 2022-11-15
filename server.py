import asyncio
import configparser
import logging
import mmap
import sys
import traceback
from collections import defaultdict
from datetime import datetime
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
MAX_BYTE = 1024
ERROR_START = 'ERROR'
ERROR_MSG = 'INTERNAL SERVER ERROR'
DEBUG_START = NEW_LINE + 'DEBUG:' + NEW_LINE

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

def default_exception():
    # Get current system exception
    ex_type, ex_value, ex_traceback = sys.exc_info()

    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)

    # Format stacktrace
    stack_trace = list()

    for trace in trace_back:
        stack_trace.append('File : {} , Line : {}, Func.Name : {}, Message : {}'\
            .format(trace[0], trace[1], trace[2], trace[3]))

    logging.error('Exception type : {}'.format(ex_type.__name__))
    logging.error('Exception message : {}'.format(ex_value))
    logging.error('Stack trace : {}'.format(stack_trace))

def debug_message(**kwargs):
    debug_str = ''

    for key, value in kwargs.items():
        debug_str += '\t {}: {}{}'.format(key, value, NEW_LINE)

    logging.debug(debug_str)
    return debug_str


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(self.peername))
        self.transport = transport

    def data_received(self, data):
        start = timer()
        start_time = datetime.now()

        try:
            if (len(data) > MAX_BYTE):
                raise ValueError('maximum payload size is {}'\
                    .format(MAX_BYTE))

            message = data.strip()
            logging.info('{} Data received: {!r}'\
                .format(self.peername, message.decode(errors='ignore')))

            if REREAD:
                found_val = load_file(LINUXPATH).find(add_new_line(message))
            else:
                found_val = HASHMAP[message]

            res_message = get_message(found_val)

        except ValueError as err:
            res_message = str(err)
            logging.error(res_message)
            res_message = ERROR_START+ ': ' + res_message

        except Exception:
            res_message = ERROR_MSG
            default_exception()

        finally:
            res_message += DEBUG_START + debug_message(
                IP_ADDRESS = self.peername[0],
                PORT = self.peername[1],
                EXECUTION_TIME = '{} ms'.format((timer() -start) * 1000),
                SEARCH_QUERY = message.decode(errors='ignore'),
                REREAD_ON_QUERY = REREAD,
                START_TIME = start_time,
                END_TIME = datetime.now(),
            )

            logging.info('{} Sending: {!r}'\
                .format(self.peername, res_message))
            self.transport.write(add_new_line(bytes(res_message, ENCODING)))

            # logging.info('Close the client socket')
            # self.transport.close()

    def connection_lost(self, exc):
        logging.info('{} is disconnnected'.format(self.peername))
        return super().connection_lost(exc)

async def main():

    if not REREAD:
        m_file = load_file(LINUXPATH)
        hash_file(m_file)

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '0.0.0.0', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

run(main())