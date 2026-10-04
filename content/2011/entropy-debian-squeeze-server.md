---
date: '2011-08-09'
title: Better Entropy on a Debian Squeeze server
category: English
tags: Debian, entropy, haveged, Linux, random, security, Debian Squeeze
---

While generating a GPG key on my server, I got the following error:

```text
Not enough random bytes available. Please do some other work to give the OS a chance to collect more entropy! (Need 283 more bytes)
```

That's a [well known issue](https://web.archive.org/web/20120420185013/http://otrs.menandmice.com/otrs/public.pl?Action=PublicFAQ&ItemID=122) on headless servers. Thanks to a [comment on Hacker News](https://news.ycombinator.com/item?id=2703349), I knew there was a way to fix this thanks to software entropy generator, like the [havege daemon](https://www.issihosts.com/haveged/).

My server is running Debian Squeeze. Luckily, a [package is available](https://packages.debian.org/squeeze-backports/haveged) in the backport repository. All we have to do is to add the latter in our source list before installing `haveged`:

```shell-session
$ echo 'deb https://backports.debian.org/debian-backports squeeze-backports main' > /etc/apt/sources.list.d/squeeze-backports.list
$ apt-get update
$ apt-get -t squeeze-backports install haveged
```

Now you can get a proof that `haveged` is running by monitoring your entropy. Here is for example the Munin graph of my server, on which you can clearly see the big jump in available entropy:

![Munin graph of available entropy, flat near zero until haveged starts, then jumping to a noisy band between 4,000 and 16,000 bytes](increased-entropy-with-haveged.png)

If I'm not sure about the quality of the [randomness it generate on virtual machines](https://jakob.engbloms.se/archives/1374), `haveged` is still a really practical solution for lack of entropy on a server.
