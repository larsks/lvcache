from __future__ import absolute_import

import logging
from cliff.command import Command

from . import lvm


def adjust_512(num):
    return 512 * (num/512)


class Create(Command):
    'Create a cache LV and attach it to an existing data LV'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument('--cache-percent', '-%',
                            type=int, default=20,
                            help='Size of cache LV as percentage of data LV')
        parser.add_argument('--cache-device', '-d',
                            help='PV on which to place cache LV')
        parser.add_argument('--cache-tag', '-t', default='cache',
                            help='Tag for selecting PV on which to place cache LV')

        parser.add_argument('lvspec')
        return parser

    def take_action(self, args):
        vg_name, lv_name = args.lvspec.split('/')
        vg = lvm.VolumeGroup(vg_name)
        lv = vg.volume(lv_name)

        if lv.is_cached():
            raise ValueError('LV %s/%s is already cached' % (
                vg_name, lv_name))

        lv_size = lv.lv_size
        cache_size = adjust_512(lv_size * (args.cache_percent/100.0))
        
        self.log.info('creating %d byte cache LV for %d byte data LV',
                      cache_size, lv_size)
        cache_lv = vg.create_cache_pool('%s_cache' % lv_name,
                                        size=cache_size,
                                        pv_tag=args.cache_tag,
                                        pv_dev=args.cache_device)

        self.log.info('attaching cache LV %s/%s to data LV %s/%s',
                      lv.vg.name, lv.name,
                      cache_lv.vg.name, cache_lv.name)
        lv.attach_cache_pool(cache_lv)

