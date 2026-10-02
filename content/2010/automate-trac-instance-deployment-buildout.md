---
date: '2010-12-01'
title: Automate Trac instance deployment with Buildout
category: English
tags: buildout, htdigest, md5, Python, Red Hat, sasl, Subversion, trac, yum, Mercurial, Regular expression
---

Recently, I started to contribute to [pbp.recipe.trac](https://pypi.python.org/pypi/pbp.recipe.trac), a [Buildout](https://www.buildout.org) recipe aimed to simplify the management and configuration of [Trac](https://trac.edgewall.org) instances.

I've taken interest in [this piece of code](https://bitbucket.org/tarek/atomisator/src/tip/packages/pbp.recipe.trac/) the day I realized the Trac instance we used at work was still running on the old 0.10.x series. Even if we spend the majority of our time there, nobody has taken care of our little Trac: it was not updated for 3 years. If you add to this a sudden need for multi-repository support (as our team is adopting other internal projects), you have enough incentives to upgrade our Trac and automate its maintenance.

So here is how I migrated our legacy Trac 0.10 instance to a brand new 0.12 thanks to Buildout and pbp.recipe.trac.

First, let's install all system dependencies using your distribution package management tool. My target server is running an [RHEL](https://www.redhat.com/rhel/) 5.4, so I'll invoke [Yum](https://fedoraproject.org/wiki/Tools/yum):

```shell-session
$ sudo yum install subversion subversion-python sqlite-devel cyrus-sasl-lib cyrus-sasl-md5 mercurial
```

On Debian/Ubuntu, equivalent packages should be installed with `apt-get`:

```shell-session
$ sudo apt-get install subversion python-subversion libsqlite-dev cyrus-sasl-lib cyrus-sasl-md5 mercurial
```

Now we create an empty structure that will host our Trac instance:

```shell-session
$ mkdir ~/trac-home
$ cd ~/trac-home
$ touch ./buildout.cfg
```

It's time to edit the file at the core of the process: `buildout.cfg`. Here is my version:

```ini
[buildout]
extensions = buildout.bootstrap
parts = my-trac
deploy-server = trac.example.net

[my-trac]
recipe = pbp.recipe.trac
project-name = My Trac instance
project-description = This is my stand-alone Trac instance hosting my development activities.
project-url = http://${buildout:deploy-server}:8000/my-trac
repos = my-repo-1 | svn | ${buildout:directory}/repos/my-repo-1 | svn://${buildout:deploy-server}:3690/my-repo-1
        my-repo-2 | svn | ${buildout:directory}/repos/my-repo-2 | svn://${buildout:deploy-server}:3690/my-repo-2
        my-repo-3 | svn | ${buildout:directory}/repos/my-repo-3 | svn://${buildout:deploy-server}:3690/my-repo-3
default-repo = my-repo-1
force-instance-upgrade = True
force-repos-resync = True
wiki-doc-upgrade = True
stats-plugin = enabled
permissions = anonymous | STATS_VIEW
header-logo = ${buildout:directory}/my_trac_logo.png
smtp-enabled = true
smtp-server = localhost
smtp-port = 25
smtp-from = trac@example.net
smtp-replyto = no-reply@example.net
smtp-always-cc = kevin@example.net bob@example.net
additional-menu-items = Buildbot | http://${buildout:deploy-server}:9080/console
trac-ini-additional = attachment   | max_size               | 26214400
                      browser      | downloadable_paths     | /*/trunk, /*/branches/*, /*/tags/*
                      notification | always_notify_owner    | true
                      notification | always_notify_reporter | true
                      timeline     | ticket_show_details    | true
                      wiki         | ignore_missing_pages   | true
                      svn          | branches               | /*/trunk, /*/branches/*
                      svn          | tags                   | /*/tags/*
```

I now encourage you to use my `buildout.cfg` above as a template and customize it to your needs. Please read [pbp.recipe.trac documentation](https://pypi.python.org/pypi/pbp.recipe.trac#detailed-documentation) carefully to set the recipe options to values you like.

Before going further, we need a `bootstrap.py` script. This script will take care of all stuff required by a bare Python interpreter to handle a Buildout project from scratch. Let's download the latest version:

```shell-session
$ wget https://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py
```

Now we can initialize our Buildout environment. The `--distribute` option here is necessary to get [something more modern](https://pypi.python.org/pypi/distribute#about-the-fork) than the [abandoned `setuptools`](https://pypi.python.org/pypi/setuptools):

```shell-session
$ python ./bootstrap.py --distribute
```

And then we can ask Buildout to construct our the instance:

```shell-session
$ ./bin/buildout
```

Now that we have an empty Trac 0.12 instance, we will migrate there our legacy Subversion repositories:

```shell-session
$ svnadmin create ./repos/my-repo-1
$ svnadmin create ./repos/my-repo-2
$ svnadmin create ./repos/my-repo-3
$ ssh -C root@legacy.example.net "svnadmin dump /software/svn/repo1" | svnadmin load ./repos/my-repo-1
$ ssh -C root@legacy.example.net "svnadmin dump /software/svn/repo2" | svnadmin load ./repos/my-repo-2
$ svnadmin load ./repos/my-repo-3 < ~/svn_repo3_20100612.dmp
```

Note that in this case my first two subversion repositories are still running on my legacy server, and I already have a local dump of the third.

Let's copy the data from our legacy Trac instance. By studying the differences between a default Trac instance and the legacy one I was working on, I came to the conclusion that I only needed to move attachments and the main database. Of course this is my personal case and your's may be a little bit different:

```shell-session
$ scp -rC root@legacy.example.net:/software/trac/project/attachments ./parts/my-trac/
$ scp -rC root@legacy.example.net:/software/trac/project/db/trac.db  ./parts/my-trac/db/
```

We need to call Buildout a second time to update our the project with all the data we've just migrated:

```shell-session
$ ./bin/buildout
```

Now we'll activate and configure SASL-based authentication in all Subversion repositories:

```shell-session
$ sed -i 's/# use-sasl = true/use-sasl = true/' ./repos/my-repo-1/conf/svnserve.conf
$ sed -i 's/# use-sasl = true/use-sasl = true/' ./repos/my-repo-2/conf/svnserve.conf
$ sed -i 's/# use-sasl = true/use-sasl = true/' ./repos/my-repo-3/conf/svnserve.conf
$ sed -i 's/# realm = My First Repository/realm = svn/' ./repos/my-repo-1/conf/svnserve.conf
$ sed -i 's/# realm = My First Repository/realm = svn/' ./repos/my-repo-2/conf/svnserve.conf
$ sed -i 's/# realm = My First Repository/realm = svn/' ./repos/my-repo-3/conf/svnserve.conf
```

Create a password database with our users:

```shell-session
$ saslpasswd2 -f sasl.db -u svn kevin
$ saslpasswd2 -f sasl.db -u svn bob
$ ...
```

Setup SASL authentication on the system (please change the `sasl.conf` location below according your file structure):

```shell-session
$ touch ./sasl.conf
$ sudo ln -s /home/kevin/trac-home/sasl.conf /etc/sasl2/svn.conf
```

And put the following content in the `sasl.conf` file we just created above (don't forget to update the `sasl.db` location):

```text
pwcheck_method: auxprop
auxprop_plugin: sasldb
sasldb_path: /home/kevin/trac-home/sasl.db
mech_list: ANONYMOUS CRAM-MD5 DIGEST-MD5
```

It's time to create and populate the password file used by Trac, with all the users we created 3 steps above:

```shell-session
$ touch ./htdigest
$ htdigest ./htdigest trac kevin
$ htdigest ./htdigest trac bob
$ ...
```

And now we can start the Subversion server in the background:

```shell-session
$ svnserve --daemon --listen-port 3690 --root ./repos/
```

Last step, we launch [Trac's standalone webserver](https://trac.edgewall.org/wiki/TracStandalone):

```shell-session
$ ./bin/tracd --port 8000 --single-env --auth="*,htdigest,trac" ./parts/my-trac
```

You can now reach Trac from your browser, on the following URL:

```text
http://trac.example.net:8000/my-trac
```

A final test consist in getting some code from Subversion:

```shell-session
$ svn co svn://trac.example.net:3690/my-repo-1
```

From now on, and that's where the fun begins, each time a new Trac version is released on PyPI, I just have to:

1. stop both Trac and Subversion standalone servers,
2. run `./bin/buildout`, and
3. restart both Subversion and Trac servers.

That's enough to upgrade my instance.

Now you can clearly see how it's important to invest time in automation to save on maintenance costs and prevent code rotting... :)
