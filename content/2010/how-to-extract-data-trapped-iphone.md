---
date: '2010-09-16'
title: How-to extract data trapped into an iPhone
category: English
tags: Android, Apple, Backup, CSV, iPhone, iTunes, Apple, macOS, Smartphones, SQLite, SQL, VLC, Mac OS X 10.6 Snow Leopard
---

After 2 years using an iPhone 3G, it's time for me to [switch to
the Android world](https://twitter.com/kdeldycke/status/24219289221). [My Apple
era is over](https://twitter.com/kdeldycke/status/22007247873), I need a
plateform that is more Linux and open-source friendly.

Before erasing and [selling my iPhone
](https://twitter.com/kdeldycke/status/24687160120), I want to backup and
extract all the data I produced with it and that is still trapped inside. This
mean photos, SMSs, voice messages, safari bookmarks, etc...

There is a nice OS X app simply called [iPhone Backup Extractor
](https://supercrazyawesome.com) which let you get these data. Instead of
getting data directly from the iPhone, it reads its backups made by iTunes.

So first thing you have to do is to backup your phone using iTunes:

![iTunes summary page for a 14.46 GB iPhone on software 4.1, the progress bar at the top reading backing up as step 1 of 4, serial and phone number scribbled out](iphone-itunes-sync.png)

Then you can download and run the iPhone Backup Extractor app:

![iPhone Backup Extractor freshly launched with an empty application list, its Read Backups and Extract buttons at the bottom, over a Finder window showing the downloaded app](iphone-backup-extractor.png)

Here you just have to click the _Read Backups_ button to get a list of all
backups available on your machine. Then choose your latest backup:

![Backup picker listing two snapshots of the same iPhone, one from September 15 and one from August 30, 2010](list-of-iphone-backups.png)

You'll get a list of all installed applications on your iPhone. As we are
interested in "core" iPhone apps (SMSs, photos and so on), we'll choose the
"iOS Files" item, then choose a place where to extract:

![Application list from the backup, showing Bloomberg, LinkedIn, Facebook and Flashlight, with the iOS Files entry selected below them](iphone-backup-content.png)

![Destination chooser pointed at the Documents folder, with an Extract Here button](iphone-backup-extraction-destination.png)

Then the extraction itself will take place:

![Small progress bar reporting the extraction of a photo from Media/PhotoData/103APPLE](iphone-backup-extraction.png)

You've just finished the essential part of the process. You now have a nice
folder structure containing all the important information that was trapped in
your phone:

![Finder on the extracted iOS Files folder, holding Library, Media, mobile and SystemConfiguration alongside the keychain backup and two SQLite databases](iphone-backup-extraction-content.png)

Let's browse the file structure that was just created. You can see photos are
available as is, in the `/iOS Files/Media/DCIM/XXXAPPLE/`:

![Finder column view drilling from Media into DCIM and the 103APPLE folder, listing the camera roll as numbered IMG JPEG files](iphone-photo-location.png)

Most of other data are located in the `/iOS Files/Library/` folder. For
example here are voice messages:

![Finder column view of the Library folder, its Voicemail subfolder holding two .amr recordings, two plists and voicemail.db](iphone-voicemessages-location.png)

Again, `.amr` files here are playable as-is, like [VLC
](https://www.videolan.org/vlc/) or [mplayer](https://mplayerhq.hu/).

Most, if not all, other kind of data and metadata are stored in SQLite
databases (`.db` files). The best GUI I found to manipulate with these files
under Mac OS X is [SQLite Database Browser
](https://sourceforge.net/projects/sqlitebrowser/). See how I can easily extract
to a CSV file all metadatas associated with my voice messages:

![SQLite Database Browser open dialog with voicemail.db selected, a 29 KB database document](sqlite-database-browser-opening.png)

![Database structure tab of voicemail.db, listing the voicemail table and its date and remote_uid indexes with their CREATE statements](iphone-voicemail-database-tables.png)

![Browse data tab showing the two rows of the voicemail table with columns for date, token, sender and duration, the personal fields blurred out](iphone-voicemail-table-content.png)

![File menu open on Export, offering to write the database to an SQL file or the table as a CSV file](sqlite-csv-table-export.png)

Finally, just in case you want to extract iPhones data from another backup than
the default backup, like from a backup of the backup (isn't that clear?),
making a symlink is enough to trick iPhone Backup Extractor:

```shell-session
sh-3.2# pwd
/Users/kevin/Library/Application Support/MobileSync
sh-3.2# mv ./Backup ./Backup-copy
sh-3.2# ln -s "/Volumes/Untitled 1/laptop-kev-osx/mirror/Users/kevin/Library/Application Support/MobileSync/Backup" .
sh-3.2# ls -lah
total 8
drwxr-xr-x   4 kevin  staff   136B Sep 16 21:56 .
drwx------+ 11 kevin  staff   374B Sep 15 19:29 ..
lrwxr-xr-x   1 root   staff    99B Sep 16 21:56 Backup -> /Volumes/Untitled 1/laptop-kev-osx/mirror/Users/kevin/Library/Application Support/MobileSync/Backup
drwxr-xr-x   4 kevin  staff   136B Aug 30 13:20 Backup-copy
sh-3.2#
```

That's how I was able to extract my iPhone data from an old backup, and get
back most of the [data I lost after my last iOS update
](https://twitter.com/kdeldycke/status/22516008513):

![iPhone Backup Extractor listing a single May 6, 2010 backup, reached through the symlinked backup folder](iphone-backup-extractor-from-old-backup.png)
