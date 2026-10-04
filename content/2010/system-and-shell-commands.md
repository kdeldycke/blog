---
date: '2010-02-28'
title: System & Shell commands
category: English
tags: CLI, echo, kernel, Linux, nohup, shell, system, cron, Regular expression, bash, font
---

## Processes

- Run a process detached to the current terminal and monitor its output:

  ```shell-session
  $ nohup my_command &
  $ tail -F ./nohup.out
  ```

- Same as above but with multiple commands, the last cloning a disk to another:

  ```shell-session
  $ nohup zsh -c "my_command && cat /dev/da1 > /dev/da0" &
  $ tail -F ./nohup.out
  ```

- Run a process with a shell for a system user which has none (i.e. its default shell is set to `/bin/false` in `/etc/passwd`):

  ```shell-session
  $ su sys_user -s /bin/bash -c "my_command"
  ```

## Shell

- Get the exit code of the latest ran command:

  ```shell-session
  $ echo $?
  ```

- Run the last command as `root` ([source](https://web.archive.org/web/20101221102958/http://blog.hardikr.com/post/2337320222/sudo-previous-command)):

  ```shell-session
  $ sudo !!
  ```

- Show the user under which I'm currently logged in:

  ```shell-session
  $ whoami
  ```

- List of most used commands:

  ```shell-session
  $ history | awk '{a[$2]++}END{for(i in a){print a[i] " " i}}' | sort -rn | head
  ```

- List cron jobs of the current user:

  ```shell-session
  $ crontab -l
  ```

- If you have the following error:

  ```shell-session
  $ -bash: ./myscript.sh: /bin/bash^M: bad interpreter: No such file or directory
  ```

  Then the fix consist of removing the bad characters:

  ```shell-session
  $ sed -i 's/\r//' ./myscript.sh
  ```

- Extract strings from a binary file:

  ```shell-session
  $ strings ./firmware.bin | less
  ```

## Memory

- Free up some memory by clearing RAM caches ([source](https://www.scottklarr.com/topic/134/linux-how-to-clear-the-cache-from-memory/)):

  ```shell-session
  $ sync ; echo 3 > /proc/sys/vm/drop_caches
  ```

## Distribution

- Display which distro is running the system ([source](https://news.ycombinator.com/item?id=1973441)):

  ```shell-session
  $ lsb_release -a
  ```

  or

  ```shell-session
  $ cat /etc/lsb-release
  ```

## Services

- Disable a service on Debian/Ubuntu, then re-enable it:

  ```shell-session
  $ update-rc.d my-service-name remove
  $ update-rc.d my-service-name defaults
  ```

- Same thing as above but on a RedHat-like system:

  ```shell-session
  $ chkconfig sshd --del
  $ chkconfig sshd --add
  ```

## Boot

- Speed-up Grub boot, but always show the boot menu:

  ```shell-session
  $ sudo sed -i 's/GRUB_TIMEOUT=10/GRUB_TIMEOUT=1/g' /etc/default/grub
  $ sudo sed -i 's/GRUB_HIDDEN_TIMEOUT/#GRUB_HIDDEN_TIMEOUT/g' /etc/default/grub
  $ sudo update-grub
  ```

## Fonts

- List fonts available on the system:

  ```shell-session
  $ fc-list | cut -d ':' -f 2 | sort | uniq
  ```

## Other Resources

- [Pure bash bible](https://github.com/dylanaraps/pure-bash-bible).
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls).
