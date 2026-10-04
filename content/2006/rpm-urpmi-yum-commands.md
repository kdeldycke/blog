---
date: '2006-11-29'
title: RPM, Urpmi & Yum commands
category: English
tags: Archive formats, CLI, cpio, genhdlist, Linux, Mandriva, Red Hat, RPM, urpmi, yum, cron
---

## RPM

- List all installed packages:

  ```shell-session
  $ rpm -qa
  ```

- Get the list of all installed packages and their architecture:

  ```shell-session
  $ rpm -qa --queryformat "%-40{NAME} %-8{ARCH}\n"
  ```

- Same as above, but show `i586` packages only:

  ```shell-session
  $ rpm -qa --queryformat "%-40{NAME} %-8{ARCH}\n" | grep i586
  ```

- Downgrade a package to an old version:

  ```shell-session
  $ wget ftp://ftp.repository.org/mandrakelinux/official/10.0/package-1.0-1mdk.i586.rpm
  $ rpm -Uvh --oldpackage package-1.0-1mdk.i586.rpm
  ```

- Unpack/Deflate/Extract a RPM without installing it:

  ```shell-session
  $ rpm2cpio dummy.src.rpm | cpio -id
  ```

- Evaluate `%mkrel 3` rpm macro:

  ```shell-session
  $ rpm --eval '%mkrel 3'
  ```

- Force removal of a package that has problems with embedded "pre-" and/or "post-" scripts:

  ```shell-session
  $ rpm -e --noscripts packagename
  ```

## Urpmi

- List all available packages with name containing `python`:

  ```shell-session
  $ urpmq --fuzzy python
  ```

- Find which RPM contain the file named `dummy`:

  ```shell-session
  $ urpmf dummy
  ```

- Get information about the `dummy` RPM:

  ```shell-session
  $ urpmq -i dummy
  ```

- Get the list of all RPMs that require `python-psyco` package:

  ```shell-session
  $ urpmf --requires python-psyco
  ```

- Get the list of all RPMs that provide `python-psyco` package:

  ```shell-session
  $ urpmf --provides python-psyco
  ```

- I use this command in a cron entry to update automatically and regularly my Mandriva:

  ```shell-session
  $ /usr/sbin/urpmi.update -a && /usr/sbin/urpmi --update --auto --auto-select
  ```

- Generate urpmi repository index and metadata of the current folder:

  ```shell-session
  $ genhdlist ./
  ```

- [APT/URPMI commands list](https://web.archive.org/web/20061201162311/http://linux.ensimag.fr/urpmiapt.html)

## Yum

- Install a new package:

  ```shell-session
  $ yum install subversion
  ```

- Search for packages containing the `x11` string:

  ```shell-session
  $ yum search x11
  ```

- Get the list of packages that provide Python's Subversion bindings:

  ```shell-session
  $ yum provides "*/svn/__init__.py"
  ```

- Update repository index:

  ```shell-session
  $ yum update
  ```

- Clear all caches (sometimes required to force a repository index update):

  ```shell-session
  $ yum clean all
  ```

- Generate [Yum](http://yum.baseurl.org/) repository index and metadata of the current folder:

  ```shell-session
  $ createrepo -v ./
  ```
