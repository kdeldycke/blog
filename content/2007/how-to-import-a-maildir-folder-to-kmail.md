---
date: '2007-11-27'
title: How-to import a Maildir++ folder to Kmail
category: English
tags: Backup, KDE, kmail, Linux, email, mailbox, maildir, Python
---

Let's say you have a local copy of a mail folder you want to browse with [Kmail](https://kontact.kde.org/kmail). This folder is normally found on a dedicated mail server and you access it through the IMAP protocol. I was in this situation some days ago and I will tell you how I've done it.

Instinctively, I assumed that my folder was of the [Maildir format](https://en.wikipedia.org/wiki/Maildir), and Kmail local mails too. So I tried to copy my `~/Maildir` folder from the mail server to my local machine (`~/.kde/share/apps/kmail/mail/`). And that was the result in Kmail:

![kmail-no-sub-folders.png](kmail-no-sub-folders.png)

It looks good but it's not: there is no sub-folders!

After some googling, I found what was wrong: my `~/Maildir` folder is not a Maildir, but a [Maildir++](https://www.inter7.com/courierimap/README.maildirquota.html) folder. This kind of folder is handle by popular IMAP [MTA](https://en.wikipedia.org/wiki/Mail_transfer_agent) like [qmail](https://cr.yp.to/qmail.html), [Dovecot](https://www.dovecot.org) and [courier-imap](https://www.courier-mta.org) (which was used on the mail server where my `~/Maildir` come from). There is some advantages of using the "`++`" flavor of Maildir over the classic one, like quotas and sub-folders. Unfortunately [Kmail is not able to read the Maildir++ folder structure](https://groups.google.com/group/comp.windows.x.kde/browse_thread/thread/1c74818b4175b3ec#487b5c78311a07c7).

To fix this, I've created a tiny python [script to migrate a Maildir++ folder to Kmail](https://github.com/kdeldycke/scripts/blob/master/maildir%2B%2B2kmail.py).

How-to use it? Simply:

1. [Download it](https://github.com/kdeldycke/scripts/blob/master/maildir%2B%2B2kmail.py) to your disk,

2. Edit it and change the `MAILDIR_SOURCE` and `KMAILDIR_DEST` variables to match your local configuration,

3. Give it execution privileges,

4. Run it!

I advise you to try it first in a safe environment (like under a temporary user account). And don't forget to backup everything before playing with it: because this script work for me doesn't mean that it will work for you! ;)
