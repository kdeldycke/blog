---
date: '2011-02-14'
title: 'Pushing Git to Subversion: the case of WordPress plugin repository'
category: English
tags: Git, Hosting, Linux, Subversion, WordPress, Regular expression
---

[Some weeks ago]({filename}/2011/moving-git-subtree-repository.md) I moved my e107 Importer project from a [big fat Git repository](https://github.com/kdeldycke/scripts) to [its own](https://github.com/kdeldycke/e107-importer).

Then I wanted to have my plugin to be available on WordPress.org. In fact, [this list](https://wordpress.org/extend/plugins/) is the tip of WordPress plugin hosting solution. It means that if you want to have your plugin there, you have to push your code in [WordPress' big Subversion repository](https://plugins.trac.wordpress.org/browser). And that's when I realized I had to sync my Git repository to Subversion...

This article details how I managed to push to Subversion all my developments activity taking place in Git.

Before going further: be careful! It's really easy to mess things up. After all, we're trying to push code on a public Subversion repository. We must be certain of what we are doing here. Risks of deleting stuff that are not ours are great.

## The simulation

To prevent any big mistake, we'll test our commands on a local subversion repository.

Let's create one:

```shell-session
$ rm -rf svn-repo
$ svnadmin create ./svn-repo
```

Now we'll launch a local Subversion server with a minimal config:

```shell-session
$ sed -i 's/# password-db = passwd/password-db = passwd/' ./svn-repo/conf/svnserve.conf
$ echo "kevin = kevin" >> ./svn-repo/conf/passwd
$ kill `ps -ef | grep svnserve | awk '{print $2}'`
$ svnserve --daemon --listen-port 3690 --root ./svn-repo
```

To test our server, let's checkout a local working copy from it:

```shell-session
$ rm -rf svn-working-copy
$ svn co svn://localhost:3690 svn-working-copy
$ cd svn-working-copy/
$ svn info
```

To simulate an already active Subversion repository, we'll make a first commit with a structure mimicking [WordPress' plugin repository](https://plugins.trac.wordpress.org):

```shell-session
$ mkdir -p e107-importer/{trunk,branches,tags}
$ svn add *
$ svn commit -m "Create a WordPress-like repository structure" --username kevin
$ svn up
$ svn info
```

Now that we have a place to hack, we can experiment on Git side. We start with a copy of my plugin repository:

```shell-session
$ cd ..
$ rm -rf e107-importer
$ git clone git@github.com:kdeldycke/e107-importer.git
$ cd e107-importer
```

Thanks to [git-svn](https://www.kernel.org/pub/software/scm/git/docs/git-svn.html), we can attach a remote Subversion repository:

```shell-session
$ git svn init --trunk=e107-importer/trunk --branches=e107-importer/branches --tags=e107-importer/tags --username kevin  svn://localhost:3690
```

Get get a copy of Subversion's content:

```shell-session
$ git svn fetch
r1 = d969aa9a11684a1cd2ba0b3eab0a3ee72a62af51 (refs/remotes/trunk)
```

Now we will rebase our whole Git tree to Subversion's trunk:

```shell-session
$ git rebase trunk
```

According gitg, the result of this is 2 parallel trees:

- the first is the untouched original tree;
- the other start on the `trunk` branch and continue with a copy of the original tree, and is the result of the rebase.

But the latter has a problem: [my initial commit]({filename}/2010/initialize-git-repositories.md) and all my tags are squashed. I tried several methods to rebase my whole Git tree onto the local `trunk` branch while keeping these. But I failed.

I resigned myself and passed over this. After all, the initial commit played its role, by taking care of this corner-case.

As for the tags, I just re-added them by hand. I forced their creation, as Git keeps them attached to the original parallel tree:

```shell-session
$ git tag -f "e107-importer-0.1" 728ec8689d13350bbfc1f2d9dc17dda2b8a8fdbf
$ git tag -f "e107-importer-0.2" 8049b92265a41f594e97020bae6f3aa74b6a7fb1
$ git tag -f "e107-importer-0.3" 9505aa0656ba61f39cd6cb91c76c1e7279c68473
$ git tag -f "e107-importer-0.4" 0da2d61239c9a9549d197737518705912fd4982d
$ git tag -f "e107-importer-0.5" 561d35b5d1b4d2c35e13c76a3f2a41689c96e991
$ git tag -f "e107-importer-0.6" c6de1a2bf60cad054c5420eab2f30f190092fb68
$ git tag -f "e107-importer-0.7" 6ad4d4a67e8b84da31565383e5eed6ceb5b7d2b2
$ git tag -f "e107-importer-0.8" 47b8efdc82132027b139a2f214f119cee1e9c06c
$ git tag -f "e107-importer-0.9" a82f5d0814db7cf6ac7a1ac171b30c300e1a91d4
```

Now we are ready to push the code to the remote Subversion repository:

```shell-session
$ git svn dcommit
```

Things seems to have worked, as if you go back to your local copy of the simulated remote SVN, you'll get all your code base and its history:

```shell-session
$ cd ..
$ cd svn-working-copy
$ svn up
$ svn log
```

If commit order is preserved, dates are not, because unlike Git, Subversion only track the commit date, not the author's date. This is sad but expected.

But here I was hoping that Git-svn was smart enough to create tags automatically. They weren't, and my `tags` folder remained empty. That may be due to the nature of tags in Subversion, which are just branches. I don't know. At the end I just decided to create tags by hand on Subversion side:

```shell-session
$ svn copy svn://localhost:3690/e107-importer/trunk@2  svn://localhost:3690/e107-importer/tags/0.1 -m "Tag e107-importer 0.1"
$ svn copy svn://localhost:3690/e107-importer/trunk@4  svn://localhost:3690/e107-importer/tags/0.2 -m "Tag e107-importer 0.2"
$ svn copy svn://localhost:3690/e107-importer/trunk@5  svn://localhost:3690/e107-importer/tags/0.3 -m "Tag e107-importer 0.3"
$ svn copy svn://localhost:3690/e107-importer/trunk@6  svn://localhost:3690/e107-importer/tags/0.4 -m "Tag e107-importer 0.4"
$ svn copy svn://localhost:3690/e107-importer/trunk@8  svn://localhost:3690/e107-importer/tags/0.5 -m "Tag e107-importer 0.5"
$ svn copy svn://localhost:3690/e107-importer/trunk@9  svn://localhost:3690/e107-importer/tags/0.6 -m "Tag e107-importer 0.6"
$ svn copy svn://localhost:3690/e107-importer/trunk@10 svn://localhost:3690/e107-importer/tags/0.7 -m "Tag e107-importer 0.7"
$ svn copy svn://localhost:3690/e107-importer/trunk@11 svn://localhost:3690/e107-importer/tags/0.8 -m "Tag e107-importer 0.8"
$ svn copy svn://localhost:3690/e107-importer/trunk@12 svn://localhost:3690/e107-importer/tags/0.9 -m "Tag e107-importer 0.9"
```

## Real life push to WordPress repository

Now that our commit simulation worked somehow, we can perform them in the real world.

First, initialize a copy of the Git repository:

```shell-session
$ rm -rf e107-importer-git
$ git clone git@github.com:kdeldycke/e107-importer.git e107-importer-git
```

Let's attach Subversion to Git:

```shell-session
$ cd e107-importer-git
$ git svn init --trunk=trunk --branches=branches --tags=tags https://plugins.svn.wordpress.org/e107-importer
```

Here you might want to do a `git svn fetch` as we did before. But this will take a while. Especially on WordPress plugin repository, as Git will browse all SVN revisions (more than 330.000 currently).

To speed things up, and [following a tip from Nicolas Kuttler](https://www.nkuttler.de/post/using-git-for-wordpress-development/), we'll search for the revision we're interested in (the start of our plugin subfolder life), then fetch from here:

```shell-session
$ svn log --limit 1 https://plugins.svn.wordpress.org/e107-importer
------------------------------------------------------------------------
r333566 | plugin-master | 2011-01-17 17:09:40 +0100 (Mon, 17 Jan 2011) | 1 line

adding e107-importer by Coolkevman
------------------------------------------------------------------------
$ git svn fetch -r333566
r333566 = b850438a98c26a8f55ee2ddd7bdf8816d0390a1b (refs/remotes/trunk)
```

And now we can send our massive payload, after rebasing our `master` branch to SVN's `trunk`:

```shell-session
$ git rebase trunk
$ git svn dcommit --username=Coolkevman
```

We can then [contemplate our work in the official WordPress plugin repository](https://plugins.trac.wordpress.org/log/e107-importer).

There is one problem though: git-svn has [left empty folders because of renaming](https://plugins.trac.wordpress.org/changeset/336234). Let's fix this:

```shell-session
$ svn rm https://plugins.svn.wordpress.org/e107-importer/trunk/bbcode -m "Git-svn doesn't delete empty folders on move." --username=Coolkevman
```

Last thing to do is to tag our old versions on Subversion, as we did in our simulation:

```shell-session
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336229 https://plugins.svn.wordpress.org/e107-importer/tags/0.1 -m "Tag e107-importer 0.1"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336231 https://plugins.svn.wordpress.org/e107-importer/tags/0.2 -m "Tag e107-importer 0.2"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336232 https://plugins.svn.wordpress.org/e107-importer/tags/0.3 -m "Tag e107-importer 0.3"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336233 https://plugins.svn.wordpress.org/e107-importer/tags/0.4 -m "Tag e107-importer 0.4"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336235 https://plugins.svn.wordpress.org/e107-importer/tags/0.5 -m "Tag e107-importer 0.5"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336236 https://plugins.svn.wordpress.org/e107-importer/tags/0.6 -m "Tag e107-importer 0.6"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336237 https://plugins.svn.wordpress.org/e107-importer/tags/0.7 -m "Tag e107-importer 0.7"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336238 https://plugins.svn.wordpress.org/e107-importer/tags/0.8 -m "Tag e107-importer 0.8"
$ svn copy https://plugins.svn.wordpress.org/e107-importer/trunk@336239 https://plugins.svn.wordpress.org/e107-importer/tags/0.9 -m "Tag e107-importer 0.9"
```

But this mean I [had to clean up tags](https://plugins.trac.wordpress.org/changeset/336466) too, to remove the remaining empty folder.

## Pushing new commits

All of the above only works with an newly created plugin structure on WordPress plugin repository. What if we want to push new commits to Subversion once we've already pushed part of our Git history?

First, let's make our life miserable and delete all our local repositories:

```shell-session
$ cd ..
$ rm -rf e107-importer-git
```

Now, if we replay the steps above, the `git rebase trunk` command will ends with loads of conflicts. The procedure is different this time and is [explained by Ikke](https://eikke.com/importing-a-git-tree-into-a-subversion-repository/).

This involves [Git's graft](https://git.wiki.kernel.org/index.php/GraftPoint):

```shell-session
$ git clone git@github.com:kdeldycke/e107-importer.git e107-importer-git
$ cd e107-importer-git
$ git svn init --trunk=trunk --branches=branches --tags=tags https://plugins.svn.wordpress.org/e107-importer
$ git svn fetch -r333566
$ git show-ref trunk
$ git log --pretty=oneline master | tail -n1
$ echo `git log --pretty=oneline master | tail -n1 | cut -d ' ' -f 1` `git show-ref trunk | cut -d ' ' -f 1` >> .git/info/grafts
$ git svn dcommit
```

The last command will not end well, with Git complaining about unmerged differences. This is [likely due to my additional commit](https://plugins.trac.wordpress.org/changeset/336352) removing the empty folder left by git-svn. Fortunately Git suggest something in its log:

```text
If you are attempting to commit  merges, try running:
  git rebase --interactive --preserve-merges  refs/remotes/trunk
Before dcommitting
```

Well, that's what I exactly did:

```shell-session
$ git rebase --interactive --preserve-merges refs/remotes/trunk
$ git svn dcommit
```

And it magically fixed the issue! :)

I'm quite happy now to have a clearly identified workflow to push my Git updates to Subversion! :)
