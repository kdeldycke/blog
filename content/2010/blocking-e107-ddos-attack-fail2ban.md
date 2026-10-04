---
date: '2010-08-03'
title: Blocking e107 dDOS attack with fail2ban
category: English
tags: Apache, Cool Cavemen, e107, fail2ban, Linux, PHP, security, Server, Web, Regular expression
---

Last month, a new security vulnerability was discovered in e107. If [a fix was
released quickly](https://e107.org/comment.php?comment.news.867), some instances
on the web were left unpatched. These sites are easy target for
<strike>hackers</strike> script-kiddies, and [a generalized dDOS attack was
carry out](https://e107.org/comment.php?comment.news.868) on every e107 websites
out there.

I'm no exception and the old and decrepit part of Cool Cavemen's website [still
running on
e107](https://web.archive.org/web/20110418072200/https://coolcavemen.com/e107_plugins/forum/forum_viewforum.php?3)
was attacked. This was enough to crash my tiny server. Unfortunately this
[happened while I was on
holidays](https://twitter.com/kdeldycke/status/17728248113). Without any time to
address this issue properly, I decided to shutdown my web server. This explain
why this blog and all Cool Cavemen's websites were dead during half of july.

![Munin weekly graph of active fail2ban bans, the apache-e107ddos jail climbing to nearly 500 before resetting and immediately climbing again](munin-fail2ban-jails-weekly-stats.png)

Now [everything is back to
normal](https://twitter.com/kdeldycke/status/19250530728) (I hope), thanks to
[`fail2ban`](https://www.fail2ban.org). I created a set of rules ([based on this
article](https://web.archive.org/web/20100720043900/http://eromang.zataz.com/2010/07/13/byroenet-casper-bot-search-e107-rce-scanner/))
to dynamically catch
[dDOS](https://en.wikipedia.org/wiki/Denial-of-service_attack) attempts and ban
all IP addresses involved. Here is how I configured `fail2ban`...

First, create a new empty file at `/etc/fail2ban/filter.d/apache-e107ddos.conf`
and put the following directives there:

```ini
# Fail2Ban configuration file
# Notes.:  Regexp to catch all attempts to exploit an e107 vulnerability.
# Author: Kevin Deldycke

[Definition]
failregex = <HOST>\s-\s-\s.*\s"(GET|POST).*\/(help_us|contact|config|avd_start|\*)\.php
            <HOST>\s-\s-\s.*(Casper|b3b4s|dex|Dex|kmccrew|plaNETWORK|sasqia|sledink|indocom) Bot Search
            <HOST>\s-\s-\s.*MaMa CaSpEr
            <HOST>\s-\s-\s.*rk q kangen
            <HOST>\s-\s-\s.*Mozilla\/4\.76 \[ru\] \(X11; U; SunOS 5\.7 sun4u\)
            <HOST>\s-\s-\s.*perl post
ignoreregex =
```

Then update you fail2ban config file (`/etc/fail2ban/jail.local` in my case)
with the appropriate section:

```ini
[apache-e107ddos]
enabled  = true
filter   = apache-e107ddos
port     = http,https
action   = iptables-allports
logpath  = /var/log/apache*/*access.log
maxretry = 1
```

Then restart your fail2ban service:

```shell-session
$ /etc/init.d/fail2ban restart
```

And you'll start to get those nice logs:

```shell-session
$ tail -F /var/log/fail2ban.log
2010-06-23 16:05:37,417 fail2ban.actions: WARNING [apache-e107ddos] Ban 193.33.21.199
2010-06-23 16:05:58,113 fail2ban.actions: WARNING [apache-e107ddos] Ban 89.108.116.226
2010-06-23 16:05:58,521 fail2ban.actions: WARNING [apache-e107ddos] Ban 69.41.162.10
2010-06-23 16:05:58,541 fail2ban.actions: WARNING [apache-e107ddos] Ban 209.62.28.178
2010-06-23 16:06:03,573 fail2ban.actions: WARNING [apache-e107ddos] Ban 69.73.147.90
2010-06-23 16:06:42,975 fail2ban.actions: WARNING [apache-e107ddos] 69.41.162.10 already banned
2010-06-23 16:06:44,227 fail2ban.actions: WARNING [apache-e107ddos] 69.41.162.10 already banned
2010-06-23 16:06:54,238 fail2ban.actions: WARNING [apache-e107ddos] 69.73.147.90 already banned
2010-06-23 16:07:50,305 fail2ban.actions: WARNING [apache-e107ddos] Ban 80.55.107.74
```
