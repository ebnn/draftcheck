#!/usr/bin/env python

setup_args = {
    'name': 'draftcheck',
    'version': '0.1',
    'description': 'LaTeX Lint for Academic Writing',
    'packages': ['draftcheck'],
    'zip_safe': True,
}

try:
    from setuptools import setup
    setup_args['entry_points'] = {
        'console_scripts': ['draftcheck = draftcheck.script:main']
    }

except ImportError:
    from distutils.core import setup
    setup_args['scripts'] = ['bin/draftcheck']

setup(**setup_args)