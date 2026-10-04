---
date: '2011-09-27'
title: How-to setup Mailman + Nginx + Exim on Debian Squeeze
category: English
tags: Debian, Debian Squeeze, email, Exim, fcgiwrap, Linux, mailing list, mailman, munin, nginx
---

![GNU Mailman logo, the wordmark beside a stylised blue envelope](mailman-logo.png)

Before going further, please take note that I start this tutorial assuming that
you already have a [minimal Exim
setup]({filename}/2011/how-to-gmail-send-mails-debian-squeeze.md)
running on your Debian machine.

## Mailman

Now that you have the context, let's proceed with
[Mailman](https://www.list.org/) install:

```shell-session
$ aptitude install mailman
```

During the installation, you'll be prompted about the languages files you want
Mailman web interface support. English is enough for me.

Now Mailman requires a meta-mailing-list from which it will send all mails
related to subscription, reminders and all:

```shell-session
$ newlist mailman kevin@deldycke.com
```

You'll then be prompted for a password.

After that, Mailman will provide you with a list of directives to add to
`/etc/aliases`:

```text
mailman:              "|/var/lib/mailman/mail/mailman post mailman"
mailman-admin:        "|/var/lib/mailman/mail/mailman admin mailman"
mailman-bounces:      "|/var/lib/mailman/mail/mailman bounces mailman"
mailman-confirm:      "|/var/lib/mailman/mail/mailman confirm mailman"
mailman-join:         "|/var/lib/mailman/mail/mailman join mailman"
mailman-leave:        "|/var/lib/mailman/mail/mailman leave mailman"
mailman-owner:        "|/var/lib/mailman/mail/mailman owner mailman"
mailman-request:      "|/var/lib/mailman/mail/mailman request mailman"
mailman-subscribe:    "|/var/lib/mailman/mail/mailman subscribe mailman"
mailman-unsubscribe:  "|/var/lib/mailman/mail/mailman unsubscribe mailman"
```

This update is not necessary, as Exim will handle them automatically.

You can now restart the Mailman server:

```shell-session
$ /etc/init.d/mailman start
```

Oh, and the first time you'll run Mailman, do a `start` as above, not a
`restart`, else you'll end up with this error:

```console
Restarting Mailman master qrunner: mailmanctl PID unreadable in: /var/run/mailman/mailman.pid
[Errno 2] No such file or directory: '/var/run/mailman/mailman.pid'
Is qrunner even running?
```

If everything is alright, you'll receive a mail similar to this one:

![Automated welcome mail announcing the new mailman list, with the list password and the admin and listinfo URLs blurred out](mailman-new-mailing-list-message.png)

## Nginx

Now we have to configure our HTTP server to make the administration interface
available from the web. If Apache is the recommended server to use with
Mailman, Nginx is already running on my machine, so let's use it instead.

First, as [explained on Nginx wiki](https://web.archive.org/web/20110901213605/http://wiki.nginx.org/Fcgiwrap) we need to
install `fcgiwrap`:

```shell-session
$ aptitude install fcgiwrap
```

Then we have to create an Nginx configuration file dedicated to Mailman.
Assuming we want all mailing-lists managed under the `lists.example.com`
domain, here are the directives you have to put in a new
`/etc/nginx/sites-available/mailman` file:

```nginx
server {
  server_name lists.example.com;

  root /usr/lib/cgi-bin;

  location = / {
    rewrite ^ /mailman/listinfo permanent;
  }

  location / {
    rewrite ^ /mailman$uri;
  }

  location /mailman {
    include /etc/nginx/fastcgi_params;
    # Fastcgi socket
    fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    # Disable gzip (it makes scripts feel slower since they have to complete
    # before getting gzipped)
    gzip off;
  }

  location /images/mailman {
    alias /var/lib/mailman/icons;
  }

  location /pipermail {
    alias /var/lib/mailman/archives/public;
    autoindex on;
  }
}

server {
  server_name *.lists.example.com .lists.example.org .lists.example.net;
  rewrite ^ http://lists.example.com$request_uri? permanent;
}
```

The configuration above is a mix between [the one available on Nginx
wiki](https://web.archive.org/web/20111018112949/http://wiki.nginx.org/Mailman) and the
`/usr/share/doc/fcgiwrap/examples/nginx.conf` example file that come with the
Debian package.

All we have to do now is to activate the configuration above and restart our
CGI and HTTP server:

```shell-session
$ ln -s /etc/nginx/sites-available/mailman /etc/nginx/sites-enabled/
$ /etc/init.d/fcgiwrap restart
$ /etc/init.d/nginx restart
```

If everything's OK, going to `http://lists.example.com` will show you this:

![Default Mailman index page reporting no publicly advertised lists, the hostname redacted, with the Mailman, Python, GNU and Debian badges along the bottom](mailman-default-welcome-screen.png)

## Exim

Now we have to setup the MTA. All information here are coming from the
documentation you can find on your Debian system in
`/usr/share/doc/mailman/README.Exim4.Debian.gz`.

First, we have to update `/etc/mailman/mm_cfg.py` (the global Mailman
configuration file). We'll aligned there the default URLs, hosts and
MTA-related parameters:

```diff
--- /etc/mailman/mm_cfg.py.orig    2011-08-31 22:28:53.000000000 +0200
+++ /etc/mailman/mm_cfg.py 2011-09-07 22:43:41.000000000 +0200
@@ -57,16 +57,16 @@
 #-------------------------------------------------------------
 # If you change these, you have to configure your http server
 # accordingly (Alias and ScriptAlias directives in most httpds)
-DEFAULT_URL_PATTERN = 'http://%s/cgi-bin/mailman/'
-PRIVATE_ARCHIVE_URL = '/cgi-bin/mailman/private'
+DEFAULT_URL_PATTERN = 'http://%s/mailman/'
+PRIVATE_ARCHIVE_URL = '/mailman/private'
 IMAGE_LOGOS         = '/images/mailman/'

 #-------------------------------------------------------------
 # Default domain for email addresses of newly created MLs
-DEFAULT_EMAIL_HOST = 'server123.example.net'
+DEFAULT_EMAIL_HOST = 'lists.example.com'
 #-------------------------------------------------------------
 # Default host for web interface of newly created MLs
-DEFAULT_URL_HOST   = 'server123.example.net'
+DEFAULT_URL_HOST   = 'lists.example.com'
 #-------------------------------------------------------------
 # Required when setting any of its arguments.
 add_virtualhost(DEFAULT_URL_HOST, DEFAULT_EMAIL_HOST)
@@ -94,7 +94,10 @@
 # Uncomment if you use Postfix virtual domains (but not
 # postfix-to-mailman.py), but be sure to see
 # /usr/share/doc/mailman/README.Debian first.
-# MTA='Postfix'
+MTA = 'Postfix'
+POSTFIX_ALIAS_CMD = '/bin/true'
+POSTFIX_MAP_CMD = 'chgrp Debian-exim'
+POSTFIX_STYLE_VIRTUAL_DOMAINS = ['lists.example.com']

 #-------------------------------------------------------------
 # Uncomment if you want to filter mail with SpamAssassin. For
```

Then we have to update the Exim configuration template. If like me you haven't
choose to split configuration into small files, here are the modifications you
have to add to `/etc/exim4/exim4.conf.template`:

```diff
--- /etc/exim4/exim4.conf.template.orig 2011-09-07 23:34:53.000000000 +0200
+++ /etc/exim4/exim4.conf.template       2011-09-07 23:44:45.000000000 +0200
@@ -395,6 +395,21 @@
 ### end main/03_exim4-config_tlsoptions
 #####################################################
 #####################################################
+### main/04_local_mailman_macros
+#####################################################
+# Home dir for your Mailman installation -- aka Mailman's prefix
+# directory.
+MAILMAN_HOME=/var/lib/mailman
+MAILMAN_WRAP=MAILMAN_HOME/mail/mailman
+
+# User and group for Mailman, should match your --with-mail-gid
+# switch to Mailman's configure script.
+MAILMAN_USER=list
+MAILMAN_GROUP=daemon
+#####################################################
+### end main/04_local_mailman_macros
+#####################################################
+#####################################################
 ### main/90_exim4-config_log_selector
 #####################################################

@@ -1371,6 +1386,44 @@
 ### end router/900_exim4-config_local_user
 #####################################################
 #####################################################
+### router/970_local_mailman
+#####################################################
+# Messages get sent out with
+# envelope from "mailman-bounces@virtual_domain"
+# But mailman doesn't put such addresses
+# in the aliases. Recognise these here.
+mailman_workaround:
+  debug_print = "R: mailman_workaround for $local_part@$domain"
+  domains = +local_domains
+  require_files = MAILMAN_HOME/lists/$local_part/config.pck
+  driver = accept
+  local_parts = mailman
+  local_part_suffix_optional
+  local_part_suffix = -bounces : -bounces+* : \
+           -confirm+* : -join : -leave : \
+           -subscribe : -unsubscribe : \
+           -owner : -request : -admin : -loop
+  transport = mailman_transport
+  group = MAILMAN_GROUP
+
+# Mailman lists
+mailman_router:
+  debug_print = "R: mailman_router for $local_part@$domain"
+  domains = +local_domains
+  condition = ${lookup{$local_part@$domain}lsearch{MAILMAN_HOME/data/virtual-mailman}{1}{0}}
+  require_files = MAILMAN_HOME/lists/$local_part/config.pck
+  driver = accept
+  local_part_suffix_optional
+  local_part_suffix = -bounces : -bounces+* : \
+                      -confirm+* : -join : -leave : \
+                      -subscribe : -unsubscribe : \
+                      -owner : -request : -admin : -loop
+  transport = mailman_transport
+  group = MAILMAN_GROUP
+#####################################################
+### end router/970_local_mailman
+#####################################################
+#####################################################
 ### router/mmm_mail4root
 #####################################################

@@ -1689,6 +1742,25 @@
 ### end transport/35_exim4-config_address_directory
 #####################################################
 #####################################################
+### transport/40_local_mailman
+#####################################################
+mailman_transport:
+  debug_print = "T: mailman_transport for $local_part@$domain"
+  driver = pipe
+  command = MAILMAN_WRAP \
+            '${if def:local_part_suffix \
+                  {${sg{$local_part_suffix}{-(\\w+)(\\+.*)?}{\$1}}} \
+                  {post}}' \
+            $local_part
+  current_directory = MAILMAN_HOME
+  home_directory = MAILMAN_HOME
+  user = MAILMAN_USER
+  group = MAILMAN_GROUP
+  freeze_exec_fail = true
+#####################################################
+### end transport/40_local_mailman
+#####################################################
+#####################################################
 ### retry/00_exim4-config_header
 #####################################################
```

Don't apply this diff as-is, as the original file contain the modifications I
previously made to [let Exim use Gmail to send
mails]({filename}/2011/how-to-gmail-send-mails-debian-squeeze.md).

Then we have to update the Exim meta-configuration that is stored in
`/etc/exim4/update-exim4.conf.conf`. There we specify our host
(`lists.example.com`) and public IP address (`123.456.78.90`):

```text
dc_eximconfig_configtype='smarthost'
dc_other_hostnames='lists.example.com'
dc_local_interfaces='127.0.0.1 ; ::1 ; 123.456.78.90'
dc_readhost='lists.example.com'
dc_relay_domains='lists.example.com'
dc_minimaldns='false'
dc_relay_nets=''
dc_smarthost='smtp.gmail.com:587'
CFILEMODE='644'
dc_use_split_config='false'
dc_hide_mailname='false'
dc_mailname_in_oh='true'
dc_localdelivery='mail_spool'
```

Finally, our hostname must be a FQDN, so we have to add it to `/etc/hosts`:

```diff
--- /etc/hosts.orig        2011-09-12 13:52:19.000000000 +0200
+++ /etc/hosts     2011-09-12 12:21:31.000000000 +0200
@@ -1,7 +1,7 @@
 # Do not remove the following line, or various programs
 # that require network functionality will fail.
 127.0.0.1      localhost.localdomain localhost
-123.456.78.90   server123.example.net
+123.456.78.90   server123.example.net lists.example.com
 # The following lines are desirable for IPv6 capable hosts
 #(added automatically by netbase upgrade)
 ::1     ip6-localhost ip6-loopback
```

Then we have to regenerate Exim's configuration before restarting Mailman:

```shell-session
$ update-exim4.conf --verbose
$ /etc/init.d/exim4 restart
$ /etc/init.d/mailman restart
```

## Testing

You can now test your setup by creating a test mailing-list:

```shell-session
$ newlist kev-test
```

Now subscribe some test users and play with this mailing-list.

By monitoring `/var/log/mailman/error`, you'll maybe run into this error:

```text
IOError: [Errno 13] Permission denied: '/var/lib/mailman/archives/private/kev-test.mbox/kev-test.mbox'
```

This can be easily fixed with:

```shell-session
$ chown -R list /var/lib/mailman/archives/private/
```

Once you're convinced that Mailman is working as expected, you can remove your
temporary test mailing-list, and regenerate aliases to clean things up:

```shell-session
$ rmlist -a  kev-test
$ /var/lib/mailman/bin/genaliases
```

## Munin monitoring

Finally, if like me you [use Munin to monitor your machine
]({filename}/2011/munin-monitor-debian-squeeze-server.md), then it's a good
idea to let it graph some Mailman usage:

```shell-session
$ wget https://exchange.munin-monitoring.org/plugins/mailman-queue-check/version/2/download --output-document=/usr/share/munin/plugins/mailman-queue-check
$ wget https://exchange.munin-monitoring.org/plugins/mailman_subscribers/version/3/download --output-document=/usr/share/munin/plugins/mailman_subscribers
$ ln -s /usr/share/munin/plugins/mailman-queue-check /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/mailman_subscribers /etc/munin/plugins/
$ echo "[mailman*]
user root
" > /etc/munin/plugin-conf.d/mailman
$ chmod 755 /usr/share/munin/plugins/mailman*
$ /etc/init.d/munin-node restart
```
