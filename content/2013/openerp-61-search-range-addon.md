---
date: '2013-04-23'
title: Addon to restore search range in OpenERP 6.1
category: English
tags: OpenERP, JavaScript, Backbone.js, jQuery, Web, addon
---

In OpenERP 6.1, the default search widget for dates and floats [no longer feature a range](https://bugs.launchpad.net/openerp-web/+bug/926390/):

![OpenERP timesheet search with hand-drawn red rings around the single Date from field and the date-from and date-to columns it has to match](openerp-61-no-range-search-widget.png)

This was [uncovered](https://bugs.launchpad.net/openerp-web/+bug/949990) by [users](https://answers.launchpad.net/openobject-server/+question/198725) in the [community](https://answers.launchpad.net/openobject-server/+question/198863). But it's not a bug, [it's a feature](https://bugs.launchpad.net/openerp-web/+bug/926390/comments/4), a design decision.

Worse, `datetime` search field in OpenERP 6.1 [no longer let you set the time](https://bugs.launchpad.net/openerp-web/+bug/1037658):

![Scheduled actions search with the next execution date field open on a calendar picker for August 2012](openerp-61-datetime-search-view.png)

To fix these issues, I've created [`web_smile_search_range`](https://github.com/hbrunn/smile_openerp_addons_6.1/tree/master/web_smile_search_range) a module which is available since 2012, but I never advertised it on this blog.

This module is based on an [open-source addon from Credativ](https://web.archive.org/web/20240617052821/https://bazaar.launchpad.net/~credativ/credativ-openerp/addons-6.1/files/head:/web_searchdaterange/). I extended the later to:

- Replace single `date`, `datetime` and `float` search fields to a range.
- Allow selection of time in `datetime` search fields.

Thus restoring the default behavior from OpenERP 6.0 that was ditched in 6.1.

And if you need to dig deeper in the code, you'll quickly find out that the core of the module lie in the [`search.js` file](https://github.com/hbrunn/smile_openerp_addons_6.1/blob/master/web_smile_search_range/static/src/js/search.js), which extend in JavaScript the search fields models of our interests.
