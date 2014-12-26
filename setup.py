#!/usr/bin/env python


"""
Setup script for FS Nav
"""


import os
import setuptools


with open('README.md') as f:
    readme = f.read()


with open('LICENSE.txt') as f:
    license = f.read()


with open('requirements.txt') as f:
    install_requires = f.read()


version = None
author = None
email = None
source = None
with open(os.path.join('fsnav', '__init__.py')) as f:
    for line in f:
        if '__version__' in line:
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif '__author__' in line:
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif '__email__' in line:
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif '__source__' in line:
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')


setuptools.setup(
    name='fsnav',
    version=version,
    author=author,
    author_email=email,
    description="FS Nav - File System Navigation shortcuts for the commandline",
    long_description=readme,
    url=source,
    license=license,
    packages=setuptools.find_packages(),
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    include_package_data=True,
    zip_safe=True,
    keywords='commandline shortcut alias navigation',
    install_requires=install_requires,
    entry_points="""
        [console_scripts]
        count=fsnav.cmdl.count:main
        nav=fsnav.cmdl.nav:main
    """
)
