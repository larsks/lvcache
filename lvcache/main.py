#!/usr/bin/python

import os
import sys
import argparse
import logging

from cliff.app import App
from cliff.commandmanager import CommandManager

class LVCache (App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(LVCache,self).__init__(
            description='LVM Cache Manager',
            version='1',
            command_manager=CommandManager('com.oddbit.lvcache'),
        )

    def build_option_parser(self, *args, **kwargs):
        parser = super(LVCache, self).build_option_parser(*args, **kwargs)
        parser.add_argument('--human', '-H',
                            action='store_true',
                            help='Display numbers with suffixes ("100G")')
        parser.add_argument('--dryrun', '-n',
                            action='store_true')

        return parser

app = LVCache()

def main():
    return app.run(sys.argv[1:])

if __name__ == '__main__':
    main()


