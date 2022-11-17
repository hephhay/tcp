import unittest
import pathlib
import sys

# project test cases
from unit_test import UnitTestCases
from integration_test import IntegrationTestCases

# set package scope to as_tcp
PACKAGE_PATH = str(pathlib.Path(sys.argv[0]).absolute().parent.parent)
sys.path.append(PACKAGE_PATH)
__package__ = PACKAGE_PATH

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTests(map(
        lambda test: unittest.makeSuite(test),
        [UnitTestCases, IntegrationTestCases]))

    runner = unittest.TextTestRunner()
    runner.run(test_suite)