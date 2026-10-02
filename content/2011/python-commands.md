---
date: '2011-01-04'
title: Python commands
category: English
tags: ascii, Computer programming, date, dateutil, development, distutils, encoding, PEP8, PyPI, PDB, Python, socket, unicode, URL, urllib2, HTTP, PyLint, Fabric, pip, boltons
---

## Strings

- Replace accentuated characters by their ASCII equivalent in a unicode string:

  ```python
  import unicodedata

  unicodedata.normalize("NFKD", "éèàçÇÉÈ²³¼ÀÁÂÃÄÅËÍÑÒÖÜÝåïš™").encode("ascii", "ignore")
  ```

- Cleanest way I found to produce slugified / tokenized strings, based on [`boltons.strutils`](https://boltons.readthedocs.io/en/latest/strutils.html#boltons.strutils.slugify):

  ```pycon
  >>> from boltons import strutils
  >>> strutils.slugify(" aBc De F   1 23 4! -- ! 56--78 - -9- %$& +eée-", "-", ascii=True)
  b'abc-de-f-1-23-4-56-78-9-eee'
  ```

  Alternative: use [`awesome-slugify`](https://pypi.python.org/pypi/awesome-slugify) package.

## Sorting

- Sort a list of dicts by dict-key ([source](https://code.pui.ch/2007/07/23/python-sort-a-list-of-dicts-by-dict-key/)):

  ```python
  import operator

  [dict(a=1, b=2, c=3), dict(a=2, b=2, c=2), dict(a=3, b=2, c=1)].sort(
      key=operator.itemgetter("c")
  )
  ```

## Date & Time

I recommend using [`Arrow`](https://crsmithdev.com/arrow/). But if you can't, here are some pure-python snippets.

- Add a month to the current date:

  ```python
  import datetime
  import dateutil

  datetime.date.today() + dateutil.relativedelta(months=1)
  ```

## Network

- Set `urllib2` timeout ([source](https://www.voidspace.org.uk/python/articles/urllib2.shtml)):

  ```python
  import socket

  socket.setdefaulttimeout(10)
  ```

- Start a dumb HTTP server on port 8000 ([source](https://news.ycombinator.com/item?id=2042008)):

  ```shell-session
  $ python -m SimpleHTTPServer 8000
  ```

## Debug

- Add a [Python's debugger](https://docs.python.org/library/pdb.html) break point:

  ```python
  import pdb

  pdb.set_trace()
  ```

- Delete all `.pyc` and `.pyo` files in the system:

  ```shell-session
  $ find / -name "*.py[co]" -print -delete
  ```

## Version

- Print Python's 3-elements version number:

  ```shell-session
  $ python -c "from __future__ import print_function; import sys; print('.'.join(map(str, sys.version_info[:3])))"
  2.7.6
  ```

- Compare Python version for use in shell scripts:

  ```shell-session
  $ python -c "import sys; exit(sys.version_info[:3] < (2, 7, 9))"
  $ if [[ $? != 0 ]]; then
  >     echo "Old Python detected.";
  > fi
  Old Python detected.
  ```

## Style

- Use [autopep8](https://pypi.python.org/pypi/autopep8/) to apply PEP8's coding style on all Python files:

  ```shell-session
  $ find ./ -iname "*.py" -print -exec autopep8 --in-place "{}" \;
  ```

## Configuration

I maintain a set of default configuration files in my [`dotfiles` repository](https://github.com/kdeldycke/dotfiles):

- PDB: [`~/.pdbrc`](https://github.com/kdeldycke/dotfiles/blob/main/dotfiles/.pdbrc)
- Pip: [`~/.pip/pip.conf`](https://github.com/kdeldycke/dotfiles/blob/main/dotfiles/.pip/pip.conf)
- PyPI: [`~/.pypirc`](https://github.com/kdeldycke/dotfiles/blob/main/dotfiles/.pypirc)
- Pycodestyle: [`~/.config/pycodestyle`](https://github.com/kdeldycke/dotfiles/blob/main/dotfiles/.config/pycodestyle)
- PyLint: [`~/.pylintrc`](https://github.com/kdeldycke/dotfiles/blob/main/dotfiles/.pylintrc)

## Package Management

- Generate a binary distribution of the current package:

  ```shell-session
  $ python ./setup.py sdist
  ```

- Register, generate and upload to [PyPI](https://pypi.python.org) the current package as a source package, an egg and a dumb binary:

  ```shell-session
  $ python ./setup.py register sdist bdist_egg bdist_dumb upload
  ```

- Download Pygments' source distribution from PyPI, without dependencies ([source](https://stackoverflow.com/a/56773693)):

  ```shell-session
  $ pip download --no-binary=:all: --no-deps pygments==2.14.0
  ```

- Hackish way to execute the CLI above with Pip's internal (tested with `pip==22.1`), [inspired by `pip._internal.cli.base_command.Command._main()`](https://github.com/pypa/pip/blob/ba38c33/src/pip/_internal/cli/base_command.py#L105-L114):

  ```python
  from pathlib import Path

  from pip._internal.cli.status_codes import SUCCESS
  from pip._internal.commands.download import DownloadCommand
  from pip._internal.utils.temp_dir import global_tempdir_manager, tempdir_registry


  tmp_path = Path("/tmp")

  # Emulate the following CLI call:
  #   $ pip download --no-binary=:all: --no-deps pygments==2.14.0
  cmd = DownloadCommand(name="dummy_name", summary="dummy_summary")

  with cmd.main_context():
      cmd.tempdir_registry = cmd.enter_context(tempdir_registry())
      cmd.enter_context(global_tempdir_manager())
      options, args = cmd.parse_args([
          "--no-binary=:all:",
          "--no-deps",
          "--dest",
          f"{tmp_path}",
          f"pygments==2.14.0",
      ])
      cmd.verbosity = options.verbose
      outcome = cmd.run(options, args)
      assert outcome == SUCCESS

  package_path = tmp_path.joinpath("Pygments-2.14.0.tar.gz")
  assert package_path.is_file()
  ```

## Jinja

To generate curly braces:

```pycon
>>> from jinja2 import Template
>>> Template(""" Yo! """).render()
u' Yo! '
>>> Template(""" {{'{{'}} """).render()
u' {{ '
>>> Template(""" {{'{'}} """).render()
u' { '
>>> Template(""" {{'{'}}machin{{'}'}} """).render()
u' {machin} '
```

## Data

- [Pandas snippets]({filename}/2015/pandas-snippets.md)
