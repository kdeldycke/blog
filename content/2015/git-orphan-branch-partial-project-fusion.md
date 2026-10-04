---
date: '2015-12-08'
title: Using Git's orphan branch for partial project fusion
category: English
tags: CLI, Git, GitHub
---

Let's say you have two projects that were living in their own repository for
ages. And all of a sudden it make sense to move a subset of code, and its whole
commit history, from the first to the second.

That's a topic I already addressed. See
for instance my previous articles on [an internal corporate project I
open-sourced]({filename}/2011/how-open-source-an-internal-corporate-project-webping.md),
a [migration from SVN to
Git]({filename}/2011/ftt-migration-subversion-git.md), and
[Git sub-tree
cleaning]({filename}/2011/moving-git-subtree-repository.md).

Should we really keep revisiting the subject again and again? Yes, cause things
have changed! [Since v1.7.2](https://web.archive.org/web/20150627141623/http://git-scm.com/docs/git-checkout/1.7.2), Git
supports orphan branches. And we'll now use them to keep unrelated branches
sharing the same root until their merging point.

We start with the source repository. The code we're about to move is available
in the `develop` branch:

```shell-session
$ git clone https://github.com/kdeldycke/source-project.git
$ cd ./source-project
$ git checkout develop
```

To prevent any bad move, we detach the local copy of the repository from its
remote branches:

```shell-session
$ git remote rm origin
```

Now we can start cleaning the `develop` branch to only keep the subset of code
we'd like to move.

First we remove other branches and all tags:

```shell-session
$ git branch -D master
$ git tag -d `git tag | grep -E '.'`
```

In my case, and after studying the whole commit history, the code lived under
the following past and current locations:

- `./folder1/lib/*`
- `./folder2/subfolder/data-lib/*`
- `./folder3/scripts/*`
- `./script_tools.py`

I then managed to produce a one-liner `find` command satisfying all these path
constraints. Combined with the `filter-branch` action, I was allowed me to
remove all content but these path within the whole commit history:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'find . -type f -not -ipath "*lib*" -and -not -ipath "*script*" -and -not -ipath "./.git*" -and -not -path "." -print -exec rm -rf "{}" \;' -- --all
```

I revisited the new commit log which was way cleaner. But the command above was
too much coarse-grained, so I had to repeat the operation again to get the
exact sub-tree I was looking for:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'find . -type f -iname ".gitignore" -print -exec rm -rf "{}" \;' -- --all
$ git filter-branch --force --prune-empty --tree-filter 'if [ -d ./calibration ]; then rm -rf ./calibration; fi' -- --all
$ git filter-branch --force --prune-empty --tree-filter 'if [ -f ./script_tools.py ]; then mkdir -p ./folder3/scripts; mv ./script_tools.py ./folder3/scripts/; fi' -- --all
```

Now that I have the perfect history for the minimal subset of code I'm
targeting, we can flatten the commit log:

```shell-session
$ git rebase --root
```

Rebasing is not an exact science and you might end-up with empty commits:

```shell-session
(...)
Could not apply 2a4f66a6fa114846bb80c3d488e41a186bce4894...
The previous cherry-pick is now empty, possibly due to conflict resolution.
If you wish to commit it anyway, use:

    git commit --allow-empty

Otherwise, please use 'git reset'
(...)
```

In which case I simply ignore the problem and order the rebasing action to
continue as many times necessary to let the process complete:

```shell-session
$ git rebase --continue
$ git rebase --continue
$ git rebase --continue
```

Finally, we clean-up:

```shell-session
$ git reflog expire --all
$ git gc --aggressive --prune
```

Let's now switch to the repository that will become the new home for our code:

```shell-session
$ cd ..
$ git clone https://github.com/kdeldycke/destination-project.git
$ cd ./destination-project
```

We create a new detached, orphan branch:

```shell-session
$ git symbolic-ref HEAD refs/heads/orphan
$ rm .git/index
$ git clean -fdx
$ git commit -m 'Temporary initial commit for orphan branch.' --allow-empty
```

Then publish that new `orphan` branch upstream:

```shell-session
$ git push --set-upstream origin orphan
```

At this point I encourage you to [check in your
GUI](https://sixohthree.com/1955/git-subtree-merges-orphaned-branches-and-github)
that the said orphan branch is really detached from your usual branches:

![GitLab network view with the orphan branch label sitting on a temporary initial commit, detached above the develop branch and its chain of history](gitlab-network-view-orphan-branch.png)

Time to import the branch we cleaned from the source repository:

```shell-session
$ git checkout orphan
$ git remote add code_import ../source-project
$ git fetch code_import
```

We then replace our `orphan` branch by the code we just imported:

```shell-session
$ git rebase code_import/develop
```

Once everything's at your taste, we can remove the relationship with the source
project and push the newly populated `orphan` branch upstream:

```shell-session
$ git branch -r -D code_import/develop
$ git push --force --set-upstream origin orphan
```
