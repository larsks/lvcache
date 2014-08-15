from __future__ import absolute_import

import logging
from cliff.show import ShowOne

from . import lvm
from . import utils

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

        data = [['cached', lv.is_cached()],
                ['size', lv.lv_size]]

        if lv.is_cached():
            cache_lv = vg.volume(lv.pool_lv)
            data.append(['cache_lv', cache_lv.name])
            data.append(['cache_lv_size', cache_lv.lv_size])

            md_lv = vg.volume(cache_lv.metadata_lv[1:-1])
            data.append(['metadata_lv', md_lv.name])
            data.append(['metadata_lv_size', md_lv.lv_size])

            status = lv.cache_status()
            for k in sorted(status.keys()):
                data.append([k, status[k]])

        for datum in data:
            if self.app.options.human and 'size' in datum[0]:
                datum[1] = utils.human_format(datum[1])

        return ([x[0] for x in data],
                [x[1] for x in data])



