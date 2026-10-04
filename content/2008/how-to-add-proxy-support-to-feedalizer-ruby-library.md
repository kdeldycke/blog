---
date: '2008-07-16'
title: How-to add proxy support to Feedalizer ruby library
category: English
tags: feed, feedalizer, hpricot, HTTP, parsing, proxy, RSS, Ruby, Ruby on Rails
---

![Feedalizer wordmark in a serif face with the red RSS icon standing in for the final letter](feedalizer.png)

Here is a little code snippet which
[monkey-patch](https://en.wikipedia.org/wiki/Monkey_patch)
[Feedalizer](https://qerub.se/feedalizer) to let it grab web content
through a HTTP proxy:

```ruby
# HTTP proxy settings
HTTP_PROXY_HOST = "123.456.78.90"
HTTP_PROXY_PORT = 8080

# Calculate proxy URL
HTTP_PROXY_URL = "http://#{HTTP_PROXY_HOST}:#{HTTP_PROXY_PORT}"

# Monkey patch feedalizer to support page grabbing through a proxy
require 'feedalizer'
class Feedalizer
  # Backup original grab_page method
  alias_method :grab_page_orig, :grab_page
  # Define new grab_page() method with proxy support
  def grab_page(url)
    open(url, :proxy => HTTP_PROXY_URL) { |io| Hpricot(io) }
  end
end
```

This fix, written for a [Ruby on Rails](https://rubyonrails.org)-based
project, lay in the `environment.rb` file, but I wonder if this is the right
place and the right way of doing it... Anyway, it works for me! :)

**Update**: A [post from Matthew Higgins' blog that answer my
question](https://web.archive.org/web/20080716184328/http://www.strictlyuntyped.com/2008/06/rails-where-to-put-other-files.html)
above has just shown up in my feed aggregator. What's he telling us? That I'm a
naughty programmer :

> Previous to 2.0, naughty developers pasted code at the bottom of
> `environment.rb`, and the `config/initializer` folder was a welcome convention
> to help organize this madness.

For your instance, the code in this post is extracted from an "old" (prior to
RoR 2.0) project, thus explaining my naughtyness... ;)
