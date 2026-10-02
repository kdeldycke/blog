---
date: '2012-11-27'
title: Linux GoPro HD Hero2 Firmware Upgrade
category: English
tags: camera, firmware, gopro, Linux, Ubuntu, upgrade, Video, wget, macOS
---

The GoPro HD Hero2 I just got was bundled with the `HD2.08.12.70` firmware:

```shell-session
$ cat /media/9016-4EF8/MISC/version.txt
{
"info version":"1.0",
"firmware version":"HD2.08.12.70",
"camera type":"HD2",
}
```

Since then a [new firmware was released
](https://gopro.com/support/hd-hero2-firmware-update/) (called the ["ProTune
feature" update](https://gopro.com/software-app/cineform-studio/)) which adds
higher video bitrate (35Mbps), a neutral color profile and 24 fps recording.
But GoPro only provides installer for Windows and Mac OS X. Here is how I
managed to upgrade the firmware under Ubuntu 12.04.

First, download the binary firmware:

```shell-session
$ wget https://software.gopro.com/Firmware/HD2/HD2-firmware.bin
$ sha256sum ./HD2-firmware.bin
3403348b39796ff1d775d759e6243d541b4d1db1c8c7992f5742bd258c7c5031  ./HD2-firmware.bin
```

Then copy the binary file to the root of your mounted GoPro:

```shell-session
$ cp ./HD2-firmware.bin /media/9016-4EF8/
```

Now unmount the GoPro, unplug it from your computer and make sure it's powered
off.

It's time to trigger the firmware upgrade:

1. Keep the shutter button on the top pressed while turning the camera on.

2. Release the shutter button.

3. Press and release the power button. The camera front will display "press
   1".

4. Again, press and release the power button. The camera will now display
   "press 2".

5. Then press and release the power button, again. The camera is now
   installing the `v70` upgrade, then turn itself off.

6. Power the camera on, to now upgrade to `v198`. The camera will turn itself
   off at the end.

You can now remove the `HD2-firmware.bin` file at the root of the camera, and
check the firmware version:

```shell-session
$ rm /media/9016-4EF8/HD2-firmware.bin
$ cat /media/9016-4EF8/MISC/version.txt
{
"info version":"1.0",
"firmware version":"HD2.08.12.198.WIFI.R47.00",
"camera type":"HD2",
}
```

Note that the configuration is lost and you have to set back the date and time
of the camera. As for the ProTune feature, it must be activated from a new item
in the configuration menu of the HD Hero2.
