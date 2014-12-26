FS Nav
======

[![Build Status](https://travis-ci.org/geowurster/FS-Nav.svg?branch=master)](https://travis-ci.org/geowurster/FS-Nav)

File System Navigation shortcuts for the commandline


Aliases
-------

Reference directories via an alias lookup table that acts like a dictionary.  In
order for an alias to be valid it must not contain spaces or punctuation.
Directories are valid if they exist and are executable.  Aliases and paths are
both validated when added.

    >>> import fsnav
    
    >>> aliases = fsnav.core.Aliases(home='~/', desk='~/Desktop')
    >>> Aliases({'home': '/Users/wursterk/', 'desk': '/Users/wursterk/Desktop'})
    Aliases({'home': '/Users/wursterk/', 'desk': '/Users/wursterk/Desktop'})
    
    >>> aliases['desk']
    '/Users/wursterk/Desktop'
    
    >>> aliases['github'] = '~/github'
    >>> print(aliases)
    Aliases({'home': '/Users/wursterk/', 'github': '/Users/wursterk/github', 'desk': '/Users/wursterk/Desktop'})
