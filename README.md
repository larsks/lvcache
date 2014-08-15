**WARNING** This is being heavily rewritten, possibly as you are
reading this.  This document has no bearing on reality at this point
in time.


## Overview

The `lvcache` command is a wrapper for the sequence of commands
required to create an LVM cache volume and attach it to an existing
"origin" volume.

## Synopsis

    lvcache.py [-h] [--cache-size CACHE_SIZE]
              [--cache-percent CACHE_PERCENT]
              [--cache-device CACHE_DEVICE] [--cache-tag CACHE_TAG]
              [--verbose] [--debug] [--dryrun]
              lvspec

## Options

- `--cache-size`, `-s` *size*

  Specifies the size of the cache volume in bytes.  As with LVM, you
  may specify units as (k)ilobytes, (m)egabytes, (g)igabytes,
  (t)erabytes, (p)etabytes, (e)xabytes.  Capitalize the units for SI
  units (multiples of 1000) instead of multiples of 1024.

- `--cache-percent`, `-%` *percent*

  Specifies the size of the cache volume as a percentage of the size
  of the origin volume.

  By default, `lvcache` will create a cache volume that is 20% the
  size of the origin volume.

- `--cache-device`, `-d` *device*

  Specify the PV (physical volume) on which to place the cache
  volume as a device path (e.g., `/dev/sdb`).

- `--cache-tag`, `-t` *tag*

  Specify the PV (physical volume) on which to place the cache
  volume as a PV tag (e.g., `cache`).  You can apply tags to your
  physical volumes using the `pvchange --addtag <tag>` command.

  By default, `lvcache` will select PVs with the `cache` tag.

- `--verbose`, `-v`

  Enable verbose output.

- `--debug`, `-D`

  Enable debug output.

- `--dryrun`, `-n`

  Print rather than execute LVM commands


## Examples

The following examples assume a volume group (VG) named `fedora`
exists and that on this volume group there exists a logical volume
(LV) named `libvirt`.

The `fedora` VG comprises the following physical volumes (PVs):

    # pvs -oname,size,tags
      PV        PSize   PV Tags
      /dev/sda2 465.27g        
      /dev/sdb  223.57g cache  

### Using default values

    # lvcache -v fedora/libvirt
    INFO:root:origin size: 42G (42949672960 bytes)
    INFO:root:cache data size: 8G (8589934592 bytes)
    INFO:root:cache metadata size: 8M (8589824 bytes)
    INFO:root:creating cache data lv libvirt_cache
      Logical volume "libvirt_cache" created
    INFO:root:creating cache metadata lv libvirt_cache_md
      Rounding up size to full physical extent 12.00 MiB
      Logical volume "libvirt_cache_md" created
    INFO:root:creating cache pool
      Converted fedora/libvirt_cache to cache pool.
    INFO:root:attach cache pool to volume fedora/libvirt
      fedora/libvirt is now cached.
    # lvs -o name,attr 2>&1 | grep libvirt
      libvirt                                     Cwi-aoC---
      libvirt_cache                               Cwi---C---

Behind the scenes, this runs the following sequence of commands:

    lvcreate -L 8589934592b -n libvirt_cache fedora @cache
    lvcreate -L 8589824b -n libvirt_cache_md fedora @cache
    lvconvert --type cache-pool --poolmetadata fedora/libvirt_cache_md fedora/libvirt_cache
    lvconvert --type cache --cachepool fedora/libvirt_cache fedora/libvirt

### Specifying cache size

This examples uses a cache volume that is 50% the size of the origin
volume:

    # lvcache -v -% 50 fedora/libvirt
    INFO:root:origin size: 42G (42949672960 bytes)
    INFO:root:cache data size: 21G (21474836480 bytes)
    INFO:root:cache metadata size: 21M (21474816 bytes)
    INFO:root:creating cache data lv libvirt_cache
      Logical volume "libvirt_cache" created
    INFO:root:creating cache metadata lv libvirt_cache_md
      Rounding up size to full physical extent 24.00 MiB
      Logical volume "libvirt_cache_md" created
    INFO:root:creating cache pool
      Converted fedora/libvirt_cache to cache pool.
    INFO:root:attach cache pool to volume fedora/libvirt
      fedora/libvirt is now cached.

## Removing a cache volume

To remove a cache volume, simply run `lvremove` on the cache volume:

    # lvremove fedora/libvirt_cache
    Do you really want to remove and DISCARD logical volume libvirt_cache? [y/n]: y
      Flushing cache for libvirt.
      0 blocks must still be flushed.
      Logical volume "libvirt_cache" successfully removed

This will flush the cache back to the origin lv and remove both the
cache data and metadata volumes.  Your origin volume will continue to
be available but without any attached cached.

