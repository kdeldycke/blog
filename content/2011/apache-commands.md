---
date: '2011-01-11'
title: Apache commands
category: English
tags: Apache, CLI, Git, HTTP, nedstat, Server, Subversion, Web, WebDAV
---

- Redirects local `/static/repository` folder to external URL:

  ```apache
  Redirect permanent /static/repository https://kevin.deldycke.free.fr/repository
  ```

- Hide Subversion and Git directories content ([source](https://news.ycombinator.com/item?id=839016)):

  ```apache
  RedirectMatch 404 /\.(svn|git)(/|$)
  ```

- Disable serving of PHP files coming from imported third party JavaScript submodules ([context](https://github.com/kdeldycke/cool-cavemen-k2-theme/blob/master/.htaccess)):

  ```apache
  RedirectMatch 404 js-(.*)\.php$
  ```

- Redirect any request to current year sub-directory (I used this for a yearly-updated static web page):

  ```apache
  RewriteEngine on
  RewriteRule !^/2010/ /2010/ [R=301,L]
  ```

- Force Apache to serve Python files as-is instead of being interpreted as CGI scripts:

  ```apache
  RemoveHandler .py
  ```

- Same as above, but for PHP files:

  ```apache
  AddType text/plain .php
  ```

- Here is my template for domain-based virtual host routing:

  ```apache
  # Setup the main website access
  <VirtualHost *:80>
    ServerName example.com
    DocumentRoot /var/www/example
    # Add extra capabilities to let CMS like WordPress manage redirections
    <Directory /var/www/example>
      Options +FollowSymLinks +SymLinksIfOwnerMatch
    </Directory>
  </VirtualHost>
  # Redirect all other access to the website from different domains to the canonical URL
  <VirtualHost *:80>
    ServerName www.example.com
    ServerAlias *.example.com
    ServerAlias example.net *.example.net
    ServerAlias example.org *.example.org
    RedirectMatch permanent (.*) http://example.com$1
  </VirtualHost>
  ```

- Insert dynamic headers in HTTP responses depending on the browser:

  ```apache
  BrowserMatchNoCase ".*MSIE\s[1-6].*" IS_DISGUSTING_BROWSER
  Header add X-advice-of-the-day "Save a kitten: use Firefox!" env=IS_DISGUSTING_BROWSER
  ```

- Prevent WebDAV connexions (thanks Guillaume!):

  ```apache
  <Location />
    <Limit PROPFIND PROPPATCH MKCOL COPY MOVE LOCK UNLOCK PATCH>
      # Leaves GET (and HEAD), POST, PUT, DELETE, CONNECT, OPTIONS and TRACE alone
      Order allow,deny
      Deny from all
    </Limit>
  </Location>
  SetEnvIf Request_Method "OPTIONS" CLIENT_PROBE
  Header set Allow "GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE" env=CLIENT_PROBE
  ```

- At work, we had to engineer a convoluted software architecture for our
  intranet to fit the network security policy of our customer. This had a bad
  side effect of letting the [web statistic
  collector](https://web.archive.org/web/20111008000404/https://www.nedstat.com)
  delete all cookies but its own, thus breaking intranet's authentication. So
  we (thanks Matthieu!) came up with this unmaintainable hack on Apache side to
  hide our intranet's cookies to Nedstat's JavaScript embedded code:

  ```apache
  <LocationMatch "/(.*)">
    LoadModule headers_module modules/mod_headers.so
    RequestHeader edit Cookie "(app_cookie_001=[^;]*(; )*)" ""
    RequestHeader edit Cookie "(app_cookie_002=[^;]*(; )*)" ""
    RequestHeader edit Cookie "(app_cookie_003=[^;]*(; )*)" ""
  </LocationMatch>
  ```

- Kill all apache processes and restart the service:

  ```shell-session
  $ /etc/init.d/apache2 stop ; pkill -9 -u www-data ; /etc/init.d/apache2 restart
  ```

- Restart Apache service if no process found:

  ```shell-session
  $ [ `ps axu | grep -v "grep" | grep --count "www-data"` -le 0 ] && /etc/init.d/apache2 restart
  ```
