import asyncio

# project packages
from .setup import TEST_STRING, logger


class ClientProtocol(asyncio.Protocol):
    """
    Base Client to be used for testing
    """

    def connection_made(self, transport):
        self.transport = transport

        # Send data to server
        data = self.send_data()
        transport.write(data)
        logger.debug('Data sent: {!r}'.format(data))

    def send_data(self):
        """
        Called to get the string to be sent to server

        Returns:
        bytes: string to be sent to server

        """

        return TEST_STRING

    def data_received(self, data):
        logger.debug('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        logger.debug('The server closed the connection')
