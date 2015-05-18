"""
Unittests for: fsnav.core
"""


import os
import re
import unittest

from fsnav import core


class TestAliases(unittest.TestCase):

    def setUp(self):
        self.homedir = os.path.expanduser('~')
        self.deskdir = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.isdir(self.deskdir):
            os.mkdir(self.deskdir)

    def test_instantiate(self):

        # Instantiate normally and check a few properties and methods
        aliases = core.Aliases()
        self.assertIsInstance(aliases, (dict, core.Aliases))
        self.assertEqual(0, len(aliases))

        aliases = core.Aliases(home='~', desktop=os.path.join('~', 'Desktop'))
        self.assertEqual(2, len(aliases))

    def test_setitem(self):

        # Override dict.__setitem__()
        aliases = core.Aliases()

        # Valid alias
        aliases['home'] = '~'
        self.assertEqual(1, len(aliases))

        # Invalid alias - no way to test __setitem__() syntax so try/except is a workaround
        try:
            aliases['invalid alias'] = '~'
            self.fail('Above line should have raised a KeyError - forcing failure')
        except KeyError:
            self.assertTrue(True)

        # Invalid path
        try:
            aliases['invalid_path'] = '.----III_DO_NOT-EX-X-IST'
            self.fail('Above line should have raised a ValueError - forcing failure')
        except ValueError:
            self.assertTrue(True)

    def test_getitem(self):

        # Override dict.__getitem__()
        aliases = core.Aliases()
        aliases['home'] = '~'
        self.assertEqual(aliases['home'], self.homedir)

    def test_as_dict(self):

        # Return aliases as an actual dictionary
        expected = {
            'home': self.homedir,
            'desktop': os.path.expanduser(os.path.join('~', 'Desktop'))
        }
        aliases = core.Aliases(**expected)
        self.assertEqual(expected, aliases.as_dict())

    def test_setdefault(self):

        # Override dict.setdefault() to force call to Aliases.__setitem__()
        aliases = core.Aliases()
        alias = 'home'
        path = self.homedir

        # These is an important tests because they validates that `Aliases.__setitem__()`
        # is ALWAYS called instead of `dict.__setitem__()`, which the case without using the
        # `super()` call in `Aliases.__setitem__()`.
        self.assertRaises(ValueError, aliases.setdefault, alias, '.INVALID----DIR')
        self.assertRaises(KeyError, aliases.setdefault, 'invalid alias', self.homedir)

        # Just supplying alias will cause path to be the default 'None' value, which is
        # invalid and should raise a ValueError
        self.assertRaises(ValueError, aliases.setdefault, alias)

        # Successful add
        self.assertEqual(path, aliases.setdefault(alias, path))
        self.assertEqual(1, len(aliases))

    def test_update(self):

        # Override dict.update() to force call to Aliases.__setitem__()
        aliases = core.Aliases()
        aliases['home'] = self.homedir
        aliases.update(home=self.deskdir)
        self.assertEqual(1, len(aliases))
        self.assertEqual(aliases['home'], self.deskdir)

        # Set back to home directory with other syntax
        aliases.update({'home': self.homedir})
        self.assertEqual(aliases['home'], self.homedir)

    def test_copy(self):

        # Return a copy instance of Aliases in its current state
        aliases1 = core.Aliases(home=self.homedir, desk=self.deskdir)
        aliases2 = aliases1.copy()
        self.assertDictEqual(aliases1, aliases2)
        self.assertIsInstance(aliases2, (dict, core.Aliases))

    def test_contextmanager(self):

        # Test syntax: with Aliases({}) as aliases: ...
        aliases = core.Aliases(home=self.homedir, desk=self.deskdir)
        self.assertIsInstance(aliases, (dict, core.Aliases))
        self.assertEqual(2, len(aliases))

    def test_user_defined(self):

        # Get all user-defined aliases
        ud = {'desk': os.path.expanduser('~'), '__h__': os.path.expanduser('~')}

        # Be sure to add the user defined LAST so they overwrite any default aliases otherwise
        # test will fail
        aliases = core.Aliases(list(core.DEFAULT_ALIASES.items()) + list(ud.items()))

        user_defined = aliases.user_defined()

        self.assertEqual(len(ud), len(user_defined))
        self.assertDictEqual(ud, user_defined)

    def test_default(self):

        # Get all default aliases
        ud = {'desk': os.path.expanduser('~'), '__h__': os.path.expanduser('~')}

        # Be sure to add the user defined LAST so they overwrite any default aliases otherwise
        # test will fail
        aliases = core.Aliases(list(core.DEFAULT_ALIASES.items()) + list(ud.items()))

        expected = {a: p for a, p in core.DEFAULT_ALIASES.copy().items() if a not in ud}
        actual = aliases.default()

        self.assertEqual(len(expected.items()), len(actual))
        self.assertDictEqual(expected, actual)

    def test_repr(self):
        aliases = core.Aliases()
        self.assertIsInstance(repr(aliases), str)
        self.assertTrue(repr(aliases).startswith(aliases.__class__.__name__))

    def test_with_statement(self):
        with core.Aliases({'home': self.homedir, 'desk': self.deskdir}) as aliases:
            self.assertEqual(aliases['home'], self.homedir)
            self.assertEqual(aliases['desk'], self.deskdir)


class TestDefaultAliases(unittest.TestCase):

    def setUp(self):

        # Make sure there's something to test
        self.assertGreater(len(core.DEFAULT_ALIASES), 0)

    def test_existence(self):

        # Make sure all the default aliases actually exist and are accessible
        for path in core.DEFAULT_ALIASES.values():
            self.assertTrue(os.path.exists(path))

    def test_validity(self):

        # Failure could mean `fsnav.core.validate_path()` and/or `fsnav.core.validate_alias()`
        # is broken
        for alias, path in core.DEFAULT_ALIASES.items():
            self.assertIsNotNone(
                re.match(core.ALIAS_REGEX, alias), msg="Alias='{}'".format(alias))
            self.assertTrue(
                os.path.isdir(path) and os.access(path, os.X_OK), msg="Path='{}'".format(path))

    def test_check_for_invalid(self):

        # The number of aliases explicitly defined in the `core._${PLATFORM}_ALIASES`
        # dictionary should generally match what ends up in `core.DEFAULT_ALIASES`.  If the
        # user has modified The default directory names on their system this test will fail

        for a in core.__dict__['_{norm_plat}_ALIASES'.format(
                norm_plat=core.NORMALIZED_PLATFORM.upper())].copy():
            self.assertTrue(a in core.DEFAULT_ALIASES)
