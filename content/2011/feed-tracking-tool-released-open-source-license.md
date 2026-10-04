---
date: '2011-03-28'
title: Feed Tracking Tool released under an Open-Source license
category: English
tags: code, feed, Git, GitHub, GPL, Pylons, Python, ruby, Ruby on Rails, Uperto, Web
---

I've just open-sourced the [Feed Tracking Tool project](https://github.com/kdeldycke/feed-tracking-tool) (aka "FTT"), my first (and only) [Ruby on Rails](https://rubyonrails.org/) experience.

This tool was developed within [Uperto](https://web.archive.org/web/20110202140419/http://www.uperto.com/), the company I currently work for, for its internal needs. The project had an ancestor written in 2006 that was based on [Pylons](https://pylonshq.com). It was a prototype and was barely working. Iterating over the abandoned Python code base was considered a waste of time. So in summer 2007, it was decided to rewrite this application from scratch.

As my co-worker was available and already played with Ruby on Rails, he was tasked to create the initial code base. I joined the project early on, as it was a great opportunity to play with the (then really trendy) Ruby on Rails framework.

At the end FTT was essentially a test project to explore Ruby on Rails. It was never deployed on a production server and was never used.

After roting for more than 3 years, and representing absolutely no business value in itself, I decided to release it under a [GPLv2 license](https://www.gnu.org/licenses/gpl-2.0.html) (with Uperto's approval of course). My intention with this open-source release is to share back knowledge and code with the community.

FTT was living in a private Subversion repository at Uperto, but we unfortunately lost it. During the last few weeks I tried to rebuild the code history from old and partial backups. I then used my [Git-based reconstruction method]({filename}/2010/git-commit-history-reconstruction.md) to consolidate everything in a Git repository. The [code is now available on GitHub](https://github.com/kdeldycke/feed-tracking-tool).

I don't plan to maintain this project. But I may reboot it in the future if I need feed-related features, or if I need an excuse to play with Ruby on Rails again. But for now beware: the code is quite outdated and is only running on old Rails 1.2.x. This project should be considered as an ugly legacy code base. So please be indulgent while looking at FTT's code: it was the work of unexperienced RoR developers! ;)
