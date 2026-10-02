---
date: '2008-07-31'
title: How-to fix ruby's FeedTools latin-1 parsing
category: English
tags: feed, FeedTools, parsing, patch, RSS, Ruby, Ruby on Rails
---

![FeedTools logo, a yellow diamond road sign with a fork and knife merged into a single outline](feedtools-logo.png)

While playing with [FeedTools](https://sporkmonger.com/projects/feedtools/), a ruby library to parse RSS (or other) feeds, I've spotted a strange behavior, that at first looks like typical unicode parsing issue. So I've started to check that the original feed was encoded in the right format, and that its charset was clearly set to the right value. But I found nothing wrong... So I dug in the [FeedTools source code](https://feedtools.rubyforge.org/svn/trunk/), and what I found is particularly disappointing...

FeedTools do a really nice job to detect the charset and handle feed's data. So when it encounter [HTML entities](https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references), it decode them to plain text. That's good as at the end you get ready-to-use strings. Unfortunately, the method it use, [CGI::unescapeHTML](https://www.noobkit.com/show/ruby/ruby/standard-library/cgi/unescapehtml.html), stick too much to the [W3C specification](https://www.w3.org/TR/xhtml1/DTD/xhtml-lat1.ent), which state that some of the HTML entities (if not all) are the expression of latin-1 characters. Hence the presence of latin-1 characters in pure UTF-8 RSS feeds...

To fix that, I've recoded the [FeedTools::HtmlHelper.unescape_entities()](https://rubyfurnace.com/docs/feedtools-0.2.26/classes/FeedTools/HtmlHelper.html#M007308) method to convert each HTML entity it encounter to pure unicode. Here is the monkey patch I call by default from the `environment.rb` file of all my [Ruby on Rails](https://rubyonrails.org) projects:

```ruby
require 'feed_tools'

# Monkey patch feed tool.
# Use case mixed UTF-8 chars and html entities: <description>Téléchargements et Multim&#233;dia</description>
module FeedTools::HtmlHelper
  class << self

    # Force UTF-8 conversion of HTML entities with number lower than 256.
    # Based on CGI::unescapeHTML method.
    def convert_html_entities_to_unicode(string)
      string.gsub(/&(.*?);/n) do
        $KCODE = "UTF8"
        match = $1.dup
        case match
        when /\A#0*(\d+)\z/n       then
          if Integer($1) < 256
            [Integer($1)].pack("U")
          else
            "&##{$1};"
          end
        when /\A#x([0-9a-f]+)\z/ni then
          if $1.hex < 256
            [$1.hex].pack("U")
          else
            "&#x#{$1};"
          end
        else
          "&#{match};"
        end
      end
    end

    # Patch unescape_entities() method
    alias_method :unescape_entities_orig, :unescape_entities
    def unescape_entities(html)
      return unescape_entities_orig(convert_html_entities_to_unicode(html))
    end

  end
end
```

Ok, so this fix the issue.

But I'm not comfortable about this problem not solved cleanly. I still don't have a clue about which component should solve the problem definitively. But I have some ideas... Here are my propositions:

1. Submit my monkey patch to FeedTools project for integration, or
2. Merge my monkey patch upstream in legacy ruby CGI library, or
3. Do not allow usage of HTML entities in feeds.
