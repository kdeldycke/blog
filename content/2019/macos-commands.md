---
date: '2019-07-22'
title: macOS commands
category: English
tags: CLI, macOS, Apple, OSX, PluginKit, TimeMachine, network, DNS, diskutil
---

## TimeMachine

- Compress sparse bundle disk image mounted over a network:

  ```shell-session
  $ sudo hdiutil compact /Volumes/time-machine-backups/my-machine.sparsebundle
  ```

## PluginKit

- List available PluginKit extensions:

  ```shell-session
  $ pluginkit -mAvvv
  ```

- Get infos on a PluginKit extensions:

  ```shell-session
  $ pluginkit -m -v -i com.agilebits.onepassword7.1PasswordSafariAppExtension
  ```

- Enable a PluginKit extensions:

  ```shell-session
  $ pluginkit -e use -i com.agilebits.onepassword7.1PasswordSafariAppExtension
  ```

## Kernel extensions

- List non-system kernel extensions currently loaded:

  ```shell-session
  $ kextstat | grep -v com.apple
  ```

- List non-system kernel extensions currently loaded:

  ```shell-session
  $ sudo kextunload -b com.google.drivefs.filesystems.dfsfuse
  ```

## Network

- Clear local DNS cache:

  ```shell-session
  $ sudo killall -HUP mDNSResponder
  ```

## Filesystem

- List all partitions of all disks:

  ```shell-session
  $ diskutil list
  ```

- Remove the first partition of the fourth disk:

  ```shell-session
  $ diskutil eraseVolume free free /dev/disk4s1
  ```

- List shared folders in iCloud:

  ```shell-session
  $ mdfind -onlyin "$HOME/Library/Mobile Documents/" 'kMDItemIsShared == 1'
  ```

- [Install Steam in a case-insensitive disk image](https://github.com/kdeldycke/dotfiles/blob/b711023285488f94fa0968a5ceff75c4322548bd/scripts/osx-install.sh#L149-L162).
