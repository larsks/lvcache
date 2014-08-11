#!/usr/bin/python

import os
import sys
import argparse
import subprocess

fields = (
    'name',
    'unknown_1',
    'unknown_2',
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
)


def parse_args():
    p = argparse.ArgumentParser()
    return p.parse_args()

def main():
    args = parse_args()

    out = subprocess.check_output(['dmsetup', 'status', '--target', 'cache'])
    segments = []
    for line in out.split('\n'):
        if not line.strip():
            continue
        data = dict(zip(fields, line.split()[:len(fields)]))
        segments.append(data)

    longest_name = max(len(x['name']) for x in segments)

    for segment in segments:
        name = segment['name'][:-1]
        md_used, md_total = [int(x) for x in
                             segment['md_utilization'].split('/')]
        cache_used, cache_total = [int(x) for x in
                             segment['cache_utilization'].split('/')]

        print ('%%%ds' % longest_name) % name,
        print 'md:%02d%% cache:%02d%% read-hit-miss:%02d%% write-hit-miss:%02d%%' % (
            int((md_used/(1.0 * md_total))*100),
            int((cache_used/(1.0 * cache_total))*100),
            int((int(segment['read_hits'])/(1.0 *
                                            int(segment['read_misses'])))*100),
            int((int(segment['write_hits'])/(1.0 *
                                            int(segment['write_misses'])))*100),
        )


if __name__ == '__main__':
    main()


