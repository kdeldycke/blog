---
date: '2009-03-18'
title: A fix to xkcd's emoticons + parentheses problem
category: English
tags: emoticons, geek, typography, unicode, UTF-8, xkcd
---

[![xkcd-emoticons-with-parentheses-problem-exposed](xkcd-emoticons-with-parentheses-problem-exposed.png)](https://xkcd.com/541/)

[xkcd comic #541 (titled "TED Talk")](https://xkcd.com/541/) expose a problem I've long been aware of: _how do you end parenthetical statements with emoticons?_

Randall reveal two possible solutions:

1. ... Linux (or BSD :) would...

2. ... Linux (or BSD :) ) would...

Of course, none of these are acceptable! But today, I think I've found the definitive solution...

As you may know, unicode comes with loads of weird characters. The weirdest are called [dingbats](https://wikipedia.org/wiki/Dingbat). Beside this family, you'll find [the weirdest of the weirdest](https://wikipedia.org/wiki/Miscellaneous_Symbols), which contain 2 interesting symbols:

- ☹ (aka [white frowning face](https://www.fileformat.info/info/unicode/char/2639/index.htm))

- ☺ (aka [white smiling face](https://www.fileformat.info/info/unicode/char/263a/index.htm))

So using the latest, our statement become:

> ... Linux (or BSD ☺) would...

Problem solved! :D
