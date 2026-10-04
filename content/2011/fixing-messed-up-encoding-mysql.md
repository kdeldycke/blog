---
date: '2011-03-14'
title: Fixing messed-up encoding in MySQL
category: English
tags: Character encoding, Databases, e107, Latin-1, MySQL, SQL, PHP, sed, SQL, unicode, UTF-8, Web, Regular expression
---

Currently working on my [e107 Importer plugin](https://wordpress.org/extend/plugins/e107-importer/), I was confronted today with badly-encoded data coming from my databases.

e107 migrated to full UTF-8 [years ago](https://e107.org/comment.php?comment.news.735), but I must have messed the upgrade process at the time. That was my conclusion when I took a close look to my tables: all of them seems to be set to Latin-1 but contain UTF-8 data. Here are screenshots from [SQLBuddy](https://web.archive.org/web/20110226231940/http://sqlbuddy.com/) (a great light-weight MySQL manager) showing just that:

![phpMyAdmin table overview of the e107 database, every table listed with a latin1 charset](e107-latin1-encoded-mysql-tables.png)

![Browsing the forum thread table, the French accents mangled into mojibake such as A-circumflex and Atilde sequences where the accented letters should be](utf8-encoded-data-in-latin1-tables.png)

To fix this, I first tried to use the following command I [found on the web](https://www.commandlinefu.com/commands/view/1575/convert-all-mysql-tables-and-fields-to-utf8):

```shell-session
$ mysql --database=e107db -B -N -e "SHOW TABLES"  | awk '{print "ALTER TABLE", $1, "CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;"}' | mysql --database=e107db
```

But this doesn't work, as it not only change the encoding of the table, but also transcode the data inside the table.

Let's try something else. First, we'll export the database to a dump file, of which the encoding is forced to Latin-1:

```shell-session
$ mysqldump -a -c -e --no-create-db --add-drop-table --default-character-set=latin1 --databases 'e107db' > ./e107-data.sql
```

Now the trick is to change the `CHARSET` parameter of all `CREATE TABLE` directives to UTF-8:

```shell-session
$ sed -i 's/CHARSET=latin1/CHARSET=utf8/g' ./e107-data.sql
```

We'll also change the `NAMES` directive to force MySQL to handle imported data as UTF-8:

```shell-session
$ sed -i 's/SET NAMES latin1/SET NAMES utf8/g' ./e107-data.sql
```

Then we're free to import the result in a new UTF-8 database:

```shell-session
$ sed -i 's/USE `e107db`;/#USE `e107db`;/g' ./e107-data.sql
$ mysql --execute="CREATE DATABASE e107db_new CHARACTER SET=utf8"
$ mysql --database=e107db_new < ./e107-data.sql
```

And now, accentuated characters appears as they should in our database, meaning we've fixed all the mess! :)

![The same table overview after conversion, every table now showing utf8 as its charset](e107-utf8-encoded-mysql-tables.png)

![The same forum rows after the fix, the French accents rendering properly again in words like activés and problème](fixed-utf8-data-in-tables.png)

PS: I [found another alternative method](https://web.archive.org/web/20110310114711/http://en.gentoo-wiki.com/wiki/Convert_latin1_to_UTF-8_in_MySQL#Alternative_Method) (look at the end of the linked page) which consists of temporarily handling `TEXT` fields as `BLOB`, to have MySQL treat them as binary content (thus skipping character transcoding). Haven't tested this but sounds tricky.
