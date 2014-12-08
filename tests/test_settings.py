"""
Unittests for settings and data
"""


import os
import unittest

from fsnav import core
from fsnav import settings


class TestDefaultAliases(unittest.TestCase):

    def setUp(self):

        # Make sure there's something to test
        self.assertGreater(len(settings.DEFAULT_ALIASES), 0)

    def test_existence(self):

        """
        Make sure all the default aliases actually exist and are accessible
        """

        for path in settings.DEFAULT_ALIASES.values():
            self.assertTrue(os.path.exists(path))

    def test_validity(self):

        """
        Failure could mean ``fsnav.core.validate_path()`` and/or
        ``fsnav.core.validate_alias()`` is broken
        """

        for alias, path in settings.DEFAULT_ALIASES.items():
            self.assertTrue(core.validate_alias(alias))
            self.assertTrue(core.validate_path(path))
