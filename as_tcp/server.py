import asyncio
from datetime import datetime
from timeit import default_timer as timer

# Project Modules
from .setup import (
    logging,
    DEBUG_START,
    ENCODING,
    ERROR_MSG,
    ERROR_START,
    HASHMAP,
    LINUXPATH,
    MAX_BYTE,
    OVERFLOW_MESSAGE,
    REREAD
)
from .util import (
    add_new_line,
    debug_message,
    default_exception,
    get_message,
    hash_file,
    load_file
)


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(self.peername))
        self.transport = transport

    def get_bytes(self):
        """
        Called to get the memeory mapped file for lookup

        Returns:
        bytes: bytes to be looked up

        """

        return load_file(LINUXPATH)

    def data_received(self, data):
        start = timer()
        start_time = datetime.now()

        message = data
        try:
            # Check for query overflow
            if (len(message) > MAX_BYTE):
                raise ValueError('{} {}'.format(OVERFLOW_MESSAGE, MAX_BYTE))

            # removes null and empty characters from string
            message = message.strip()
            logging.info('{} Data received: {!r}'.format(
                self.peername,
                message.decode(errors='ignore')))

            if REREAD:
                found_val = self.get_bytes().find(add_new_line(message))
            else:
                found_val = HASHMAP[message]

            res_message = get_message(found_val)

        # handle overflow exeption
        except ValueError as err:
            res_message = str(err)
            logging.error(res_message)
            res_message = ERROR_START + ': ' + res_message

        # handle other server errors
        except Exception:
            res_message = ERROR_MSG
            default_exception()

        finally:
            # add debug messages to response
            res_message += DEBUG_START + debug_message(
                IP_ADDRESS=self.peername[0],
                PORT=self.peername[1],
                EXECUTION_TIME='{} ms'.format((timer() - start) * 1000),
                SEARCH_QUERY=message.decode(errors='ignore'),
                REREAD_ON_QUERY=REREAD,
                START_TIME=start_time,
                END_TIME=datetime.now()
            )

            logging.info('{} Sending: {!r}'.format(self.peername, res_message))
            self.transport.write(add_new_line(bytes(res_message, ENCODING)))

    def connection_lost(self, exc):
        logging.info('{} is disconnnected'.format(self.peername))
        return super().connection_lost(exc)


async def serve(ip_address, port):
    """
    Starts and serves the asynchronous server

    Parameters:
    ip_address(string): IP Address to server the server
    port(int): Port where server will be served

    Returns:
    None

    """

    if not REREAD:
        m_file = load_file(LINUXPATH)
        hash_file(m_file)

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ServerProtocol(),
        ip_address, port)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()
