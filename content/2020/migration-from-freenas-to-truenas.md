---
date: '2020-12-27'
title: Migration from FreeNAS to TrueNAS
category: English
tags: NAS, filesystem, OS, FreeNAS, TrueNAS, hdd, hard-drive, ssd, raid, storage, network, ZFS
---

The upgrade itself is quite straightforward by the way of the GUI. But things gets complicated if you've got an encrypted pool.

## Encrypted pool migration

Upgrading from FreeNAS to TrueNAS will render your encrypted pool unavailable. FreeNAS relies on [`geli`](https://en.wikipedia.org/wiki/Geli_%28software%29)'s block-layer disk encryption and is considered legacy. TrueNAS moved to native ZFS encryption at the dataset level.

We have no choice but to convert it. And [there is no easy path](https://www.truenas.com/docs/hub/initial-setup/storage/encryption/#conversion-from-geli) but destroying the pool and recreating it. 😱

So first things first: **BACKUP YOUR POOL**!

But I'm stupid. So I will attempt the migration without any safe guard.

I currently run a [4 * 6 TB RAID-Z2 array]({filename}/2020/nas-hardware.md#raid-array), which is half-empty. I feel the risk is worth taking as long as I only manipulate one disk at a time.

My plan consist in:

1. Removing the encryption on the array, disk by disk;
2. Then upgrade the array to the new OpenZFS 2.0;
3. To finally re-activate the encryption later.

## Logging in

After the migration to TrueNAS `12.0-U1`, the main pool (which I called `big`), gets locked:

![TrueNAS pools page listing the big pool as the system dataset pool under legacy encryption, marked LOCKED with the note that this geli-encrypted pool failed to decrypt](legacy-encrypted-truenas-zfs-offline-pool.jpeg)

All system metadata resides there. We can no longer SSH into the box with our regular users. We'll hack our way in and create a new temporary one.

Go to `Accounts` > `Users`, click `Add` button. Then setup our new user:

- Username: `kev-tmp`
- Password: Get a good random one
- Home Directory: `/nonexistent`
- Keep all other defaults as-is

Go to `Services`. Stop all daemons, but make sure `SSH` is `Running`.

Click `SSH`'s `Actions`, and in the `General Options` check `Allow Password Authentication`.

Double check you're allowed to authenticate with a password from your machine:

~~~{.ssh filename="~/.ssh/config" hl_lines="3"}
(…)
Host truenas.local
    PasswordAuthentication yes
~~~

Then login to your NAS as `root`:

```{.shell-session hl_lines="16"}
$ ssh kev-tmp@truenas.local
Host key fingerprint is SHA256:XXXXXXXXXXXXXXXXXXXXXXXXX
kev-tmp@truenas.local's password:
FreeBSD 12.2-RELEASE-p2 663e6b09467(HEAD) TRUENAS

TrueNAS (c) 2009-2020, iXsystems, Inc.
All rights reserved.
TrueNAS code is released under the modified BSD license with some
files copyrighted by (c) iXsystems, Inc.

For more information, documentation, help or support, go here:
http://truenas.com
Welcome to TrueNAS
Could not chdir to home directory /nonexistent: No such file or directory

truenas% sudo su

root@truenas[/]#
```

## Decrypt geli disks

Get a copy of your pool encryption key. You kept it around from back then, when you created your pool. Right? 🧐

So let's push a copy of it from your machine to the NAS:

```shell-session
$ scp ~/pool_big_encryption.key kev-tmp@truenas.local:/tmp/pool_big_encryption.key
```

Get the list of your partitions IDs:

```shell-session
root@truenas[/]# glabel status
Name                                       Status Components
gptid/4e377340-917d-11ea-a640-b42e99bf5e8f N/A    ada1p2
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f N/A    ada2p2
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f N/A    ada3p2
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f N/A    ada4p2
```

Our pool is composed of the four `ada[1,2,3,4]p2` partitions.

Now decrypt each partition with the key:

```shell-session
root@truenas[/]# geli attach -p -k /tmp/pool_big_encryption.key /dev/gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli attach -p -k /tmp/pool_big_encryption.key /dev/gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli attach -p -k /tmp/pool_big_encryption.key /dev/gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli attach -p -k /tmp/pool_big_encryption.key /dev/gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
```

Check our partitions are properly active and decrypted:

```shell-session
root@truenas[/]# geli status
Name                                           Status Components
gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
```

Notice the `.eli` suffix indicating the partition is encrypted.

## Activating the pool

At this point a couple of notifications will pop-up:

![Alerts panel filled by a critical VolumeStatus traceback ending in AttributeError, NoneType object has no attribute values, raised from flatten_topology](truenas-critical-error-volume-status.jpeg)

```pytb
Failed to check for alert VolumeStatus:
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/middlewared/plugins/alert.py", line 706, in __run_source
    alerts = (await alert_source.check()) or []
  File "/usr/local/lib/python3.8/site-packages/middlewared/alert/source/volume_status.py", line 31, in check
    for vdev in await self.middleware.call("pool.flatten_topology", pool["topology"]):
  File "/usr/local/lib/python3.8/site-packages/middlewared/main.py", line 1238, in
    call return await self._call(
  File "/usr/local/lib/python3.8/site-packages/middlewared/main.py", line 1206, in _call
    return await self.run_in_executor(prepared_call.executor, methodobj, *prepared_call.args)
  File "/usr/local/lib/python3.8/site-packages/middlewared/main.py", line 1110, in run_in_executor
    return await loop.run_in_executor(pool, functools.partial(method, *args, **kwargs))
  File "/usr/local/lib/python3.8/site-packages/middlewared/utils/io_thread_pool_executor.py", line 25, in run
    result = self.fn(*self.args, **self.kwargs)
  File "/usr/local/lib/python3.8/site-packages/middlewared/plugins/pool.py", line 438, in flatten_topology
    d = deque(sum(topology.values(), []))
AttributeError: 'NoneType' object has no attribute 'values'
```

I chose to simply ignore that one.

And now the pool is materialized in the GUI:

![Pools page with the big pool now listed but flagged OFFLINE with a red cross](legacy-encrypted-offline-zfs-pool.jpeg)

It is offline, but can be activated from the shell:

```shell-session
root@truenas[/]# zpool import big
```

The pool is now online:

```{.shell-session hl_lines="3"}
root@truenas[/]# zpool status big
  pool: big
 state: ONLINE
status: One or more devices has experienced an unrecoverable error. An
		attempt was made to correct the error. Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
		using 'zpool clear' or replace the device with 'zpool replace'.
		see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
  scan: resilvered 30.6M in 00:00:04 with 0 errors on Thu Dec 10 13:24:46 2020
config:

		NAME                                           		STATE  	 READ WRITE CKSUM
		big                                                 ONLINE 		0     0     0
		  raidz2-0                                          ONLINE 		0     0     0
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     2
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     2
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     0

errors: No known data errors
```

![Pool status page after a finished resilver with zero errors, the RAIDZ2 vdev and all four partitions ONLINE, though ada1p2 and ada2p2 each carry two checksum errors](legacy-encrypted-online-zfs-pool.jpeg)

We got a couple of notifications, one that is warning us about the [`ZFS-8000-9P` error](https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P/).

![Critical alert saying pool big is ONLINE but one or more devices hit an unrecoverable error that an attempt was made to correct, with applications unaffected](zfs-online-pool-unrecoverable-error.jpeg)

```text
CRITICAL
Pool big state is ONLINE: One or more devices has experienced an unrecoverable error. An attempt was made to correct the error. Applications are unaffected.
```

The data seems OK and safe thanks to RAID-Z2. This issue might just be a side-effect of reviving the pool one disk at a time via the `geli` commands above. So I choose to ignore this minor warning and `clear` it:

```shell-session
root@truenas[/]# zpool clear big
root@truenas[/]# zpool status big
  pool: big
 state: ONLINE
status: Some supported features are not enabled on the pool. The pool can
		still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
		the pool may no longer be accessible by software that does not support
		the features. See zpool-features(5) for details.
  scan: resilvered 30.6M in 00:00:04 with 0 errors on Thu Dec 10 13:24:46 2020
config:

		NAME                                           		STATE    READ WRITE CKSUM
		big                                            		ONLINE 		0     0     0
		  raidz2-0                                       	ONLINE      0     0     0
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE      0     0     0
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE  	0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE 		0     0     0

errors: No known data errors
```

ZFS is also proposing to upgrade the pool, but we will not:

![Warning offering new ZFS feature flags for pool big, cautioning that upgrading is one-time and blocks rolling back to an earlier TrueNAS version](zfs-feature-flag-pool-upgrade.jpeg)

```text
WARNING
New ZFS version or feature flags are available for pool big. Upgrading pools is a one-time process that can prevent rolling the system back to an earlier TrueNAS version. It is recommended to read the TrueNAS release notes and confirm you need the new ZFS feature flags before upgrading a pool.
```

Doing so will prevent us to revert back to FreeNAS if anything bad happens. [We'll do that later](#zfs-upgrade).

## Removing encryption

The strategy here consist in replacing each encrypted partition by itself, un-encrypted. The pool will be in a `DEGRADED` state during the operation.

First, we choose one partition (`ada1p2` in this case), and offline the disk from the web interface:

![Offline Disk confirmation for ada1 over the partition list, warning that disks cannot be brought back online in encrypted pools](offline-zfs-disk.jpeg)

Double-check the status of the pool with the CLI:

```{.shell-session hl_lines="15"}
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: One or more devices has been taken offline by the administrator.
		Sufficient replicas exist for the pool to continue functioning in a
		degraded state.
action: Online the device using 'zpool online' or replace the device with
		'zpool replace'.
  scan: resilvered 30.6M in 00:00:04 with 0 errors on Thu Dec 10 13:24:46 2020
config:

		NAME                                           		STATE     READ WRITE CKSUM
		big                                            		DEGRADED 	 0     0     0
		  raidz2-0                                          DEGRADED 	 0     0     0
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE  	 0     0     0
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0

errors: No known data errors
```

And verify our disk is no longer referenced by `geli`:

```shell-session
root@truenas[/]# geli status
Name                                           Status Components
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
```

We can now proceed with the resilvering of that disk into the pool:

```shell-session
root@truenas[/]# zpool replace big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
```

This is going to be a slow operation:

```{.shell-session hl_lines="7-9 15-17"}
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: One or more devices is currently being resilvered. The pool will
		continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Thu Dec 10 16:11:52 2020
		2.85T scanned at 889M/s, 1.29T issued at 402M/s, 12.3T total
		320G resilvered, 10.49% done, 07:57:38 to go
config:

		NAME                                                  STATE     READ WRITE CKSUM
		big                                                   DEGRADED     0     0     0
		  raidz2-0                                            DEGRADED     0     0     0
			replacing-0                                       DEGRADED 	   0     0     0
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE  	   0     0     0
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      ONLINE       0     0     0     (resilvering)
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0

errors: No known data errors
```

Wait until it completes. It took around 7 hours for one disk in my situation.

Once the resilvering finishes, redo with each disk the whole process from that section. You'll end up with a unencrypted pool with the same data as before:

```shell-session
root@truenas[/]# zpool status big
  pool: big
 state: ONLINE
status: Some supported features are not enabled on the pool. The pool can
        still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
        the pool may no longer be accessible by software that does not support
        the features. See zpool-features(5) for details.
  scan: resilvered 2.99T in 10:58:55 with 0 errors on Tue Jan  5 11:47:29 2021
config:

        NAME                                            STATE     READ WRITE CKSUM
        big                                             ONLINE       0     0     0
          raidz2-0                                      ONLINE       0     0     0
            gptid/4e377340-917d-11ea-a640-b42e99bf5e8f  ONLINE       0     0     0
            gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f  ONLINE       0     0     0
            gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f  ONLINE       0     0     0
            gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f  ONLINE       0     0     0

errors: No known data errors
```

### ZFS upgrade

We can now upgrade the ZFS version of the pool.

You can first check the pools which do not have all supported features enabled and those still in the legacy version:

```shell-session
root@truenas[/]# zpool upgrade
This system supports ZFS pool feature flags.

All pools are formatted using feature flags.


Some supported features are not enabled on the following pools. Once a
feature is enabled the pool may become incompatible with software
that does not support the feature. See zpool-features(5) for details.

POOL  FEATURE
---------------
big
      large_dnode
      userobj_accounting
      encryption
      project_quota
      allocation_classes
      resilver_defer
      bookmark_v2
      redaction_bookmarks
      redacted_datasets
      bookmark_written
      log_spacemap
      livelist
      device_rebuild
      zstd_compress
freenas-boot
      large_dnode
      userobj_accounting
      encryption
      project_quota
      allocation_classes
      resilver_defer
      bookmark_v2
      redaction_bookmarks
      redacted_datasets
      bookmark_written
      log_spacemap
      livelist
      device_rebuild
      zstd_compress
```

Then you can proceed with the upgrade itself for each pool:

```shell-session
root@truenas[/]# zpool upgrade big
This system supports ZFS pool feature flags.

Enabled the following features on 'big':
  large_dnode
  userobj_accounting
  encryption
  project_quota
  allocation_classes
  resilver_defer
  bookmark_v2
  redaction_bookmarks
  redacted_datasets
  bookmark_written
  log_spacemap
  livelist
  device_rebuild
  zstd_compress
```

```shell-session
root@truenas[/]# zpool upgrade freenas-boot
This system supports ZFS pool feature flags.

Enabled the following features on 'freenas-boot':
  large_dnode
  userobj_accounting
  encryption
  project_quota
  allocation_classes
  resilver_defer
  bookmark_v2
  redaction_bookmarks
  redacted_datasets
  bookmark_written
  log_spacemap
  livelist
  device_rebuild
  zstd_compress
```

And run a final check on the current feature status:

```shell-session
root@truenas[/]# zpool upgrade
This system supports ZFS pool feature flags.

All pools are formatted using feature flags.

Every feature flags pool has all supported features enabled.
```

Now you have a clean and upgraded pool.

## Re-encryption

Re-encrypting your newly migrated pool is left as an exercise to the user! 😁

## Failed replace

While performing the process above, you're still at the mercy of any corruption issue. It happened to me, and I woke up at one time with an failed replace operation. 😵

This section should help you recover from a failed operation.

In my case, the pool looked like this:

```{.shell-session hl_lines="15-17 19"}
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: One or more devices is currently being resilvered. The pool will
		continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Thu Dec 10 16:11:52 2020
		6.63T scanned at 464M/s, 5.63T issued at 394M/s, 12.3T total
		954G resilvered, 45.79% done, 04:55:41 to go
config:

		NAME                                           		  STATE     READ WRITE CKSUM
		big                                            		  DEGRADED     0     0     0
		  raidz2-0                                       	  DEGRADED 	   0     0     0
	 	    replacing-0                                    	  UNAVAIL      0   160     0     insufficient replicas
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE      0     0     0
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      REMOVED      0     0     0     (resilvering)
		  	gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli 	  ONLINE       0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli    REMOVED      0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0

errors: No known data errors
```

I don't know what happened, but I quickly discovered 2 disks were no longer actively decrypted:

```shell-session
root@truenas[/]# geli status
Name                                           Status Components
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
```

And one disk, `ada1p2`, i.e. the one being replaced, disappeared:

```shell-session
root@truenas[/]# glabel status
Name                                       Status Components
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f N/A    ada3p2
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f N/A    ada4p2
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f N/A    ada2p2
gptid/4e8b58ff-917d-11ea-a640-b42e99bf5e8f N/A    ada2p1
```

So I quickly re-attached the one still encrypted (not the one being replaced):

```{.shell-session hl_lines="7"}
root@truenas[/]# geli attach -p -k /tmp/pool_big_recovery.key /dev/gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f

root@truenas[/]# geli status
Name                                           Status Components
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
```

Fortunately, ZFS re-integrated it to the pool, changing its state from `REMOVED` to `ONLINE`, at the price of an automatic resilvering:

```{.shell-session hl_lines="7-9 19"}
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: One or more devices is currently being resilvered. The pool will
		continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Fri Dec 11 00:18:45 2020
		1.76T scanned at 139G/s, 324K issued at 24.9K/s, 12.3T total
		0B resilvered, 0.00% done, no estimated completion time
config:

		NAME                                                  STATE     READ WRITE CKSUM
		big                                                   DEGRADED     0     0     0
		  raidz2-0                                            DEGRADED 	   0     0     0
			replacing-0                                       UNAVAIL  	   0   160     0     insufficient replicas
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE      0     0     0
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      REMOVED  	   0     0     0
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0

errors: No known data errors
```

Another 7 hours later, with the resilvering completed, it was time to fix the failed `replacing-0` operation.

I tried to force my way but it did not worked:

```shell-session
root@truenas[/]# zpool replace big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
cannot open 'gptid/4e377340-917d-11ea-a640-b42e99bf5e8f': no such device in /dev
must be a full path or shorthand device name
```

```shell-session
root@truenas[/]# zpool online big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
cannot online gptid/4e377340-917d-11ea-a640-b42e99bf5e8f: no such device in pool
```

That's when I realized `4e377340-917d-11ea-a640-b42e99bf5e8f` (a.k.a. `ada1p2`), was completely kicked-out by the system. I stumbled upon some worrying logs that might hint to a kind of hardware issue:

```{.log hl_lines="12 38 69 76"}
Dec 10 19:18:35 truenas ahcich3: Timeout on slot 31 port 0
Dec 10 19:18:35 truenas ahcich3: is 00000000 cs 80000000 ss 80000000 rs 80000000 tfd c0 serr 00000000 cmd 0000df17
Dec 10 19:18:35 truenas (ada2:ahcich3:0:0:0): READ_FPDMA_QUEUED. ACB: 60 80 30 6b 94 40 08 02 00 00 00 00
Dec 10 19:18:35 truenas (ada2:ahcich3:0:0:0): CAM status: Command timeout
Dec 10 19:18:35 truenas (ada2:ahcich3:0:0:0): Retrying command, 3 more tries remain
Dec 10 19:18:35 truenas ahcich5: Timeout on slot 1 port 0
Dec 10 19:18:35 truenas ahcich5: is 00000000 cs 00000002 ss 00000002 rs 00000002 tfd c0 serr 00000000 cmd 0000c117
Dec 10 19:18:35 truenas (ada3:ahcich5:0:0:0): READ_FPDMA_QUEUED. ACB: 60 80 30 6b 94 40 08 02 00 00 00 00
Dec 10 19:18:35 truenas (ada3:ahcich5:0:0:0): CAM status: Command timeout
Dec 10 19:18:35 truenas (ada3:ahcich5:0:0:0): Retrying command, 3 more tries remain
Dec 10 19:18:52 truenas ada2 at ahcich3 bus 0 scbus3 target 0 lun 0
Dec 10 19:18:52 truenas ada2: <TOSHIBA HDWN160 FS1M> s/n 10LSK1FPFAXG detached
Dec 10 19:18:52 truenas GEOM_ELI: g_eli_read_done() failed (error=6) gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli[READ(offset=4469598543872, length=65536)]
Dec 10 19:18:52 truenas GEOM_MIRROR: Device swap0: provider ada2p1 disconnected.
Dec 10 19:19:23 truenas ahcich1: Timeout on slot 31 port 0
Dec 10 19:19:23 truenas ahcich1: is 00000000 cs 80000000 ss 80000000 rs 80000000 tfd c0 serr 00000000 cmd 0000df17
Dec 10 19:19:23 truenas (ada1:ahcich1:0:0:0): WRITE_FPDMA_QUEUED. ACB: 61 80 38 6b 94 40 08 02 00 00 00 00
Dec 10 19:19:23 truenas (ada1:ahcich1:0:0:0): CAM status: Command timeout
Dec 10 19:19:23 truenas (ada1:ahcich1:0:0:0): Retrying command, 3 more tries remain
Dec 10 19:19:57 truenas ahcich3: AHCI reset: device not ready after 31000ms (tfd = 00000080)
Dec 10 19:20:01 truenas ahcich1: AHCI reset: device not ready after 31000ms (tfd = 00000080)
Dec 10 19:20:31 truenas ahcich1: Timeout on slot 0 port 0
Dec 10 19:20:31 truenas ahcich1: is 00000000 cs 00000000 ss 00000000 rs 00000001 tfd 150 serr 00000000 cmd 0000c017
Dec 10 19:20:31 truenas (aprobe1:ahcich1:0:0:0): ATA_IDENTIFY. ACB: ec 00 00 00 00 40 00 00 00 00 00 00
Dec 10 19:20:31 truenas (aprobe1:ahcich1:0:0:0): CAM status: Command timeout
Dec 10 19:20:31 truenas (aprobe1:ahcich1:0:0:0): Retrying command, 0 more tries remain
Dec 10 19:21:05 truenas ahcich1: Timeout on slot 1 port 0
Dec 10 19:21:05 truenas ahcich1: is 00000000 cs 00000002 ss 00000000 rs 00000002 tfd 1d0 serr 00000000 cmd 0000c117
Dec 10 19:21:05 truenas (aprobe1:ahcich1:0:0:0): ATA_IDENTIFY. ACB: ec 00 00 00 00 40 00 00 00 00 00 00
Dec 10 19:21:05 truenas (aprobe1:ahcich1:0:0:0): CAM status: Command timeout
Dec 10 19:21:05 truenas (aprobe1:ahcich1:0:0:0): Error 5, Retries exhausted
Dec 10 19:21:39 truenas ahcich1: Timeout on slot 2 port 0
Dec 10 19:21:39 truenas ahcich1: is 00000000 cs 00000004 ss 00000000 rs 00000004 tfd 1d0 serr 00000000 cmd 0000c217
Dec 10 19:21:39 truenas (aprobe1:ahcich1:0:0:0): ATA_IDENTIFY. ACB: ec 00 00 00 00 40 00 00 00 00 00 00
Dec 10 19:21:39 truenas (aprobe1:ahcich1:0:0:0): CAM status: Command timeout
Dec 10 19:21:39 truenas (aprobe1:ahcich1:0:0:0): Error 5, Retry was blocked
Dec 10 19:21:39 truenas ada1 at ahcich1 bus 0 scbus1 target 0 lun 0
Dec 10 19:21:39 truenas ada1: <TOSHIBA HDWN160 FS1M> s/n Z9B3K1OAFAXG detached
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): ATA_IDENTIFY. ACB: ec 00 00 00 00 40 00 00 00 00 00 00
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): CAM status: ATA Status Error
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): ATA status: 31 (DF SERV ERR), error: 04 (ABRT )
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): RES: 31 04 e0 6a 94 48 08 02 00 00 00
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): Retrying command, 0 more tries remain
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): ATA_IDENTIFY. ACB: ec 00 00 00 00 40 00 00 00 00 00 00
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): CAM status: ATA Status Error
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): ATA status: 31 (DF SERV ERR), error: 04 (ABRT )
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): RES: 31 04 e0 6a 94 48 08 02 00 00 00
Dec 10 19:22:00 truenas (aprobe0:ahcich1:0:0:0): Error 5, Retries exhausted
Dec 10 19:22:00 truenas xptioctl: pass driver is not in the kernel
Dec 10 19:22:00 truenas xptioctl: put "device pass" in your kernel config file
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): SETFEATURES ENABLE RCACHE. ACB: ef aa 00 00 00 40 00 00 00 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): CAM status: ATA Status Error
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): ATA status: 31 (DF SERV ERR), error: 04 (ABRT )
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): RES: 31 04 e0 6a 94 48 08 02 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): Error 5, Periph was invalidated
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): SETFEATURES ENABLE WCACHE. ACB: ef 02 00 00 00 40 00 00 00 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): CAM status: ATA Status Error
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): ATA status: 31 (DF SERV ERR), error: 04 (ABRT )
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): RES: 31 04 e0 6a 94 48 08 02 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): Error 5, Periph was invalidated
Dec 10 19:22:00 truenas ahcich1: Error while READ LOG EXT
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): WRITE_FPDMA_QUEUED. ACB: 61 80 38 6b 94 40 08 02 00 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): CAM status: ATA Status Error
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): ATA status: 00 ()
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): RES: 00 00 00 00 00 00 00 00 00 00 00
Dec 10 19:22:00 truenas (ada1:ahcich1:0:0:0): Error 5, Periph was invalidated
Dec 10 19:22:02 truenas GEOM_ELI: Device gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli destroyed.
Dec 10 19:22:02 truenas GEOM_ELI: Detached gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli on last close.
Dec 10 19:22:02 truenas (ada2:ahcich3:0:0:0): Periph destroyed
Dec 10 19:22:02 truenas ada2 at ahcich3 bus 0 scbus3 target 0 lun 0
Dec 10 19:22:02 truenas ada2: <TOSHIBA HDWN160 FS1M> ATA8-ACS SATA 3.x device
Dec 10 19:22:02 truenas ada2: Serial Number 10LSK1FPFAXG
Dec 10 19:22:02 truenas ada2: 600.000MB/s transfers (SATA 3.x, UDMA5, PIO 8192bytes)
Dec 10 19:22:02 truenas ada2: Command Queueing enabled
Dec 10 19:22:02 truenas ada2: 5723166MB (11721045168 512 byte sectors)
Dec 10 19:22:02 truenas (ada1:ahcich1:0:0:0): Periph destroyed
```

So with no resilvering or any heavy operation pending on the pool, I decided to offline the partitions and restart the machine:

```shell-session
root@truenas[/]# zpool offline big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f
```

```shell-session
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: Some supported features are not enabled on the pool. The pool can
		still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
		the pool may no longer be accessible by software that does not support
		the features. See zpool-features(5) for details.
  scan: resilvered 15.5M in 05:42:26 with 0 errors on Fri Dec 11 06:01:11 2020
config:

		NAME                                                STATE    READ WRITE CKSUM
		big                                                 DEGRADED    0     0     0
		  raidz2-0                                          DEGRADED 	0     0     0
		  replacing-0                                       OFFLINE  	0   160     0     all children offline
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE  	0     0     0
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      OFFLINE  	0     0     0
		  gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE   	0     0     0
		  gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE   	0     0     0
		  gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE   	0     0     0

errors: No known data errors
```

```shell-session
root@truenas[/]# poweroff
Shutdown NOW!
poweroff: [pid 27282]

root@truenas[/]#
*** FINAL System shutdown message from kev-tmp@truenas.local ***

System going down IMMEDIATELY

System shutdown time has arrived
Shared connection to truenas.local closed.
```

![Hello IT, have you tried turning it off and on again?](have-you-tried-turning-it-off-and-on-again.jpg)

I got lucky, `ada1p2` showed up after the reboot:

```{.shell-session hl_lines="3"}
root@truenas[/]# glabel status
Name                                       Status Components
gptid/4e377340-917d-11ea-a640-b42e99bf5e8f N/A    ada1p2
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f N/A    ada2p2
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f N/A    ada3p2
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f N/A    ada4p2
```

I was able to decrypted all partitions again (but the one being replaced):

```shell-session
root@truenas[/]# geli attach -p -k /tmp/pool_big_recovery.key /dev/gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli attach -p -k /tmp/pool_big_recovery.key /dev/gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli attach -p -k /tmp/pool_big_recovery.key /dev/gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
root@truenas[/]# geli status
Name                                           Status Components
gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f
gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f
gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli ACTIVE gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f
```

And get back my pool in the state I left it:

```shell-session
root@truenas[/]# zpool import big
root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: Some supported features are not enabled on the pool. The pool can
		still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
		the pool may no longer be accessible by software that does not support
		the features. See zpool-features(5) for details.
  scan: resilvered 15.5M in 05:42:26 with 0 errors on Fri Dec 11 06:01:11 2020
config:

		NAME                                           		  STATE     READ WRITE CKSUM
		big                                            		  DEGRADED     0     0     0
		  raidz2-0                                            DEGRADED     0     0     0
		    replacing-0                                       OFFLINE      0     0     0     all children offline
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli  OFFLINE      0     0     0
			  gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      OFFLINE      0     0     0
	  	    gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
		    gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0
		    gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli    ONLINE       0     0     0

errors: No known data errors
```

This time, I finally fixed the failed `replacing-0` operation by detaching the old encrypted partition, and resilvering the new, unencrypted one:

```{.shell-session hl_lines="17 40"}
root@truenas[/]# zpool detach big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f.eli

root@truenas[/]# zpool status big
  pool: big
 state: DEGRADED
status: One or more devices has been taken offline by the administrator.
		Sufficient replicas exist for the pool to continue functioning in a
		degraded state.
action: Online the device using 'zpool online' or replace the device with
		'zpool replace'.
  scan: resilvered 15.5M in 05:42:26 with 0 errors on Fri Dec 11 06:01:11 2020
config:

		NAME                                           		STATE     READ WRITE CKSUM
		big                                            		DEGRADED 	 0     0     0
		  raidz2-0                                          DEGRADED 	 0     0     0
		    gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      OFFLINE  	 0     0     0
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE   	 0     0     0

errors: No known data errors

root@truenas[/]# zpool online big gptid/4e377340-917d-11ea-a640-b42e99bf5e8f

root@truenas[/]# zpool status big
  pool: big
 state: ONLINE
status: One or more devices is currently being resilvered. The pool will
		continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Fri Dec 11 09:53:51 2020
		4.46T scanned at 623M/s, 2.78T issued at 388M/s, 12.3T total
		690G resilvered, 22.63% done, 07:07:37 to go
config:

		NAME                                           		STATE   READ WRITE CKSUM
		big                                            		ONLINE     0     0     0
		  raidz2-0                                          ONLINE 	   0     0     0
			gptid/4e377340-917d-11ea-a640-b42e99bf5e8f      ONLINE     0     0     0     (resilvering)
			gptid/4ea9ae2e-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE     0     0     0
			gptid/4eb3e8fc-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE     0     0     0
			gptid/4ece25f4-917d-11ea-a640-b42e99bf5e8f.eli  ONLINE     0     0     0

errors: No known data errors
```

And off we went, spending another 7 hours of resilvering, but back on track in the migration process.

All in all, RAID-Z2 saved my ass here. Lesson learned: **a disk failure during heavy-duty operations is [no longer a statistically rare event](/2020/05/nas-hardware/#raid-array)**.

So remember the wise man who once said to **BACKUP YOUR F#@\$% POOL**!

## Bad hardware

As I considered the issue above solved, it resurrected on other devices, with variations of the same logs as above. All these errors randomly kicked HDDs out of the array. It was a nightmare.

At that point everything broke loose and couldn't find any solid explanation. I could only qualify the situation as general hardware issues.

Of all possible root causes, I listed these:

- **Power-supply overcapacity**: impossible.

  PSU was 450W and each HDD is operating at 7.72W of typical consumption.

- **Bad motherboard firmware**: unlikely.

  Motherboard has been upgraded from the latest version from day 1.

- Bad HDD firmwares

- Bad cables

- Cooling issue

- Bad HDD series

- **Shitty controller**: most likely possibility.

  I only encountered this behaviour while rebuilding the array. So under load the disk controllers on the motherboard might have just given up. All disks are managed by the [Intel C246 chipset](https://ark.intel.com/content/www/us/en/ark/products/147326/intel-c246-chipset.html).

  A solution to explore would be to [reduce SATA speed in FreeBSD kernel](https://forums.freebsd.org/threads/ata-4-timeouts-continue-after-disk-replacement-on-new-12-0-installation-issues-with-nvidia-mcp51.69770/).

## Epilog

After these serial failures, I realized I had no time to debug this whole affair, so I ended purchasing an official TrueNAS Mini X+ (8x cores 2.2GHz CPU, 32GB ECC DDR4 RAM, 2x 10G Base-T ports) from iXsystems.

It cost me the same price as [my custom setup](/2020/05/nas-hardware/#final-configuration), minus the tariff and import taxes. But comes with a 1 year warranty and support, and the peace of mind that the hardware is fully compatible with TrueNAS and thoroughly qualified for a NAS load.

And 2 years later, my TrueNAS Mini X+ is working fine without an issue. I should have bought it from the start.
