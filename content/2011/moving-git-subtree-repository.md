---
date: '2011-02-01'
title: Moving a Git sub-tree to its own repository
category: English
tags: code, Git, GitHub, Regular expression
---

Coming from Subversion (and with [Plone collective repository](https://web.archive.org/web/20070826171223/http://dev.plone.org/collective/browser/) structure in mind), I've [recently moved all my tiny software projects]({filename}/2010/git-commit-history-reconstruction.md) in a big standalone Git repository (named `kev-code`). Now that I figured out that GitHub allows you to create unlimited amount of repositories, as long as they are open-source public projects, it make sense to emancipate some of my projects to their own repository. How do I move a sub-tree to its own repository? That's what I talk about in this article.

First, there is an automated way of performing this task with [git-subtree](https://github.com/apenwarr/git-subtree). You should try it first. For some reasons I didn't investigate, git-subtree didn't worked for me. So I'll explain now how I did it by hand.

The idea is to revisit the history of my bloated Git repository and massively delete everything that is not related to the sub-folder I'm looking to export. In this case, I try to make a dedicated repository for my [e107 importer for WordPress](https://wordpress.org/extend/plugins/e107-importer/).

Let's start by getting a local copy of my source repository:

```shell-session
$ git clone git@github.com:kdeldycke/kev-code.git
$ cd scripts
```

Then I'll use the `filter-branch` action with a combination of `find` and `rm` to remove everything except the source code of my plugin:

```shell-session
$ git filter-branch --prune-empty --tree-filter 'find ./ -maxdepth 1 -not -path "./e107*" -and -not -path "./wordpress-e107*" -and -not -path "./.git" -and -not -path "./" -print -exec rm -rf "{}" \;' -- --all
```

Instead of the command above, I could have use the `--subdirectory-filter` option ([as suggested by _jamessan_ on Stack Overflow](https://stackoverflow.com/questions/1662753/export-subtree-in-git-with-history/1662787#1662787)):

```shell-session
$ git filter-branch --prune-empty --subdirectory-filter e107-importer -- --all
```

But this doesn't work in my case as my e107 Importer plugin didn't started its life straight in a dedicated folder. So this command squash some of the history I want to preserve.

At this point I'm left with this following history:

![Commit history of the extracted importer, tagged from e107-importer-0.1 in 2006 through 0.9, with one foreign commit for the Drupal 5.0 release](git-subtree-cleanup-results.png)

This looks pretty good, as all the history of my plugin is kept in order. But tags unrelated to my plugin are still there. Let's remove them:

```shell-session
$ git tag -d coolkevmen-0.3 cool-blue-0.1 sapphire-0.1 sapphire-0.2 sapphire-0.3 sapphire-0.4
```

Now there is some commits polluting my history. These are left-overs of `git-modules` additions. I [tried to removed them](https://stackoverflow.com/questions/1260748/how-do-i-remove-a-git-submodule/1260982#1260982), but it didn't worked. Also left in the history are unwanted merges and empty commits [from an old CVS import]({filename}/2010/how-to-fork-cvs-project-git.md). To clean this up, I started an interactive rebase:

```shell-session
$ git rebase --interactive init
```

There, using my text editor, I deleted the entries corresponding to these unrelated commits (namely `c21a840`, `0dc1d76`, `37473a8` and `c6f9f64`), and hoped Git will be smart enough to reconstruct a clean history:

![Interactive rebase in the editor, every commit prefixed with pick above the usual list of rebase commands](git-interactive-rebase.png)

Luckily, it worked for me. If Git complain about such abuse, you may ignore warnings and force it to continue:

```shell-session
$ git rebase --continue
```

Now that we only have a clean sub-tree, let's create a dedicated local Git repository to receive our branch:

```shell-session
$ cd ..
$ mkdir e107-importer
$ cd e107-importer
$ git init
```

Add a temporary origin hooked on our source repository:

```shell-session
$ git remote add origin ../kev-code
```

And import the master branch we carefully crafted (including tags):

```shell-session
$ git pull --tags origin master
```

Now we can create on GitHub the new repository that will receive our exported project:

![GitHub's create-a-new-repository form filled in for e107-importer, described as a WordPress plugin to import from a legacy e107 CMS, set to public](github-new-repository-form.png)

It's time to push our changes. Let's replace our temporary origin to the new GitHub repository we just created:

```shell-session
$ git remote rm origin
$ git remote add origin git@github.com:kdeldycke/e107-importer.git
$ git push origin master --force --tags
```

So now we have a copy of the sub-tree of my plugin into its own repository. That's great, but there is still some stuff to clean-up.

First, we will rewrite the repository to look as if the `./e107-importer` sub-folder had been its project root since the beginning:

```shell-session
$ git filter-branch --tree-filter 'test -d ./e107-importer && mv ./e107-importer/* ./ || echo "No folder found"' -- --all
```

Then, I've altered some commit messages to fix inconsistencies due to sub-folder removal:

```shell-session
$ git filter-branch --msg-filter 'sed "s/Move the script to a dedicated folder/Rename script/g"' -- --all
```

Finally, at the bottom of the history, I still have my initial commit (a personal habit of mine when I [initialize my Git repositories]({filename}/2010/initialize-git-repositories.md)). But its date was updated by the first `filter-branch` call. Let's set its date back to epoch:

```shell-session
$ git filter-branch --force --env-filter \
    'if [ $GIT_COMMIT = a2a5c05aed893fdd10250b724eb6a54bc6e7f122 ]
        then
            export GIT_AUTHOR_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
            export GIT_COMMITTER_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
    fi' -- --all
```

We can now send our latest changes to the remote GitHub repository by forcing a push:

```shell-session
$ git push --force
```

Last thing we have to do, is to remove the plugin code from the fat source repository (I don't like duplicates). But that's another story for another article...
