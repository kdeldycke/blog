---
date: '2012-04-10'
title: Check Point's SNX client on Ubuntu 11.04
category: English
tags: check point, Linux, Network, snx, SSL, Ubuntu, VPN
---

Last month I had no other alternative but to reach a server through a [Check Point](https://wikipedia.org/wiki/Check_Point)'s VPN. Fortunately the editor provides a Linux client to access its proprietary stack.

The version I found to work on my Ubuntu 11.04 is the _SSL Network Extender (SNX) R71_ package that [can be downloaded there](https://supportcontent.checkpoint.com/file_download?id=10656) ([source](https://supportcenter.checkpoint.com/supportcenter/portal?eventSubmit_doGoviewsolutiondetails=&solutionid=sk41808)).

Just for reference, the build working for me is numbered `800005013`, and here is a copy of what to expect when the connection succeed:

```shell-session
$ snx -s vpn.example.net -u my_user
Check Point's Linux SNX
build 800005013
Please enter your password:

SNX - connected.

Session parameters:
===================
Office Mode IP      : 10.32.10.23
DNS Server          : 10.168.10.1
Secondary DNS Server: 10.168.10.2
Timeout             : 3 hours
```
