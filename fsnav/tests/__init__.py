"""
Unittests
"""


from os.path import dirname
import sys
import unittest

from . import test_core
from . import test_settings


def _run_tests(stream=sys.stderr, descriptions=True, verbosity=2):

    """
    Automatically discover and run all unit tests

    Parameters
    ----------
    stream : file or sys.stdout or sys.stdout
        Open file object where ``unittest`` prints results, errors, and messages
    descriptions : bool
        Specifies whether test results are printed
    verbosity : {1, 2, 3}
        Set verbosity for descriptions

    Returns
    -------
    unittest.runner.TextTestResult
    """

    # Discover tests
    test_suite = unittest.TestLoader().discover(dirname(__file__))

    # Run tests
    result = unittest.TextTestRunner(stream=stream, descriptions=descriptions, verbosity=verbosity).run(test_suite)

    return result
