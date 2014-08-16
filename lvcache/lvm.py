import os
import logging

from sh import (
    dmsetup,
    lvs,
    lvremove,
    lvcreate,
    lvconvert)
from collections import namedtuple

lv_attributes = namedtuple('lv_attributes', [
    'type',
    'permissions',
    'allocation',
    'minor',
    'state',
    'open',
    'target',
    'zero',
    'health',
    'skip'
])

cache_status_fields = [
    'start',
    'end',
    'segment_type',
    'md_block_size',
    'md_utilization',
    'cache_block_size',
    'cache_utilization',
    'read_hits',
    'read_misses',
    'write_hits',
    'write_misses',
    'demotions',
    'promotions',
    'dirty',
    'features',
]

lvs = lvs.bake('--noheadings', '--unbuffered',
               '--nosuffix', '--units', 'b')


def find_device(parent, major, minor):
    for dev in os.listdir(parent):
        path = os.path.join(parent, dev)
        s = os.stat(path)

        this_major = os.major(s.st_rdev)
        this_minor = os.minor(s.st_rdev)

        if this_major == major and this_minor == minor:
            return path


class LogicalVolume(object):

    log = logging.getLogger(__name__)

    def __init__(self, vg, lv_name):
        self.vg = vg
        self.name = lv_name

    def __str__(self):
        return '<LV %s/%s>' % (self.vg.name, self.name)

    def attributes(self):
        res = lvs('-o', 'lv_attr', '%s/%s' % (self.vg.name,
                                              self.name))

        return lv_attributes(*(x for x in res.strip()))

    def is_cached(self):
        return self.attributes().type == 'C'

    def cache_status(self):
        if not self.is_cached():
            raise ValueError('LV is of wrong type')

        devpath = self.path
        s = os.stat(devpath)
        major, minor = os.major(s.st_rdev), os.minor(s.st_rdev)
        mapper = find_device('/dev/mapper', major, minor)

        if mapper is None:
            raise KeyError('failed to find device mapper entry for '
                           '%s/%s' % (self.vg.name, self.name))

        status = dmsetup('status', mapper)

        status = dict(zip(cache_status_fields,
                          status.strip().split()[:len(cache_status_fields)]))
        for k in status.keys():
            if status[k].isdigit():
                status[k] = int(status[k])
            elif '/' in status[k]:
                a, b = [int(x) for x in status[k].split('/')]
                status['%s_pct' % k] = (a*1.0/b*1.0)*100

        return status

    def remove_cache_pool(self):
        if not self.is_cached():
            raise ValueError('LV is of wrong type')

        for line in lvremove('-f', '%s/%s' % (self.vg.name, self.pool_lv),
                             _iter=True):
            self.log.info(line.strip())

    def attach_cache_pool(self, cache_lv):
        lvconvert('--type', 'cache',
                  '--cachepool', '%s/%s' % (cache_lv.vg.name,
                                            cache_lv.name),
                  '%s/%s' % (self.vg.name, self.name))

    def __getattr__(self, k):
        res = lvs('-o', k, '%s/%s' % (self.vg.name,
                                      self.name))

        res = res.strip()
        if res.isdigit():
            res = int(res)

        return res


class VolumeGroup(object):
    def __init__(self, vg_name):
        self.name = vg_name

    def __str__(self):
        return '<VG %s>' % self.name

    def volumes(self):
        res = lvs('-o', 'name', self.name)
        return [LogicalVolume(self, x.strip())
                for x in res.split('\n') if x.strip()]

    def volume(self, lv_name):
        return LogicalVolume(self, lv_name)

    def create_volume(self, lv_name, size=None, pv_tag=None, pv_dev=None):
        if pv_tag is not None:
            pvargs = ['@%s' % pv_tag]
        elif pv_dev is not None:
            pvargs= [pv_dev]

        lvcreate('-n', lv_name, '-L', '%sb' % size, self.name, *pvargs)
        return LogicalVolume(self, lv_name)

    def create_cache_pool(self, lv_name,
                          mode='writeback',
                          metadata_lv=None,
                          **kwargs):
        cache_lv = self.create_volume(lv_name, **kwargs)
        if mode not in ['writeback', 'writethrough']:
            raise ValueError('invalid cache mode: %s' % mode)

        args = ('--type', 'cache-pool',
                '--cachemode', mode)

        if metadata_lv is not None:
            md_args = ('--poolmetadata',
                       '%s/%s' % (metadata_lv.vg.name,
                                  metadata_lv.name))
            args = args + md_args

        lvconvert(*(args + ('%s/%s' % (self.name,
                                       cache_lv.name),)))

        return cache_lv
