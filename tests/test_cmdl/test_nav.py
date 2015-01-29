"""
FS Nav unittests for utility: nav
"""


import json
import os
import tempfile
import unittest

from click.testing import CliRunner

import fsnav
from fsnav.cmdl import nav


class TestNav(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.configfile = tempfile.NamedTemporaryFile(mode='r+')
        self.default_aliases = fsnav.Aliases(fsnav.settings.DEFAULT_ALIASES)

    def tearDown(self):
        self.configfile.close()

    def test_get(self):

        # nav get ${alias}
        a = 'home'
        result = self.runner.invoke(nav.main, ['-nlc', 'get', a])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.default_aliases[a], result.output.strip())

    def test_startup_generate(self):

        # nav startup generate
        result = self.runner.invoke(nav.main, ['-nlc', 'startup', 'generate'])
        self.assertEqual(result.exit_code, 0)
        actual = sorted(result.output.strip().replace('} ; ', '}__SPLIT__').split('__SPLIT__'))
        expected = sorted(fsnav.fg_tools.generate_functions(self.default_aliases))
        self.assertEqual(actual, expected)

    def test_startup_profile(self):

        # nav startup profile
        result = self.runner.invoke(nav.main, ['-nlc', 'startup', 'profile'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), fsnav.fg_tools.startup_code.strip())

    def test_config_default(self):

        # nav config default
        result = self.runner.invoke(nav.main, ['-nlc', 'config', 'default', '-np'])
        self.assertEqual(result.exit_code, 0)
        self.assertDictEqual(json.loads(result.output), self.default_aliases.default())

    def test_config_userdefined(self):

        # nav config userdefined
        expected = {'__h__': os.path.expanduser('~')}
        aliases_to_load = dict(list(expected.items()) + list(fsnav.settings.DEFAULT_ALIASES.items()))
        self.configfile.write(json.dumps({fsnav.settings.CONFIGFILE_ALIAS_SECTION: aliases_to_load}))
        self.configfile.seek(0)
        result = self.runner.invoke(nav.main, ['-c', self.configfile.name, 'config', 'userdefined', '-np'])
        self.assertEqual(result.exit_code, 0)
        self.assertDictEqual(expected, json.loads(result.output.strip()))

    def test_config_addalias(self):

        # nav config addalias ${alias}=${path}
        a1 = '__h__'
        p1 = os.path.expanduser('~')
        a2 = '___h___'
        p2 = os.path.expanduser('~')
        result = self.runner.invoke(nav.main, [
            '-c', self.configfile.name, 'config', 'addalias', '%s=%s' % (a1, p1), '%s=%s' % (a2, p2)])
        self.assertEqual(result.exit_code, 0)
        actual = json.load(self.configfile)[fsnav.settings.CONFIGFILE_ALIAS_SECTION]
        expected = {a1: p2, a2: p2}
        self.assertDictEqual(expected, actual)

        # If specified, make sure the configfile won't be overwritten
        result = self.runner.invoke(
            nav.main, ['-c', self.configfile.name, 'addalias', '-no', '%s=%s' % (a1, p1), '%s=%s' % (a2, p2)])
        self.assertNotEqual(result.exit_code, 0)

    def test_config_path(self):

        # nav config path
        result = self.runner.invoke(nav.main, ['config', 'path'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), fsnav.settings.CONFIGFILE)

    def test_license(self):

        # nav --license
        result = self.runner.invoke(nav.main, ['--license'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), fsnav.__license__.strip())

    def test_version(self):

        # nav --version
        result = self.runner.invoke(nav.main, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), fsnav.__version__.strip())

    def test_aliases(self):

        # nav aliases
        result = self.runner.invoke(nav.main, ['-nlc', 'aliases', '-np'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output.strip()), fsnav.settings.DEFAULT_ALIASES)

    def test_deletealias(self):

        # nav config deletealias ${alias}
        self.configfile.write(
            json.dumps({fsnav.settings.CONFIGFILE_ALIAS_SECTION: {'__h__': os.path.expanduser('~/')}}))
        self.configfile.seek(0)
        result = self.runner.invoke(nav.main, ['-c', self.configfile.name, 'config', 'deletealias', '__h__'])
        self.assertEqual(result.exit_code, 0)
        self.assertDictEqual(
            {fsnav.settings.CONFIGFILE_ALIAS_SECTION: {}}, json.loads(self.configfile.read()))
