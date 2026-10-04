---
date: '2011-03-21'
title: Why I chose Ubercart instead of Magento or osCommerce.
category: English
tags: CMS, Drupal, Magento, osCommerce, Online Store, Ubercart
---

About a year ago a friend asked me why I chose the
[Ubercart](https://web.archive.org/web/20100228034803/http://www.ubercart.org/)/[Drupal](https://drupal.org) combo as the
engine for [Cool Cavemen's online shop](https://coolcavemen.bandcamp.com). He
specifically asked me why not choose [Magento](https://web.archive.org/web/20110321222912/http://www.magentocommerce.com/)
or [osCommerce](https://www.oscommerce.com). I never really took the time to
answer him. Let's fix this.

First, I selected a couple of web eCommerce solution based on the same
[requirements upon which I choose WordPress]({filename}/2006/e107-to-wordpress-migration-here-is-why.md)
some years ago. Namely:

- Open-source free software
- Active project
- Healthy community

I excluded osCommerce right away. I quickly played with it in 2005 and in 2007
for projects that never came to fruition. And I keep a really bad memory of
these experiences: both code and templates felt poorly designed and implemented.
That's why osCommerce is classified in my brain as a giant legacy code base,
hard to maintain. Maybe the project has evolved a lot since then. I should have
looked back at it, but was attracted by another project...

...which was Magento. So yes, I seriously considered to use Magento at some
point. It looked great. And clean. But digging deeper I found that something was
missing.

My shop was supposed to sell tee-shirts for the band. And a tee-shirt is a
product that can have lots of variations:

- different colors (white, black, yellow, ...),
- of different sizes (S, M, L, X, XL, ...),
- in different shapes (teeshirt, hoodie, sweatshirt, ...),
- for different peoples (guy, girl, baby, ...).

I wanted to track stocks and prices for each combination. And this degree of
complexity is not supported by Magento. To be fair, I remember to have heard of
this feature, but was only available in a third party module (that I don't
remember the name). Alas, this module was proprietary. That is the main reason I
discarded Magento.

And then I found Ubercart, which allowed me to do exactly what I wanted. Here is
for example prices and stocks for a
black Cool Cavemen tee-shirt (`https://coolcavemen.bandcamp.com/merch/white-tee-shirt-black-logo`):

![Ubercart options tab for a black tee-shirt, listing men's sizes L to 2XL and women's sizes with cost, price and weight fields for each](ubercart-product-options.png)

![Ubercart stock tab for the same tee-shirt, one row per SKU with its stock level and low-stock threshold](ubercart-product-stocks.png)

I use Ubercart since 2008 and I'm really happy with it. The future is
interesting, as [Ubercart was forked](https://web.archive.org/web/20110811224311/http://www.drupalcommerce.org/about/history)
as the [Drupal Commerce](https://www.drupalcommerce.org) project
[a year ago](https://web.archive.org/web/20110716052709/http://www.bywombats.com/blog/01-14-2010/rose-any-other-name). I'm
waiting for the 1.0 release of the latter to decide if it is worth switching to
the fork or not. But having it based on Drupal 7 is good news, as Ubertcart
still stick to the (old) Drupal 6.
