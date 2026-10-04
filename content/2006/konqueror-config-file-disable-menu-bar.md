---
date: '2006-08-31'
title: 'Konqueror config file: disable menu bar'
category: English
tags: KDE, kmail, konqueror, Linux
---

To disable the menu bar in [konqueror](https://www.konqueror.org), you have a specific action in menus. If you want to do this by hand, just add the following directive in your `~/.kde/share/config/konquerorrc` file:

```ini
[KonqMainWindow]
MenuBar=Disabled
```

This tip is interesting because you can also apply it for any KDE application that doesn't support this feature.

For example, in [kmail](https://web.archive.org/web/20060901050821/http://kmail.kde.org/), you can add the "`MenuBar=Disabled`" statement in "`[Main Window]`" section: this will have the same effect as in konqueror.
