---
date: '2013-01-22'
title: WordPress to Disqus Migration
category: English
tags: Comment, Disqus, HTML, migration, MySQL, SQL, Regular expression, WordPress, Perl
---

I've just finished migrating all the comments of this blog from WordPress to
[Disqus](https://disqus.com). Why using an external comment platform? It's just
that I plan to ditch WordPress entirely, and switch to a static site generator
in the near future. Here are some details on my migration to Disqus.

Disqus has everything you need to easily import WordPress comments. But first,
I had to massage some data.

Articles of this blog features a lots of code. Comments are no exception and
embed snippets too. Code blocks are rendered by the [SyntaxHighlighter Evolved
WordPress plugin](https://wordpress.org/extend/plugins/syntaxhighlighter/). This
extension use square brackets to enclose code. [Disqus uses standard HTML
tags](https://web.archive.org/web/20130129203443/http://help.disqus.com/customer/portal/articles/665057).

Let's update this notation directly in WordPress database:

```shell-session
$ mysqldump --opt kevblog wp_comments > ./comments.sql
$ perl -pe 's/\[code lang=(.*?)\]/<pre><code class=\1>/g' ./comments.sql > comments-fixed.sql
$ sed -i 's/\[\/code\]/<\/code><\/pre>/g' ./comments-fixed.sql
$ mysql kevblog < ./comments-fixed.sql
```

[Disqus doesn't support HTML
lists](https://help.disqus.com/customer/portal/articles/466253-what-html-tags-are-allowed-within-comments).
So I manually updated WordPress comments to remove occurrences of `<ul>` and
`<ol>`, and replace `<li>` by an UTF-8 `•`
[bullet](https://en.wikipedia.org/wiki/Bullet_%28typography%29).

Another issue: if [Disqus support images in
comment](https://web.archive.org/web/20130125092858/http://blog.disqus.com/post/3764930816/fun-with-images), in imported
comments they are left as HTML tags and therefore not rendered by Disqus. I was
the only one on my blog posting images in comments. So I simply moved them to
the corresponding parent article.

I then had to fix the comment threading. In the first versions of WordPress,
sub-commenting was not supported. I addressed this issue by recomposing
threading with a series of MySQL queries:

```mysql
UPDATE `wp_comments` SET `comment_parent` = 234   WHERE `comment_ID` = 342;
UPDATE `wp_comments` SET `comment_parent` = 4987  WHERE `comment_ID` = 5667;
UPDATE `wp_comments` SET `comment_parent` = 10915 WHERE `comment_ID` = 10916;
(...)
```

After all these updates, my comments where ready to be [exported to
Disqus](https://help.disqus.com/customer/portal/articles/466255-exporting-comments-from-wordpress-to-disqus).

If most of my comments were successfully imported, some were left-out. The
importer was not able to find their parents:

![Disqus comment import: unable to find parent
post](disqus-import-error.png)

But the reported error was not true: parent's IDs were good and referenced an
existing comment. Besides, comments Disqus was not able to import were
correctly placed in their thread on my original WordPress blog.

For a moment I trough Disqus import code was [subject to a race
condition](https://groups.google.com/d/topic/disqus-dev/LqCcFy67RJY/discussion).
But there was no `<wp:comment_parent />` tags in my XML file.

I also checked that no comment were moderated:

```shell-session
$ grep -c "<wp:comment_approved>0</wp:comment_approved>" ./kevindeldycke.wordpress.2013-01-15-fixed.xml
0
$ grep -c "<wp:comment_approved>1</wp:comment_approved>" ./kevindeldycke.wordpress.2013-01-15-fixed.xml
892
```

I decided to check the comments carefully. Following the chain of comment's
parents, I found the root cause. All unimported comments were descendants of an
anonymous commenter. These shared the following empty properties:

```text
<wp:comment_author><![CDATA[]]></wp:comment_author>
<wp:comment_author_email></wp:comment_author_email>
```

I then decided to forced anonymous comments to bear a generic author's name:

```shell-session
$ perl -0p -e 's/(<wp:comment_author><!\[CDATA\[)(\]\]><\/wp:comment_author>\s*<wp:comment_author_email><\/wp:comment_author_email>)/\1Anonymous\2/sg' ./kevindeldycke.wordpress.2013-01-15-fixed.xml > test.xml
```

Resulting in the following changes:

```diff
--- ./kevindeldycke.wordpress.2013-01-15-disqus-import-fixed.xml        2013-01-15 11:24:06.929837283 +0100
+++ ./test.xml  2013-01-27 16:19:00.062626017 +0100
@@ -6595,7 +6595,7 @@
    </wp:postmeta>
    <wp:comment>
      <wp:comment_id>1883</wp:comment_id>
-     <wp:comment_author><![CDATA[]]></wp:comment_author>
+     <wp:comment_author><![CDATA[Anonymous]]></wp:comment_author>
      <wp:comment_author_email></wp:comment_author_email>
      <wp:comment_author_url></wp:comment_author_url>
      <wp:comment_author_IP>123.45.67.89</wp:comment_author_IP>
@@ -8376,7 +8376,7 @@
    </wp:comment>
    <wp:comment>
      <wp:comment_id>2382</wp:comment_id>
-     <wp:comment_author><![CDATA[]]></wp:comment_author>
+     <wp:comment_author><![CDATA[Anonymous]]></wp:comment_author>
      <wp:comment_author_email></wp:comment_author_email>
      <wp:comment_author_url></wp:comment_author_url>
      <wp:comment_author_IP>123.45.67.89</wp:comment_author_IP>
(...)
```

I then sent the fixed WordPress XML export to Disqus as-is, which imported my
24 missing comments:

![Disqus comment import: missing comments
imported](disqus-import-complete.png)
