---
date: '2011-08-30'
title: How I Open-Sourced an Internal Corporate Project (WebPing)
category: English
tags: CLI, Git, GitHub, Linux, Perl, Python, Regular expression, Subversion, trac, webping
---

[2 weeks ago I released WebPing]({filename}/2011/webping-open-sourced.md). This article is more or less the same I wrote 4 months ago when I [released the FTT project]({filename}/2011/feed-tracking-tool-released-open-source-license.md) and needed to [move it from SVN to Git]({filename}/2011/ftt-migration-subversion-git.md). But this time I added more details on how I removed all sensible information that were hard-coded in the project files.

## Subversion to Git migration

Everything starts out of a local copy of the Subversion repository that was hosting the WebPing project since its inception:

```shell-session
$ rm -rf ./svn-repository-copy
$ tar xvzf ./svn-repository-copy.tar.gz
$ kill `ps -ef | grep svnserve | awk '{print $2}'`
$ svnserve --daemon --listen-port 3690 --root ./svn-repository-copy
```

Let's initialize a Git repository:

```shell-session
$ rm -rf ./webping-git
$ mkdir ./webping-git
$ cd ./webping-git
$ git init
$ git commit --allow-empty -m 'Initial commit'
$ git tag "init"
```

We now migrate the code from Subversion to Git:

```shell-session
$ git svn init --no-metadata --username deldycke svn://localhost:3690
$ git svn fetch
$ git rebase --onto git-svn master
$ rm -rf ./.git/svn/
$ rm -rf ./.git/refs/original/
$ git reflog expire --all
$ git gc --aggressive --prune
```

## Removing unrelated files and folders

As WebPing was not alone in the original Subversion repository, we need to clean up the latter and only keep code of the former. Worse, WebPing didn't started its life in a dedicated subfolder, but as a tool of another project, and jumped from folders to folders. After identifying in the history all places were WebPing lived once, I came up with this big, convoluted command line to do the cleaning:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'find ./ -not -ipath "*webping*" -and -not -path "./other-project/trunk/tools/web-ping*" -and -not -path "./other-project/trunk/tools" -and -not -path "./other-project/trunk" -and -not -path "./other-project" -and -not -path "./.git*" -and -not -path "./" | xargs rm -rf' -- --all
```

Strangely enough, my `init` tag went off after the command above. So I had to rebased it to get it in line:

```shell-session
$ git rebase init master
```

We can now remove SVN tags and branches, get rid of the imported `git-svn` branch, and clean up our Git repository:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'find -path "./WebPing/tags*" | xargs rm -rf' -- --all
$ git filter-branch --force --prune-empty --tree-filter 'find -path "./WebPing/branches*" | xargs rm -rf' -- --all
$ git branch -r -D git-svn
$ rm -rf ./.git/svn/
$ rm -rf ./.git/refs/original/
$ git reflog expire --all
$ git gc --aggressive --prune
```

If I now only have WebPing code in the repository, it still jumps through the history between these following locations:

- `other-project/trunk/tools/web-ping.py`
- `other-project/trunk/tools/web-ping/`
- `WebPing/trunk/`

Using a series of `git filter-branch` invocations, I managed to move everything to the root of the repository:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'test -d ./other-project/trunk/tools && cp -axv ./other-project/trunk/tools/* ./ && rm -rf ./other-project/trunk/tools || echo "No tools folder found"' -- --all
$ git filter-branch --force --prune-empty --tree-filter 'test -d ./other-project/trunk/tools/web-ping && cp -axv ./other-project/trunk/tools/web-ping/* ./ && rm -rf ./other-project/trunk/tools/web-ping || echo "No web-ping folder found"' -- --all
$ git filter-branch --force --prune-empty --tree-filter 'test -d ./WebPing/trunk && cp -axv ./WebPing/trunk/* ./ && rm -rf ./WebPing/trunk || echo "No trunk folder found"' -- --all
```

## Hide and obfuscate hard-coded content

As WebPing was created for internal needs in my previous job, its original code base contains lots of references to the former infrastructure it lives in. My professional standards requires me to remove all these sensible information before making WebPing available to the public.

For example, here is the commands which allowed me to remove all references to hostnames of our intranets:

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'find . -type f -exec perl -i -pe "s/([\w-.]*?)\.(company(-intranet|-extension)?)\.(fr|com|net|org)/intranet\.example\.com/g" "{}" \;' -- --all
```

The Perl one-liner embedded in the command above will only apply the regular expression on a line-by-line basis. If you want to have the regexp applied on the whole content of each file, you have to use Perl's _slurp_ mode ([source of that tip](https://web.archive.org/web/20110907121124/http://www.math.uiuc.edu/~hildebr/computer/perltips.html)):

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'perl -0777 -i -pe "s/MAILING_LIST\s*=\s*\[(.*?)\]/MAILING_LIST = \[\]/gs" ./web-ping.py' -- --all
```

The specific example above helped me removed the content of the `MAILING_LIST` Python list found in `web-ping.py`, in order to protect from spam the email addresses of my former co-workers that were unfortunately hard-coded in that variable.

Another place to hunt for sensible information is commit messages. These can be easily modified thanks to the `--msg-filter` option. Here is how I removed references to our internal [Trac](https://trac.edgewall.org/) tickets:

```shell-session
$ git filter-branch --force --msg-filter 'sed "s/ (see ticket:666)//g"' -- --all
```

I also had to remove line returns introduced by abusive usage of Windows text editors (remember, WebPing was born in a corporate environment):

```shell-session
$ git filter-branch --force --prune-empty --tree-filter 'perl -i -pe "s/\r//" ./*' -- --all
```

The last useful command I use was the following, to fix author's name and email:

```shell-session
$ git filter-branch --force --env-filter '
    if [ "$GIT_AUTHOR_NAME" = "deldycke" ]
        then
            export GIT_AUTHOR_NAME="Kevin Deldycke"
            export GIT_AUTHOR_EMAIL="kevin@deldycke.com"
    fi
    if [ "$GIT_AUTHOR_NAME" = "diehr" ]
        then
            export GIT_AUTHOR_NAME="Matthieu Diehr"
            export GIT_AUTHOR_EMAIL="matthieu.diehr@gmail.com"
    fi
    ' -- --all
```

By using a dozen variations of the commands above, and carefully reviewing the code, I was able to engineer a clean code history.

But I certainly have been a little too blunt with these regular expressions. Some of them were able to act on binary content. As a result, I [had to restore static images](https://github.com/kdeldycke/webping/commit/8c72cbee1a4f72066ffe9fa82b2b06baadca9f24) to their original copy.

## Final steps

Now that your code is clean, all you need is to recreate you tag and fix the `init` tag date before committing everything to GitHub:

```shell-session
$ git tag -f "0.0" bad4ff7fc48b8b34f6f661d75c782c7fc0d098c5
$ git tag -f "0.1" 590ac9953df0e3bc76fd02615471e36a9796a065
$ git tag -f "0.2" 33f731054042b02c6d2600e7aead5bb7c4991b12
$ git filter-branch --env-filter '
        if [ $GIT_COMMIT = 361224542bc73bba747c7ca382e992e2cdd0c356 ]
        then
            export GIT_AUTHOR_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
            export GIT_COMMITTER_DATE="Thu, 01 Jan 1970 00:00:00 +0000"
        fi' -- --all
$ git remote add origin git@github.com:kdeldycke/webping.git
$ git push -u origin master
$ git push --tags
```
