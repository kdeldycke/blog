---
date: '2007-01-02'
title: 'Mandriva 2007.0 Screenshots: 3D Desktop'
category: English
tags: 3D, Celestia, Compiz, desktop, GPU, Intel, laptop, lspci, Mandriva, Samsung, X.org
---

For some months, [I own a Samsung Q35 laptop]({filename}/2006/samsung-q35-xic-5500-tiny-review-of-a-strong-compact-laptop.md) which is powered by a Mandriva 2007.0.

As describe in its technical specification this machine include an [Intel GMA 950 GPU](https://en.wikipedia.org/wiki/Intel_GMA#GMA_950). `lspci` give us more details:

```text
00:00.0 Host bridge: Intel Corporation Mobile 945GM/PM/GMS, 943/940GML and 945GT Express Memory Controller Hub (rev 03)
00:02.0 VGA compatible controller: Intel Corporation Mobile 945GM/GMS, 943/940GML Express Integrated Graphics Controller (rev 03)
00:02.1 Display controller: Intel Corporation Mobile 945GM/GMS, 943/940GML Express Integrated Graphics Controller (rev 03)
```

This chipset is recognized out of the box by `drakconf` and thanks to this GUI, I was able to setup X.org with [AIGLX](https://en.wikipedia.org/wiki/AIGLX) in no more than 2 clicks!

![Mandriva 2007.0 : Drakconf, a GUI to setup 3D Desktop](mandriva-20070-drakconf-3d-desktop-control-panel.png)

Here are some screenshots of the resulting 3D desktop:

![glxgear-pseudo-benchmark.jpg](glxgear-pseudo-benchmark.jpg)

![mandriva-20070-3d-desktop-video-and-transparency.jpg](mandriva-20070-3d-desktop-video-and-transparency.jpg)

![mandriva-20070-3d-desktop-video-and-window-flicker.jpg](mandriva-20070-3d-desktop-video-and-window-flicker.jpg)

![mandriva-20070-3d-desktop-video-expose-like-panel.jpg](mandriva-20070-3d-desktop-video-expose-like-panel.jpg)

![mandriva-20070-3d-desktop-video-and-desktop-chooser.jpg](mandriva-20070-3d-desktop-video-and-desktop-chooser.jpg)

![mandriva-20070-3d-desktop-video-and-desktop-cube.jpg](mandriva-20070-3d-desktop-video-and-desktop-cube.jpg)

![opengl-software-and-3d-desktop.jpg](opengl-software-and-3d-desktop.jpg)

![opengl-software-and-3d-desktop-flicker-bug.jpg](opengl-software-and-3d-desktop-flicker-bug.jpg)

As you can see there is still some bugs but I had to test many software to find one which had problems with the 3D desktop. Except [Celestia](https://celestiaproject.space/), everything was working as usual. Beside this, I just had to redefine some shortcuts in [Compiz](https://web.archive.org/web/20061112131958/http://www.compiz.org/) (to match the default KDE shortcuts) and I was feeling at home! :)
