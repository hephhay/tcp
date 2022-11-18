import mmap
import sys
import traceback

# Project Modules
from .setup import (
    ENCODING,
    FOUND_MESSAGE,
    HASHMAP,
    NEW_LINE,
    NOT_FOUND_MESSAGE,
    logger,
)


def load_file(path):
    """
    loads file from path to memory

    Parameters:
    path(path): path to file location

    Returns:
    bytes: Memory mapped bytes of file

    """

    with open(path, "r+b") as f:
        logger.debug('file opened successfully')
        # memory-map the file, size 0 means whole file and return
        mfile = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        logger.debug('file mapped to memmory')
        return mfile


def hash_file(mfile):
    """
    converts each line of a byte string to hashmap keys

    Parameters:
    mfile(bytes): bytes to be hash mapped

    Returns:
    None

    """

    logger.debug('started hashing file')

    while True:
        line = mfile.readline()
        if is_empty(line):
            break
        line = line.strip()
        if is_empty(line):
            continue
        HASHMAP[line] = 1

    logger.debug('file hashed successfully')


def is_empty(word):
    """
    check if byte is null

    Parameters:
    word(bytes): bytes to be checked

    Returns:
    bool: 'True' if byte is null and 'False' otherwise

    """

    return True if word == b'' else False


def get_message(value):
    if value < 0:
        logger.debug(NOT_FOUND_MESSAGE)
        return NOT_FOUND_MESSAGE

    logger.debug(FOUND_MESSAGE)
    return FOUND_MESSAGE


def add_new_line(word):
    return word + bytes(NEW_LINE, ENCODING)


def debug_message(**kwargs):
    """
    gets server debug message

    Parameters:
    kwargs(**kwargs): key value pair containing debug tages and values

    Returns:
    string: debug message

    """

    debug_str = ''

    for key, value in kwargs.items():
        debug_str += '\t {}: {}{}'.format(key, value, NEW_LINE)

    logger.debug(debug_str)
    return debug_str


def default_exception():
    """
    gracefull handling and logger of exceptions

    Returns:
    None

    """

    # Get current system exception
    ex_type, ex_value, ex_traceback = sys.exc_info()

    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)

    # Format stacktrace
    stack_trace = list()

    for trace in trace_back:
        stack_trace.append('File : {} , Line : {}, \
            Func.Name : {}, Message : {}'.format(*trace))

    logger.error('Exception type : {}'.format(ex_type.__name__))
    logger.error('Exception message : {}'.format(ex_value))
    logger.error('Stack trace : {}'.format(stack_trace))
