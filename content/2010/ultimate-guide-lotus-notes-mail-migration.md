---
date: '2010-09-09'
title: Ultimate guide of Lotus Notes mail migration
category: English
tags: Dovecot, email, Lotus Notes, IMAP, Mac OS X 10.5 Leopard, Linux, macOS, maildir, Microsoft, Windows, Apple, TCPIP, port, Python, Mac OS X 10.6 Snow Leopard
---

The title may sounds pretentious but extracting mails out of Lotus Notes is
soooo hard and complicated, that achieving such a task feels like winning an
epic battle against the forces of evil.

Anyway. The goal of this post is to help you migrate all your Lotus Notes mails
to a more convenient and standard format like maildir or mailbox.

There are several ways of extracting all your mail trapped in Lotus Notes'
proprietary databases.

## Method #1: using integrated IMAP service

This is probably the simplest method. It consists in using the Lotus Notes
desktop client (were your emails currently resides) as an IMAP client.

Essentially, what you have to do is just to create a secondary account linked
to an IMAP server, like Gmail, etc. This works well and is [explained in
details in this tutorial
](https://salesittech.blogspot.com/2009/02/transfer-lotus-notes-email-to-gmail-and.html).

But sometimes your Notes client is behind firewalls and proxies. So you can't
reach the Internet.

And some other times, Lotus Notes clients are crippled and don't let you create
an IMAP connexion. Unfortunately this happened to me:

![French Lotus Notes new-account window filled in for imap.test.com over IMAP with SSL, its status bar ending on the error: Mail (IMAP) template does not exist](missing-lotus-notes-imap-template.png)

So I had to found another approach.

## Method #2: using `nlconverter`

This method is [explored in details in my previous article
]({filename}/2010/convert-lotus-notes-nsf-files-mbox-nlconverter.md).

But again, it seems that the Lotus Notes on my machine was crippled and/or
corrupted. The `nlconverter` GUI gave me this error:

![Lotus Notes Converter on Windows, its log repeating Could not connect to Notes and Could not find and register the dll](nlconverter-gui-fail.png)

And the command line gave me this:

```pytb
Traceback (most recent call last):
  File "notes2mbox.py", line 21, in <module>
    db = NlconverterLib.getNotesDb(notesNsfPath, notesPasswd)
  File "C:\winnlc-alpha-1\NlconverterLib.py", line 43, in getNotesDb
    session = win32com.client.Dispatch(r'Lotus.NotesSession')
  File "C:\Python26\lib\site-packages\win32com\client\__init__.py", line 95, in Dispatch
    dispatch, userName = dynamic._GetGoodDispatchAndUserName(dispatch,userName,clsctx)
  File "C:\Python26\lib\site-packages\win32com\client\dynamic.py", line 104, in _GetGoodDispatchAndUserName
    return (_GetGoodDispatch(IDispatch, clsctx), userName)
  File "C:\Python26\lib\site-packages\win32com\client\dynamic.py", line 84, in _GetGoodDispatch
    IDispatch = pythoncom.CoCreateInstance(IDispatch, None, clsctx, pythoncom.IID_IDispatch)
pywintypes.com_error: (-2147221231, 'ClassFactory ne peut pas fournir la classe demand\xe9e', None, None)
```

After these two failed attempts, I was quite depressed and not far from
surrender to the evil power of proprietary software. Then I managed to setup a
new (but complicated) strategy.

## Method #3: using Lotus Notes client for Mac OS X

This is the only method that worked for me, and basically, is the same as the
first one, but on Mac OS X. Additionally, it involves a local mail server. This
procedure was tested several times on Mac OS X Leopard.

1. First things first, [download the trial version of Lotus Notes
   ](https://www.ibm.com/developerworks/downloads/ls/lsndad/?S_TACT=105AGX28&S_CMP=TRIALS)
   client for Mac OS X (unfortunately you have to register) and install it. I
   used Lotus Notes 7.0.3 for Mac OS X Leopard:

```
![]({attach}lotus-notes-mac-osx-leopard-install.png)
```

2. You'll be welcomed by a [wizard
   ](https://en.wikipedia.org/wiki/Wizard_%28software%29):

```
![]({attach}lotus-notes-wizard-screen-1.png)
```

3. On the next screen, enter a dummy name and uncheck the
   "_I want to connect to a Domino server_" box:

```
![]({attach}lotus-notes-wizard-screen-2.png)
```

4. Then proceed to the next step in which you'll uncheck
   "_Setup instant messaging_":

```
![]({attach}lotus-notes-wizard-screen-3.png)
```

5. In the last screen, uncheck all boxes. We don't want to setup any other
   service yet:

```
![]({attach}lotus-notes-wizard-screen-4.png)
```

6. Initial setup is now complete:

```
![]({attach}lotus-notes-wizard-screen-5.png)

You can now launch Lotus Notes:

![]({attach}launch-lotus-notes-for-mac-osx.png)

![]({attach}lotus-notes-7-on-mac-osx-leopard.png)
```

7. On first run, there will be the following screen, where you should click
   on the "_No thanks, just give me the defaults_":

```
![]({attach}lotus-notes-wizard-screen-6.png)
```

8. You'll end up on what will be your default Lotus Notes main page from now
   on:

```
![]({attach}lotus-notes-wizard-screen-7.png)
```

9. The next step is to go back to the machine (Windows for me) from which
   you're running the Notes client containing all the mails you plan to migrate.
   From there, [export your mail database
   ]({filename}/2010/how-to-export-backup-lotus-notes-mails.md):

```
![]({attach}export-screen.png)

All details of this operation can be found in [this dedicated article
]({filename}/2010/how-to-export-backup-lotus-notes-mails.md).
```

10. Then go back to your Mac OS X machine and import your freshly exported
    `.nsf` database. This is as simple as opening the file via the `File` >
    `Database` > `Open...` menu and dialog:

```
![]({attach}lotus-notes-database-opening.png)

![]({attach}lotus-notes-open-database-dialog.png)
```

11. When Notes attempts to open the file, you'll be prompted by several
    dialogs regarding the security attached to the database. If you get the
    "_Create Cross Certificate_" screen, then just answer "_Yes_" as below:

```
![]({attach}lotus-notes-cross-certificate-creation-dialog.png)

And every time you get an "_Execution Security Alert_" message, always check
the "_Start trusting the signer to execute this action_" option before clicking
"_OK_":

![]({attach}lotus-notes-execution-security-alert-dialog.png)
```

12. The client will then rebuild the index before giving you a plain view of
    your inbox:

```
![]({attach}lotus-notes-database-import.png)

![]({attach}lotus-notes-database-successful-import.png)
```

13. Next step is to setup a local IMAP server:

```
![]({attach}dovecot-on-macosx.png)

As you can see I [used Dovecot, and all is explained here
]({filename}/2010/setup-lightweight-imap-server-macos-leopard-dovecot.md).
```

14. Now it's time to create a new account in Lotus Notes to access this local
    IMAP server. Click on the `Address Book` in your toolbar and add a new
    `Account`:

```
![]({attach}lotus-notes-address-book-icon.png)

![]({attach}lotus-notes-create-new-mail-account.png)
```

15. Here is where you configure Notes to let it be aware of our local server
    existence. Only the first tab must be changed to your local parameters. You
    can left the last two tabs untouched:

```
![]({attach}lotus-notes-local-imap-config.png)
```

16. Open within Notes your local IMAP mailbox. It is found in the workspace,
    which you can access via the `Databases` icon on your toolbar:

```
![]({attach}lotus-notes-open-workspace.png)

![]({attach}lotus-notes-workspace.png)
```

17. You'll be welcomed by a useless help screen:

```
![]({attach}lotus-notes-imap-welcome-screen.png)

Just close it to get your local IMAP mail view:

![]({attach}lotus-notes-local-imap-mailbox-view.png)
```

18. While trying to opening the local IMAP mailbox, you may encounter this
    `TCPIP port` error:

```
![]({attach}lotus-notes-tcp-ip-error.png)

In this case, please have a look at my other [article explaining how to open
TCPIP port in Lotus Notes
]({filename}/2010/how-to-fix-lotus-notes-disabled-tcp-ip-port-error.md).
```

19. For this step, just copy or cut, then paste, mails from your local `.nsf`
    database to your local IMAP account:

```
![]({attach}lotus-notes-copy-nsf-mails.png)

![]({attach}lotus-notes-copying-nsf-mails.png)

![]({attach}lotus-notes-paste-mails-to-local-imap.png)

![]({attach}lotus-notes-pasting-mails-to-local-imap.png)

![]({attach}lotus-notes-mails-migrated-to-local-imap.png)
```

20. While playing with copy'n'paste, you may encounter this error:

```
![]({attach}notes-rich-text-to-mime-conversion-error.png)

A [workaround can be found in this article
]({filename}/2010/lotus-notes-rich-text-mime-conversion-error.md).
```

21. Finally, if like me you've played a lot with mails during the transfer
    step above, you may ends up with loads of duplicate mails. In this case have
    a look at the [deduplication script
    ]({filename}/2010/maildir-deduplication-script-python.md) I
    wrote. It will help you clean-up your Maildir folder.

22. That's it! You now have a standard Maildir of your Lotus Notes mails,
    located in your user home directory (`~/Maildir`):

```
![]({attach}maildir-containing-lotus-notes-mails.png)
```

My ultimate action was to [convert the Dovecot maildir to Kmail maildir
]({filename}/2007/how-to-import-a-maildir-folder-to-kmail.md),
as I wanted to use Kmail to finally upload everything in Gmail. But you can use
anything that suit your needs, like [thunderbird
](https://www.thunderbird.net/) or any mail conversion tools.

## Method #4: Lotus Notes client v8.5 on Mac OS X Leopard

The same procedure as in method #3 can be performed with the trial version of
the Lotus Notes client v8.5, running on Mac OS X Snow Leopard.

Here are the equivalent screenshots:

![Notes 8.5 for Mac installer open on its Read Me step, in front of a Finder window showing the trial disk image](010-lotus-notes-mac-install.png)

![Installer component list with Composite Application Editor and Sametime both left unchecked, so the space required stays at 0 KB](015-lotus-notes-mac-install-components.png)

![Installer summary with a green tick and the message: the installation was successful](020-lotus-notes-mac-install-finished.png)

![Welcome step of the Lotus Notes 8.5 client configuration wizard, listing the Domino, mail, newsgroup and directory servers it can set up](030-lotus-notes-wizard-welcome.png)

![Wizard user information step with the name set to kevin, the Domino server box empty and the option to connect to a Domino server unchecked](040-lotus-notes-wizard-config-1.png)

![Wizard additional services step with all five boxes unchecked, including internet mail servers and replication](050-lotus-notes-wizard-config-2.png)

![Small dialog announcing that Notes setup is complete](060-lotus-notes-wizard-finished.png)

![Lotus Notes 8.5 splash screen, an IBM yellow swoosh above the licensing small print](065-lotus-notes-mac-splash-screen.png)

![Startup dialog with a barber-pole progress bar reading: Lotus Notes is starting, please wait](070-lotus-notes-start-init.png)

![Prompt asking whether to make Lotus Notes the default email program, with the option to skip the check in future ticked](080-lotus-notes-default-email-program.png)

![Notes 8.5 Getting Started page explaining the Open button, the toolbar search and the sidebar](090-lotus-notes-8-5-mac-default-screen.png)

![File menu open on Open, with the Lotus Notes Application entry highlighted](100-lotus-notes-open-nsf-database.png)

![File chooser on the Desktop with kevin-notes-big-backup.nsf selected, the preview reporting a 167 MB Notes database file](110-lotus-notes-open-database-dialog.png)

![Create Cross Certificate dialog, organisation and public key redacted, warning that documents from this organisation cannot be verified](120-lotus-notes-certificate-dialog.png)

![Execution Security Alert about a GetProfileField action, with the option to start trusting the signer selected](130-lotus-notes-security-alert-dialog.png)

![Imported .nsf database open on a French inbox of 8715 messages, senders and subjects blurred, the quota bar at 28% of 550 MB](140-lotus-notes-opened-nsf-database.png)

![Lotus Notes application menu with Preferences highlighted](150-lotus-notes-open-preferences.png)

![Accounts pane of the preferences with the New Account menu unrolled and IMAP Online highlighted among the protocol choices](160-lotus-notes-create-new-account.png)

![New Account dialog naming the account Local IMAP, of type IMAP Online, pointing at localhost and logging in as kevin](170-lotus-notes-new-account-parameters.png)

![Open button menu drilling through Applications and the workspace tab to the Local IMAP entry](180-lotus-notes-open-local-imap.png)

![Local IMAP account open in Notes on a completely empty inbox](190-lotus-notes-local-imap-inbox-view.png)

![Edit menu open on Copy in the .nsf inbox, the status bar reporting 22 documents selected](200-lotus-notes-copy-nsf-mails.png)

![Edit menu open on Paste in the still-empty Local IMAP inbox](210-lotus-notes-paste-mails-to-local-imap.png)

![Local IMAP inbox filled with the migrated messages, senders and subjects blurred](220-lotus-notes-mails-migrated-to-local-imap.png)

## Method #5: Lotus Notes client on Windows XP

I just tried the first method again (IMAP connection with Note's fat client).
But this time I installed Lotus Notes 8.5.2 trial version on a fresh Windows XP running within a QEMU
instance.

As you can see, it works:

![Windows XP running inside QEMU, French Notes client pasting into a notes-import IMAP folder with 184 documents left to go at 74%](lotus-notes-imap-mail-migration-via-qemu.png)

With simple copy'n'paste, I was able to migrate several batch of mails. Until
the target `notes-import` folder on my Gmail account reached 2000+ mails, at
which point my Notes client freezed hard. So I'm stuck with only part of my
mails migrated. Again, this is not the solution I'm looking for, as it can't
handle large quantity of mails. :(

## Conclusion

- Lotus Notes sucks. [Everybody knows that
  ](https://www.guardian.co.uk/technology/2006/feb/09/guardianweeklytechnologysection),
  but I feel liberated saying that! ;)

- The smartest thing to do is to avoid Notes like the plague in the first
  place. Sadly when working for the man, it's not always possible... :(

- The only method I found to work for me (the third solution in this article)
  is far from perfect from my point of view. What I dream about is a 100%
  automated solution, like a command line utility we can name `nsf2maildir`.
  And as I don't plan to own Apple hardware and software in a near future, such
  a command should be 100% free software and running on Linux. I really think
  there is a "market" for a free software component able to read and understand
  `.nsf` files. Any motivated volunteer? ;)
