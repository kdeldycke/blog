---
date: '2011-08-16'
title: WebPing Open-sourced!
category: English
tags: Apache, email, flot, GitHub, HTML, HTTP, javascript, jquery, munin, nagios, Plone, Python, Server, SQLite, SQL, Web, webping, yaml, cron
---

I've just released WebPing under a GPL license. It's available right now on a [GitHub repository](https://github.com/kdeldycke/webping).

WebPing is a script I started to work on in 2009 while working at [EDF](https://www.edf.com/). Back then, I needed a monitoring tool to keep an eye on the 80+ [Plone](https://plone.org/) instances that my team managed. For several corporate reasons, I wasn't allowed to use a proper monitoring tool like [Munin](https://munin-monitoring.org/) or [Nagios](https://www.nagios.org/). So I created a small script to fill this need. That's how WebPing came to be.

WebPing is just a stupid Python script that is designed to be ticked regularly by a cron job. It try to fetch a list of URLs and store response times in an SQLite database. Then it create a static HTML report you're free to serve with any HTTP server (an [example Apache configuration](https://github.com/kdeldycke/webping/blob/master/apache.conf) is provided). The configuration of WebPing and the list of URLs it monitor is stored in a YAML file.

The produced HTML report use the [Flot jQuery plugin](https://www.flotcharts.org/) to render graphs. Here is how the dashboard looks like:

![WebPing dashboard monitoring 18 URLs, most rows green for string found, with two red failures for a 401 and a refused connection and one orange warning, each row carrying a response-time sparkline](webping-dashboard.png)

Finally, WebPing is able to send reports and alerts by emails. Here is how a mail alert looks like:

![Alert email listing the two failures and one warning, each with its URL, status, error message and check time](webping-email-alert.png)

Since I created WebPing, I found several other projects more or less developed around the same idea. See [Kong](https://github.com/ericholscher/django-kong), which is based on Django and [Twill](https://web.archive.org/web/20110818061254/http://twill.idyll.org/), a web-oriented [DSL](https://en.wikipedia.org/wiki/Domain-specific_language). Another project I spotted after the facts was [multi-mechanize](https://testutils.org/multi-mechanize/). Like Kong, it's written in Python. But I never played with one or the other.
