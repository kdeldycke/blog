---
date: '2010-09-02'
title: Convert Lotus Notes' nsf files to mbox with nlconverter
category: English
tags: CLI, email, GUI, Lotus Notes, iCal, mbox, nlconverter, Python, Windows, Windows 2000, Mercurial
---

There is a great piece of software called [nlconverter](https://code.google.com/p/nlconverter/). It's a tool designed to convert Lotus Notes' `.nsf` files to `mbox`. It rely on win32's COM/DDE API so it can only be used on Windows.

If you want to extract mails out of your `.nsf` database, this might be the tool you're looking for. Bonus point: it's written in Python! ;)

## Installing nlconverter and its dependencies

Here is how I installed `nlconverter` on a Windows 2000 (SP4) machine:

1. First I downloaded and installed the [official Python builds for Windows](https://www.python.org/download/releases/) ([2.6.6 precisely](https://www.python.org/ftp/python/2.6.6/python-2.6.6.msi)):

   ![Python 2.6.6 Windows installer asking whether to install for all users or just the current one, with all users selected](001-python-266-install-on-windows-2000.png)

   ![Installer destination step keeping the default Python26 directory at the root of the C: drive](002-python-266-install-on-windows-2000.png)

   ![Feature tree of the Python installer with all five subfeatures selected, including Tcl/Tk, documentation and the test suite](003-python-266-install-on-windows-2000.png)

   ![Python installer part way through copying new files](004-python-266-install-on-windows-2000.png)

   ![Final installer screen thanking Mark Hammond for the Windows expertise behind Python for Windows](005-python-266-install-on-windows-2000.png)

2. Then [Python for Windows extensions](https://sourceforge.net/projects/pywin32/) ([build 214 for Python 2.6 in my case](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20214/pywin32-214.win32-py2.6.exe/download)):

   ![pywin32 setup wizard opening on the package description for build 214 by Mark Hammond, its buttons in French](001-pywin32-214-install-on-windows-2000.png)

   ![pywin32 setup having found Python 2.6 in the registry, targeting the Python26 directory on the C: drive and its site-packages directory](002-pywin32-214-install-on-windows-2000.png)

   ![pywin32 setup copying files, currently on a win32com test script](003-pywin32-214-install-on-windows-2000.png)

   ![pywin32 post-install log reporting registered DLLs and confirming the extensions were successfully installed](004-pywin32-214-install-on-windows-2000.png)

3. Finally I had to [download the latest `icalendar` archive](https://pypi.python.org/pypi/icalendar), then extract the `\iCalendar-1.2\src\icalendar` folder to `C:\Python26\Lib\site-packages\`:

   ![7-Zip window open on the iCalendar source archive next to an Explorer window on Python's site-packages, where the extracted icalendar folder now sits](extract-icalendar-python-package-on-windows.png)

4. Next step is to [download nlconverter](https://code.google.com/p/nlconverter/downloads) itself and extract it:

   ![7-Zip showing the 13 MB winnlc-alpha-1 archive next to an Explorer window on C:, where the extracted winnlc-alpha-1 folder is highlighted](nlconverter-install-on-windows.png)

## `nlconverter` GUI

First thing you have to do is to create an [export of your mails as a `.nsf` database]({filename}/2010/how-to-export-backup-lotus-notes-mails.md). Follow the previous link to get the instructions.

Now let's convert this `nsf` to a `mbox`. [nlconverter's FAQ](https://code.google.com/p/nlconverter/wiki/Faq) tells you to run the `gui.exe` program to perform the conversion.

Unfortunately it didn't work for me:

![Lotus Notes Converter on Windows, its log repeating Could not connect to Notes and Could not find and register the dll](nlconverter-gui-fail.png)

So I tried the alternative approach by using the command line.

## `nlconverter` command line

Again, most of the things I'm writing here are based on [nlconverter's FAQ](https://code.google.com/p/nlconverter/wiki/Faq):

1. First, we have to [download the `notes2mbox.py` script](https://nlconverter.googlecode.com/hg/notes2mbox.py) from [nlconverter's mercurial repository](https://code.google.com/p/nlconverter/source/browse/), as this file is not distributed in the `winnlc-alpha-1.zip` archive I unzipped previously. Let's put `notes2mbox.py` in `C:\winnlc-alpha-1\`:

   ![Firefox on the Google Code page for notes2mbox.py, with a save dialog pointed at the winnlc-alpha-1 folder](download-notes2mbox-python-script.png)

2. Now we'll modify the `notes2mbox.py` script to set the password (via the `notesPasswd` variable) and location (`notesNsfPath` variable) of the `.nsf` file. Here are the modifications I applied:

   ```diff
   --- notes2mbox.py.orig	2010-09-02 13:49:58.000000000 +0200
   +++ notes2mbox.py	2010-09-02 13:51:24.000000000 +0200
   @@ -14,8 +14,8 @@
    import NlconverterLib

    #Constantes
   -notesPasswd = "foobar"
   -notesNsfPath = "C:\\archive.nsf"
   +notesPasswd = "XXXXXXXXXXXXX"
   +notesNsfPath = "C:\\winnlc-alpha-1\\kevin-notes-big-backup-part-1.nsf"

    #Connection à Notes
    db = NlconverterLib.getNotesDb(notesNsfPath, notesPasswd)
   ```

3. Before running the script, we have to register a Notes DLL used by nlconverter:

   ```bat
   regsvr32 "C:\Program Files\Notes\nlsxbe.dll"
   ```

   ![Command prompt after running regsvr32 on nlsxbe.dll, with a dialog confirming DllRegisterServer succeeded](notes-nlsxbe-dll-registered1.png)

   And make the Python interpreter available system-wide:

   ```bat
   C:\winnlc-alpha-1>SET Path=%Path%;C:\Python26
   ```

4. Now we can run the `notes2mbox.py` script:

   ```bat
   C:\winnlc-alpha-1>C:\Python26\python.exe notes2mbox.py
   ```

   If you're lucky, you'll get a nice mbox at the end of the process.

   But I was not and the `notes2mbox.py` ended up with the following error:

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

As you can see, I tried hard to make nlconverter working, without any success. But this should not stop you to try. In fact I suspect the Lotus Notes installed on my machine to be crippled or corrupted (can't really tell). So you may be more lucky than me. In any case, feel free to report any success or failure in the comment section below!
