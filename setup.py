#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='lvcache',
    version='1.0.1',
    description='Wrapper for creating cached LVM logical volumes',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    url='http://github.com/larsks/lvcache',
    install_requires=['cliff', 'sh'],
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'lvcache=lvcache.main:main',
        ],
        'com.oddbit.lvcache': [
            'status = lvcache.cmd_status:Status',
            'create = lvcache.cmd_create:Create',
            'remove = lvcache.cmd_remove:Remove',
            'list = lvcache.cmd_list:List',
        ],
    }
)

