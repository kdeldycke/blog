---
date: '2008-12-28'
title: dpkg, APT & Aptitude commands
category: English
tags: apt, aptitude, backport, CLI, Debian, dpkg, Linux, Ubuntu
---

## Search

- List all installed packages:

  ```shell-session
  $ dpkg -l
  ```

- List all recently installed packages:

  ```shell-session
  $ zcat -f /var/log/dpkg.log* | grep "\ install\ " | sort
  ```

- Show the changelog of a package (here, the linux kernel of Ubuntu):

  ```shell-session
  $ aptitude changelog linux-generic
  ```

- Which package contain a given file:

  ```shell-session
  $ apt-file search file_to_search
  ```

- Get the list of files of a package:

  ```shell-session
  $ apt-file list package_name
  ```

- Extract content of a package:

  ```shell-session
  $ ar vx mypackage.deb
  ```

## Install

- Install a package from a lower-priority repository, like the backport repository:

  ```shell-session
  $ apt-get -t squeeze-backports install my-package
  ```

- Force reinstallation of a package:

  ```shell-session
  $ apt-get -d --reinstall install my-package
  $ dpkg --install --force-confmiss /var/cache/apt/archives/my-package.deb
  ```

## Upgrade

- Upgrade package listing and metadata:

  ```shell-session
  $ sudo apt update
  ```

- Force `yes` so that package maintainer's version of config files always prevails:

  ```shell-session
  $ sudo apt upgrade -y --force-yes
  ```

## Holding

- Hold a package with either `dpkg` or `aptitude`:

  ```shell-session
  $ echo "kdenlive hold" | dpkg --set-selections
  ```

  or:

  ```shell-session
  $ aptitude hold kdenlive
  ```

- Unhold a package:

  ```shell-session
  $ echo "kdenlive install" | dpkg --set-selections
  ```

  or:

  ```shell-session
  $ aptitude unhold kdenlive
  ```

- List held packages:

  ```shell-session
  $ dpkg --get-selections | grep hold
  ```

## Uninstall

- Uninstall a package thoroughly (both program files and configuration):

  ```shell-session
  $ apt-get remove --purge my_package
  ```

- Force removal of a package while ignoring all dependencies:

  ```shell-session
  $ dpkg --remove --force-depends libsomething
  ```

- Remove orphaned packages:

  ```shell-session
  $ deborphan | xargs apt-get -y remove --purge
  ```

## Clean-up

- Clean aptitude local cache:

  ```shell-session
  $ apt-get clean
  ```

- Remove `dpkg` lock file:

  ```shell-session
  $ rm /var/lib/dpkg/lock
  ```
