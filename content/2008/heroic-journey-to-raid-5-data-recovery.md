---
date: '2008-07-24'
title: Heroic journey to RAID-5 data recovery
category: English
tags: array, Backup, disk, drive, Hardware, HDD, Linux, mdadm, monitoring, RAID, Server, system, UPS
---

Last week there was a power grid failure which break down my server's RAID array. I have no [UPS](https://en.wikipedia.org/wiki/Uninterruptible_power_supply) (as I'm a skinflint) and no automatic email alerts (because I'm too lazy to set it up). As a result, for 5 days, my 3-disk [RAID-5 array](https://en.wikipedia.org/wiki/RAID_5) was relying on only 2 disks until I noticed the issue...

By using a combination of following commands, I was soon aware of the gravity of the situation:

```shell-session
$ cat /proc/mdstat
$ mdadm --examine /dev/sda1
```

My `/dev/sda1` disk was kicked out of the array, so I did the right stuff which consisted of reconstructing the array:

```shell-session
$ mdadm /dev/md0 -a /dev/sda1
```

Then, in an unlucky combination of cosmic ray bombardment, spooky action at a distance and astrological misalignment, half-way to the end of the rebuilding process (which can take up to 5 hours), another disk failed! It was late, I was tired and utterly worried about losing 1.5 To of precious data. In such a bad shape, I was afraid to worsen the situation. So I decided to shutdown the server and sleep on the problem.

The next day I tried to boot my server to find it (surprise!) stuck in the middle of the boot process, with the famous message:

```text
hit control-D to continue or give root password to fix manually
```

This is "normal" as my server tried to mount the [ext3 filesystem](https://en.wikipedia.org/wiki/Ext3) from the `/dev/md0` partition that was just assembled by `mdadm`. Of course `md0`, if assembled and available to the system, was not running because only one disk, out of three, was in a clean state.

I skip here the epic substory in which I wasted days in a search of a working keyboard, but I let you imagine how such adventures makes my week...

Eventually, I was able to analyze the situation in details. My first reflex? Check that disks are not physically dead:

```shell-session
$ fdisk -l /dev/sda
$ fdisk -l /dev/sdb
$ fdisk -l /dev/sdc
```

"Linux raid partitions" (type code "`fd`") are still there. Good. I assumed here that disks where not physically damaged. Maybe I should have looked at [S.M.A.R.T.](https://en.wikipedia.org/wiki/Self-Monitoring,_Analysis,_and_Reporting_Technology) data and statistics (via [smartmontools](https://www.smartmontools.org/)). But remember, I'm lazy (and a bit crazy).

The next step was to get information about the RAID array itself using:

```shell-session
$ mdadm --detail /dev/md0
```

which output the status table below (probably inaccurate as I reconstructed it afterwards):

```text
Number   Major   Minor   RaidDevice State
   0       0        0        0      removed
   1       0        0        1      faulty removed
   2       8       33        2      active sync   /dev/sdc1
   3       8       17        3      spare
```

What this table told us?

- The array is up, but not running. One of its device (`sdc1`) was clean and active, but it's not enough to get a working RAID-5.

- My first attempt to rebuild the array lead to an unexpected result: it added `sda1` as a spare device (in slot #3).

- It confirm that `sdb1` unexpectedly failed and is now in a bad state ("`faulty removed`").

Then I stopped the array and tried to fearlessly (re)assemble it using 3 different methods:

```shell-session
$ mdadm -S /dev/md0
$ mdadm -A /dev/md0
$ mdadm --assemble /dev/md0 --verbose /dev/sd[abc]1
$ mdadm --assemble --force --scan /dev/md0 --verbose
```

It always failed with messages like:

```text
mdadm: failed to RUN_ARRAY /dev/md0: Input/output error
mdadm: /dev/md0 assembled from 1 drives and 1 spare - not enough to start the array.
```

So I examined each drive from `mdadm`'s point of view:

```shell-session
$ mdadm -E /dev/sda1
$ mdadm -E /dev/sdb1
$ mdadm -E /dev/sdc1
$ mdadm -E /dev/sd[abc]1 | grep Event
```

The latest command compare the "`Event`" attribute of all devices. It output something like:

```text
Events : 0.53120
Events : 0.53108
Events : 0.53120
```

which indicate that `sda1` and `sdc1` are somewhat synced (share the same number) and `sdb1` "late" (lower number).

Here I've got the idea of recreating the raid array without `sdb1`, relying only on `sda1` and `sdc1`, by using the "magic" (hence dangerous) `--assume-clean` option. The latter doesn't build, erase or initialize a new array. It just try to assemble it "as is". Here is the command:

```shell-session
$ mdadm --create /dev/md0 --assume-clean --level=5 --verbose --raid-devices=3 /dev/sda1 missing /dev/sdc1
```

And it worked! :D

I mounted the `md0` partition and cleaned it up:

```shell-session
$ fsck.ext3 -v /dev/md0
$ mount /dev/md0
```

I updated my [mdadm](https://web.archive.org/web/20080718190124/http://neil.brown.name/blog/mdadm) configuration before rebooting my server:

```shell-session
$ mdadm --detail --scan >> /etc/mdadm/mdadm.conf
$ vi /etc/mdadm/mdadm.conf
$ reboot
```

But history repeat itself, and again, the system hang up during boot. Except this time I knew what was happening: the boot process detected the remaining `sdb1` device as part of the old array (the one before the regeneration I did above) and tried to run it. [Remembering my last year post]({filename}/2007/how-to-recover-a-raid-array-after-having-zero-ized-superblocks.md), I zero-ized the superblock of `sdb1`:

```shell-session
$ mdadm -S /dev/md0
$ mdadm --zero-superblock /dev/sdb1
```

A server reboot proved I was right and my `md0` partition was automagically mounted in altered state:

```shell-session
$ cat /proc/mdstat
Personalities : [raid6] [raid5] [raid4]
md0 : active raid5 sdb1[3] sda1[0] sdc1[2]
      1465143808 blocks level 5, 64k chunk, algorithm 2 [3/2] [U_U]

unused devices: <none>
```

I just had to re-add `sdb1` to fill the available slot and update the mdadm configuration to get back my array in its initial state:

```shell-session
$ mdadm --manage /dev/md0 --add /dev/sdb1
$ mdadm --detail --scan >> /etc/mdadm/mdadm.conf
$ vi /etc/mdadm/mdadm.conf
```
