#!/usr/bin/python

import os
import sys
import argparse
import subprocess
import lvm
import logging

args = None


os.environ['LVM_SUPPRESS_FD_WARNINGS'] = '1'


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
    p.add_argument('--cache-size', '-s',
                   help='Size of cache volume')
    p.add_argument('--cache-percent', '-p', '-%',
                   default=20, type=int,
                   help='Size of cache volume as %% of origin volume')
    p.add_argument('--cache-device', '-d',
                   help='PV on which to place cache volume')
    p.add_argument('--cache-tag', '-t', default='cache',
                   help='Tag for selecting PV on which to place cache volume')
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('--debug', '-D',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.add_argument('--dryrun', '-n',
                   action='store_true',
                   help='Print rather than execute LVM commands')
    p.add_argument('lvspec',
                   help='Origin LV specified as vg_name/lv_name')

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

    if args.cache_size:
        cache_size = int(parse_units(args.cache_size))
    elif args.cache_percent:
        cache_size = int(lv_size * (args.cache_percent/100.0))
    else:
        logging.error('unable to determine size of cache volume')
        sys.exit(1)

    cache_data_name = '%s_cache' % lv_name
    cache_md_name = '%s_cache_md' % lv_name

    try:
        vg.lvFromName(cache_data_name)
        logging.error('a logical volume named %s already exists.',
                      cache_data_name)
        sys.exit(1)
    except Exception, detail:
        pass

    vg.close()

    cache_md_size = max(parse_units('8m'), cache_size/1000)
    cache_size = adjust_512(cache_size)
    cache_md_size = adjust_512(cache_md_size)

    logging.info('origin size: %s (%d bytes)', human_format(lv_size),
                 lv_size)
    logging.info('cache data size: %s (%d bytes)',
                 human_format(cache_size), cache_size)
    logging.info('cache metadata size: %s (%d bytes)',
                 human_format(cache_md_size), cache_md_size)

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


