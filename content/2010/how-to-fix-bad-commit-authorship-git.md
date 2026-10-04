---
date: '2010-05-05'
title: How-to fix bad commit authorship in Git
category: English
tags: commit, DVCS, Git, GitHub, history
---

Several months ago I committed some code in my GitHub repository, but I did it from a temporary system. If I registered my authentication keys correctly to commit stuff, I forgot to create a minimal `~/.gitconfig` file with the right stuff in it.

The result was not good looking, as my usual name and mail address were not attached to the commit:

![Web commit history for kev-code where the top commit is credited to a bare kevin with a blank avatar, while the older ones below carry the proper kdeldycke identity](bad-git-commit-history-authorship.png)

Let's fix this!

First, get a local copy of the remote Git repository:

```shell-session
$ git clone git@github.com:kdeldycke/kev-code.git
```

What was missing in my `~/.gitconfig` file were the following options:

```ini
[user]
name = Kevin Deldycke
email = kevin@deldycke.com
```

These values can be set with Git command line with the following syntax:

```text
--author 'user.name <user.email>'
```

The commit I want to change is the latest in history, so I'll use the `--amend` directive to make my changes. Putting all things together, our final command becomes:

```shell-session
$ git commit --amend --author 'Kevin Deldycke <kevin@deldycke.com>'
```

After this, here is how the local branches looks like in [gitg](https://web.archive.org/web/20100219234841/http://trac.novowork.com/gitg/):

![gitg after the amend, master pointing at a commit authored by Kevin Deldycke while origin/HEAD and origin/master still sit on the identical commit credited to kevin](amended-git-commit-in-gitg.png)

Using the `git log -n1` command, we can compare the old commit:

```text
commit 81a26f03901918ed4a954d964b2659187f1cc988
Author: kevin <kevin@laptop-kev.(none)>
Date:   Mon Mar 8 22:49:43 2010 +0100

    Update old shop logo with the brand new one
```

with the new one:

```text
commit adf4620f3d8a89746dd643dcefc3f900f0f69878
Author: Kevin Deldycke <kevin@deldycke.com>
Date:   Mon Mar 8 22:49:43 2010 +0100

    Update old shop logo with the brand new one
```

Notice the fixed authorship. The commit ID was also updated as it's just a hash depending on commit metadata.

Now we can push our changes back to the remote repository:

```shell-session
$ git push origin
```

But this doesn't work and throw the following error:

```text
To git@github.com:kdeldycke/kev-code.git
 ! [rejected]        master -> master (non-fast forward)
error: failed to push some refs to 'git@github.com:kdeldycke/kev-code.git'
```

This is Git protection mechanism in action. Modifying already-published commits like this is [a bad idea](https://stackoverflow.com/questions/253055/how-do-i-push-amended-commit-to-the-remote-git-repo). It can break updates of other developers' repository (if they already have pulled the commit we're trying to change).

In our case we will force the remote repository to take our changes:

```shell-session
$ git push origin +master:master
```

As I told you before this is bad, but nobody really cares: I'm the only person working on this repository! ;)

Finally, you can contemplate the result on GitHub, a clean and tidy commit history:

![The same web history once fixed, every commit including the top one now attributed to kdeldycke](fixed-git-commit-history-authorship.png)
