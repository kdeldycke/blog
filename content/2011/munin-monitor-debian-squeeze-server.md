---
date: '2011-06-06'
title: Using Munin to monitor a Debian Squeeze server
category: English
tags: acpi, Debian, fail2ban, Hardware, Linux, lm-sensors, munin, nginx, nut, RAID, Server, Debian Squeeze, Perl, Regular expression
---

Again, here is a tutorial article exposing the recipe I use to cook a [Munin](https://en.wikipedia.org/wiki/Munin_%28network_monitoring_application%29) on a Debian Squeeze.

As usual, let's start by installing the main Munin package:

```shell-session
$ aptitude install munin
```

FYI, the version that aptitude choose to install was Munin 1.4.5. The default configuration coming along will make it produce graphs and HTML content to `/var/cache/munin/www`. Now we need to serve these pages via a web server.

As I wanted to play with [nginx](https://en.wikipedia.org/wiki/Nginx) for a long time, I will use this opportunity to serve Munin's content. The default version coming with Squeeze is quite old, so we'll get the latest version from the [Dotdeb](https://www.dotdeb.org/) repository:

```shell-session
$ echo "deb https://packages.dotdeb.org squeeze all" > /etc/apt/sources.list.d/squeeze-dotdeb.list
$ aptitude update
$ aptitude install nginx
```

And if you don't want to get those error messages about untrusted packages, don't forget to [add Dotdeb's keys to your keyring](https://www.dotdeb.org/2010/07/11/dotdeb-packages-are-now-signed/).

We can now test that nginx is working by starting it up then fetch the default served page:

```shell-session
$ /etc/init.d/nginx start
$ wget --output-document=- http://localhost | grep "Welcome to nginx"
```

Then we'll disable the default nginx config and create a new one for Munin:

```shell-session
$ rm /etc/nginx/sites-enabled/default
$ touch /etc/nginx/sites-available/munin
```

In the latter, we put this minimal configuration:

```nginx
server {
  server_name munin.example.com;
  root /var/cache/munin/www/;
  location / {
    index index.html;
    access_log off;
  }
}
```

Now we have to activate it before restarting nginx:

```shell-session
$ ln -s  /etc/nginx/sites-available/munin /etc/nginx/sites-enabled/munin
$ /etc/init.d/nginx restart
```

Now we are free to point our browser to the `https://munin.example.com` URL to get our graphs.

You'll see that by default, Munin refer to your machine as `localhost.localdomain`. It's time to tweak Munin a little to get nice reports:

```shell-session
$ sed -i 's/\[localhost\.localdomain\]/\[munin\.example\.com\]/g' /etc/munin/munin.conf
```

By default Munin activate a lot of great graphs. But I always find that some crucial monitoring are missing. Let's add some more monitoring scripts:

```shell-session
$ aptitude install munin-plugins-extra
```

Here is a collection of general purpose graphs I automatically add to Munin:

```shell-session
$ ln -s /usr/share/munin/plugins/df_abs  /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/netstat /etc/munin/plugins/
$ echo "[netstat]
user root
" > /etc/munin/plugin-conf.d/netstat
```

It's also good to have a clue about your connectivity to the rest of the world:

```shell-session
$ ln -s /usr/share/munin/plugins/ping_  /etc/munin/plugins/ping_google.com
$ ln -s /usr/share/munin/plugins/ping_  /etc/munin/plugins/ping_ovh.fr
$ ln -s /usr/share/munin/plugins/ping_  /etc/munin/plugins/ping_example.com
```

I also like to have insight about my [automated backups]({filename}/2011/cloud-based-server-backups-duplicity-amazon-s3.md):

```shell-session
$ ln -s /usr/share/munin/plugins/ps_ /etc/munin/plugins/ps_duplicity
$ ln -s /usr/share/munin/plugins/ps_ /etc/munin/plugins/ps_sshd
```

Monitoring temperatures, voltages and other hardware metrics is a must, unless your machine is a virtual server :) :

```shell-session
$ ln -s /usr/share/munin/plugins/cpuspeed         /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/acpi             /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/hddtemp_smartctl /etc/munin/plugins/
$ aptitude install i2c-tools lm-sensors
$ sensors-detect
$ ln -s /usr/share/munin/plugins/sensors_ /etc/munin/plugins/sensors_temp
$ ln -s /usr/share/munin/plugins/sensors_ /etc/munin/plugins/sensors_volt
```

I sometimes have a Fail2Ban daemon running on a server, so that's a good thing to monitor it:

```shell-session
$ ln -s /usr/share/munin/plugins/fail2ban /etc/munin/plugins/
$ echo "[fail2ban*]
user root
" > /etc/munin/plugin-conf.d/fail2ban
```

[Having an UPS]({filename}/2011/mge-ellipse-750-ups-debian-squeeze.md), it's good to monitor it too. Here is for the UPS on the local system having the `MGE-Ellipse750` ID (as defined in your `/etc/nut/ups.conf` file):

```shell-session
$ ln -s /usr/share/munin/plugins/nutups_   /etc/munin/plugins/nutups_MGE-Ellipse750_voltages
$ ln -s /usr/share/munin/plugins/nutups_   /etc/munin/plugins/nutups_MGE-Ellipse750_charge
$ ln -s /usr/share/munin/plugins/nutups_   /etc/munin/plugins/nutups_MGE-Ellipse750_freq
$ ln -s /usr/share/munin/plugins/nutups_   /etc/munin/plugins/nutups_MGE-Ellipse750_current
$ ln -s /usr/share/munin/plugins/nut_misc  /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/nut_volts /etc/munin/plugins/
$ echo "[nut*]
user root

[nut_*]
env.upsname MGE-Ellipse750@localhost
" > /etc/munin/plugin-conf.d/nut
```

And if you have a MySQL server running on the machine, that's a good idea to get stats:

```shell-session
$ ln -s /usr/share/munin/plugins/mysql_threads     /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/mysql_slowqueries /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/mysql_queries     /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/mysql_bytes       /etc/munin/plugins/
```

I also use some other Munin plugins coming from [Munin exchange](https://web.archive.org/web/20110727101750/http://exchange.munin-monitoring.org/):

```shell-session
$ wget https://exchange.munin-monitoring.org/plugins/mysql_size_all/version/1/download --output-document=/usr/share/munin/plugins/mysql_size_all
$ ln -s /usr/share/munin/plugins/mysql_size_all /etc/munin/plugins/
```

An here is how I monitor my RAID array:

```shell-session
$ wget https://exchange.munin-monitoring.org/plugins/raid/version/3/download --output-document=/usr/share/munin/plugins/raid
$ ln -s /usr/share/munin/plugins/raid /etc/munin/plugins/
$ echo "[raid]
user root
" > /etc/munin/plugin-conf.d/raid
```

Finally, it's time to monitor nginx itself:

```shell-session
$ ln -s /usr/share/munin/plugins/nginx_status  /etc/munin/plugins/
$ ln -s /usr/share/munin/plugins/nginx_request /etc/munin/plugins/
$ echo "[nginx_*]
env.url http://localhost/nginx_status
" > /etc/munin/plugin-conf.d/nginx
```

These two scripts above have some Perl module dependencies:

```shell-session
$ aptitude install libio-all-lwp-perl
```

If you don't install the libraries above, you'll get these kind of errors in `/var/log/munin/munin-node.log`:

```text
2011/05/03-17:50:10 [2009] Error output from nginx_request:
2011/05/03-17:50:10 [2009]      Can't locate object method "new" via package "LWP::UserAgent" at /etc/munin/plugins/nginx_request line 106.
2011/05/03-17:50:10 [2009] Service 'nginx_request' exited with status 9/0.
2011/05/03-17:50:10 [2009] Error output from nginx_status:
2011/05/03-17:50:10 [2009]      Can't locate object method "new" via package "LWP::UserAgent" at /etc/munin/plugins/nginx_status line 109.
2011/05/03-17:50:10 [2009] Service 'nginx_status' exited with status 2/0.
```

But for this to work, we have to update the `/etc/nginx/sites-enabled/munin` file. Now it looks like this:

```nginx
server {
  server_name munin.example.com;
  root /var/cache/munin/www/;
  # Restrict Munin access
  auth_basic "Restricted";
  auth_basic_user_file /etc/nginx/htpasswd;
  location / {
    index index.html;
    access_log off;
  }
}
server {
 allow 127.0.0.1;
 deny all;
 location /nginx_status {
   stub_status on;
   access_log off;
 }
}
```

Note that I've added a simple HTTP authentication to Munin webpages and restricted access to nginx statistics from the local machine only.

At last, before rebooting Munin and Nginx, make sure all downloaded plugins are executables. This is important and always forgotten:

```shell-session
$ chmod -R 755 /usr/share/munin/plugins/
$ /etc/init.d/nginx restart
$ /etc/init.d/munin-node restart
```
