"""
Core functions and classes for FS Nav
"""


import getpass
import os
from os.path import expanduser
from os.path import join
import re
import sys


__all__ = ['Aliases', 'CONFIGFILE', 'DEFAULT_ALIASES']


class Aliases(dict):

    def __init__(self, *args, **kwargs):

        """
        Reference specific directories on the filesystem via user-defined aliases
        stored in a dictionary-like object.

        One could just store the aliases and directories in a dictionary but they
        should be validated when added.  Furthermore directory locations and names
        are not completely standardized across operating systems.  The default
        aliases found in `fsnav.DEFAULT_ALIASES` are almost identical when loaded
        on every platform but point to slightly different directories.

        In general, treat `Aliases()` as though it was a dictionary.  In order
        to add an alias, set a key equal to a directory.  Aliases must not
        have spaces or punctuation and directories must exist and be executable.

        An instance of `Aliases()` can be created the following ways:

            >>> aliases = Aliases()
            >>> aliases['home'] = '~/'
            >>> aliases['desk'] = '~/Desktop'

            >>> aliases = Aliases(home='~/', desk='~/Desktop')

            >>> aliases = Aliases({'home': '~/', 'desk': '~/Desktop'})

            >>> aliases = Aliases((('home', '~/'), ('desk', '~/Desktop')))

            >>> print(aliases)
            Aliases({'home': '/Users/wursterk/', 'desk': '/Users/wursterk/Desktop'})

        Aliases can then be used for navigation, most notably via the included
        commandline utility ``nav``.  See ``nav --help`` for more information

            >>> os.chdir(aliases['home'])
            >>> os.getcwd()
            '~/'
        """

        dict.__init__(self)

        # Call update to load items - it already handles the syntax for the following
        # Aliases(alias='path')
        # Aliases(
        self.update(*args, **kwargs)

    def __repr__(self):

        return "%s(%s)" % (self.__class__.__name__, dict((a, p) for a, p in list(self.items())))

    __str__ = __repr__

    def __enter__(self):

        """
        Included to enable contextmanager syntax - doesn't do any setup
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Included to enable contextmanager syntax - doesn't do any teardown
        """

        pass

    def __setitem__(self, alias, path):

        """
        Enable ``Aliases[alias] = path`` syntax with the necessary validations.
        A valid `alias` does not contain spaces or punctuation and must match
        the regex defined in `fsnav.ALIAS_REGEX`.  A valid `path` must
        exist and be executable.  Note that `~/` is expanded but `*` wildcards
        are not supported.

        Raises
        ------
        ValueError
            Invalid alias.
        KeyError
            Invalid path.

        Returns
        -------
        None
        """

        # ave to check for None before expanduser() otherwise an AttributeError is raised
        if path is None:
            raise ValueError("Path cannot be NoneType")
        else:
            path = os.path.expanduser(path)

        # Validate the alias
        if re.match(ALIAS_REGEX, alias) is None:
            raise KeyError(
                "Aliases can only contain alphanumeric characters and '-' or '_': '%s'"
                % alias)

        # Validate the path
        elif not os.path.isdir(path) and not os.access(path, os.X_OK):
            raise ValueError("Can't access path: '%s'" % path)

        # Alias and path passed validate - add
        else:
            # Forces all non-overridden methods that normally call `dict.__setitem__` to call
            # `Aliases.__setitem__()` in order to take advantage of the alias and path
            # validation
            super(Aliases, self).__setitem__(alias, path)

    def as_dict(self):

        """
        Return the dictionary containing aliases and paths as an actual dictionary

        Returns
        -------
        dict
        """

        return dict(self)

    def setdefault(self, alias, path=None):

        """
        Overrides dict.setdefault() to force usage of new self.__setitem__() method

        Returns
        -------
        str
            Path assigned to alias
        """

        try:
            self[alias]
        except KeyError:
            self[alias] = path
        return self[alias]

    def update(self, alias_iterable=None, **alias_path):

        """
        Overrides dict.update() to force usage of new self.__setitem__()

        Returns
        -------
        None
        """

        if alias_iterable and hasattr(alias_iterable, 'keys'):
            for alias in alias_iterable:
                self[alias] = alias_iterable[alias]
        elif alias_iterable and not hasattr(alias_iterable, 'keys'):
            for (alias, path) in alias_iterable:
                self[alias] = path
        for alias, path in list(alias_path.items()):
            self[alias] = path

    def copy(self):

        """
        Creates a copy of `Aliases()` and all contained aliases and paths

        Returns
        -------
        Aliases
        """

        return Aliases(**self.as_dict())

    def user_defined(self):

        """
        Extract user-defined aliases from an `Aliases()` instance

        Returns
        -------
        Aliases
            All user-defined aes
        """

        return Aliases({a: p for a, p in list(self.items()) if a not in DEFAULT_ALIASES or
                        p != DEFAULT_ALIASES[a]})

    def default(self):

        """
        Extract aliases defined by FS Nav on import

        Returns
        -------
        Aliases
            Default aliases
        """

        return Aliases({a: p for a, p in list(self.items()) if a in DEFAULT_ALIASES and
                        p == DEFAULT_ALIASES[a]})


ALIAS_REGEX = "^[\w-]+$"
NAV_UTIL = 'nav'


if 'darwin' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'mac'
elif 'cygwin' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'cygwin'
elif 'linux' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'linux'
elif 'win' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'windows'
else:  # pragma no cover
    NORMALIZED_PLATFORM = 'UNKNOWN'


CONFIGFILE = join(expanduser('~'), '.fsnav')
CONFIGFILE_ALIAS_SECTION = 'aliases'


_homedir = expanduser('~')
_username = getpass.getuser()


_MAC_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(_homedir, 'Pictures'),
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}

_DARWIN_ALIASES = _MAC_ALIASES.copy()

_LINUX_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(_homedir, 'Pictures'),
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}

_CYGWIN_ALIASES = {
    'applications':         join(os.sep, 'cygdrive', 'c', 'Program Files'),
    'desk':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Desktop'),
    'desktop':              join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Desktop'),
    'documents':            join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Documents'),
    'docs':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Documents'),
    'downloads':            join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Downloads'),
    'dl':                   join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Downloads'),
    'dropbox':              join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Dropbox'),
    'ghub':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'github'),
    'google_drive':         join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Google Drive'),
    'gdrive':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Google Drive'),
    'hard_drive':           join(os.sep, 'cygdrive', 'c'),
    'hd':                   join(os.sep, 'cygdrive', 'c'),
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Pictures'),
    'movies':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Videos'),
    'music':                join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Music'),
    'pictures':             join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Pictures'),
    'public':               join(os.sep, 'cygdrive', 'c', 'Users', 'Public'),
    'winhome':              join(os.sep, 'cygdrive', 'c', 'Users', _username),
    'windowshome':          join(os.sep, 'cygdrive', 'c', 'Users', _username)
}

_WINDOWS_ALIASES = {
    'cyghome':      join('C:', 'cygwin', 'home', _username),
    'cygwinhome':   join('C:', 'cygwin', 'home', _username),
    'cygwin_home':  join('C:', 'cygwin', 'home', _username),
    'desk':         join(_homedir, 'Desktop'),
    'desktop':      join(_homedir, 'Desktop'),
    'documents':    join(_homedir, 'My Documents'),
    'downloads':    join(_homedir, 'Downloads'),
    'dropbox':      join(_homedir, 'Dropbox'),
    'github':       join(_homedir, 'github'),
    'google_drive': join(_homedir, 'Google Drive'),
    'hard_drive':   'C:',
    'hd':           'C:',
    'home':         _homedir,
    'homedir':      _homedir,
    'images':       join(_homedir, 'My Pictures'),
    'top_level':    join('C:'),
    'movies':       join(_homedir, 'My Videos'),
    'music':        join(_homedir, 'My Music'),
    'pictures':     join(_homedir, 'My Pictures'),
    'public':       join(_homedir, 'Public'),
    'system_apps':  join('C:', 'Program Files'),
    'user_apps':    join(_homedir, 'Program Files')
}

_UNKNOWN_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}


if NORMALIZED_PLATFORM == 'mac':  # pragma no cover
    _DEFAULT_ALIASES = _MAC_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'linux':  # pragma no cover
    _DEFAULT_ALIASES = _LINUX_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'cygwin':  # pragma no cover
    _DEFAULT_ALIASES = _CYGWIN_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'win':  # pragma no cover
    _DEFAULT_ALIASES = _WINDOWS_ALIASES.copy()
else:  # pragma no cover
    _DEFAULT_ALIASES = _UNKNOWN_ALIASES.copy()

# Remove aliases pointing towards non-existent directories
# Python 2.6 does not support direct dictionary comprehension
_DEFAULT_ALIASES = dict(
    (a, p) for a, p in list(_DEFAULT_ALIASES.copy().items())
    if os.path.isdir(p) and os.access(p, os.X_OK)
)
DEFAULT_ALIASES = _DEFAULT_ALIASES.copy()
