import configparser
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

LINUXPATH = config['DEFAULT'].get('linuxpath')
REREAD = config['DEFAULT'].getboolean('REREAD_ON_QUERY')
IP_ADRESS = config['DEFAULT'].get('IP_ADDRESS')
PORT = config['DEFAULT'].getint('PORT')

HASHMAP = defaultdict(lambda: -1)
NEW_LINE = '\r\n'
ENCODING = 'utf-8'
MAX_BYTE = 1024
ERROR_START = 'ERROR'
ERROR_MSG = 'INTERNAL SERVER ERROR'
DEBUG_START = NEW_LINE + 'DEBUG:' + NEW_LINE

NOT_FOUND_MESSAGE = 'STRING NOT FOUND'
FOUND_MESSAGE = 'STRING EXISTS'

OVERFLOW_MESSAGE = 'maximum payload size is'

logging.debug('linuxpath: {!r}'.format(LINUXPATH))
logging.debug('REREAD_ON_QUERY: {!r}'.format(REREAD))
