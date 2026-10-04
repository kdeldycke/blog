---
date: '2011-11-01'
title: Bazaar commands
category: English
tags: bazaar, CLI, development, Launchpad, Linux, OpenERP, programming
---

- Check-out in the local `openerp-server` folder the `6.0` branch of the OpenERP server project from Launchpad:

  ```shell-session
  $ bzr branch lp:openobject-server/6.0 openerp-server
  ```

- Same command as above, but fetch a particular revision:

  ```shell-session
  $ bzr branch lp:openobject-server/6.0 -r 3425 openerp-server
  ```

- Check-out the current head of a branch, without its history. This is particularly useful when working on large repositories with huge history ([source](https://web.archive.org/web/20130608041942/http://doc.bazaar.canonical.com/beta/en/user-guide/using_checkouts.html#getting-a-lightweight-checkout)):

  ```shell-session
  $ bzr checkout --lightweight lp:openobject-addons/7.0 addons
  ```

- Export a copy of a branch, without any Bazaar metadata:

  ```shell-session
  $ bzr export addons lp:openobject-addons/7.0
  ```

- Get revision number of the local copy we sit in:

  ```shell-session
  $ bzr revno ./
  ```

- Change the repository to a previous revision:

  ```shell-session
  $ bzr revert -r 1234
  ```

- Remove lock file on the current repository:

  ```shell-session
  $ bzr break-lock
  ```

- Produce a patch from uncommitted local changes with absolute path:

  ```shell-session
  $ bzr diff --prefix=`pwd`/:`pwd`/ > server.patch
  ```
