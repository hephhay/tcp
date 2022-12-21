import configparser
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict
from pathlib import Path
from os import path
import sys

MAX_BYTE = 1024
BASE_DIR = Path(__file__).resolve().parent
INI_FILE = 'config.ini'

# setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

file_handler = RotatingFileHandler(
    BASE_DIR / 'logs.log',
    maxBytes=MAX_BYTE + MAX_BYTE
)
file_handler.setFormatter(formatter)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

config = configparser.ConfigParser()
config.read(BASE_DIR / INI_FILE)

LINUXPATH = config['DEFAULT'].get('LINUXPATH')
REREAD = config['DEFAULT'].getboolean('REREAD_ON_QUERY')
IP_ADRESS = config['DEFAULT'].get('IP_ADDRESS')
PORT = config['DEFAULT'].getint('PORT')

TEST_STRING = config['TEST'].get('TEST_STRING').encode()

# check if linux path configuration is absolute or relative
if path.exists(LINUXPATH):
    FILEPATH = LINUXPATH
elif path.exists(BASE_DIR / LINUXPATH):
    FILEPATH = BASE_DIR / LINUXPATH
else:
    raise FileNotFoundError('{!r} does not exist \
        please edit "LINUXPATH" in {!r}'.format(
            LINUXPATH,
            BASE_DIR / INI_FILE))

HASHMAP = defaultdict(lambda: -1)
NEW_LINE = '\r\n'
ENCODING = 'utf-8'
ERROR_START = 'ERROR'
ERROR_MSG = 'INTERNAL SERVER ERROR'
DEBUG_START = NEW_LINE + 'DEBUG:' + NEW_LINE

NOT_FOUND_MESSAGE = 'STRING NOT FOUND'
FOUND_MESSAGE = 'STRING EXISTS'

OVERFLOW_MESSAGE = 'maximum payload size is'

logger.debug('FILEPATH: {!r}'.format(FILEPATH))
logger.debug('REREAD_ON_QUERY: {!r}'.format(REREAD))
