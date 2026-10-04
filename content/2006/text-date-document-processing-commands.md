---
date: '2006-12-13'
title: Text, Date & Document processing commands
category: English
tags: calendar, CLI, date, epoch, find, Linux, recode, sed, VIM, Markdown, Perl, Regular expression, Amazon
---

## Search

- Count the number of lines with at least one occurrence of the `y` character:

  ```shell-session
  $ cat test.txt
  asd  dd :; >
  y YYYyy  yyy
   .

  asdkjlyes
      kjkjhkjhy

  $ grep -o '.*y.*' ./test.txt | wc -l
  3
  ```

## Replace

- Text replacement:

  ```shell-session
  $ sed 's/string to replace/replacement string/g' original-file.txt > new-file.txt
  ```

- Dynamic, in-place replacement of `unreleased` text with today's date:

  ```shell-session
  $ sed -i "s/unreleased/`date +'%Y-%m-%d'`/" ./changelog.md
  ```

- Update the release date in `citation.cff` file:

  ```shell-session
  $ perl -pi -e "s/date-released: \d+-\d+-\d+/date-released: $(date +'%Y-%m-%d')/" ./citation.cff
  ```

- Replace all occurrences of `str1` by `str2` in all files below the `/folder` path:

  ```shell-session
  $ find /folder -type f -print -exec sed -i 's/str1/str2/g' "{}" \;
  ```

- Same as above but ignore all content of `.svn` folders and `.zip` files:

  ```shell-session
  $ find /folder -type f -not -regex ".*\/\.svn\/.*" -not -iname "*\.zip" -print -exec sed -i 's/str1/str2/g' "{}" \;
  ```

- Remove trailing spaces and tabs in every XML files:

  ```shell-session
  $ find /folder -iname "*.xml" -exec sed -i 's/[ \t]*$//' "{}" \;
  ```

- Place a new `---` line at the start of each `.markdown` files ([see result](https://github.com/kdeldycke/blog/commit/19d1b082e93966f82873ce9d8de238a889d371b7)):

  ```shell-session
  $ find ./folder -iname "*.markdown" -exec sed -i '1s/^/---\n/' "{}" \;
  ```

- Place a new `---` line before the first empty line of each `.markdown` files ([see result](https://github.com/kdeldycke/blog/commit/8628d53284e41917159e344ea45ad9e9d16b90b1)):

  ```shell-session
  $ find ./folder -iname "*.markdown" -exec sed -i '0,/^$/s//---\n/' "{}" \;
  ```

- Remove lines starting with `prefix1:` or `prefix2:` in all `.markdown` files:

  ```shell-session
  $ find /folder -iname "*.markdown" -exec perl -p -i -e 's/(prefix1|prefix2): .*\n//sg' "{}" \;
  ```

- Strip time from `date:` prefixed lines and quote the value. I.e. replace all occurrences of `date: 2012-01-01 00:00:00 +0000` by `date: "2012-01-01"`:

  ```shell-session
  $ find /folder -iname "*.markdown" -exec perl -p -i -e 's/date: (\d+-\d+-\d+) .*\n/date: "$1"\n/sg' "{}" \;
  ```

- Remove in all `.markdown` files all occurrences of Amazon's pixel tracking links in the form of `![](https://www.assoc-amazon.com…)`:

  ```shell-session
  $ find ./* -iname "*.md" -exec perl -0777 -i -pe "s/\!\[\]\(https:\/\/www\.assoc-amazon\.com.*?\)//gs" "{}" \;
  ```

- Shorten in all `.markdown` files Amazon' product URLs from `(https://www.amazon.com/dp/B00F3F0GLU/?tag=accounid-20)` to `(https://amzn.com/B00F3F0GLU/?tag=accounid-20)`:

  ```shell-session
  $ find ./* -iname "*.md" -exec perl -0777 -i -pe "s/\(https:\/\/www\.amazon\.com\/dp\/(.*?)\)/\(https:\/\/amzn\.com\/\1\)/gs" "{}" \;
  ```

- Remove lines matching a regex (encoding [particular markdown TOC entries](https://github.com/kdeldycke/awesome-iam/blob/295a4fa4229c5966ce4bc207704e32fb6f1491d6/.github/workflows/lint.yaml#L24)), save the result in place and save a backup of the original content in a `.bak` file:

  ```shell-session
  $ gawk -i inplace -v INPLACE_SUFFIX=.bak '!/^- \[(Contribute|Contributing|Licence|License)\]\(#.+\)$/{print}' ./readme.md
  ```

- Use [`sed` address ranges](https://www.linuxtopia.org/online_books/linux_tool_guides/the_sed_faq/sedfaq3_006.html)
  to spot, in a Markdown file, all blocks led by a
  `:::` directive, and terminated by a blank line. Then replace in each of
  these matched blocks the `a` letter by `XXX`. Notice how `a` occurrences
  outside the blocks are not replaced by `XXX`:

  ```{.shell-session hl_lines="19" anchorlinenos=True}
  $ cat ./example.md

  This is a code block:

  :::shell-session
  → apache
  → java
  → python

  This is another block:

  :::shell-session
  → rust
  → haskell
  → javascript

  This is a random sentence.

  $ sed "/^:::/,/^$/ s/a/XXX/g" ./example.md

  This is a code block:

  :::shell-session
  → XXXpXXXche
  → jXXXvXXX
  → python

  This is another block:

  :::shell-session
  → rust
  → hXXXskell
  → jXXXvXXXscript

  This is a random sentence.
  ```

- In the same spirit as above but this time to spot indented blocks
  starting with `:::`, then wrap them into triple-backticks fences:

  ````{.shell-session hl_lines="19 20 21"}
  $ cat ./example.md

  This is a code block:

      :::shell-session
      → apache
      → java
      → python

  This is another block:

      :::shell-session
      → rust
      → haskell
      → javascript

  This is a random sentence.

  $ find ./folder -iname "*.md" \
  > -exec sed -i "/^    :::/,/^$/ s/^$/    \`\`\`\n/" "{}" \; \
  > -exec sed -i "/^    :::/,/^$/ s/:::/\`\`\`/"      "{}" \;

  $ cat ./example.md

  This is a code block:

      ```shell-session
      → apache
      → java
      → python
      ```

  This is another block:

      ```shell-session
      → rust
      → haskell
      → javascript
      ```

  This is a random sentence.
  ````

- Strip in-place the block of text starting with `XXX` and ending with an empty line:

  ```{.shell-session hl_lines="12"}
  $ cat ./example.md

  This is a code block:

  XXX{shell-session}
  → apache
  → java
  → python

  This is a random sentence.

  $ perl -i -ne "print if not /XXX/ .. /^$/" ./example.md

  $ cat ./example.md

  This is a code block:

  This is a random sentence.
  ```

- Same as above, but with `sed`:

  ```shell-session
  $ sed -i "/^XXX/,/^$/ d" ./example.md
  ```

- Python one-liner to delete the first occurrence of a block of text delimited by triple-backticks fences. Contrary to methods above, this one is not distracted by blank lines within the text block:

  ```shell-session
  $ python -c 'import re; from pathlib import Path; file = Path("./example.md"); file.write_text(re.sub(r"^\`\`\`.*?\`\`\`\n\n", "", file.read_text(), count=1, flags=re.MULTILINE | re.DOTALL))'
  ```

- Append the content of the `addendum.txt` file to all `.markdown` files:

  ```shell-session
  $ find ./folder -iname "*.markdown" -print -exec bash -c 'cat ./addendum.txt >> "{}"' \;
  ```

- Replace all accentuated characters by their non-accentuated variants (thanks Matthieu for the tip):

  ```shell-session
  $ echo "éÈça-$" | iconv -t ASCII//translit
  ```

## Date & Time

- Get the date of last week:

  ```shell-session
  $ date +"%Y-%m-%d" -d last-week
  ```

- Get the current date in english:

  ```shell-session
  $ env LC_TIME=en date +"%a %b %d %Y"
  ```

- Get the number of seconds since [epoch](https://en.wikipedia.org/wiki/Epoch_%28computing%29#Notable_epoch_dates_in_computing):

  ```shell-session
  $ date +%s
  ```

- Convert back epoch time to human-readable date:

  ```shell-session
  $ date --date=@1234567890
  ```

## Transcoding

- In place charset transcoding:

  ```shell-session
  $ recode utf-8..latin-1 utf8text.txt
  ```

## Edition

- VIM: [no autoindent on paste](https://vim.wikia.com/wiki/How_to_stop_auto_indenting).
- [Get rid of Non-Breaking space](https://hauweele.net/~gawen/blog/?p=32) on Linux systems by the way X.org's `~/.xmodmap` config file.

## Additional References

- [CLI text processing with GNU awk](https://learnbyexample.github.io/learn_gnuawk/awk-introduction.html)
- A list of [`sed` one-liners](https://web.archive.org/web/20061213120811/http://sed.sourceforge.net/sed1line.txt).
- [PDF commands]({filename}/2006/pdf-commands.md)
