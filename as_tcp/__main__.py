# third party libraries
from aiorun import run
import daemon


# Project Modules
from .server import serve
from .setup import IP_ADRESS, PORT

print(__name__)

if __name__ == '__main__':
    run(serve(IP_ADRESS, PORT))
