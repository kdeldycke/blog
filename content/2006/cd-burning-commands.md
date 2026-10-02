---
date: '2006-10-25'
title: CD Burning commands
category: English
tags: burning, Compact disc, cdrdao, cdrecord, CLI, DVD, Hardware, Linux, mkisofs
---

- List all CD devices:

  ```shell-session
  $ cdrdao scanbus
  ```

- Blank a CD-RW:

  ```shell-session
  $ cdrdao blank --device ATA:0,1,0 --driver generic-mmc
  ```

- Burn an ISO:

  ```shell-session
  $ cdrecord -v speed=8 dev=ATA:0,1,0 ./geexbox-0.98-fr.iso
  ```

- Generate an ISO image of a CD-ROM:

  ```shell-session
  $ dd if=/dev/cdrom of=/tmp/cdrom-image.iso
  ```

- Create an ISO from a local directory:

  ```shell-session
  $ mkisofs -R -r -l -J -V volid -o /tmp/cdrom-image.iso src
  ```

  Where:

  - `volid` is the volume ID to be written into the master block;
  - `/tmp/cdrom-image.iso` is the destination filename of the newly created ISO image;
  - `src` is the temporary ISO directory containing the files and file structure you wish to have included in the ISO image.

- Mount a local ISO image as if it's a physical CD-Rom:

  ```shell-session
  $ mount -t iso9660 -o loop /tmp/cdrom-image.iso /media/cd-image/
  ```

- Mount an UDF file system image:

  ```shell-session
  $ fuseiso -p dvd.img /media/dvd-image/
  ```

- Convert a [Nero's proprietary `.nrg` CD image](https://en.wikipedia.org/wiki/NRG_(file_format)) to standard ISO file:

  ```shell-session
  $ nrg2iso dvd-image.nrg dvd-image.iso
  ```
