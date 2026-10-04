---
date: '2010-05-25'
title: How I initialize my Git repositories
category: English
tags: code, Git, GitHub
---

The first few days I used Git, I messed up my repository. I had to reset and
recreate it from scratch several times. With enough trials and errors, I came up
with an idea of how I should initialize my repositories. Let me explain in this
post why `git init` is not enough to me.

To create a Git repository, nothing else is absolutely necessary than these few
trivial commands:

```shell-session
$ mkdir kev-code
$ cd kev-code/
$ git init
```

But after reading
[some documentation](http://www-cs-students.stanford.edu/~blynn/gitmagic/apa.html#_initial_commit)
and user experiences on the web, it looks like Git has some limitations when
dealing with the root of a repository history. As I plan to heavily manipulate
the commit history (to do some kind of
[code archaeology and history reconstruction]({filename}/2010/git-commit-history-reconstruction.md)),
I need to have the widest time latitude to play with commits.

In this situation, I came to the conclusion that it's a good idea to create an
empty commit at the start of your repository life, and date it to the start of
epoch. In the future, I'll be able to leverage this initial commit as an ordinary
history point from which I can start a branch. Then in this branch I'll be free
to mess up the history, until merging my changes back in the mainline tree.

So, let's create an empty commit:

```shell-session
$ git commit --allow-empty -m 'Initial commit'
```

Then get the commit hash:

```shell-session
$ git log
commit 395290bcdb8ffccfbff89e42cb976077fbd3c1b7
Author: Kevin Deldycke <kevin@deldycke.com>
Date:   Tue Dec 1 15:37:49 2009 +0100

    Initial commit
```

We now change the commit date of our first commit to epoch start:

```shell-session
$ git filter-branch --env-filter '
>     if [ $GIT_COMMIT = 395290bcdb8ffccfbff89e42cb976077fbd3c1b7 ]
>     then
>         export GIT_AUTHOR_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
>         export GIT_COMMITTER_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
>     fi' -- --all
Rewrite 395290bcdb8ffccfbff89e42cb976077fbd3c1b7 (1/1)
Ref 'refs/heads/master' was rewritten
```

And check that the previous operation did what we expected:

```shell-session
$ git log
commit 8fe2934d1552c97246836987f0ea08e10ba749ae
Author: Kevin Deldycke <kevin@deldycke.com>
Date:   Thu Jan 1 00:00:00 1970 +0000

    Initial commit
```

Looks good!

For convenience, we'll now attach a tag to this initial commit. Let's call it
`init`:

```shell-session
$ git tag "init"
```

This will came handy later when we'll need to create a branch from here.

It's time to push all changes to our brand new public repository:

```shell-session
$ git remote add origin git@github.com:kdeldycke/kev-code.git
$ git status
# On branch master
nothing to commit (working directory clean)
$ git push origin master --force

Counting objects: 2, done.
Writing objects: 100% (2/2), 159 bytes, done.
Total 2 (delta 0), reused 0 (delta 0)
To git@github.com:kdeldycke/kev-code.git
 + 86bd2c7...8fe2934 master -> master (forced update)
```

And here is the result on GitHub:

![Web view of a fresh repository holding a single empty initial commit dated 1 January 1970, with no files listed underneath](git-first-commit.png)

Maybe this "first commit" trick is unnecessary. So, if you have a better
understanding of the issue, or can explain me why this is stupid, please tell
me! :)
