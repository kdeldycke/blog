---
date: '2011-06-28'
title: Nginx + PHP-FPM + MySQL on a Debian Squeeze server
category: English
tags: Debian, Debian Squeeze, Linux, MySQL, SQL, nginx, PHP, php-fpm, Server, Web
---

This post is not about optimization: it only describe a sure and fast way to get all those 3 components talk to each other. This article will help you bootstrap a minimal setup, something that I wouldn't recommend for a production server without serious tweaking (to get both high performances and security).

First, we'll get all our packages from an up-to-date [DotDeb repository](https://www.dotdeb.org/). If this is not already done, add those repositories to aptitude:

```shell-session
$ echo "deb https://packages.dotdeb.org squeeze all" > /etc/apt/sources.list.d/squeeze-dotdeb.list
$ gpg --keyserver keys.gnupg.net --recv-key 89DF5277
$ gpg -a --export 89DF5277 | apt-key add -
$ aptitude update
```

Now we can install the whole stack:

```shell-session
$ aptitude install nginx
$ aptitude install php5-fpm php5-mysql php5-gd php5-curl
$ aptitude install mysql-server
```

FYI, here is the list of versions I installed:

- Nginx 1.0.2
- PHP 5.3.6
- MySQL 5.1.57

As a way to test that our setup is working, we'll serve a simple PHP file:

```shell-session
$ mkdir -p /var/www/example.com/
$ cd /var/www/example.com/
$ echo "
<?php phpinfo(); ?>
" > ./index.php
$ chown -R www-data:www-data /var/www
```

Now let's create a minimal Nginx configuration file for this site:

```shell-session
$ touch /etc/nginx/sites-available/example.com
```

In this brand new file, put the following directives:

```nginx
server {
  server_name example.com;
  include /etc/nginx/php.conf;
  root /var/www/example.com/;
  location / {
    root /var/www/example.com/;
    access_log on;
  }
}
```

This will only work if you've updated your DNS with an `A` record having `example.com` redirecting to the IP address of your Nginx server.

Now it's time to create the `/etc/nginx/php.conf` file referenced in the Nginx configuration above. This file is where I put the generic setup making the bridge between Nginx and PHP-FPM. Here is what it should contain:

```nginx
index index.php index.html index.htm;

location ~ \.php$ {
  # Zero-day exploit defense.
  # https://forum.nginx.org/read.php?2,88845,page=3
  # Won't work properly (404 error) if the file is not stored on this server, which is entirely possible with php-fpm/php-fcgi.
  # Comment the 'try_files' line out if you set up php-fpm/php-fcgi on another machine.  And then cross your fingers that you won't get hacked.
  try_files $uri =404;

  fastcgi_split_path_info ^(.+\.php)(/.+)$;
  include /etc/nginx/fastcgi_params;

  # As explained in https://kbeezie.com/view/php-self-path-nginx/ some fastcgi_param are missing from fastcgi_params.
  # Keep these parameters for compatibility with old PHP scripts using them.
  fastcgi_param PATH_INFO       $fastcgi_path_info;
  fastcgi_param PATH_TRANSLATED $document_root$fastcgi_path_info;
  fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;

  # Some default config
  fastcgi_connect_timeout        60;
  fastcgi_send_timeout          180;
  fastcgi_read_timeout          180;
  fastcgi_buffer_size          128k;
  fastcgi_buffers            4 256k;
  fastcgi_busy_buffers_size    256k;
  fastcgi_temp_file_write_size 256k;

  fastcgi_intercept_errors    on;
  fastcgi_ignore_client_abort off;

  fastcgi_pass 127.0.0.1:9000;
}
```

Finally you can activate the site configuration and restart the whole stack:

```shell-session
$ ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
$ /etc/init.d/mysql restart
$ /etc/init.d/php5-fpm restart
$ /etc/init.d/nginx restart
```

If everything's OK on your DNS, pointing your browser to `https://example.com` will show you the famous page produced by `phpinfo()`:

![phpinfo header for PHP 5.3.6 from dotdeb, reporting the FPM/FastCGI server API and the list of additional ini files loaded from the conf.d directory](phpinfo-536.png)

Note that MySQL doesn't need any special attention to make it work out of the box. But again, if you plan to use it in production, its configuration needs special care, as for Nginx and PHP.
