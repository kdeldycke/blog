---
date: '2007-04-20'
title: How-to Backup / Mirror a public SVN repository
category: English
tags: Backup, Linux, SCM, Subversion, SVK
---

In this little how-to I will show you how to backup a public SVN repository
thanks to [SVK](https://svk.bestpractical.com), a tool build upon SVN framework
that add decentralized capabilities.

First, create a local repository:

```shell-session
$ svk mirror //local https://username@svn.kde.org/home/kde
```

SVK will ask you to create a new repository. Tell it you want so:

```text
Repository /home/user/.svk/local does not exist, create? (y/n) y
```

Then, sync the remote repository with the local one:

```shell-session
$ svk sync //local
```

That's all!

To update your locale repository with the latest set of changes from the remote
one, just run the previous command from time to time.

Now you can play with your local repository (`/home/user/.svk/local` in this
example) as if it was a normal SVN repository!

**_Update_**: If you want to generate a vanilla SVN dump out of your SVK local
mirror, as suggest by [Thomas Mølhave](https://moelhave.dk) in his
"[Remote Backup Of A Subversion (svn) Repository](https://web.archive.org/web/20070505062431/http://moelhave.dk/2006/07/remote-mirroring-a-subversion-svn-repository/)"
blog post, use `svnadmin`:

```shell-session
$ svnadmin dump -r2:HEAD ~/.svk/local > my-repository-dump
```
