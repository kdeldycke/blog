---
date: '2011-01-18'
title: New blog header and tiny WordPress theme customizations
category: English
tags: artwork, CSS, maomium, WordPress, Ubercart
---

I maintain a bunch of websites for friends on my server. In this context, [Maomium](https://maomium.com)'s owner owed me some bucks for his `.com` domain name. Here is the envelope I received yesterday with a check:

![Hand-addressed kraft envelope with French stamps lying on dark wood, next to the card it held: a pen-and-ink bird of prey trailing swirling tendrils, under a round monogram](maomium-thank-you-artwork.jpg)

Now that's what I call a personalized letter! This original artwork is so great that I had to share it.

The hours he put creating this original artwork mirror the effort I invested maintaining his digital properties (a [WordPress blog](https://maomium.com), a [Drupal-based online store](https://www.ubercart.org) and a [ZenPhoto gallery](https://maomium.com/zenphoto/)). That's the best thank you note I have received so far! :)

Jim from Maomium is a really talented artist and really deserve attention. He used to have an [online shop](https://shop.maomium.com) where you can buy his paintings and customized furnitures. But we shut it down some weeks ago. Its replacement is not available yet, so if you want to buy him unique hand-made piece of art, don't hesitate to get in touch with him at [jim@maomium.com](mailto:jim@maomium.com).

And with Jim's approval, I now use his letter's artwork as my blog image header. It's much better than the default theme image! ;)

Talking about this , here is a quick tip to make minimal design changes to a WordPress theme. The idea is to put custom CSS directives in a widget, as below:

![WordPress text widget holding a small inline stylesheet that zeroes the header padding and hides the site title and description](wordpress-widget-with-inline-css-customizations.png)

As widgets are site-wide, all these CSS customizations will be applied everywhere. Here is for example the code I applied on this site to hide blog's name and description from [TwentyTen](https://wordpress.org/extend/themes/twentyten)'s header:

```html
<style type="text/css">
 <!--
#header {
  padding-top: 0;
}
#site-title a, #site-description {
  display: none;
}
-->
</style>
```

This quick and dirty hack is perfect for tiny customizations. It will make your CSS easier to maintain as you don't have to modify the core style files or create a child theme.

## Update (Aug. 2011)

As I moved from TwentyTen to the new TwentyEleven default WordPress theme, I just updated the header.

For archive, here is the customized header I used with TwentyTen:

![The artwork cropped into a wide blog banner, the inked bird and tendrils fading into a grey gradient with the name lettered in the middle](maomium-artwork-banner.jpeg)
