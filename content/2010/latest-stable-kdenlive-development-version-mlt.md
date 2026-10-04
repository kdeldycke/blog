---
date: '2010-11-23'
title: Using latest stable Kdenlive with a development version of MLT
category: English
tags: apt-get, aptitude, dpkg, Git, Kdenlive, Kubuntu, Ubuntu, mlt, Video
---

Today I stumble upon a bug in the Kdenlive 0.7.8 running on my Kubuntu 10.10: the crop filter was messing with the display ratio of my video clips. Digging the web I [found a bug report](https://web.archive.org/web/20101206082837/http://kdenlive.org/mantis/view.php?id=1814) that was really close to my problem. According to the comments, this issue was fixed in the upcoming version of MLT. Is that bug the one I encountered? The only way to find out was to install the development version of MLT. Here is how I did it...

First, make sure to [use the latest stable Kdenlive stack](https://web.archive.org/web/20101205182044/http://kdenlive.org/download-kdenlive-0) for you system. For me, the [Sunab's alternative repository for Kubuntu 10.10](https://launchpad.net/~sunab/+archive/kdenlive-release/?field.series_filter=maverick) was the ultimate source:

```shell-session
$ sudo apt-get update && sudo apt-get install kdenlive
```

The idea is to keep the version of Kdenlive installed above, and replace the pre-packaged MLT on our system with a custom development version of our choice.

But first, we'll install all the libraries required to build MLT from sources:

```shell-session
$ sudo apt-get install libavdevice-dev libswscale-dev libvorbis-dev libsox-dev libsamplerate-dev frei0r-plugins-dev libdv-dev libavformat-dev libquicktime-dev libxml2-dev libsdl-dev libsdl-image1.2-dev
```

Let's now remove the installed MLT. If we use `apt-get` or KPackageKit, this will remove Kdenlive. So we'll use the following command to remove MLT while ignoring all the dependencies:

```shell-session
$ sudo dpkg --remove --force-depends libmlt2 libmlt++3 libmlt-data melt
```

At this point, and every time we try to use it, `apt` will complain of broken Kdenlive dependencies, and will try to remove it. This mean we can't upgrade other packages on the system.

To avoid this issue, I tried to freeze the state in which Kdenlive and MLT are, by setting the `hold` flag on `kdenlive`, `kdenlive-data`, `libmlt2`, `libmlt++3`, `libmlt-data` and `melt` packages. I tried with both `dpkg` and `aptitude`, but unfortunately it doesn't work as expected. So we'll continue our hack anyway...

Let's get MLT sources:

```shell-session
$ git clone git://mltframework.org/mlt.git
```

The command above will give you the latest development version. But if you target a particular revision (like [commit 21a3f68](https://github.com/mltframework/mlt/commit/21a3f68d56ce1237eb6510cdf03ebfc40b5641c2) in my case), you have to use this additional command:

```shell-session
$ git checkout 21a3f68
```

We can now follow the [procedure detailed in the Kdenlive manual](https://web.archive.org/web/20101205214035/http://kdenlive.org/user-manual/downloading-and-installing-kdenlive/installing-source/installing-mlt-rendering-engine):

```shell-session
$ cd mlt
$ ./configure --prefix=/usr --enable-gpl
$ make clean
$ make
$ sudo make install
```

That's it! Now you can launch Kdenlive, and if you run the wizard, you'll see that the MLT version on your system is the latest:

![Kdenlive's French MLT engine check listing version 0.5.11 as correct, with green ticks against the melt, avformat, DV, QImage and title modules](kdenlive-with-mlt-dev.png)

Oh, and by the way, it [fixed my problem with the crop filter](https://github.com/mltframework/mlt/commit/21a3f68d56ce1237eb6510cdf03ebfc40b5641c2)! :)

Finally, if you want to revert the mess we created on the system, you have to remove the MLT we built in place:

```shell-session
$ sudo rm -rf /usr/lib/libmlt*
$ sudo rm -rf /usr/lib/mlt*
$ sudo rm -rf /usr/lib/pkgconfig/mlt*
$ sudo rm -rf /usr/include/mlt*
$ sudo rm -rf /usr/share/mlt*
```

I came with the list above by searching my system with the following command:

```shell-session
$ sudo find / -path "/home" -prune -or -iname "*mlt*" -print -or -iname "*melt*" -print
```

Then, we can let `apt` handle Kdenlive and MLT properly and get back to the pre-packaged binaries:

```shell-session
$ sudo apt-get remove kdenlive && sudo apt-get update && sudo apt-get install kdenlive
```
