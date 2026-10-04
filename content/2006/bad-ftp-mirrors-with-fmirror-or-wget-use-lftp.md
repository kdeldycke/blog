---
date: '2006-04-29'
title: Bad FTP mirrors with fmirror or wget? Use lftp!
category: English
tags: Backup, CLI, fmirror, FTP, lftp, Linux, Web, wget
---

Today I've found that my websites were not backed up as expected. I was using `fmirror` (v0.8.4) to get a copy from my host provider to my backup machine. Here is the command line I was using:

```shell-session
$ fmirror -kRS -u kevin -p pass -s ftp.website.com -r /html -l /mnt/removable/website_backup/current
```

But `fmirror` seems to not care about sub-directories starting from a given depth. One source of the problem could be strange file names (spaces, utf8 chars, etc).

Because I don't had the time to investigate further, I was looking for an alternative. So I tried `wget` (v1.10) with the following command:

```shell-session
$ wget -r -nH -N --cut-dirs=1 -l0 -np --cache=off ftp://kevin:pass@ftp.website.com:21/html -o ../backup.log
```

This work perfectly on small websites. But on my biggest one (hundreds of MB), wget hang up with the following error:

```text
*** glibc detected *** double free or corruption (top): 0x08097750 ***
```

It seems to be a known limitation of wget: "Wget has got serious problems retrieving huge sites" ([source: "Possible Alternatives to WGET"](https://web.archive.org/web/20060427035018/http://www.ccp14.ac.uk/mirror/wget.htm)).

So I went back to basics by using the good old `lftp`, which is efficient and reliable. Here is the command:

```shell-session
$ lftp -c 'open -e "mirror -e . ./ " ftp://kevin:pass@ftp.website.com:21/html'
```
