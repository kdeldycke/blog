---
date: '2019-12-18'
title: Unlocking, Rooting and Custom Recovery for Sony Xperia E3
category: English
tags: Android, Smartphone, Sony, ROM, bootloader, brew, fastboot, adb, macOS, firmware
---

Got hold of a second-hand [Sony Xperia E3](https://en.wikipedia.org/wiki/Sony_Xperia_E3) a couple of weeks ago and was surprised by its general build quality and IPS screen for a 2014 phone.

Of course it was loaded with crapware and bloatware both from the ISP and manufacturer. Time to get my hands dirty back in the Android ecosystem, and try to clean that up.

This process started with the following devices:

- Sony Xperia E3 with stock firmware and OS:
  - Model number: `D2203` (LTE variant)
  - Android version: `4.4.2` (KitKat)
  - Baseband version: `8926-DAAAANAZQ-00282-04` (Europe, France, Orange)
  - Kernel version: `3.4.0`
  - Build number: `18.4.C.1.29`
- MacBook Air (macOS 10.14 Mojave)

## Factory Reset

First things first, let's clean up that phone using the standard functions:

1. Connect to local wifi.

2. Update phone's stock firmware, OS and apps using Sony's *Update Center*.

3. Format the attached SD card if any to destroy previous user's personal data.

4. Factory reset the phone.

## Unlock Bootloader

Phone was locked, tied to an Orange contract. Sony is providing everything online to properly unlock the phone, and the warranty has been expired for a long time. So let's proceed!

1. Enter service mode by dialing `*#*#7378423#*#*` on the phone.

2. Go to `Service info` > `Configuration` > `Rooting Status`.

3. There, the presence of the `Bootloader unlock allowed: Yes` status confirm the phone is currently locked, but allowed to be unlocked.

4. Dial `*#06#` on the phone to get its IMEI unique ID. Note that number somewhere.

5. Go to [Sony developer website to obtain an unlock code](https://developer.sony.com/develop/open-devices/get-started/unlock-bootloader).

6. Follow the procedure on that site, and enter your phone's IMEI to get an unlock key. Write it down.

There are several ways to feed that key to the phone. Here is how I did it under macOS:

01. We need to activate the developer mode. On the phone, go to phone's `Settings` app > `About phone`. At the bottom, click 7 times on the `Build number` line. Developer mode has been unlocked once you get the `You are now a developer` notification.

02. Then you can enable it for good in the `Settings` > `System` > `Developer options` menu. There, check the `Developer option` toggle button is set to `ON`.

03. We're now going to [activate USB access with CLI tools](https://www.kingoapp.com/root-tutorials/how-to-enable-usb-debugging-mode-on-android.htm). Scroll down in the menu to find the `Debugging` item, and enable the `USB debugging` option.

04. On a macOS terminal, [install Homebrew](https://docs.brew.sh/Installation):

    ```shell-session
    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```

05. Now install Android tools with Homebrew from the terminal:

    ```shell-session
    $ brew install android-platform-tools
    ```

06. Plug the phone to your computer with a micro USB cable.

07. Check your device is recognized by `adb`:

    ```shell-session
    $ adb devices
    List of devices attached
    BL4828DXXXXX	device
    ```

08. Reboot device in bootloader mode:

    ```shell-session
    $ adb reboot bootloader
    ```

09. Unlock the device with the unlock key previously fetched from Sony:

    ```shell-session
    $ fastboot oem unlock 0x0828XXXXXXXXXXXX
    ```

10. Reboot the device in standard mode:

    ```shell-session
    $ fastboot reboot
    ```

11. Go back to service mode (dial `*#*#7378423#*#*`; go to `Service info` > `Configuration` > `Rooting Status`) and confirm the `Bootloader unlock : Yes` status. If so, your phone is now unlocked!

All the steps above have been performed with the stock ecosystem: firmware, ROM and OS are all standard. Now we'll delves into the dark side.

## Root Phone

We'll now root the phone.

1. Get a microSD card and insert it in the phone.

2. Format the external SD card from the phone. Unmount it, then physically remove it from the phone.

3. Plug that card to your computer.

4. Download [King Root](https://kingroot.net) for Android (v5.3.7 in my case). Copy the `.apk` file to the SD card.

5. Unmount and remove the card from the computer. Insert it back into the phone, and mount it.

6. In `Settings` > `Security` menu, allow applications to be installed from unknown sources.

7. Connect to wifi, go to Google Play store and install a file browser. My personal favorite: [Amaze File Manager](https://play.google.com/store/apps/details?id=com.amaze.filemanager).

8. Use the file manager to browse into the SD card, [find the APK, install it and run KingRoot](https://kingroot.net/tutorials).

## Flash Custom Recovery

The custom ROM I'll provide here only targets Sony Xperia E3 D2203 LTE model with the stock 4.4.2 Android.

Before proceeding any further, please double check your device is the right one, with the expected versions. If not you're at risk of bricking your device for good.

1. It was hard to find an appropriate ROM so [here is a copy of the `boot_D2203_4.4.2.img` file]({attach}boot_D2203_4.4.2.img). I originally found it on an article on [*How to Install Custom Recovery on Sony Xperia E3*](https://consumingtech.com/how-to-install-a-custom-recovery-on-the-sony-xperia-e3/), and the [image itself is hosted on MediaFire](http://www.mediafire.com/file/627epe7817tolaf/boot_D2203_4.4.2.img/file).

   It is a CMW-based Recovery v6.0.4.7 uniquely built for the D2203 LTE model.

   Download it and compare its checksum:

   ```shell-session
   $ wget -P ~/Downloads/ http://download1582.mediafire.com/d8vmcjzc4xfg/627epe7817tolaf/boot_D2203_4.4.2.img
   (...)

   $ sha1sum ~/Downloads/boot_D2203_4.4.2.img
   7fdf48efa91167ee20282b6595e11fe5afef72f2  boot_D2203_4.4.2.img
   ```

2. Make sure the phone is plugged into your computer, and reboot the device in bootloader mode:

   ```shell-session
   $ adb devices
   List of devices attached
   BL4828DXXXXX	device
   $ adb reboot bootloader
   ```

3. Flash the custom ROM:

   ```shell-session
   $ fastboot flash boot ~/Downloads/boot_D2203_4.4.2.img
   ```

   Here you might stumble upon the following error:

   ```shell-session
   Writing 'recovery' FAILED (remote: 'partition table doesn't exist')
   ```

   If that the case it's because you tried to flash the ROM into the recovery partition (as generally advised in most tutorials out there), with a command similar to:

   ```shell-session
   $ fastboot flash recovery boot.img
   ```

   This doesn't cut it: as [*foxite* explained in 2016](https://forum.xda-developers.com/showpost.php?s=875aad126d132fea99ba9cee073c67ed&p=68056829&postcount=3), the custom ROM provided here targets the boot partition.

4. Reboot the device:

   ```shell-session
   $ fastboot reboot
   ```

   The boot process should be eventless, as if nothing happened.

5. Now if you reboot your device once more, you'll notice a slight difference.

   When the Sony Xperia logo show up, at the very start of the boot process, the front notification LED gets turned on in pink for a couple of seconds while the phone briefly vibrate.

   And right at that time you press alternatively the ++up++ and ++down++ volume buttons a couple of times, while the LED last, you'll boot into the custom recovery ROM you just flashed:

   ![Yellow-cased Sony Xperia booted into CWM-based Recovery 6.0.4.7, its menu offering reboot, install zip, wipe, backup and mount options](sony-xperia-e3-d2203-lte-cmw-recovery.jpg)

## Custom OS

In this section we will install a new OS to refresh the dated one.

I choose a tweaked yet stable distribution based on the stock Android 4.4.4 and 18.5.C.0.19 firmware. The main reason being that more experimental ports of Android 5.0 exists but often lacks support for the camera.

01. Download the so called [*De-bloated, Tweaked, Pre-Rooted, ROM for the Sony Xperia E3* from XDA forums](https://forum.xda-developers.com/xperia-e3/development/rom-t3067374). The original ROM being long gone, a [copy is available online](http://www.mediafire.com/download/2lt57jv2w5k8lyu/Version_1_RegisUpload.zip) (SHA1 checksum: `d2e949d15aea97c64414ae2ef493f7b18e32dd78`).

02. Unzip that file. You should end up with that structure:

    ```shell-session
    [  96]  clockworkmod
    └── [ 128]  backup
        └── [ 352]  Version_1
            ├── [ 20M]  boot.img
            ├── [   0]  cache.ext4.tar
            ├── [1.1M]  cache.ext4.tar.a
            ├── [   0]  data.ext4.tar
            ├── [2.5K]  data.ext4.tar.a
            ├── [ 343]  nandroid.md5
            ├── [232K]  recovery.log
            ├── [   0]  system.ext4.tar
            └── [871M]  system.ext4.tar.a
    ```

03. Copy the `clockworkmod` folder and its content at the root of the SD card. Unmount the card and place it into the phone.

04. Reboot the phone and enter the recovery ROM.

05. Go to `wipe data/factory reset` > `Yes - Wipe all user data` to clean up cache.

06. Repeat same thing but this time go to `wipe cache partition` > `Yes - Wipe Cache`.

07. Again, go to `advanced` > `wipe dalvik cache` > `Yes - Wipe Dalvik Cache`.

08. Go back to the main recovery menu, then mount the SD card: `mounts and storage` > `mount /storage/sdcard1`.

09. Then go back, `backup and restore` > `restore from /storage/sdcard1` > `Version_1` (i.e. the name of the first subfolder from the ZIP file we downloaded above) > `Yes - Restore`.

10. Wait while the installation is performed. At the end you can reboot the device and you should have a brand new and clean phone:

    ![The phone's About screen confirming model D2203 on Android 4.4.4, running a custom kernel built in March 2015](sony-xperia-e3-d2203-android-444.jpg)

## Epilogue

I wrote this article along the way, as I was (re)discovering the whole Android development scene. Brings back memories. But I'm a little rusty which explain the somewhat convoluted process.

At the end, I realized there's no need to go through the extra hoops of rooting the phone and copying APKs on SD card when you can simply download and execute them from the phone's browser.

Another huge detour I took was the hunt for a custom CMW recovery image. I could have instead unzip the `Version_1_RegisUpload.zip` file and flash the `clockworkmod/backup/Version_1/boot.img` image right away, instead of `boot_D2203_4.4.2.img`. The benefit being a slightly newer version (6.0.5.1), the LED being turned on in white instead of pink, and an appropriate screen size:

![The same phone on the newer CWM-based Recovery 6.0.5.1, the reboot entry gone from the top of the menu](sony-xperia-e3-cmw-recovery-6051.jpg)
