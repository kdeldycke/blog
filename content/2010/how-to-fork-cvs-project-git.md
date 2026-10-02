---
date: '2010-02-23'
title: How-to fork a CVS project with Git
category: English
tags: CVS, Drupal, Fork, Git, GitHub, Theme
---

This week I've decided to put
[my work on Cool Cavemen's concert videos]({filename}/2010/cool-cavemen-live-gayant-expo-part-ii.md)
aside, and work instead on refreshing
[our online store](https://coolcavemen.bandcamp.com). After all,
[fans are requesting this](https://www.youtube.com/watch?v=qE-bis-wYxs#show_link_8i9W6PA9rEcKAmnYaXfANlo9U1TASUD9jXw7PtUS3n0),
so I can't escape my duty...

The theme the store is based on is [Drupify](https://drupal.org/project/drupify),
an adaptation of the
[RokWebify Joomla theme](https://www.rockettheme.com/joomla-downloads/folder/115-rokwebify).
All these themes are licensed under the GPL, so I have to share all my
modifications with the community. This is a great opportunity to seriously
experiment with [Git](https://git-scm.com) (at last!).

Here is my plan:

1. Make an exact copy of Drupify's code base in my GitHub repository.
2. Hack it in this playground.
3. ???
4. [Profit!](https://knowyourmeme.com/memes/profit) :D

Problem:
[Drupify lives in a CVS repository](https://drupalcode.org/viewvc/drupal/contributions/themes/drupify/).

Solution: Git features a [`cvsimport`](https://kernel.org/pub/software/scm/git-core/docs/git-cvsimport.html)
command.

Before going further, we need to install
[`cvsps`](https://web-beta.archive.org/web/20160125062146/https://www.cobite.com:80/cvsps/). For [MacPorts](https://www.macports.org)
users, this is as simple as:

```shell-session
$ sudo port install cvsps
Password:
--->  Computing dependencies for cvsps
--->  Fetching cvsps
--->  Attempting to fetch cvsps-2.1.tar.gz from https://arn.se.distfiles.macports.org/cvsps
--->  Attempting to fetch cvsps-2.1.tar.gz from https://distfiles.macports.org/cvsps
--->  Verifying checksum(s) for cvsps
--->  Extracting cvsps
--->  Applying patches to cvsps
--->  Configuring cvsps
--->  Building cvsps
--->  Staging cvsps into destroot
--->  Installing cvsps @2.1_1
--->  Activating cvsps @2.1_1
--->  Cleaning cvsps
```

Then we create a temporary copy of Drupify's CVS repository:

```shell-session
$ git cvsimport -a -k -d:pserver:anonymous:anonymous@cvs.drupal.org:/cvs/drupal-contrib -C drupify-copy contributions/themes/drupify
Initialized empty Git repository in /Users/kevin/drupify-copy/.git/
parse error on user@server in pserver
cvs rlog: Logging contributions/themes/drupify
cvs rlog: Logging contributions/themes/drupify/css
cvs rlog: Logging contributions/themes/drupify/images
```

The new Git repository automatically created is named `drupify-copy`. Here is
how it looks like in [GitX](https://gitx.frim.nl) (notice tags and branches):

![GitX showing the 17 commits imported from CVS, all by the upstream author, with the DRUPAL-6--1 and DRUPAL-5 tags marking the branch points](git-cvs-import-in-gitx.png)

To keep things clean and tidy, I want to relocate all the content of this
repository to a `drupify-fork` folder.
[Inspired by Pedro Melo](https://www.simplicidade.org/notes/archives/2009/04/merging_two_unr.html),
we'll use the
[`git filter-branch`](https://www.kernel.org/pub/software/scm/git/docs/git-filter-branch.html)
to do this job:

```shell-session
$ cd drupify-copy
$ git filter-branch -f --prune-empty --tree-filter '
  mkdir -p /tmp/drupify-fork;
  mv $(ls -A) /tmp/drupify-fork;
  mv /tmp/drupify-fork drupify-fork
' -- --all
Rewrite a9319cebb234c46cc8e0ada95ffb2cd81b87993c (17/17)
Ref 'refs/heads/DRUPAL-5' was rewritten
Ref 'refs/heads/DRUPAL-6--1' was rewritten
Ref 'refs/heads/master' was rewritten
Ref 'refs/heads/origin' was rewritten
Ref 'refs/tags/DRUPAL-6--1-0' was rewritten
```

The command we just used alter all the commits, in a way that let Drupify act as
if it was located, since the beginning of its history, in the `drupify-fork`
sub-directory.

By default, `filter-branch` creates a backup of the tree using references
prefixed by `refs/original/`:

```shell-session
$ git show-ref
4c33470f0f59bcfe7d0d88ee64945bb5625d6d02 refs/heads/DRUPAL-5
8930672eaf97eefa8f9d4ed9f5144f466a97728f refs/heads/DRUPAL-6--1
e5907fac0160febbd91f0cda73633b3e6eafa2a9 refs/heads/master
e5907fac0160febbd91f0cda73633b3e6eafa2a9 refs/heads/origin
af9786625a280930b532541722806739e221ebda refs/original/refs/heads/DRUPAL-5
a9319cebb234c46cc8e0ada95ffb2cd81b87993c refs/original/refs/heads/DRUPAL-6--1
328f3440e202ed72253974dbbbd45f39db23ea4a refs/original/refs/heads/master
328f3440e202ed72253974dbbbd45f39db23ea4a refs/original/refs/heads/origin
957bb22704bc8188c0421b68cbb2f52a3fdcdef6 refs/original/refs/tags/DRUPAL-6--1-0
ee44c42250a2552c1dbef2f7165d65179e1d19c6 refs/tags/DRUPAL-6--1-0
```

We're not the only ones to not see through this mess. GitX seems to be confused
too:

![The same repository after the branch filter, GitX now listing 34 commits because every one appears twice, once under its original refs/original ref](gitx-confused-by-git-branch-filter-backups.png)

But
[according Jakub Narębski on the Git mailing-list](https://n2.nabble.com/Removing-some-files-from-history-tp1344670p1344919.html),
we can safely removes Git's backups:

```shell-session
$ rm -Rf .git/refs/original
$ git gc --prune=now
Counting objects: 106, done.
Delta compression using up to 2 threads.
Compressing objects: 100% (88/88), done.
Writing objects: 100% (106/106), done.
Total 106 (delta 40), reused 0 (delta 0)
```

After the cleaning, references are back to normal:

```shell-session
$ git show-ref
4c33470f0f59bcfe7d0d88ee64945bb5625d6d02 refs/heads/DRUPAL-5
8930672eaf97eefa8f9d4ed9f5144f466a97728f refs/heads/DRUPAL-6--1
e5907fac0160febbd91f0cda73633b3e6eafa2a9 refs/heads/master
e5907fac0160febbd91f0cda73633b3e6eafa2a9 refs/heads/origin
ee44c42250a2552c1dbef2f7165d65179e1d19c6 refs/tags/DRUPAL-6--1-0
```

We can then fire up GitX to get the ultimate proof that the relocation
operation didn't change anything, but the base folder (and SHA hashes):

![Commit detail after the folder move, with a red hand-drawn arrow and circle pointing at the rewritten path drupify-fork/page.tpl.php](history-tree-in-gitx-after-folder-change.png)

It's time to import all this code in our main repository. First, get a local
copy of our public [GitHub](https://github.com/) code base:

```shell-session
$ cd
$ git clone git@github.com:kdeldycke/kev-code.git
Initialized empty Git repository in /Users/kevin/kev-code/.git/
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 5 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (5/5), done.
```

Now let's include our temporary `drupify-copy` as a tracked remote repository:

```shell-session
$ cd kev-code/
$ git remote add drupify ../drupify-copy
$ git fetch drupify
warning: no common commits
remote: Counting objects: 106, done.
remote: Compressing objects: 100% (48/48), done.
remote: Total 106 (delta 40), reused 106 (delta 40)
Receiving objects: 100% (106/106), 61.62 KiB, done.
Resolving deltas: 100% (40/40), done.
From ../drupify-copy
 * [new branch]      DRUPAL-5   -> drupify/DRUPAL-5
 * [new branch]      DRUPAL-6--1 -> drupify/DRUPAL-6--1
 * [new branch]      master     -> drupify/master
 * [new branch]      origin     -> drupify/origin
From ../drupify-copy
 * [new tag]         DRUPAL-6--1-0 -> DRUPAL-6--1-0
```

As you can see, all the little particularities of the remote repository are well
tracked (HEAD, branches and tags are there):

```shell-session
$ git remote show drupify
* remote drupify
  Fetch URL: ../drupify-copy
  Push  URL: ../drupify-copy
  HEAD branch (remote HEAD is ambiguous, may be one of the following):
    master
    origin
  Remote branches:
    DRUPAL-5    tracked
    DRUPAL-6--1 tracked
    master      tracked
    origin      tracked
  Local ref configured for 'git push':
    master pushes to master (local out of date)
```

Another way to check this is to list all tracked remote branches:

```shell-session
$ git branch -r
  drupify/DRUPAL-5
  drupify/DRUPAL-6--1
  drupify/master
  drupify/origin
  origin/HEAD -> origin/master
```

It's time to merge all our tracked remote code (from `drupify-copy`) in our
local repository (`kev-code`). The branch I'm interested in is `DRUPAL-6--1`, as
it holds the latest Drupify code for Drupal 6.x:

```shell-session
$ git merge drupify/DRUPAL-6--1
Merge made by recursive.
 drupify-fork/README.txt               |   16 +
 drupify-fork/css/editor_content.css   |    7 +
 drupify-fork/css/index.html           |    1 +
 drupify-fork/css/template_ie.css      |   55 +++
 drupify-fork/drupify.info             |   11 +
 drupify-fork/images/arrow.png         |  Bin 0 -> 278 bytes
 drupify-fork/images/bg.png            |  Bin 0 -> 315 bytes
 drupify-fork/images/bottom-bg.png     |  Bin 0 -> 583 bytes
 drupify-fork/images/col-divider.png   |  Bin 0 -> 200 bytes
 drupify-fork/images/emailButton.png   |  Bin 0 -> 454 bytes
 drupify-fork/images/favicon.ico       |  Bin 0 -> 1150 bytes
 drupify-fork/images/footer-bg.png     |  Bin 0 -> 544 bytes
 drupify-fork/images/footer-l.png      |  Bin 0 -> 593 bytes
 drupify-fork/images/footer-r.png      |  Bin 0 -> 592 bytes
 drupify-fork/images/footer-rocket.png |  Bin 0 -> 3391 bytes
 drupify-fork/images/header-bg.png     |  Bin 0 -> 638 bytes
 drupify-fork/images/header-l.png      |  Bin 0 -> 430 bytes
 drupify-fork/images/header-r.png      |  Bin 0 -> 444 bytes
 drupify-fork/images/indent1.png       |  Bin 0 -> 214 bytes
 drupify-fork/images/indent2.png       |  Bin 0 -> 214 bytes
 drupify-fork/images/indent3.png       |  Bin 0 -> 214 bytes
 drupify-fork/images/indent4.png       |  Bin 0 -> 214 bytes
 drupify-fork/images/index.html        |    1 +
 drupify-fork/images/menu-bg.png       |  Bin 0 -> 343 bytes
 drupify-fork/images/menu-bullet.png   |  Bin 0 -> 933 bytes
 drupify-fork/images/menu-divider.png  |  Bin 0 -> 200 bytes
 drupify-fork/images/pdf_button.png    |  Bin 0 -> 482 bytes
 drupify-fork/images/printButton.png   |  Bin 0 -> 467 bytes
 drupify-fork/logo.png                 |  Bin 0 -> 27829 bytes
 drupify-fork/node.tpl.php             |   31 ++
 drupify-fork/page.tpl.php             |  173 ++++++++++
 drupify-fork/screenshot.png           |  Bin 0 -> 11289 bytes
 drupify-fork/style.css                |  593 +++++++++++++++++++++++++++++++++
 drupify-fork/template.php             |   10 +
 34 files changed, 898 insertions(+), 0 deletions(-)
 create mode 100644 drupify-fork/README.txt
 create mode 100644 drupify-fork/css/editor_content.css
 create mode 100644 drupify-fork/css/index.html
 create mode 100644 drupify-fork/css/template_ie.css
 create mode 100644 drupify-fork/drupify.info
 create mode 100644 drupify-fork/images/arrow.png
 create mode 100644 drupify-fork/images/bg.png
 create mode 100644 drupify-fork/images/bottom-bg.png
 create mode 100644 drupify-fork/images/col-divider.png
 create mode 100644 drupify-fork/images/emailButton.png
 create mode 100644 drupify-fork/images/favicon.ico
 create mode 100644 drupify-fork/images/footer-bg.png
 create mode 100644 drupify-fork/images/footer-l.png
 create mode 100644 drupify-fork/images/footer-r.png
 create mode 100644 drupify-fork/images/footer-rocket.png
 create mode 100644 drupify-fork/images/header-bg.png
 create mode 100644 drupify-fork/images/header-l.png
 create mode 100644 drupify-fork/images/header-r.png
 create mode 100644 drupify-fork/images/indent1.png
 create mode 100644 drupify-fork/images/indent2.png
 create mode 100644 drupify-fork/images/indent3.png
 create mode 100644 drupify-fork/images/indent4.png
 create mode 100644 drupify-fork/images/index.html
 create mode 100644 drupify-fork/images/menu-bg.png
 create mode 100644 drupify-fork/images/menu-bullet.png
 create mode 100644 drupify-fork/images/menu-divider.png
 create mode 100644 drupify-fork/images/pdf_button.png
 create mode 100644 drupify-fork/images/printButton.png
 create mode 100644 drupify-fork/logo.png
 create mode 100644 drupify-fork/node.tpl.php
 create mode 100644 drupify-fork/page.tpl.php
 create mode 100644 drupify-fork/screenshot.png
 create mode 100644 drupify-fork/style.css
 create mode 100644 drupify-fork/template.php
```

We can remove the attached `drupify` repository and its local `drupify-copy`
source:

```shell-session
$ git remote rm drupify
$ cd ..
$ rm -rf ./drupify-copy
```

At this stage, here is what our repository looks like:

![The kev-code repository after the merge, the imported CVS history threaded underneath my own initial commit and README](cvs-fork-merged-to-git-with-full-history.png)

To keep all the details that were created by `git cvsimport`, we can add by hand
all the missing refs. The only difference with the original ones is that I
unified the namespace with a `drupify/` prefix:

```shell-session
$ git update-ref refs/heads/drupify/DRUPAL-6--1 8930672
$ git update-ref refs/heads/drupify/master e5907fa
$ git update-ref refs/heads/drupify/origin e5907fa
$ git tag drupify/DRUPAL-6--1-0 DRUPAL-6--1-0
$ git tag -d DRUPAL-6--1-0
Deleted tag 'DRUPAL-6--1-0'
```

And finally, we can contemplate our work:

![Final imported history with the upstream refs preserved as drupify/master, drupify/origin and the two DRUPAL tags alongside my own master](final-cvs-import-and-merge-with-refs.png)

This let me work cleanly on the CVS branch I wanted to in the first place. But
there is one missing thing: all other tracked remote branches were not merged
properly. I really wanted to import all of them (especially the `DRUPAL-5`
branch), to keep a perfect copy of the original CSV tree. But I failed to find a
way. Does anyone have a clue?
