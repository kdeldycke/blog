---
date: '2008-03-07'
title: HP w2207h external display on Intel 945
category: English
tags: chipset, display, graphic, Hewlett Packard, Intel, laptop, Linux, Samsung, screen, X.org
---

I recently had the opportunity to plug the HP w2207h screen (see [review #1](https://www.anandtech.com/displays/showdoc.aspx?i=3054) and [review #2](https://www.prad.de/en/monitore/review/2007/review-hp-w2207.html)) as an external display to my [Samsung Q35 laptop]({filename}/2006/samsung-q35-xic-5500-tiny-review-of-a-strong-compact-laptop.md). The external display has a native resolution of 1680x1050 and the laptop's is 1280x800.

The laptop is powered by an [Intel 945 graphic chip](https://en.wikipedia.org/wiki/Intel_GMA#GMA_950):

```shell-session
$ lspci
00:00.0 Host bridge: Intel Corporation Mobile 945GM/PM/GMS, 943/940GML and 945GT Express Memory Controller Hub (rev 03)
00:02.0 VGA compatible controller: Intel Corporation Mobile 945GM/GMS, 943/940GML Express Integrated Graphics Controller (rev 03)
00:02.1 Display controller: Intel Corporation Mobile 945GM/GMS/GME, 943/940GML Express Integrated Graphics Controller (rev 03)
(...)
```

After some googling (`https://slforums.typo3-factory.net/lofiversion/index.php/t63508.html`) and tests, I've designed the perfect `xorg.conf` for this configuration:

```text
# **********************************************************************
# Refer to the xorg.conf man page for details about the format of
# this file.
# **********************************************************************

Section "Extensions"
  Option "Composite"
EndSection

Section "ServerFlags"
  AllowMouseOpenFail # allows the server to start up even if the mouse does not work
EndSection

Section "Module"
  Load "dbe" # Double-Buffering Extension
  Load "v4l" # Video for Linux
  Load "extmod"
  Load "type1"
  Load "freetype"
  Load "glx" # 3D layer
  Load "dri" # direct rendering
EndSection

Section "InputDevice"
  Identifier "Keyboard1"
  Driver "kbd"
  Option "XkbModel" "pc105"
  Option "XkbLayout" "fr"
  Option "XkbOptions" "compose:rwin"
EndSection

Section "InputDevice"
  Identifier "Mouse1"
  Driver "mouse"
  Option "Protocol" "ExplorerPS/2"
  Option "Device" "/dev/mouse"
EndSection

Section "InputDevice"
  Identifier "SynapticsMouse1"
  Driver "synaptics"
  Option "SHMConfig" "on"
EndSection

Section "Monitor"
  Identifier "laptop"
  Option "PreferredMode" "1280x800"
  Option "Below" "external"
EndSection

Section "Monitor"
  Identifier "external"
  Option "PreferredMode" "1680x1050@60"
  HorizSync 24.0 - 82.0
  VertRefresh 48.0 - 76.0
  Modeline "1680x1050@60" 147.14 1680 1784 1968 2256 1050 1051 1054 1087 -HSync +Vsync
EndSection

Section "Device"
  Identifier "device1"
  VendorName "Intel Corporation"
  BoardName "Intel 810 and later"
  Driver "intel"
  Option "DPMS"
  # Option "XaaNoOffscreenPixmaps" "1"
  Option "monitor-LVDS" "laptop"
  Option "monitor-VGA" "external"
EndSection

Section "Screen"
  Identifier "screen1"
  Device "device1"
  Monitor "external"
  Subsection "Display"
    Virtual 1680 1850
  EndSubsection
EndSection

Section "ServerLayout"
  Identifier "layout1"
  InputDevice "Keyboard1" "CoreKeyboard"
  InputDevice "Mouse1" "CorePointer"
  InputDevice "SynapticsMouse1" "AlwaysCore"
  Screen "screen1"
EndSection
```

What I've learned so far during these experiments:

- With DRI, [virtual screen can't be greater than 2048x2048](https://www.thinkwiki.org/wiki/Xorg_RandR_1.2#the_Virtual_screen) for Intel 945 (or less) chips. This explain why my screens are one above the other instead of side-by-side.

- [XRandR](https://www.x.org/wiki/Projects/XRandR) and its friend [KRandRTray](https://web.archive.org/web/20080516102259/http://www.novell.com/coolsolutions/trench/16034.html) make screen positioning user-friendly...

- ...until you play with the `xrandr`'s "`--off`" option! After I manually called it, this parameter disabled all my screens, forever, and at each boot. I've randomly deleted xorg-related files, but I still didn't know how I solved this mess. If you have a better understanding of how `xrandr` store its configuration, please let me know!

- Dual screening is awesome! :D
