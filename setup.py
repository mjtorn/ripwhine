# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from setuptools import setup

import glob

import os
import sys

NAME = 'ripwhine'
VERSION = '1.2.1' # Maybe parse from git tag some day

AUTHOR_EMAIL = 'mjt@fadconsulting.com'
URL = 'http://github.com/mjtorn/ripwhine'

packages = []

def get_packages(arg, dir, fnames):
    global packages

    if '__init__.py' in fnames:
        packages.append(dir.replace('/', '.'))

os.path.walk(NAME, get_packages, None)

setup(
    name = NAME,
    version = VERSION,
    author = 'Markus Törnqvist',
    author_email = AUTHOR_EMAIL,
    url = URL,
    packages = packages,
    scripts = glob.glob('bin/*') or None,
    include_package_data = True,
    long_description = '%s.' % NAME,
)

# EOF

