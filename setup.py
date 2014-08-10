#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='lvcache',
    version='1',
    description='Wrapper for creating cached LVM logical volumes',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    url='http://github.com/larsks/lvcache',
    install_requires=open('requirements.txt').readlines(),
    py_modules=['lvcache'],
    entry_points = {
        'console_scripts': [
            'lvcache=lvcache:main',
        ],
    }
)

