---
date: '2010-04-26'
title: Setup a lightweight IMAP server on Mac OS X Leopard with Dovecot
category: English
tags: Dovecot, email, IMAP, Mac OS X 10.5 Leopard, Apple, macOS, maildir, OpenSSL, SSL
---

![Terminal tailing the mail log after starting Dovecot, showing successful IMAP logins from the loopback address over TLS](dovecot-on-macosx.png)

Last week I needed a local IMAP server on Mac OS X Leopard for temporary
testing. After struggling with [courier-imap](https://www.courier-mta.org/imap/)
for hours, I've finally settled on [Dovecot](https://www.dovecot.org/). You'll
see below how easy it is to install and configure it.

We're lucky, [Dovecot is available in MacPorts
](https://www.macports.org/ports.php?by=name&substr=dovecot), so we can install
it easily:

```shell-session
$ port install dovecot
```

It's time to configure it. We start with the default configuration template:

```shell-session
$ cp /opt/local/etc/dovecot/dovecot-example.conf /opt/local/etc/dovecot/dovecot.conf
```

Then we can edit the `dovecot.conf` configuration file as we wish. FYI, here
are my modifications:

```diff
--- /opt/local/etc/dovecot/dovecot-example.conf	2010-04-23 14:29:52.000000000 +0200
+++ /opt/local/etc/dovecot/dovecot.conf	2010-04-23 14:51:06.000000000 +0200
@@ -21,7 +21,7 @@

 # Protocols we want to be serving: imap imaps pop3 pop3s
 # If you only want to use dovecot-auth, you can set this to "none".
-#protocols = imap imaps
+protocols = imap

 # A space separated list of IP or host addresses where to listen in for
 # connections. "*" listens in all IPv4 interfaces. "[::]" listens in all IPv6
@@ -45,7 +45,7 @@
 # SSL/TLS is used (LOGINDISABLED capability). Note that if the remote IP
 # matches the local IP (ie. you're connecting from the same computer), the
 # connection is considered secure and plaintext authentication is allowed.
-#disable_plaintext_auth = yes
+disable_plaintext_auth = no

 # Should all IMAP and POP3 processes be killed when Dovecot master process
 # shuts down. Setting this to "no" means that Dovecot can be upgraded without
@@ -221,7 +221,7 @@
 #
 # <doc/wiki/MailLocation.txt>
 #
-#mail_location =
+mail_location = maildir:~/Maildir

 # If you need to set multiple mailbox locations or want to change default
 # namespace settings, you can do it by defining namespace sections.
```

Before starting Dovecot, we have to create a dummy SSL certificate:

```shell-session
$ mkdir -p /opt/local/etc/ssl/{certs,private}
$ openssl req -new -x509 -days 3650 -nodes -out /opt/local/etc/ssl/certs/dovecot.pem -keyout /opt/local/etc/ssl/private/dovecot.pem
```

And finally, we can launch the Dovecot server itself as `root`:

```shell-session
$ dovecot
```

That's all!

You can now access your local IMAP server with any client. Here is an example
with [Thunderbird](https://www.thunderbird.net/):

![Thunderbird server settings for the local account, pointed at localhost on port 143 over STARTTLS with automatic checking switched off](thunderbird-macosx-local-imap-server-config.png)

And if you have problems, the first reflex is to read Dovecot's logs:

```shell-session
$ tail -F /var/log/mail.log
```
