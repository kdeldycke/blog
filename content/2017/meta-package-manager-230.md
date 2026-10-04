---
date: '2017-01-18'
title: Meta Package Manager v2.3.0
tags: GitHub, Python, Apple, macOS, Linux, Windows, BitBar, Homebrew, Cask, node.js, atom, apm, npm, ruby, gem, pipi, Meta Package Manager
---

Last time I [mentioned
]({filename}/2016/bitbar-package-manager-v13.md) my *Package
Manager Plugin*, it was a simple [standalone Python script for BitBar
](https://web.archive.org/web/20170221024438/https://getbitbar.com/plugins/Dev/MetaPackageManager/meta_package_manager.7h.py).

The BitBar plugin is [still actively maintained
](https://mpm.run/bar-plugin/), but all
its core functionalities are now provided by an independent Python module:
[Meta Package Manager](https://pypi.python.org/pypi/meta-package-manager). The
latest version, [2.3.0, has recently been released
](https://github.com/kdeldycke/meta-package-manager/blob/v2.3.0/CHANGES.rst#230-2017-12-15).

This Python module also install a new CLI called `mpm`, which aims to provide a
unified interface to all package managers, on all 3 major platforms (macOS,
Linux and Windows).

This is both ambitious and silly.

Ambitious because there is [too many package managers
](https://en.wikipedia.org/wiki/List_of_software_package_management_systems)
out there, all with their own idiosyncrasies. So much that I had to compile a
list of [Falsehoods Programmers Believe About Package Managers
](https://mpm.run/falsehoods/).

And silly because, well, `mpm` actually [tries to implement
](https://github.com/kdeldycke/meta-package-manager/issues/10) an XKCD joke:

![XKCD #1654](https://imgs.xkcd.com/comics/universal_install_script.png)

Of course another classic XKCDs might apply to this endeavor:
[*Standards*](https://xkcd.com/927/).

So while I wait for someone to write a meta-meta-package-manager, the [project
is open to contributions on
GitHub](https://github.com/kdeldycke/meta-package-manager).
