from __future__ import absolute_import

import logging
from cliff.lister import Lister

from . import lvm

class List(Lister):
    'List available LVs on a given VG'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('--all', '-a',
                            action='store_true',
                            help='Also list inactive LVs')
        parser.add_argument('vgname')
        return parser

    def take_action(self, args):
        vg = lvm.VolumeGroup(args.vgname)

        return (('name', 'is_cached', 'attributes'),
                ((x.name, x.is_cached(), x.lv_attr) for x in vg.volumes()
                 if args.all or x.attributes().state == 'a'))
