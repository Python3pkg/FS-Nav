#!/usr/bin/env python


"""
Setup script for FS Nav
"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import fsnav


with open('README.md') as f:
    readme = f.read()


setup(
    name='fsnav',
    version=fsnav.__version__,
    author=fsnav.__author__,
    author_email=fsnav.__email__,
    description=fsnav.__doc__,
    long_description=readme,
    url=fsnav.__source__,
    license=fsnav.__license__,
    packages=['fsnav'],
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    include_package_data=True,
    zip_safe=False,
    keywords='commandline shortcut alias navigation',
    entry_points="""
        [console_scripts]
        count=fsnav.cmdl.count:main
        nav=fsnav.cmdl.nav:cli
    """
)
