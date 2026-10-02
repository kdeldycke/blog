---
date: '2013-02-06'
title: WordPress to Pelican
category: English
tags: WordPress, Pelican, Python, migration, PHP, MySQL, sed, Markdown, reStructuredText, ZenPhoto, Cool Cavemen, Regular expression
---

You probably noticed this blog dramatically changed lately and was sometimes
broken. That's because I was in the middle of migrating it from
[WordPress](https://wordpress.org) to a static site generator.

In the last few years, tweaking and maintaining my server proved to be a
challenging but rewarding experience. Most of the [knowledge I
acquired]({tag}debian) in the process has landed in
my bag of tricks and makes me more productive than I was before.

But now that I've learned what I had to learn, the adventure turned into a
chore. It's time to save time. And money. And ditch this machine for good.

Another factor in this decision was [the end of Cool
Cavemen](https://coolcavemen.com/2012/12/22/cool-cavemen-the-end/). My band
announced their last album to be released this year. Since the beginning we
were armed with a website, an online shop, multiple internal tools and a strong
web presence to support our activities. There's no longer any need of all of
these.

So I closed the [Drupal
shop]({filename}/2011/chose-ubercart-magento-oscommerce.md)
and [moved it to
Bandcamp](https://coolcavemen.com/2012/05/27/cool-cavemen-bandcamp-baisse-prix/).
I merged [ZenPhoto galleries into
WordPress]({filename}/2012/zenphoto-wordpress-migration.md).
All WordPress sites I hosted [moved to
wordpress.com](https://en.support.wordpress.com/moving-a-blog/#moving-from-wordpress-org).
bbPress forums were closed: I [archived private forums to
emails]({filename}/2012/converting-bbpress-forum-mailbox-archive.md),
and [public ones to plain WordPress
content]({filename}/2012/transfer-bbpress-to-plain-wordpress.md).
As for Mailman mailing-lists, they were archived and the ones remaining active
moved to Google Groups.

Listing all of this work today makes me realize that I spent most of 2012
preparing the retirement of my server. And my band. Until only one thing
remained: this blog.

The next evolution of this site couldn't be anything but a bunch of statically
generated pages. First, static websites are cool. They're also fast and cheap.
And they don't requires a [full nginx/PHP/MySQL
stack]({filename}/2011/nginx-php-fpm-mysql-debian-squeeze-server.md)
to be managed, upgraded and
[monitored]({filename}/2011/munin-monitor-debian-squeeze-server.md).

I started my quest for a tool:

- written in Python,
- supporting Markdown and
- supported by an active community.

After a little survey, the remaining contenders were
[Pelican](https://getpelican.com) and [Nikola](https://nikola.ralsina.com.ar).

If I like Nikola for its fast release cycles and huge list of configurable
features, I ultimately choose Pelican. I found it was easier for the latter to
naturally match my previous WordPress URLs (good for SEO).

So, let's install Pelican and its dependencies:

```shell-session
$ aptitude install python-markdown python-pygments python-beautifulsoup pandoc
$ pip install pelican mdx_video
```

And create a new site:

```shell-session
$ mkdir blog
$ cd ./blog/
$ pelican-quickstart
Welcome to pelican-quickstart v3.1.1.

This script will help you create a new Pelican-based website.

Please answer the following questions so this script can generate the files needed by Pelican.

> Where do you want to create your new web site? [.]
> What will be the title of this web site? Kevin Deldycke
> Who will be the author of this web site? Kevin Deldycke
> What will be the default language of this web site? [en]
> Do you want to specify a URL prefix? e.g., http://example.com   (Y/n) Y
> What is your URL prefix? (see above example; no trailing slash) https://kevin.deldycke.com
> Do you want to enable article pagination? (Y/n) n
> Do you want to generate a Makefile to easily manage your website? (Y/n) Y
> Do you want an auto-reload & simpleHTTP script to assist with theme and site development? (Y/n) Y
> Do you want to upload your website using FTP? (y/N)
> Do you want to upload your website using SSH? (y/N) Y
> What is the hostname of your SSH server? [localhost]
> What is the port of your SSH server? [22]
> What is your username on that server? [root]
> Where do you want to put your web site on that server? [/var/www]
> Do you want to upload your website using Dropbox? (y/N) N
Done. Your new project is available at /home/kevin/blog
```

Basically, that's it. You're now free to tweak the configuration and structure
of your site.

The next important step is to migrate our content. We can't import the XML file
WordPress produces as is. We need to massage some data first.

During my [Disqus
migration]({filename}/2013/wordpress-disqus-migration.md), I
had to update the markup of the code blocks. Same thing apply here. I need to
replace occurrences of:

```bbcode
[code lang="shell"]
(...)
[/code]
```

by this kind of pure HTML:

```html
<pre><code class="shell">
(...)
</code></pre>
```

The magic command to perform that job is:

```shell-session
$ sed -e 's/\[\/code\]/<\/code><\/pre>/g' -e 's/\[code lang=\(.*\)\]/<pre><code class=\1>/g' < ./wordpress.xml > ./wordpress-fixed.xml
```

Pelican consumes by default
[reStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) content, but
it supports [Markdown](https://en.wikipedia.org/wiki/Markdown) too. To convert
WordPress content to Markdown, the command is:

```shell-session
$ pelican-import --wpfile -m markdown -o ./content/ ./wordpress-fixed.xml
```

The thing is, Pelican's built-in importer produces files requiring, in my
opinion, too much cleaning afterwards.

I was right to choose Markdown over reStructuredText: the former is much more
popular that the latter. Plenty of tools are available.
[exitwp](https://github.com/thomasf/exitwp) is the one I was looking for. It's
a WordPress to Jekyll importer written in Python.

Let's fetch it:

```shell-session
$ git clone https://github.com/thomasf/exitwp
```

Before using it, I had to apply a tiny patch to transform Jekyll metadata to
Pelican's:

```shell-session
$ cd exitwp
$ git rev-parse HEAD
f62d758e853bb718cd013aa808e9b8aaae5df1df
$ git diff
```

```diff
diff --git a/exitwp.py b/exitwp.py
index fad5a4e..61e626e 100755
--- a/exitwp.py
+++ b/exitwp.py
@@ -265,7 +265,7 @@ def write_jekyll(data, target_format):
            yaml_header['published'] = False

        if i['type'] == 'post':
-            i['uid'] = get_item_uid(i, date_prefix=True)
+            i['uid'] = get_item_uid(i, date_prefix=False)
            fn = get_item_path(i, dir='_posts')
            out = open_file(fn)
            yaml_header['layout'] = 'post'
@@ -311,13 +311,15 @@ def write_jekyll(data, target_format):
                        continue
                    tax_out[t_name].append(tvalue)

-            out.write('---\n')
            if len(yaml_header) > 0:
                out.write(toyaml(yaml_header))
            if len(tax_out) > 0:
-                out.write(toyaml(tax_out))
+                for tax_type, tax_values in tax_out.items():
+                    if tax_type == 'categories':
+                        tax_type = 'category'
+                    out.write("%s: %s\n" % (tax_type, ', '.join(tax_values)))
+            out.write('\n')

-            out.write('---\n\n')
            try:
                out.write(html2fmt(i['body'], target_format))
            except:
```

Now call exitwp and move all Markdown files to Pelican:

```shell-session
$ rm -f ./wordpress-xml/*
$ rm -rf ./build
$ cp ../wordpress-fixed.xml ./wordpress-xml/
$ python exitwp.py
$ cd ..
$ mv ./exitwp/build/jekyll/kevin.deldycke.com/_posts/* ./content/
$ rename "s/\.markdown/\.md/g" ./content/*.markdown
```

We still have to clean-up articles. Like convert HTML code blocks to use
Pelican's tag:

```shell-session
$ find ./content/ -iname "*.md" -exec perl -0777 -i -pe "s/<code class=\"(.*?)\">(.*?)<\/code>/:::\1\2/gs" "{}" \;
```

We can also fix some metadata like authors, and misquoted titles produced by
exitwp:

```shell-session
$ find ./content/ -iname "*.md" -exec sed -i 's/Author: Admin/Author: Kevin Deldycke/' "{}" \;
$ find ./content/ -iname "*.md" -exec sed -i "s/^title: '\(.*\)'/title: \1/" "{}" \;
```

I'll take the opportunity to consolidate some tags:

```shell-session
$ find ./content/ -iname "*.md" -exec sed -i "s/tags:\(.*\)leopard\(.*\)/tags:\1Mac OS X Leopard\2/" "{}" \;
$ find ./content/ -iname "*.md" -exec sed -i "s/tags:\(.*\), Mac,\(.*\)/tags:\1, MacBook,\2/" "{}" \;
```

I also had to fix my YouTube's tags:

```shell-session
$ find ./content/ -iname "*.md" -exec sed -i "s/^\[youtube \(.*\)/\1/g" "{}" \;
$ find ./content/ -iname "*.md" -exec sed -i "s/\?rel=0\]$//g" "{}" \;
$ find ./content/ -iname "*.md" -exec sed -i "s/\&rel;=0\]$//g" "{}" \;
```

I decided to get rid of all image thumbnails generated by WordPress. With the
command below, I reduced all my thumbnails linking to their full-size version,
to their full-size version only:

```shell-session
$ find ./content/ -iname "*.md" -exec sed 's/\[!\[\(.*\)\](.*)\](\(.*\).\(jpe\?g\|png\|gif\))/!\[\1\](\2.\3)/g' "{}" \;
```

You're now ready to publish your site to the world:

```shell-session
$ make clean
$ make ssh_upload
```

If you need an example or inspiration, my [current Pelican blog, its theme,
configuration and content are all available on
GitHub](https://github.com/kdeldycke/blog).
