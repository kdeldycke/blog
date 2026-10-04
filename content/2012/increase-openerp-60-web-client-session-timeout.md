---
date: '2012-04-24'
title: Increase OpenERP 6.0 web-client session timeout
category: English
tags: CherryPy, OpenERP, Python, Single sign-on, Smile, SSO, timeout, Web, ERP
---

Another week working with [OpenERP](https://openerp.com) means another trick learned to answer some intricate customer's needs.

Today I was asked to keep users logged-in on OpenERP's 6.0 web client. The latter being powered by [CherryPy](https://cherrypy.org), it was a matter of adding the following configuration directive in the web client configuration file to increase the session timeout:

```ini
tools.sessions.timeout = 720
```

Now this will keep any client sessions opened for 12 hours (12h * 60 minutes = 720 minutes) before expiring. This is enough to keep employees not complaining about having to login to OpenERP several times a day.

Problem solved!

Oh, and another way to address this issue consist in implementing some kind of Single Sign-On. And you know what? We have that in store thanks to the [`smile_sso` module for OpenERP](https://github.com/tejastank/smile_openerp_addons_6.0/tree/master/smile_sso)! :)
