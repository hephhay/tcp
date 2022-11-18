# third party libraries
from aiorun import run
import daemon


# Project Modules
from .server import serve
from .setup import IP_ADRESS, PORT, REREAD, FILEPATH, logger
from .util import load_file, hash_file

if __name__ == '__main__':
    if not REREAD:
        m_file = load_file(FILEPATH)
        hash_file(m_file)

    logger.info('Serving on {}'.format((IP_ADRESS, PORT)))

    # start server deamon
    with daemon.DaemonContext():
        run(serve(IP_ADRESS, PORT))
