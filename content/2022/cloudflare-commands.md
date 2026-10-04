---
date: '2022-06-10'
title: CloudFlare commands
category: English
tags: cloud, cloud computing, saas, iaas, paas, development, CLI, dns, cloudflare, API
---

## DNS records

- List DNS records of a zone:

  ```shell-session
  $ curl -X GET "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type:application/json"
  ```

- List DNS records IDs of a zone:

  ```shell-session
  $ curl -X GET "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type:application/json" \
      | jq '.result[].id'
  "82c881261189dc8b8ddbd756cffccd21"
  "324437ed3e1212770edeabb65bb3cd6a"
  ```

- Delete one DNS record:

  ```shell-session
  $ curl -X DELETE "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records/<RECORD_ID>" \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type:application/json"
  ```

- Delete all DNS records of a zone:

  ```shell-session
  $ curl -X GET "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type:application/json" \
      | jq --raw-output '.result[].id' \
      | xargs -I '{}' \
      curl -X DELETE "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records/{}" \
          -H "Authorization: Bearer <TOKEN>" \
          -H "Content-Type:application/json"
  ```

## Redirects

CloudFlare have several redirection options:

- [Pages redirects](https://developers.cloudflare.com/pages/platform/redirects/): for static sites hosted on CloudFlare, via a `_redirects` file.
- [Page Rules](https://developers.cloudflare.com/rules/page-rules/how-to/url-forwarding/)

### Pages redirects

This blog uses [CloudFlare Pages](https://pages.cloudflare.com/) to host all its static content. To redirect old URLs to new ones, I use a [`_redirects` file at the root of the repository](https://github.com/kdeldycke/blog/blob/main/content/extra/_redirects). You should inspect that file to see how it works.

Note that this kind of redirects are not working at the domain-level: Pages rules match on path only, never on host. If you want to redirect `https://example.com/` to `https://www.example.com/`, you need a zone-level [Single Redirect](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/) matching on `http.host` (I used [Page Rules](#page-rules) for this before Cloudflare deprecated them).

Here are some of the most useful rules:

- By default, [pages are redirected for normalization](https://developers.cloudflare.com/pages/platform/serving-pages/#route-matching):

  | From                | To         |
  | ------------------- | ---------- |
  | `/contact`          | `/contact` |
  | `/contact/`         | `/contact` |
  | `/contact.html`     | `/contact` |
  | `/about`            | `/about/`  |
  | `/about/`           | `/about/`  |
  | `/about/index.html` | `/about/`  |

  Note how folder roots with an `index.html` are always redirected to an URL with a trailing slash, while HTML files are stripped of their extension.

  This behavior cannot be changed.

- Redirect a single URL:

  ```text
  /old-url /new-url 301
  ```

- Redirect empty folders to the root of the site:

  ```text
  /empty-folder      /   301
  /empty-folder/     /   301
  ```

  I use this double rule to catch both the folder named `empty-folder`, and an hypothetical file named `empty-folder.html`. That way I am sure a parasitic `empty-folder.html` won't be served.

### The rule budget is positional

Update from 2026: I lost the last 18 rules of my `_redirects` file for years to an accounting subtlety the documentation does not state. I only found it by reading the parser in [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk) (`parseRedirects.ts`, also bundled in wrangler and Miniflare):

- A rule only counts against the *static* budget (2,000) while it appears **before the first rule containing a `*` or a `:placeholder`**.
- From that first dynamic rule on, **every** line burns the *dynamic* budget (100), even plain `/old /new 301` ones.
- At rule 101 of that mixed stream the parser does not skip a line: it **stops reading the file**, and everything after is silently discarded. Nothing in the deploy output tells you.

So the shape of a large `_redirects` file is not a style choice: put every exact rule first, every wildcard and placeholder rule second, or the tail of your file does not exist.

Two matching facts from the same source (`rules-engine.ts`) worth knowing:

- Sources are matched as anchored regexes: `:name` compiles to `[^/]+` (never empty, never crosses a slash) and `*` to `.*` (may be empty). `/a` and `/a/` are therefore different sources, and neither matches the other.
- Because a splat may match empty, a rule ending in `/*` also answers the bare trailing-slash URL. WordPress URLs all ended with a slash, so for old blogs this empty-splat behavior is what keeps two decades of inbound links alive.

I keep a [faithful Python replica of the engine](https://github.com/kdeldycke/blog/blob/main/tests/pages_redirects_engine.py) in this blog's repository, and [a test suite](https://github.com/kdeldycke/blog/blob/main/tests/test_redirects.py) that parses my `_redirects` with it and probes every rule against production. The full write-up lives in [`docs/redirects.md`](https://github.com/kdeldycke/blog/blob/main/docs/redirects.md).

## Page rules

`TODO`
