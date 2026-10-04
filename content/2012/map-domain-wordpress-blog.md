---
date: '2012-07-31'
title: How-To map a non-US domain name to a WordPress.com blog
category: English
tags: DNS, SOA, WordPress
---

I'm currently migrating most of my self-hosted WordPress blogs from my server to [WordPress.com hosting](https://en.wordpress.com/features/), which allows you to [use your own domain](https://en.support.wordpress.com/domain-mapping).

But setting the DNS records from your registrar may trigger some errors. I myself wasn't able to properly update my domain configuration and [OVH](https://ovh.com) always sent me back this notification email each time I tried to update the DNS record of `mydomain.fr`:

```text
DNS update failed. Fix the zone-check error, and relaunch the operation.
The zone-check error is: [TEST SOA record exists]: answer refused by the server: (SOA mydomain.fr)
```

This errors is mostly due to the use of a non-US domain.

To fix this `SOA`-related issues, the only extra step required consist in [asking WordPress.com to set a zone record](https://web.archive.org/web/20120731153846/http://en.support.wordpress.com/domain-mapping/dns-zone-records/) on their servers. After that, you can proceed to the [standard mapping procedure](https://web.archive.org/web/20120726053726/http://en.support.wordpress.com/domain-mapping/map-existing-domain/#instructions-for-mapping-an-existing-domain).
