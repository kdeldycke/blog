---
date: '2010-04-15'
title: Subversion commands
category: English
tags: ack, CLI, find, grep, Linux, sed, shell, Subversion, Regular expression
---

## Native commands

- Produce a patch file of changes committed in revision 1377:

  ```shell-session
  $ svn diff -r 1376:1377 > diff.patch
  ```

- Merge revision `3403` of the trunk into the "1.0" branch:

  ```shell-session
  $ cd branches/1.0
  $ svn merge -c3403 https://svn.example.com/my_project/trunk
  $ svn commit -m "Merge r3403 into the 1.0 branch."
  ```

- Revert current local folder to revision 666:

  ```shell-session
  $ svn merge -rHEAD:666 ./
  ```

- Create an empty repository:

  ```shell-session
  $ svnadmin create ./my-repo
  ```

- Dump a repository (a sure way to migrate a subversion repository from one version to another):

  ```shell-session
  $ svnadmin dump ./my-repo > ./my-repo.dmp
  ```

- Migrate a remote Subversion repository without creating an intermediate dump file:

  ```shell-session
  $ ssh -C user@myserver.com "svnadmin dump /home/user/my-repo" | svnadmin load /home/user2/my-new-repo
  ```

- Launch a standalone Subversion server listening on port 3690 and serving all repositories located in `./repos/`:

  ```shell-session
  $ svnserve --daemon --listen-port 3690 --root ./repos/
  ```

## Local working copy hacking

- Recursive and case insensitive content search on non-binary files from the current folder, while ignoring `.svn` folders and their content:

  ```shell-session
  $ find ./ -type f -not -regex ".*\/.svn\/.*" -exec grep -Iil "string to search" {} \;
  ```

- Same thing as above but with an alternative approach (that don't work with large folder content):

  ```shell-session
  $ grep -Ii "string to search" $(find . | grep -v .svn)
  ```

Other alternative: use [ack](https://beyondgrep.com/).

- Use `sed` to replace text in all files except in subversion metadatas:

  ```shell-session
  $ find ./ -type f -not -regex ".*\/.svn\/.*" -print -exec sed -i 's/str1/str2/g' "{}" \;
  ```

- Use `svn delete` to remove all files containing a tilde in their name without touching local subversion metadatas:

  ```shell-session
  $ find -type f -not -regex ".*\/.svn\/.*" -name "*˜*" -print -exec svn delete "{}" \;
  ```

- In a repository structure containing sub-projects (thinks of [Plone's collective repository](https://web.archive.org/web/20070701061128/http://svn.plone.org/svn/collective/) as an example), get the list of all folders in all trunks, while ignoring subversion metadata folders:

  ```shell-session
  $ find ./ -type d -regex ".*\/trunk\/?.*" -not -regex ".*\/.svn\/?.*" -print
  ```

- Similarly to the command above, replace all occurrences of the string `@coolcavemen.fr` by `@coolcavemen.com` in all `trunk` subfolders while ignoring `.svn` content:

  ```shell-session
  $ find ./ -type f -regex ".*\/trunk\/.*" -not -regex ".*\/.svn\/.*" -print -exec sed -i 's/@coolcavemen\.fr/@coolcavemen\.com/g' "{}" \;
  ```

- Set a svn property to ignore all `.mo` files during commit in every folder of our local working copy containing `.po` files:

  ```shell-session
  $ find ./ -type f -name "*.po" -regex ".*\/trunk\/.*" -not -regex ".*\/.svn\/.*" -printf "%h\n" | uniq | xargs svn propset "svn:ignore" "*.mo"
  ```
