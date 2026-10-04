---
date: '2012-10-23'
title: Ultimate Gmail backup with Gmvault
category: English
tags: Backup, Gmail, gmvault, Linux, email, Pip, Python, Ubuntu, cron
---

For several weeks, I started a quest to find the best solution to locally backup a Gmail account.

I [tried `offline-imap`]({filename}/2012/backup-gmail-offlineimap.md), but it is bidirectional and can push back to your Gmail account local mistakes. Then I [played with `mbsync`]({filename}/2012/gmail-backup-mbsync.md), but it [doesn't support sub-folders/tags](https://www.mail-archive.com/isync-devel@lists.sourceforge.net/msg00220.html).

I finally found the Holy Grail in [Gmvault](https://web.archive.org/web/20120925124651/http://gmvault.org/), a recent open-source project especially designed for the task and all its subtleties.

To install it on Ubuntu, starts by getting [distribute](https://pypi.python.org/pypi/distribute), a Python dependency:

```shell-session
$ sudo pip install --upgrade distribute
Downloading/unpacking distribute
  Running setup.py egg_info for package distribute
Installing collected packages: distribute
  Found existing installation: distribute 0.6.24dev-r0
    Uninstalling distribute:
      Successfully uninstalled distribute
  Running setup.py install for distribute
    Before install bootstrap.
    Scanning installed packages
    Setuptools installation detected at /usr/lib/python2.7/dist-packages
    Non-egg installation
    Removing elements out of the way...
    Already patched.
    /usr/lib/python2.7/dist-packages/setuptools.egg-info already patched.
    Installing easy_install script to /usr/local/bin
    Installing easy_install-2.7 script to /usr/local/bin
    After install bootstrap.
    Don't have permissions to write /usr/local/lib/python2.7/dist-packages/setuptools-0.6c11-py2.7.egg-info, skipping
    Creating /usr/local/lib/python2.7/dist-packages/setuptools-0.6c11-py2.7.egg-info
    Creating /usr/local/lib/python2.7/dist-packages/setuptools.pth
Successfully installed distribute
Cleaning up...
```

Then install Gmvault itself:

```shell-session
$ sudo pip install gmvault
Downloading/unpacking gmvault
  Downloading gmvault-1.7-beta.tar.gz (73Kb): 73Kb downloaded
  Running setup.py egg_info for package gmvault
    PATH = /home/kevin/build/gmvault/./src/gmv/gmvault_utils.py
    1.7-beta
    Gmvault version = 1.7-beta
Downloading/unpacking argparse (from gmvault)
  Downloading argparse-1.2.1.tar.gz (69Kb): 69Kb downloaded
  Running setup.py egg_info for package argparse
    warning: no previously-included files matching '*.pyc' found anywhere in distribution
    warning: no previously-included files matching '*.pyo' found anywhere in distribution
    warning: no previously-included files matching '*.orig' found anywhere in distribution
    warning: no previously-included files matching '*.rej' found anywhere in distribution
    no previously-included directories found matching 'doc/_build'
    no previously-included directories found matching 'env24'
    no previously-included directories found matching 'env25'
    no previously-included directories found matching 'env26'
    no previously-included directories found matching 'env27'
Downloading/unpacking Logbook==0.3 (from gmvault)
  Downloading Logbook-0.3.tar.gz (89Kb): 89Kb downloaded
  Running setup.py egg_info for package Logbook
Downloading/unpacking IMAPClient==0.9 (from gmvault)
  Downloading IMAPClient-0.9.zip (119Kb): 119Kb downloaded
  Running setup.py egg_info for package IMAPClient
    no previously-included directories found matching 'doc/doctrees'
Downloading/unpacking gdata==2.0.17 (from gmvault)
  Downloading gdata-2.0.17.tar.gz (2.4Mb): 2.4Mb downloaded
  Running setup.py egg_info for package gdata
Installing collected packages: gmvault, argparse, Logbook, IMAPClient, gdata
  Running setup.py install for gmvault
    PATH = /home/kevin/build/gmvault/./src/gmv/gmvault_utils.py
    1.7-beta
    Gmvault version = 1.7-beta
    changing mode of build/scripts-2.7/gmvault from 644 to 755
    changing mode of /usr/local/bin/gmvault to 755
  Found existing installation: argparse 1.2.1
    Uninstalling argparse:
      Successfully uninstalled argparse
  Running setup.py install for argparse
    warning: no previously-included files matching '*.pyc' found anywhere in distribution
    warning: no previously-included files matching '*.pyo' found anywhere in distribution
    warning: no previously-included files matching '*.orig' found anywhere in distribution
    warning: no previously-included files matching '*.rej' found anywhere in distribution
    no previously-included directories found matching 'doc/_build'
    no previously-included directories found matching 'env24'
    no previously-included directories found matching 'env25'
    no previously-included directories found matching 'env26'
    no previously-included directories found matching 'env27'
  Running setup.py install for Logbook
    building 'logbook._speedups' extension
    gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.7 -c logbook/_speedups.c -o build/temp.linux-x86_64-2.7/logbook/_speedups.o
    logbook/_speedups.c:4:20: fatal error: Python.h: No such file or directory
    compilation terminated.
    ==========================================================================
    WARNING: The C extension could not be compiled, speedups are not enabled.
    Failure information, if any, is above.
    Retrying the build without the C extension now.
    ==========================================================================
    WARNING: The C extension could not be compiled, speedups are not enabled.
    Plain-Python installation succeeded.
    ==========================================================================
  Running setup.py install for IMAPClient
    no previously-included directories found matching 'doc/doctrees'
  Running setup.py install for gdata
Successfully installed gmvault argparse Logbook IMAPClient gdata
Cleaning up...
```

Now [for authentication, please read the documentation](https://web.archive.org/web/20121015184634/http://gmvault.org/in_depth.html#authentication). It's quite easy and straightforward.

Finally, to start the backup of your remote Gmail account, just launch:

```shell-session
$ gmvault sync me@example.com --resume
```

All you have to do next is to put the command above in a cron job to trigger a regular backup.
