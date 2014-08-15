from __future__ import absolute_import

import logging
from cliff.command import Command

from . import lvm

class Remove(Command):
    'Detach a cache LV from a data LV and destroy the cache LV'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Remove, self).get_parser(prog_name)
        parser.add_argument('lvspec')
        return parser

    def take_action(self, args):
        vg_name, lv_name = args.lvspec.split('/')
        vg = lvm.VolumeGroup(vg_name)
        lv = vg.volume(lv_name)

        if not lv.is_cached():
            raise ValueError('LV %s/%s is not cached' % (
                vg_name, lv_name))

        self.log.info('removing cache LV %s/%s' % (lv.vg.name,
                                                   lv.pool_lv))
        lv.remove_cache_pool()
