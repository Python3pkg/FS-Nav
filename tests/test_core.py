"""
Unittests for core components
"""


from glob import glob
import os
import stat
import unittest

from fsnav import core


class TestAliases(unittest.TestCase):
    
    def setUp(self):
        self.homedir = os.path.expanduser('~')
        self.deskdir = os.path.join(os.path.expanduser('~'), 'Desktop')

    def test_instantiate(self):

        """
        Instantiate normally and check a few properties and methods
        """

        aliases = core.Aliases()
        self.assertIsInstance(aliases, (dict, core.Aliases))
        self.assertEqual(0, len(aliases))

        aliases = core.Aliases(home='~', desktop=os.path.join('~', 'Desktop'))
        self.assertEqual(2, len(aliases))

    def test_setitem(self):

        """
        Override dict.__setitem__()
        """

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

        """
        Override dict.__getitem__()
        """

        aliases = core.Aliases()
        aliases['home'] = '~'
        self.assertEqual(aliases['home'], self.homedir)

    def test_as_dict(self):

        """
        Return aliases as an actual dictionary
        """
        
        expected = {
            'home': self.homedir,
            'desktop': os.path.expanduser(os.path.join('~', 'Desktop')) 
        }
        aliases = core.Aliases(**expected)
        self.assertEqual(expected, aliases.as_dict())
        
    def test_setdefault(self):

        """
        Override dict.setdefault() to force call to Aliases.__setitem__()
        """
        
        aliases = core.Aliases()
        alias = 'home'
        path = self.homedir

        # These is an important tests because they validates that Aliases.__setitem__() is ALWAYS called
        # instead of dict.__setitem__(), which the case without using the super() call in Aliases.__setitem__()
        self.assertRaises(ValueError, aliases.setdefault, alias, '.INVALID----DIR')
        self.assertRaises(KeyError, aliases.setdefault, 'invalid alias', self.homedir)

        # Just supplying alias will cause path to be the default 'None' value, which is
        # invalid and should raise a ValueError
        self.assertRaises(ValueError, aliases.setdefault, alias)

        # Successful add
        self.assertEqual(path, aliases.setdefault(alias, path))
        self.assertEqual(1, len(aliases))

    def test_update(self):

        """
        Override dict.update() to force call to Aliases.__setitem__()
        """

        aliases = core.Aliases()
        aliases['home'] = self.homedir
        aliases.update(home=self.deskdir)
        self.assertEqual(1, len(aliases))
        self.assertEqual(aliases['home'], self.deskdir)

        # Set back to home directory with other syntax
        aliases.update({'home': self.homedir})
        self.assertEqual(aliases['home'], self.homedir)

    def test_copy(self):

        """
        Return a copy instance of Aliases in its current state
        """

        aliases1 = core.Aliases(home=self.homedir, desk=self.deskdir)
        aliases2 = aliases1.copy()
        self.assertDictEqual(aliases1, aliases2)
        self.assertDictEqual(aliases1.as_dict(), aliases2.as_dict())
        self.assertIsInstance(aliases1, (dict, core.Aliases))
        self.assertIsInstance(aliases2, (dict, core.Aliases))
        for a, p in aliases1.iteritems():
            self.assertEqual(aliases2[a], p)

    def test_contextmanager(self):

        """
        Test syntax: with Aliases({}) as aliases: ...
        """

        with core.Aliases(home=self.homedir, desk=self.deskdir) as aliases:
            self.assertIsInstance(aliases, (dict, core.Aliases))
            self.assertEqual(2, len(aliases))


class TestValidateAlias(unittest.TestCase):

    def test_valid(self):

        """
        Valid alias name should return True
        """

        self.assertTrue(core.validate_alias('desk'))

    def test_dash_underscore(self):

        """
        Dashes and underscores are valid
        """

        self.assertTrue(core.validate_alias('-'))
        self.assertTrue(core.validate_alias('_'))

    def test_whitespace(self):

        """
        No whitespace allowed
        """

        self.assertFalse(core.validate_alias(' '))
        self.assertFalse(core.validate_alias('\t'))
        self.assertFalse(core.validate_alias('\r'))

    def test_punctuation(self):

        """
        No punctuation allowed
        """

        self.assertFalse(core.validate_alias('.'))
        self.assertFalse(core.validate_alias('?'))
        self.assertFalse(core.validate_alias('/'))
        self.assertFalse(core.validate_alias('|'))


class TestValidatePath(unittest.TestCase):

    def setUp(self):

        self.homedir = os.path.expanduser('~')
        self.test_file_path = '.TEST-FILE-fffffIIIILLLEEEEE__---_-%s' % self.__class__.__name__
        if os.path.isfile(self.test_file_path):
            os.remove(self.test_file_path)
        elif os.path.isdir(self.test_file_path):
            os.rmdir(self.test_file_path)

    def tearDown(self):
        if os.path.isfile(self.test_file_path):
            os.remove(self.test_file_path)
        elif os.path.isdir(self.test_file_path):
            os.rmdir(self.test_file_path)

    def test_valid(self):

        """
        Valid path and standard usage
        """

        self.assertTrue(core.validate_path(self.homedir))

    def test_non_existent(self):

        """
        Non-existent paths should return False
        """

        self.assertFalse(core.validate_path('.I-DO-NOT___eX-ist-T'))

    def test_no_execute(self):

        """
        Paths without execute permission should return False.
        """

        os.mkdir(self.test_file_path)
        os.chmod(self.test_file_path, stat.S_IREAD | stat.S_IWRITE)

        # Independently verify that the file cannot be executed
        self.assertFalse(os.access(self.test_file_path, os.X_OK), "Test file has X bit flipped - test will always fail")
        self.assertFalse(core.validate_path(self.test_file_path))

    def test_exists_but_not_directory(self):

        """
        Paths that are not a directory are not valid as they cannot be
        ``cd``'d into.
        """

        with open(self.test_file_path, 'w') as f:
            f.write("")

        self.assertFalse(core.validate_path(self.test_file_path))


class TestCount(unittest.TestCase):

    def setUp(self):

        self.homedir = os.path.expanduser('~')
        self.homedir_contents = glob(os.path.join(self.homedir, '*'))

        # Make sure there's something to test with
        self.assertGreater(self.homedir_contents, 0)

    def test_standard(self):

        """
        No duplicate items, and no validation.  Just return the number of input
        items.  Return value should be equal to the length of the input list
        """

        self.assertEqual(len(self.homedir_contents), core.count(self.homedir_contents))

    def test_duplicate(self):

        """
        Count with duplicate items should return a count of all unique items
        """

        # list() call ensures a new list is returned
        test_items = list(self.homedir_contents)
        test_items.append(self.homedir_contents[0])
        test_items.append(self.homedir_contents[1])
        self.assertEqual(len(self.homedir_contents), core.count(test_items))
        self.assertRaises(TypeError, core.count, [[]])

    def test_non_existent(self):

        """
        Non-existent items should be ignored and not reflected int he final count
        """

        test_items = list(self.homedir_contents)
        test_items.append('.I-_DO-NOT___--EXIST')
        self.assertEqual(len(self.homedir_contents), core.count(test_items))
