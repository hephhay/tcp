import configparser
import io
import logging
import mmap
from os import path
import unittest

# Project Modules
from as_tcp import (
    load_file,
    HASHMAP,
    hash_file,
    is_empty,
    add_new_line,
    get_message,
    NOT_FOUND_MESSAGE,
    FOUND_MESSAGE,
    logger
)
from as_tcp.setup import BASE_DIR

INI_FILE = 'config.ini'

logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read(BASE_DIR / INI_FILE)

LINUXPATH = config['TEST'].get('LINUXPATH')

# check if linux path configuration is absolute or relative
if path.exists(LINUXPATH):
    TEST_FILE_PATH = LINUXPATH
elif path.exists(BASE_DIR / LINUXPATH):
    TEST_FILE_PATH = BASE_DIR / LINUXPATH
else:
    raise FileNotFoundError('{!r} does not exist \
        please edit "LINUXPATH" in {!r}'.format(
            LINUXPATH,
            BASE_DIR / 'config.ini'))


class UnitTestCases(unittest.TestCase):
    """
    Tests every single utility function
    """

    def setUp(self):
        self.file_path = TEST_FILE_PATH
        HASHMAP.clear()

        return super().setUp()

    """
    Test that file is successfuly read and loaded to memory
    """
    def test_load_file_success(self):
        loaded_file = load_file(self.file_path)
        self.assertIsInstance(loaded_file, mmap.mmap)

    """
    Test exception is correct if file name is wrong
    """
    def test_load_file_exception(self):
        illegal_file = 'illegal_file_name'
        with self.assertRaises(FileNotFoundError) as exception_context:
            load_file(illegal_file)
            self.assertIn(
                illegal_file,
                str(exception_context.exception))

    """
    Test hashing function
    """
    def test_hash_file_success(self):
        """confirm that HASHMAP id empty"""
        self.assertEqual(len(HASHMAP), 0)

        """hash bytes"""
        hash_file(io.BytesIO(b'algo\r\nsciences\r\n\r\n'))

        """test that empty lines are not hashed"""
        self.assertEqual(len(HASHMAP), 2)

        """test that hashmap is correct"""
        self.assertEqual(HASHMAP[b'algo'], 1)

        """test for illegal value"""
        self.assertEqual(HASHMAP[b'illegal value'], -1)

    def tearDown(self):
        HASHMAP.clear()

        return super().tearDown()

    """
    Test is empty function
    """
    def test_is_empty_success(self):
        """test for empty case"""
        expected = is_empty(b'')
        self.assertEqual(expected, True)

        """test for not empty case"""
        expected = is_empty(b'algosciences')
        self.assertEqual(expected, False)

    """
    Test get message function
    """
    def test_get_message_success(self):
        """Test when value < 0"""
        expected = get_message(-1)
        self.assertEqual(expected, NOT_FOUND_MESSAGE)

        """Test when value > 0"""
        expected = get_message(1)
        self.assertEqual(expected, FOUND_MESSAGE)

    """
    Test function add new line
    """
    def test_add_new_line(self):
        self.assertEqual(add_new_line(b'sciences'), b'sciences\r\n')


if __name__ == '__main__':
    unittest.main()
