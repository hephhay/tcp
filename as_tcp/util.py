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
    logging
)

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
        if is_empty(line):
            break
        line = line.strip()
        if is_empty(line):
            continue
        HASHMAP[line] = 1

    logging.debug('file hashed successfully')

def is_empty(word):
    return True if word == b'' else False

def get_message(value):
    if value < 0:
        logging.debug(NOT_FOUND_MESSAGE)
        return NOT_FOUND_MESSAGE

    logging.debug(FOUND_MESSAGE)
    return FOUND_MESSAGE

def add_new_line(word):
    return word + bytes(NEW_LINE, ENCODING)

def debug_message(**kwargs):
    debug_str = ''

    for key, value in kwargs.items():
        debug_str += '\t {}: {}{}'.format(key, value, NEW_LINE)

    logging.debug(debug_str)
    return debug_str

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