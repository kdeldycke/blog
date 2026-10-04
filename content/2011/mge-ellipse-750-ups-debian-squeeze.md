---
date: '2011-05-31'
title: MGE Ellipse 750 UPS on Debian Squeeze
category: English
tags: Debian, Linux, nut, Server, Debian Squeeze, udev, UPS, USB, Regular expression
---

My home server is protected by an [MGE Ellipse 750 UPS](https://web.archive.org/web/20090226031303/http://www.mgeops.com/index.php/products__1/230v_products/ups/ellipse_asr) for years. I bought it for several reasons: it's affordable, has good capacity and is Ubuntu certified.

I also read back then [rumors](https://blog.mansonthomas.com/2008/10/setting-up-ups-link-with-ubuntu-server.html) implying that Nut's maintainer was employed by MGE. Having a hardware manufacturer employing a fellow open-source hacker has certainly influenced my purchase decision.

MGE is no more and has been [merged with EATON](https://web.archive.org/web/20111021213431/http://www.eaton.com/Eaton/OurCompany/NewsEvents/NewsReleases/CT_136576). But my UPS is still supported, and the release of Debian Squeeze is a good opportunity to consolidate my knowledge in the form of this tutorial.

So here is how I setup Nut on Debian Squeeze to monitor my UPS.

First things first, we have to install the main package and its USB driver:

```shell-session
$ aptitude install nut nut-usb
```

Now let's configure Nut and run it:

```shell-session
$ sed -i 's/MODE=none/MODE=standalone/g' /etc/nut/nut.conf
$ echo '
[MGE-Ellipse750]
driver = usbhid-ups
port = auto
desc = "MGE UPS Systems"
' >> /etc/nut/ups.conf
$ sed -i 's/# LISTEN 127\.0\.0\.1 3493/LISTEN 127\.0\.0\.1/g' /etc/nut/upsd.conf
$ echo '
[kevin]
password = badpassword
upsmon master
' >> /etc/nut/upsd.users
$ sed -i 's/# NOTIFYCMD \/usr\/local\/ups\/bin\/notifyme/NOTIFYCMD \/sbin\/upssched/g' /etc/nut/upsmon.conf
$ echo '
MONITOR MGE-Ellipse750@localhost 1 kevin badpassword master
NOTIFYFLAG ONBATT SYSLOG+WALL+EXEC
NOTIFYFLAG ONLINE SYSLOG+WALL+EXEC
' >> /etc/nut/upsmon.conf
$ sed -i 's/CMDSCRIPT \/upssched-cmd/CMDSCRIPT \/etc\/nut\/upssched-cmd/g' /etc/nut/upssched.conf
$ sed -i 's/# PIPEFN \/var\/run\/nut\/upssched\/upssched.pipe/PIPEFN \/var\/run\/nut\/upssched.pipe/g' /etc/nut/upssched.conf
$ sed -i 's/# LOCKFN \/var\/run\/nut\/upssched\/upssched.lock/LOCKFN \/var\/run\/nut\/upssched.lock/g' /etc/nut/upssched.conf
$ echo '
AT ONBATT * START-TIMER onbatt 30
AT ONLINE * CANCEL-TIMER onbatt
' >> /etc/nut/upssched.conf
$ echo '
#!/bin/sh
exit 0
' > /etc/nut/upssched-cmd
$ /etc/init.d/nut restart
```

As you can see you have lots of stuff to configure before Nut can do what it was designed for. But after all of these commands, you should have a working UPS.

You can now test that your system works by using the command below, which list statistics of a given UPS:

```shell-session
$ upsc MGE-Ellipse750@localhost
```

But in some rare cases, your UPS will not be recognized and you'll have like me the following messages in your `/var/log/syslog`:

```text
May  5 16:12:36 paris-server upsmon[10773]: Poll UPS [MGE-Ellipse750@127.0.0.1] failed - Driver not connected
```

In this case, you should run Nut's driver in debug mode:

```shell-session
$ /lib/nut/usbhid-ups -DDD -a MGE-Ellipse750
Network UPS Tools - Generic HID driver 0.34 (2.4.3)
USB communication driver 0.31
    0.000000     debug level is '3'
    0.013911     upsdrv_initups...
    0.189541     Checking device (0463/FFFF) (005/003)
    0.189705     - VendorID: 0463
    0.189741     - ProductID: ffff
    0.189767     - Manufacturer: unknown
    0.189794     - Product: unknown
    0.189819     - Serial Number: unknown
    0.189842     - Bus: 005
    0.189862     Trying to match device
    0.189906     Device matches
    0.189954     failed to claim USB device: could not claim interface 0: Operation not permitted
    0.189995     failed to detach kernel driver from USB device: could not detach kernel driver from interface 0: Operation not permitted
    0.190033     failed to claim USB device: could not claim interface 0: Operation not permitted
    0.190070     failed to detach kernel driver from USB device: could not detach kernel driver from interface 0: Operation not permitted
    0.190108     failed to claim USB device: could not claim interface 0: Operation not permitted
    0.190145     failed to detach kernel driver from USB device: could not detach kernel driver from interface 0: Operation not permitted
    0.190181     failed to claim USB device: could not claim interface 0: Operation not permitted
    0.190217     failed to detach kernel driver from USB device: could not detach kernel driver from interface 0: Operation not permitted
    0.190252     Can't claim USB device [0463:ffff]: could not detach kernel driver from interface 0: Operation not permitted
```

As you can see in messages above, Nut can't see my UPS. By chance, forcing nut to use the `root` user let it see my UPS:

```shell-session
$ /lib/nut/usbhid-ups -DDD -u root -a MGE-Ellipse750
Network UPS Tools - Generic HID driver 0.34 (2.4.3)
USB communication driver 0.31
    0.000000     debug level is '3'
    0.001678     upsdrv_initups...
    0.172877     Checking device (0463/FFFF) (005/003)
    1.112408     - VendorID: 0463
    1.112464     - ProductID: ffff
    1.112489     - Manufacturer: MGE OPS SYSTEMS
    1.112516     - Product: ELLIPSE
    1.112542     - Serial Number: BDCJ3800Q
    1.112569     - Bus: 005
    1.112595     Trying to match device
    1.112647     Device matches
    1.112726     failed to claim USB device: could not claim interface 0: Device or resource busy
    1.113239     detached kernel driver from USB device...
    1.251394     HID descriptor, method 1: (9 bytes) => 09 21 00 01 21 01 22 01 03
    1.251460     HID descriptor, method 2: (9 bytes) => 09 21 00 01 21 01 22 01 03
    1.251491     HID descriptor length 769
    1.351379     Report Descriptor size = 769
    1.351456     Report Descriptor: (769 bytes) => 05 84 09 04 a1 01 09 24 a1 00 09 02 a1 00
    1.351509      55 00 65 00 85 01 75 01 95 05 15 00 25 01 05 85 09 d0 09 44 09 45 09 42 0b
(...)
```

So the issue is now clear and is related to permissions. I was able to fix this issue by changing the permissions on the USB device corresponding to my UPS:

```shell-session
$ chmod 0666 /dev/bus/usb/005/003
```

Another working way to fix this is to change the group of the device to `nut`:

```shell-session
$ chown :nut /dev/bus/usb/005/003
```

BTW, to get the bus number (`005` here) and device number (`003` in my case) of your UPS, run `lsudb`:

```shell-session
$ lsusb
Bus 005 Device 003: ID 0463:ffff MGE UPS Systems UPS
Bus 005 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 004 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 003 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 002 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Of course this fix is absolutely temporary, as you'll need to perform the change above after every reboot. This is far from practical. In fact, as describe in this [Fedora 10 bug report](https://bugzilla.redhat.com/show_bug.cgi?id=488368), but also in [some](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=529664) [other](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=334105) Debian [bug report](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=325878), this issue is directly tied to conflicting Udev rules.

Based on clues from these bug reports you can fix Udev using different strategies. As I can't decide which one is the cleanest, I just did something that is quite brutal, but works. It consist of replacing in `/lib/udev/rules.d/91-permissions.rules` the line setting rights for USBfs-like devices:

```diff
--- /lib/udev/rules.d/91-permissions.rules-orig 2011-05-05 18:49:08.015538434 +0200
+++ /lib/udev/rules.d/91-permissions.rules      2011-05-05 18:49:16.663537978 +0200
@@ -33,7 +33,7 @@

 # usbfs-like devices
 SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", \
-                               MODE="0664"
+                               MODE="0666"

 # serial devices
 SUBSYSTEM=="tty",
```

Now all you have to do is to unplug the power cord and wait until your machine gracefully shut down as soon as batteries are low! :)
