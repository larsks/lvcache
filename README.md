## Overview

The `lvcache` command helps you create and manage LVM cache devices.

## Global options

- `--human`, `-H`

  Display volume sizes using SI suffixes (e.g., 1M = 1000K =
  1000000B).

## Listing information about existing LVs

    lvcache list [-h] [-f {csv,table}] [-c COLUMN] [--max-width <integer>]
                 [--quote {all,minimal,none,nonnumeric}] [--all]
                 vgname

List LVs on VG `tank`:

    # lvcache list tank
    +---------+-----------+------+
    | name    | is_cached | size |
    +---------+-----------+------+
    | home    | False     | 157G |
    | root    | True      | 53G  |
    | vol0    | False     | 2G   |
    +---------+-----------+------+

## Creating and attaching a cache volume

    lvcache create [-h] [--cache-percent CACHE_PERCENT]
                   [--cache-device CACHE_DEVICE]
                   [--cache-tag CACHE_TAG] [--cache-mode CACHE_MODE]
                   lvspec

- `--cache-percent`, `-%` *percent*

  Set the size of the cache LV as a percentage of the size of the
  origin LV.

  Defaults to 20%.

- `--cache-tag`, `-t` *tag*

  Places cache and metadata LV on PV identified by tag *tag*.  You can
  see tags associated with PVs by running:

      pvs -o+tags

  You can apply a tag to a PV with the `pvchange` command:

      pvchange --addtag <tag> /dev/sdx

  Defaults to `cache`.

- `--cache-device`, `-d` *device*

  Please cache and metadata LV on specific a specific PV identified by
  a device path (e.g., `/dev/sda`).

- `--cache-mode`, `-m` *mode*

  Sets cache mode for cache LV.  Can be either `writeback` or
  `writethrough`.  **NB**: This option may not be implemented in LVM
  at this time.

    The default mode is `writethrough`.

Create a cache LV and attach it to `tank/home`:

    # lvcache create tank/home
    creating 8388608 byte metadata LV
    creating 6442450944 byte cache LV
    attaching cache LV tank/home to data LV tank/home_cache

## Detaching and removing a cache LV

    lvcache remove [-h] lvspec

Remove the cache LV associated with `tank/home`:

    # lvcache remove tank/home
    removing cache LV tank/home_cache
    Flushing cache for home.
    534 blocks must still be flushed.
    0 blocks must still be flushed.

## Getting the status of a cached LV

    lvcache status [-h] [-f {shell,table,value}] [-c COLUMN]
                   [--max-width <integer>]
                   [--variable VARIABLE] [--prefix PREFIX]
                   lvspec

Display status of the `home` LV:

    # lvcache status -H tank/home
    +-----------------------+------------------+
    | Field                 | Value            |
    +-----------------------+------------------+
    | cached                | True             |
    | size                  | 32G              |
    | cache_lv              | home_cache       |
    | cache_lv_size         | 6G               |
    | metadata_lv           | home_cache_cmeta |
    | metadata_lv_size      | 8M               |
    | cache_block_size      | 128              |
    | cache_utilization     | 0/98304          |
    | cache_utilization_pct | 0.0              |
    | demotions             | 0                |
    | dirty                 | 0                |
    | end                   | 62914560         |
    | features              | 1                |
    | md_block_size         | 8                |
    | md_utilization        | 200/2048         |
    | md_utilization_pct    | 9.765625         |
    | promotions            | 0                |
    | read_hits             | 0                |
    | read_misses           | 0                |
    | segment_type          | cache            |
    | start                 | 0                |
    | write_hits            | 0                |
    | write_misses          | 0                |
    +-----------------------+------------------+

Because `lvcache` is using the [cliff][] framework, it is very easy to
extract individual values from this list for graphing or monitoring
purposes:

    # lvcache status tank.home -f value -c md_utilization_pct
    9.765625

Or:

    # lvcache status tank.home -f shell
    cached="True"
    size="32G"
    cache_lv="nova_cache"
    cache_lv_size="6G"
    metadata_lv="nova_cache_cmeta"
    metadata_lv_size="8M"
    cache_block_size="128"
    cache_utilization="0/98304"
    cache_utilization_pct="0.0"
    demotions="0"
    dirty="0"
    end="62914560"
    features="1"
    md_block_size="8"
    md_utilization="200/2048"
    md_utilization_pct="9.765625"
    promotions="0"
    read_hits="0"
    read_misses="0"
    segment_type="cache"
    start="0"
    write_hits="0"
    write_misses="0"


[cliff]: http://cliff.readthedocs.org/en/latest/

## License

lvcache, a program for managing LVM cache devices  
Copyright (C) 2014 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

