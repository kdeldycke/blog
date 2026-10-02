---
date: '2011-05-03'
title: How-to use GMail to send mails from Debian Squeeze
category: English
tags: Debian, Exim, Gmail, Google Apps, Linux, email, Server, Debian Squeeze, RSA
---

Here is quick guide on how I configured Exim 4 to let a Debian Squeeze server send mails through a GMail account. This article is just a rip-off of [a tutorial I found on the web](https://www.manu-j.com/blog/wordpress-exim4-ubuntu-gmail-smtp/75/), which is itself an updated version of [a Debian's Wiki page](https://wiki.debian.org/GmailAndExim4).

Debian come with Exim (v4.72) pre-installed: it's the default MTA on this distribution. There is absolutely no need to install extra packages. Let's start right away by calling Exim's configuration wizard:

```shell-session
$ dpkg-reconfigure exim4-config
```

Here are the options I choose in each step of the wizard:

01. Choose `Mail sent by smarthost; received via SMTP or fetchmail`.

02. System mail name: `server.deldycke.com`.

03. IP addresses to listen on for incoming SMTP connections: `127.0.0.1 ; ::1` (which is the default proposed value).

04. Other destinations for which mail is accepted: leave blank.

05. Machines to relay mail for: leave blank.

06. Machine handling outgoing mail for this host (smarthost): `smtp.gmail.com::587`.

07. Hide local mail name in outgoing mail: `No`.

08. Keep number of DNS-queries minimal (Dial-on-Demand): `No`.

09. Mailboxes format: `mbox`.

10. Split configuration into small files: `No`.

All these parameters you just answered are saved in the `/etc/exim4/update-exim4.conf.conf`:

```ini
# /etc/exim4/update-exim4.conf.conf
#
# Edit this file and /etc/mailname by hand and execute update-exim4.conf
# yourself or use 'dpkg-reconfigure exim4-config'
#
# Please note that this is _not_ a dpkg-conffile and that automatic changes
# to this file might happen. The code handling this will honor your local
# changes, so this is usually fine, but will break local schemes that mess
# around with multiple versions of the file.
#
# update-exim4.conf uses this file to determine variable values to generate
# exim configuration macros for the configuration file.
#
# Most settings found in here do have corresponding questions in the
# Debconf configuration, but not all of them.
#
# This is a Debian specific file

dc_eximconfig_configtype='smarthost'
dc_other_hostnames=''
dc_local_interfaces='127.0.0.1 ; ::1'
dc_readhost=''
dc_relay_domains=''
dc_minimaldns='false'
dc_relay_nets=''
dc_smarthost='smtp.gmail.com:587'
CFILEMODE='644'
dc_use_split_config='false'
dc_hide_mailname='false'
dc_mailname_in_oh='true'
dc_localdelivery='mail_spool'
```

Then I updated the `/etc/exim4/exim4.conf.template` to add proper handling of GMail SMTP server. Here are the differences between the untouched original `exim4.conf.template` file and my version:

```diff
--- /etc/exim4/exim4.conf.template-orig  2011-05-03 10:49:43.207938577 +0200
+++ /etc/exim4/exim4.conf.template       2011-05-03 10:52:26.235438776 +0200
@@ -1077,15 +1077,11 @@
 # domains, you'll need to copy the dnslookup_relay_to_domains router
 # here so that mail to relay_domains is handled separately.

-smarthost:
-  debug_print = "R: smarthost for $local_part@$domain"
-  driver = manualroute
-  domains = ! +local_domains
-  transport = remote_smtp_smarthost
-  route_list = * DCsmarthost byname
-  host_find_failed = defer
-  same_domain_copy_routing = yes
-  no_more
+send_via_gmail:
+       driver = manualroute
+       domains = ! +local_domains
+       transport = gmail_smtp
+       route_list = * smtp.gmail.com

 .endif

@@ -1632,6 +1628,12 @@
 # to a smarthost. The local host tries to authenticate.
 # This transport is used for smarthost and satellite configurations.

+gmail_smtp:
+       driver = smtp
+       port = 587
+       hosts_require_auth = $host_address
+       hosts_require_tls = $host_address
+
 remote_smtp_smarthost:
   debug_print = "T: remote_smtp_smarthost for $local_part@$domain"
   driver = smtp
@@ -1759,6 +1761,11 @@

 begin authenticators

+gmail_login:
+       driver = plaintext
+       public_name = LOGIN
+       client_send = : system@deldycke.com : XXXXXXXXX
+

 #####################################################
 ### end auth/00_exim4-config_header
@@ -1999,27 +2006,27 @@
                    ^${sg{PASSWDLINE}{\\N([^:]+:)(.*)\\N}{\\$2}}"
 .endif

-login:
-  driver = plaintext
-  public_name = LOGIN
-.ifndef AUTH_CLIENT_ALLOW_NOTLS_PASSWORDS
-  # Return empty string if not non-TLS AND looking up $host in passwd-file
-  # yields a non-empty string; fail otherwise.
-  client_send = "<; ${if and{\
-                          {!eq{$tls_cipher}{}}\
-                          {!eq{PASSWDLINE}{}}\
-                         }\
-                      {}fail}\
-                 ; ${extract{1}{::}{PASSWDLINE}}\
-                ; ${sg{PASSWDLINE}{\\N([^:]+:)(.*)\\N}{\\$2}}"
-.else
-  # Return empty string if looking up $host in passwd-file yields a
-  # non-empty string; fail otherwise.
-  client_send = "<; ${if !eq{PASSWDLINE}{}\
-                      {}fail}\
-                 ; ${extract{1}{::}{PASSWDLINE}}\
-                ; ${sg{PASSWDLINE}{\\N([^:]+:)(.*)\\N}{\\$2}}"
-.endif
+#login:
+#  driver = plaintext
+#  public_name = LOGIN
+#.ifndef AUTH_CLIENT_ALLOW_NOTLS_PASSWORDS
+#  # Return empty string if not non-TLS AND looking up $host in passwd-file
+#  # yields a non-empty string; fail otherwise.
+#  client_send = "<; ${if and{\
+#                          {!eq{$tls_cipher}{}}\
+#                          {!eq{PASSWDLINE}{}}\
+#                         }\
+#                      {}fail}\
+#                 ; ${extract{1}{::}{PASSWDLINE}}\
+#               ; ${sg{PASSWDLINE}{\\N([^:]+:)(.*)\\N}{\\$2}}"
+#.else
+#  # Return empty string if looking up $host in passwd-file yields a
+#  # non-empty string; fail otherwise.
+#  client_send = "<; ${if !eq{PASSWDLINE}{}\
+#                      {}fail}\
+#                 ; ${extract{1}{::}{PASSWDLINE}}\
+#               ; ${sg{PASSWDLINE}{\\N([^:]+:)(.*)\\N}{\\$2}}"
+#.endif
 #####################################################
 ### end auth/30_exim4-config_examples
 #####################################################
```

Now all we have to do is to regenerate Exim's configuration and restart the mail server:

```shell-session
$ update-exim4.conf
$ /etc/init.d/exim4 restart
```

You can then send a dummy email to test your mail system:

```shell-session
$ mail kevin@deldycke.com
Subject: This is an exim test
.
Cc:
Null message body; hope that's ok
```

And check in the log that everything's fine:

```shell-session
$ tail -F /var/log/exim4/mainlog
2011-05-03 10:56:32 1QHBPE-0000ne-CW <= root@server.deldycke.com U=root P=local S=362
2011-05-03 10:56:36 1QHBPE-0000ne-CW => kevin@deldycke.com R=send_via_gmail T=gmail_smtp H=gmail-smtp-msa.l.google.com [209.85.227.109] X=TLS1.0:RSA_ARCFOUR_SHA1:16 DN="C=US,ST=California,L=Mountain View,O=Google Inc,CN=smtp.gmail.com"
2011-05-03 10:56:36 1QHBPE-0000ne-CW Completed
```
