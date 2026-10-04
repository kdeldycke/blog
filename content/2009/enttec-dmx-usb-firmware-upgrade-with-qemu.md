---
date: '2009-05-14'
title: Enttec DMX-USB firmware upgrade with Qemu
category: English
tags: DMX, enttec, firmware, Hardware, Linux, Qemu, Stage lighting, USB
---

A year ago, I brought a
[Enttec Pro USB/DMX widget](https://web.archive.org/web/20081121003007/http://www.enttec.com/dmxusb.php). Since then, a new
firmware was released. If it doesn't fix any critical bug to me, I still _have
to_ upgrade it (don't mind asking why... ;) ). And to make things fun (read
"dangerous"), I choose to do it with Qemu.

This article explains how I upgraded the firmware of my Enttec DMX/USB widget
under linux thanks to Qemu.

First, plug your device in one of your computer's USB port. We need to get the
hardware UID of the widget. We can do so as root in a linux terminal:

```shell-session
$ cat /proc/bus/usb/devices
```

This command output a big mess in which you should find a block of lines
separated by two blank lines (one above and one below) corresponding to your USB
device. It's easy to spot, as it contain the `ENTTEC` string. Mine look like
this:

```text
T:  Bus=02 Lev=01 Prnt=01 Port=00 Cnt=01 Dev#=  2 Spd=12  MxCh= 0
D:  Ver= 2.00 Cls=00(>ifc ) Sub=00 Prot=00 MxPS= 8 #Cfgs=  1
P:  Vendor=0403 ProdID=6001 Rev= 6.00
S:  Manufacturer=ENTTEC
S:  Product=DMX USB PRO
S:  SerialNumber=ENQXXXXX
C:* #Ifs= 1 Cfg#= 1 Atr=a0 MxPwr=300mA
I:* If#= 0 Alt= 0 #EPs= 2 Cls=ff(vend.) Sub=ff Prot=ff Driver=ftdi_sio
E:  Ad=81(I) Atr=02(Bulk) MxPS=  64 Ivl=0ms
E:  Ad=02(O) Atr=02(Bulk) MxPS=  64 Ivl=0ms
```

What we are looking for is the vendor's ID and the product's ID, that's all Qemu
needs to talk to the device. This is found on the line starting with `P:`.
For me:

- Vendor ID: `0403`
- Products ID: `6001`

With this information, we can launch Qemu and bind it to the device. Assuming
you already have a Qemu image containing a working version of windows XP, the
command looks like this:

```shell-session
$ qemu -m 512 -usb -usbdevice host:0403:6001 -hda ./qemu-win-xp-with-freestyler.qcow
```

Alternatively, you can "hotplug" the USB device once inside Qemu. This can be
done by calling the
[Qemu interactive shell](https://web.archive.org/web/20090519075718/http://www.nongnu.org/qemu/qemu-doc.html#SEC11) by
pressing ++ctrl+alt+2++ simultaneously. Then, to hotplug the USB device, type:

```shell-session
$ usb_add host:0403:6001
```

If you're as unlucky as I am, you'll get this error message:

```text
Could not add USB device 'host:0403:6001'
```

Which is doubled by the following message from your legacy console:

```text
/proc/bus/usb/002/002: Permission denied
```

The latter point to the restrictive access rights on our device, which can be
fixed by:

```shell-session
$ chmod -R a+rw /proc/bus/usb/002/002
```

![qemu-usb-console](qemu-usb-console.png)

Instead, if you get the following error message:

```text
usb_host: device already grabbed
```

It probably mean that your linux kernel has already identified the device when
you plugged in and has loaded some drivers. To unload them and free the device,
I had to do:

```shell-session
$ lsmod
$ rmmod dmx_usb
$ rmmod ftdi_sio
```

At last, you can check under the emulated Windows that your Enttec widget is
recognized by windows:

![enttec-usb-dmx-widget-on-windows-xp-through-qemu](enttec-usb-dmx-widget-on-windows-xp-through-qemu.png)

And finally you're free to upgrade (at your own risks) your widget's firmware
with the tools available on Enttec's official website:

![enttec-dmx-usb-widget-firmware-upgrade-on-windows-xp-through-qemu](enttec-dmx-usb-widget-firmware-upgrade-on-windows-xp-through-qemu.png)

FYI, all these operations where performed on a Mandriva 2008.1, Qemu 0.9.0 and
linux kernel 2.6.24.
