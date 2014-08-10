#!/usr/bin/python

import os
import sys
import argparse
import subprocess
import lvm
import logging

args = None


class LVException(Exception):
    pass


def lv_create(*lvargs):
    logging.debug('running lvcreate as: %s',
                  ' '.join(lvargs))

    lvargs = ['lvcreate'] + list(lvargs)

    if args.dryrun:
        res = 0
        print ' '.join(lvargs)
    else:
        res = subprocess.call(lvargs)

    if res != 0:
        raise LVException('Failed to create logical volume: %d',
                          res)


def lv_convert(*lvargs):
    logging.debug('running lvconvert as: %s',
                  ' '.join(lvargs))

    lvargs = ['lvconvert'] + list(lvargs)

    if args.dryrun:
        res = 0
        print ' '.join(lvargs)
    else:
        res = subprocess.call(lvargs)

    if res != 0:
        raise LVException('Failed to run lvconvert: %d',
                          res)


def parse_units(spec):
    siunits = 'BKMGTPE'
    btunits = 'bkmgtpe'

    if spec[-1].isdigit():
        return spec

    num = int(spec[:-1])
    unit = spec[-1]

    if unit not in siunits+btunits:
        raise ValueError('invalid unit: %s' % unit)

    if unit in siunits:
        pos = siunits.find(unit)
        mul = 1000
    elif unit in btunits:
        pos = btunits.find(unit)
        mul = 1024

    bytes = num * (mul**pos)

    return bytes


def adjust_512(num):
    return 512 * (num/512)


def human_format(num):
    if num < 1000:
        return '%d' % num
    elif num < 1000**2:
        return '%dK' % int(num/1000)
    elif num < 1000**3:
        return '%dM' % int(num/1000**2)
    elif num < 1000**4:
        return '%dG' % int(num/1000**3)
    elif num < 1000**5:
        return '%dT' % int(num/1000**4)
    elif num < 1000**6:
        return '%dP' % int(num/1000**5)
    else:
        return '%dE' % int(num/1000**6)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--cache-size', '-s')
    p.add_argument('--cache-percent', '-p', '-%',
                   default=20, type=int)
    p.add_argument('--cache-device', '-d')
    p.add_argument('--cache-tag', '-t', default='cache')
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('--debug', '-D',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.add_argument('--dryrun', '-n',
                   action='store_true')
    p.add_argument('lvspec')

    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()


def main():
    global args

    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    vg_name, lv_name = args.lvspec.split('/')

    try:
        vg = lvm.vgOpen(vg_name)
    except lvm.LibLVMError, detail:
        logging.error('failed to open volume group "%s": %s',
            vg_name, detail.message)
        sys.exit(1)

    try:
        lv = vg.lvFromName(lv_name)
    except lvm.LibLVMError, detail:
        logging.error('failed to open logical volume "%s": %s',
            lv_name, detail.message)
        sys.exit(1)

    lv_size = lv.getSize()
    vg.close()

    if args.cache_size:
        cache_size = int(parse_units(args.cache_size))
    elif args.cache_percent:
        cache_size = int(lv_size * (args.cache_percent/100.0))
    else:
        sys.exit(1)

    cache_md_size = max(parse_units('8m'), cache_size/1000)

    cache_size = adjust_512(cache_size)
    cache_md_size = adjust_512(cache_md_size)

    print 'LV %s/%s' % (vg_name, lv_name)
    print '  Original size:', human_format(lv_size), lv_size
    print '  Cache data size:', human_format(cache_size), cache_size
    print '  Cache metadata size:', human_format(cache_md_size), cache_md_size

    cache_data_name = '%s_cache' % lv_name
    cache_md_name = '%s_cache_md' % lv_name

    if args.cache_device:
        dev_arg=args.cache_device
    elif args.cache_tag:
        dev_arg='@%s' % args.cache_tag

    logging.info('creating cache data lv %s', cache_data_name)
    lv_create('-L', '%sb' % cache_size,
              '-n', cache_data_name, vg_name, dev_arg)

    logging.info('creating cache metadata lv %s', cache_md_name)
    lv_create('-L', '%sb' % cache_md_size,
              '-n', cache_md_name, vg_name, dev_arg)

    logging.info('creating cache pool')
    lv_convert('--type', 'cache-pool',
               '--poolmetadata', '%s/%s' % (vg_name, cache_md_name),
               '%s/%s' % (vg_name, cache_data_name))

    logging.info('attach cache pool to volume %s/%s',
                 vg_name, lv_name)
    lv_convert('--type', 'cache',
               '--cachepool', '%s/%s' % (vg_name, cache_data_name),
               '%s/%s' % (vg_name, lv_name))

if __name__ == '__main__':
    main()
