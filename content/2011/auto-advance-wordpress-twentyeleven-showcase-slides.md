---
date: '2011-12-27'
title: Auto-advance WordPress' TwentyEleven showcase slides
category: English
tags: javascript, showcase, Template, Theme, twentyeleven, WordPress
---

WordPress default theme, [TwentyEleven](https://theme.wordpress.com/themes/twentyeleven/), has a built-in [showcase mode](https://twentyelevendemo.wordpress.com/showcase/) that is displaying a set a slides (composed of sticky posts) at the top of a page. This mode can be activated by creating a static page and set its _Template_ page attribute to _Showcase Template_.

The problem with this mode to me was the lack of an auto-advance feature that will cycle through the slides every X seconds. Luckily I [found a way](https://pastebin.com/s6JEthVi) to automate implement this with some lines of JavaScript:

```html
<script charset="utf-8" type="text/javascript">
 // Auto-advance the showcase slider
  // Source: https://pastebin.com/s6JEthVi
  jQuery(document).ready(function(){
    var change_every = 5; // The number of seconds that the slider will auto-advance in
    var current = 1;
    function auto_advance(){
      if(current == -1) return false;
      jQuery('.feature-slider a').eq(current % jQuery('.feature-slider a').length).trigger('click', [true]);
      current++;
    };
    setInterval(function(){auto_advance()}, change_every * 1000);
  });
</script>
```

All you have to do is to embed this snippet of code within your home page. It could either be in the static page you use as a showcase template or in a showcase widget. The latter is the exact same method I used earlier that year to [customize CSS in WordPress without messing with the original code]({filename}/2011/new-blog-header-and-tiny-wordpress-theme-customizations.md).

And of course this code is currently live at the front page of that very blog.
