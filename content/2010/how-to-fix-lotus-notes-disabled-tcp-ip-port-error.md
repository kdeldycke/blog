---
date: '2010-08-25'
title: How-to fix Lotus Notes' disabled TCPIP port error
category: English
tags: Lotus Notes, Mac OS X 10.5 Leopard, Mac OS X 10.6 Snow Leopard, Lotus Notes, Apple, macOS, Network
---

Today I encountered this error message:

![Alert reading: error logging into server localhost, you must enable the Notes TCPIP port](lotus-notes-tcp-ip-error.png)

> Error logging into server localhost: You must enable the Notes TCPIP port.

This appeared in the fat Lotus Notes client v7.0.3 running on Mac OS X Leopard.

To fix this issue, first of all, quit Notes. Then [locate the Notes' preference
file](https://web.archive.org/web/20140604133422/http://www-01.ibm.com/support/docview.wss?uid=swg21090921) attached to
your current user. Mine was found in my home directory at
`/Users/kevin/Library/Preferences/Notes Preferences`. At the end of this file,
add [these two directives](https://web.archive.org/web/20101013195759/http://macosx.com/forums/1277870-post4.html):

```ini
TCPIP=TCP,0,15,0
Ports=TCPIP
```

Then relaunch Lotus Notes and switch from `Island (Disconnected)` location to
another that will allow your client to listen to the network. In my case,
`Home (Network Dialup)` did the trick:

![Location menu in the Notes status bar listing Home, Internet, Island, Office and Travel, with Island (Disconnected) currently ticked](lotus-notes-location-switch.png)

Problem solved! :)

FYI, this error can still be encountered in Lotus Notes 8.5 on Mac OS X
Snow Leopard. In this context, the solution is exactly the same.

Here is a screenshot of the location drop-down menu with the new Notes
interface:

![The slimmer 8.5 version of the same menu, offering only Home, Offline, Online and Travel](lotus-notes-8-5-location-switch.png)

And if you're looking for the `notes.ini` file on Windows, it's located at
`C:\Documents and Settings\[username]\Local Settings\Application Data\Lotus\Notes\Data\`.
At least in my case with Lotus Notes 8.5.2 under Windows XP SP2:

![Windows XP Explorer on the Lotus Notes Data directory, with notes.ini sitting among the .nsf databases and id files](notes-ini-location-windows-xp.png)
