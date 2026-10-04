---
date: '2009-08-25'
title: eAccelerator for PHP5 on Debian Lenny
category: English
tags: Apache, aptitude, Debian, eAccelerator, Debian Lenny, PHP, Server
---

[eAccelerator](https://github.com/eaccelerator/eaccelerator) is an _open-source PHP accelerator,
optimizer, and dynamic content cache_ (to quote the official website of the
project). It can effectively speed-up PHP processing on a server by caching
bytecode.

As Wikipedia tells you,
[several tools of this kind exists](https://wikipedia.org/wiki/List_of_PHP_accelerators).
Why choosing eAccelerator in particular? I really have no clue... I've never
used any of these tools, so I had to start somewhere. That's as simple as that!

Now, I have a Debian server as a target system. Unfortunately, eAccelerator is
not bundled in Lenny. Browsing the web, I found some personal repositories of
people kindly sharing their deb packages, like
[Andrew McMillan](https://andrew.mcmillan.net.nz/node/70) and
[schnuckelig.eu](https://web.archive.org/web/20090908034250/http://www.schnuckelig.eu/blog/debian-lenny-eaccelerator-packages-amd64-20090527).
The former provides a version of eAccelerator for the `i386`, the latter for the
`amd64` architecture. In this how-to, I've combined the 2 repositories to give
both 32 bits and 64 bits users a chance to use eAccelerator on Lenny.

Let's start the installation! First, add the following lines to your
`/etc/apt/sources.list` file:

```sourceslist
deb https://debian.mcmillan.net.nz/debian lenny awm
deb-src https://debian.mcmillan.net.nz/debian lenny awm
deb https://debian.schnuckelig.eu/ lenny main contrib non-free
```

To kill annoying warning messages, register the cryptographic fingerprint of
each repository:

```shell-session
$ gpg --keyserver keyring.debian.org --recv-keys 0x8f068012;
$ gpg --export --armor 0x8f068012 | apt-key add -
$ wget -O - https://debian.schnuckelig.eu/repository-key.gpg | apt-key add -
```

Then, update your package database:

```shell-session
$ aptitude update
```

And finally, you can install eAccelerator for PHP5 without any pain:

```shell-session
$ apt-get install php5-eaccelerator
```

Happy [fine-tuning](https://github.com/eaccelerator/eaccelerator)!
