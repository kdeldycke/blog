---
date: '2020-10-27'
title: TrueNAS Configuration and Maintenance
category: English
tags: hardware, NAS, filesystem, OS, FreeNAS, TrueNAS, hdd, hard-drive, ssd, raid, storage, network, ZFS, disk, package manager, FreeBSD, NTFS, partition, SuperMicro, BMC
---

A collection of personal notes on the setup, configuration and maintenance of a home-office TrueNAS appliance.

## 🖥 Hardware

I dedicated a whole post on [building the machine]({filename}/2020/nas-hardware.md), in which you'll get the detailed bill of material, cost breakdown and parts selection process.

### Reset BMC password

If you have one of iXsystems' TrueNAS server whose motherboard was produced by SuperMicro, there's a way to reset the BMC password with that CLI to use as `root`:

```{.shell-session}
[root@truenas] ~# ipmitool raw 0x3c 0x40

[root@truenas] ~#
```

## 📊 Reports

### Disk Temperature

⚠️ Do not activate any aggressive power-management parameters on disks. This is the main reasons temperatures are not reported in graphs.

## 📦 Package Management

To prevent the administrator to mess up with TrueNAS install, FreeBSD's package management has been locked down. Installing a package does not work:

```{.shell-session hl_lines="6"}
root@truenas[/]# pkg install dmg2img
Updating local repository catalogue...
pkg: file:///usr/ports/packages/meta.txz: No such file or directory
repository local has no meta file, using default settings
pkg: file:///usr/ports/packages/packagesite.txz: No such file or directory
Unable to update repository local
Error updating repositories!
```

If you know what you're doing and want to unlock package management, here is the fix:

```shell-session
root@truenas[/]# sed -i .orig 's/enabled: yes/enabled: no/' /usr/local/etc/pkg/repos/local.conf
root@truenas[/]# sed -i .orig 's/enabled: no/enabled: yes/' /usr/local/etc/pkg/repos/FreeBSD.conf
```

Now you're ready to update the package index:

```{.shell-session hl_lines="6"}
root@truenas[/]# pkg update
Updating FreeBSD repository catalogue...
Fetching meta.conf: 100%    163 B   0.2kB/s    00:01
Fetching packagesite.txz: 100%    6 MiB   6.7MB/s    00:01
Processing entries: 100%
FreeBSD repository update completed. 31953 packages processed.
All repositories are up to date.
```

And install your package:

```shell-session
root@truenas[/]# pkg install dmg2img
Updating FreeBSD repository catalogue...
FreeBSD repository is up to date.
All repositories are up to date.
New version of pkg detected; it needs to be installed first.
The following 1 package(s) will be affected (of 0 checked):

Installed packages to be UPGRADED:
	pkg: 1.14.6 -> 1.15.10 [FreeBSD]

Number of packages to be upgraded: 1

The operation will free 31 MiB.
7 MiB to be downloaded.

Proceed with this action? [y/N]: y
[1/1] Fetching pkg-1.15.10.txz: 100%    7 MiB   6.9MB/s    00:01
Checking integrity... done (0 conflicting)
[1/1] Upgrading pkg from 1.14.6 to 1.15.10...
[1/1] Extracting pkg-1.15.10: 100%
Updating FreeBSD repository catalogue...
FreeBSD repository is up to date.
All repositories are up to date.
The following 1 package(s) will be affected (of 0 checked):

New packages to be INSTALLED:
	dmg2img: 1.6.7 [FreeBSD]

Number of packages to be installed: 1

22 KiB to be downloaded.

Proceed with this action? [y/N]: y
[1/1] Fetching dmg2img-1.6.7.txz: 100%   22 KiB  22.5kB/s    00:01
Checking integrity... done (0 conflicting)
[1/1] Installing dmg2img-1.6.7...
[1/1] Extracting dmg2img-1.6.7: 100%

root@truenas[/]# dmg2img

dmg2img v1.6.7 (c) vu1tur (to@vu1tur.eu.org)

Usage: dmg2img [-l] [-p N] [-s] [-v] [-V] [-d] <input.dmg> [<output.img>]
or     dmg2img [-l] [-p N] [-s] [-v] [-V] [-d] -i <input.dmg> -o <output.img>

Options: -s (silent) -v (verbose) -V (extremely verbose) -d (debug)
         -l (list partitions) -p N (extract only partition N)
```

## 💾 Storage

### List all connected devices

`nvd0` is the system's NVMe SSD, `ada0` a SATA HDD and `da0` a USB external drive.

```shell-session
root@truenas[/mnt]# geom disk list
Geom name: nvd0
Providers:
1. Name: nvd0
   Mediasize: 250059350016 (233G)
   Sectorsize: 512
   Mode: r1w1e2
   descr: WDC WDS250G2B0C
   rotationrate: 0
   fwsectors: 0
   fwheads: 0

Geom name: ada0
Providers:
1. Name: ada0
   Mediasize: 6001175126016 (5.5T)
   Sectorsize: 512
   Stripesize: 4096
   Stripeoffset: 0
   Mode: r1w1e3
   descr: TOSHIBA HDWN160
   rotationrate: 7200
   fwsectors: 63
   fwheads: 16

Geom name: da0
Providers:
1. Name: da0
   Mediasize: 320072933376 (298G)
   Sectorsize: 512
   Mode: r0w0e0
   descr: ST332082 0ACE
   rotationrate: unknown
   fwsectors: 63
   fwheads: 255
```

### Mount an NTFS partition

```shell-session
root@truenas[/mnt]# kldload fuse.ko
root@truenas[/mnt]# mkdir usb-hdd
root@truenas[/mnt]# ntfs-3g /dev/da0p2 /mnt/usb-hdd
```

### Mount exFAT partition

```shell-session
root@truenas[/mnt]# gpart show ada4
=>        34  7814037101  ada4  GPT  (3.6T)
          34           6        - free -  (3.0K)
          40      409600     1  efi  (200M)
      409640        2008        - free -  (1.0M)
      411648  7813623808     2  ms-basic-data  (3.6T)
  7814035456        1679        - free -  (840K)

root@truenas[/mnt]# mkdir hdd-4tb                                              

root@truenas[/mnt]# kldload fusefs

root@truenas[/mnt]# mount.exfat-fuse /dev/ada4p2 ./hdd-4tb                     
```

### Delete a partition

```shell-session
root@truenas[/mnt]# gpart show da0
=>        34  7814037101  da0  GPT  (3.6T)
          34           6       - free -  (3.0K)
          40      409600    1  efi  (200M)
      409640  7813365344    2  apple-hfs  (3.6T)
  7813774984      262151       - free -  (128M)

root@truenas[/mnt]# gpart delete -i 1 da0
da0p1 deleted

root@truenas[/mnt]# gpart show da0
=>        34  7814037101  da0  GPT  (3.6T)
          34      409606       - free -  (200M)
      409640  7813365344    2  apple-hfs  (3.6T)
  7813774984      262151       - free -  (128M)
```

### 3-pass USB HDD wipe

```shell-session
root@truenas[/mnt]# bcwipe -v -me -t2 -b /dev/da0
Multithreading not supported.
Run ./configure with --enable-pthreads option, then rebuild BCWipe to enable multithreading.
Wiping scheme: US DoE, 3 pass(es)
Wipe /dev/da0 (y/[n]/a)?y
Wiping char device '/dev/da0'
Device '/dev/da0' opened in direct access mode
Device size 320072933376 bytes (312571224 kB), method 3
Wiping char device '/dev/da0' pass 1/3 [random] started
wipe pass  1/3 :    212992/312571224 kB (  0%)   Rate: 21233 kB/s
```

### ZFS

- List all snapshots of the `tank/my-data` dataset:

  ```shell-session
  $ zfs list -r -t snapshot tank/my-data
  ```

- Rename all snapshot's names prefixes from `auto-` to `daily-`, for the `tank/my-data` dataset and its children:

  ```shell-session
  $ zfs list -r -t snapshot tank/my-data
  NAME                                                       USED  AVAIL     REFER  MOUNTPOINT
  tank/my-data@auto-2021-09-02_00-00                           0B      -      209G  -
  tank/my-data@auto-2021-09-03_00-00                           0B      -      209G  -
  tank/my-data@auto-2021-09-04_00-00                           0B      -      209G  -
  (...)
  $ zfs list -r -t snapshot -o name -H tank/my-data | awk '{$2 = $1; sub(/@auto\-/, "@daily-", $2); printf "%s\n%s\n", $1, $2;}' | tr '\n' '\0' | xargs -0 -n 2 -t zsh -c 'zfs rename "$0" "$1"'
  zsh -c zfs rename "$0" "$1" tank/my-data@auto-2021-09-02_00-00 tank/my-data@daily-2021-09-02_00-00
  zsh -c zfs rename "$0" "$1" tank/my-data@auto-2021-09-03_00-00 tank/my-data@daily-2021-09-03_00-00
  zsh -c zfs rename "$0" "$1" tank/my-data@auto-2021-09-04_00-00 tank/my-data@daily-2021-09-04_00-00
  (...)
  $ zfs list -r -t snapshot tank/my-data
  NAME                                                       USED  AVAIL     REFER  MOUNTPOINT
  tank/my-data@daily-2021-09-02_00-00                          0B      -      209G  -
  tank/my-data@daily-2021-09-03_00-00                          0B      -      209G  -
  tank/my-data@daily-2021-09-04_00-00                          0B      -      209G  -
  (...)
  ```

## 🐛 Issues

### FreeNAS to TrueNAS migration

I wrote a long article on [how to migrate an encrypted pool from FreeNAS to TrueNAS]({filename}/2020/migration-from-freenas-to-truenas.md).

### Unreachable Network due to Multiple NICs

My machine was regularly disconnected from the network and couldn't be cleanly rebooted. This started under `FreeNAS 11.3-U4.1` and is still reproducible with a fresh `TrueNAS 12.0`.

The issue lies somewhere in all connected interfaces being granted DHCP active service:

https://www.youtube.com/watch?v=vDMooVj-flM

The [issue is being discussed on iXsystems' JIRA](https://jira.ixsystems.com/browse/NAS-108043).

### `ValidateUpdate` error on upgrade

Got the following error on upgrade?

```pytb
PermissionError: [Errno 13] Permission denied: './ValidateUpdate'
```

The fix: temporary [switch the System Dataset](https://www.truenas.com/docs/hub/tasks/advanced/system-dataset/) to `freenas-boot`. Your default system dataset is probably set to your ZFS pool which might be unavailable for whatever reason. In my case, I was in the middle of a [pool migration process]({filename}/2020/migration-from-freenas-to-truenas.md).
