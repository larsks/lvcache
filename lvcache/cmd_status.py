from __future__ import absolute_import

import logging
from cliff.show import ShowOne

from . import lvm

class Status(ShowOne):
    'Show information about LVM cache volumes'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Status, self).get_parser(prog_name)

        parser.add_argument('lvspec')
        return parser

    def take_action(self, args):
        vg_name, lv_name = args.lvspec.split('/')
        vg = lvm.VolumeGroup(vg_name)
        lv = vg.volume(lv_name)

        columns = ['cached', 'size']
        data = [lv.is_cached(), lv.lv_size]

        if lv.is_cached():
            cache_lv = vg.volume(lv.pool_lv)
            columns.append('cache_pool')
            data.append(cache_lv.name)
            columns.append('cache_size')
            data.append(cache_lv.lv_size)

            md_lv = vg.volume(cache_lv.metadata_lv[1:-1])
            columns.append('metadata_name')
            data.append(md_lv.name)
            columns.append('metadata_size')
            data.append(md_lv.lv_size)

            status = lv.cache_status()
            for k in sorted(status.keys()):
                columns.append(k)
                data.append(status[k])

        return (columns,data)



