# Infrastructure

Everything needed to rebuild this site's hosting from nothing, and the reasoning behind each deviation from a stock setup. The repository is the source of truth: if something here disagrees with the Cloudflare dashboard, run `scripts/cloudflare_config.py --check` and reconcile deliberately rather than editing this file to match reality.

No account, zone or project identifier is recorded here. This repository is public, and those identifiers are resolved at runtime from the credential instead. Find them with `wrangler whoami` or in any dashboard URL.

## What the site actually runs on

| Piece | Where | Notes |
| --- | --- | --- |
| Hosting | Cloudflare Pages project `kevin-deldycke-blog` | Created 2023-03-01, Free plan |
| Domains | `kevin.deldycke.com` and `kevin-deldycke-blog.pages.dev` | The apex `deldycke.com` zone is separate and hosts other things |
| Build | GitHub Actions, `.github/workflows/deploy.yaml` | Pelican, then jampack, then `wrangler pages deploy` |
| Search index | Stork, built during the deploy job | `cargo install stork-search --version 1.6.0`, output served as `/search-index.st` |
| Analytics | Cloudflare Web Analytics | Token lives in the project's `build_config`, injected by Cloudflare |
| Redirects | `content/extra/_redirects` | Copied verbatim into `output/`, read by Pages at the edge |
| Headers | `content/extra/_headers` | Sets feed and search-index content types |
| Oversized files | R2 bucket `blog-files`, served at `files.deldycke.com` | Pages rejects files over 25 MiB; see [oversized files](#oversized-files-live-in-r2) |

There are no Workers scripts, no KV namespaces and no D1 databases. R2 carries a single bucket, `blog-files`, holding the files too large for Pages. The blog is the only thing on this account that this repository is responsible for. Losing the repository would therefore cost the blog and nothing else: even the bucket's objects are recoverable from git history, as described [below](#oversized-files-live-in-r2).

The same Cloudflare account carries other domains, and `deldycke.com` itself carries mail records. Neither is needed to rebuild the blog and neither is documented here: that is deliberate, since this repository is public and those describe a personal network rather than a website. They live in a private infrastructure knowledge base instead, and `scripts/cloudflare_dns.py` enforces the split in code rather than by memory.

## How a deploy actually reaches readers

The site is **never built by Cloudflare**. GitHub Actions renders it and uploads the finished tree:

1. A push to `main` touching `content/**`, `*.py`, `pyproject.toml`, `uv.lock`, `wrangler.toml` or the workflow itself starts `deploy.yaml`. A monthly cron starts it too, for reasons under [token expiry](#the-deploy-token).
2. `uv run pelican` renders `output/`, Stork indexes it, jampack optimises it.
3. `wrangler pages deploy ./output` uploads the tree. Cloudflare promotes it once the upload completes, so an interrupted run leaves the previous deployment serving.

This is a Direct Upload flow. In the API, those deployments carry `deployment_trigger.type = "ad_hoc"`, and the live one is the project's `canonical_deployment`.

Two version pins in that job are hand-held, and both were floating until 2026-08-11. `cargo install stork-search --version 1.6.0` has to keep matching the runtime Plumage loads from `files.stork-search.net/releases/v1.6.0/stork.js`: the index format is versioned, so an indexer running ahead of that runtime breaks site search without failing the build. `wranglerVersion: "4.118.0"` pins the CLI that `cloudflare/wrangler-action` otherwise resolves on every deploy, its own default being the floating major `4`. repomatic's `sync-workflow-pins` walks npm literals, PyPI literals and the `setup-uv` version input only, so neither of these gets bumped for me: check them when Stork or wrangler moves.

### Oversized files live in R2

Pages Direct Upload rejects any file over 25 MiB, and `wrangler` fails the whole deploy on the first one it meets. A file over that cap lives in the `blog-files` R2 bucket instead, served at `files.deldycke.com`. The hostname sits directly under the apex on purpose: Universal SSL covers `*.deldycke.com` and nothing deeper, so a name under `kevin.deldycke.com` would need a paid certificate. Egress from R2 is free, and storage is free up to 10 GB-month.

To move a file there:

1. Upload it with the `r2 object put` command below.
2. Link it from its article with its absolute `https://files.deldycke.com/{file}` URL, not with `{attach}`.
3. `git rm` it from `content/`. `STATIC_PATHS` copies every file under `content/` into `output/`, so a file left there still reaches the deploy and fails it.
4. Add a 301 from its old `/{year}/{file}` path in `content/extra/_redirects`, with its corpus entry in `tests/test_redirects.py`, so inbound links keep working.

The upload is a one-time local act, never a deploy step, which is what keeps `CLOUDFLARE_API_TOKEN` on its single Pages permission. The OAuth token `wrangler login` stores drives it, and its consent page lets you narrow the grant. Five scopes did the whole job on 2026-09-30, with wrangler `4.128.0`: `user:read` and `offline_access` (both required), `account:read`, `workers:write` and `zone:read`. No OAuth scope names R2 storage: `workers:write` carries it. `zone:read` was granted for the domain attach, and whether the attach needs it is untested. `wrangler whoami` then warns about every default scope left out, which is expected. The wrangler version mirrors the deploy job's pin:

```bash
npx wrangler@4.118.0 r2 bucket create blog-files
npx wrangler@4.118.0 r2 object put blog-files/{file} --file {path} --content-type {media-type} --remote
npx wrangler@4.118.0 r2 bucket domain add blog-files --domain files.deldycke.com --zone-id {zone-id} --min-tls 1.2
```

Only the `object put` line repeats per file: the other two ran once, on 2026-09-30.

`--remote` is not optional. Without it, wrangler 4 writes the object to local Miniflare storage under `.wrangler/state/`, reports success, and leaves the real bucket empty. `--content-type` sets the type R2 serves: a format with no registered media type gets `application/octet-stream`, for the reason the `.img` rule under [content types at the edge](#content-types-at-the-edge) gives.

The `domain add` command makes the bucket public. It asks for confirmation, and a non-interactive shell answers yes on its own. `{zone-id}` comes from the `deldycke.com` zone's Overview page, because wrangler has no command that lists zones. `--min-tls 1.2` is there because an R2 custom domain accepts TLS 1.0 by default. The certificate is issued after the attach: `wrangler r2 bucket domain list blog-files` shows `ssl_status` go from `pending` to `active`. Then regenerate [`dns.md`](dns.md), since the attachment writes a proxied record into the zone.

A file removed from `content/` stays in git history. To re-upload one, `git log --diff-filter=D -- {path}` names the deleting commit, and its parent holds the blob. When the article publishes a checksum, verify the recovered file against it before the upload.

### Content types at the edge

Every file type the site serves was audited against production on 2026-08-10, one live sample per extension. Pages guesses far more correctly than its documentation suggests: `.otp`, `.psd`, `.toml`, `.webmanifest`, `.scss`, `.woff2`, `.ico` and the whole mainstream set all arrive with the right type and needed no rule. `content/extra/_headers` therefore only carries the exceptions, and each rule there exists because the guess was measured wrong, not because it might be.

Two types stay `application/octet-stream` **on purpose** and must not grow rules: `.qtz` (Quartz Composer, a dead format with no registered media type, where octet-stream is the honest answer) and `.img` (a firmware image, which is exactly a byte stream). If a future audit finds them "missing", this paragraph is the reason.

Pages also sends `X-Content-Type-Options: nosniff` on every response as a platform default. The `/*` rule in `_headers` pins that to the site rather than the platform, so a host migration or a changed default cannot silently drop it: the value was measured, then declared.

The same audit caught the build publishing an artefact of its own: webassets dropped its cache into the published theme folder, and six opaque hash-named files went live at `/theme/.webassets-cache/*` with every deploy. The cache now lands at the repository root via `WEBASSETS_CONFIG` in `pelicanconf.py`, whose comment records the trap that made the first fix silently do nothing: Plumage always defines `WEBASSETS_CONFIG`, so the older `ASSET_CONFIG` key is never read under this theme, while still triggering the plugin's deprecation warning. Verified with a full build on 2026-08-10 (cache at the root, none in `output/`); the stray copy in production disappears on the next deploy, since every deploy replaces the whole tree. Worth pushing upstream to [kdeldycke/plumage](https://github.com/kdeldycke/plumage) so user-supplied webassets config merges instead of being shadowed.

### No source repository

The project has no repository attached, and must not gain one. Its `source` reads `null`, which is what keeps Cloudflare out of the build path entirely: the only thing that ever reaches the edge is the tree uploaded in step 4.

Attaching one reintroduces a second, competing publisher for the same project, and Cloudflare has no build configuration here that would produce a usable site. `scripts/cloudflare_config.py --check` fails when `source` stops being null, which is the guard against it coming back by accident.

## Defaults versus what this project sets

`scripts/cloudflare_config.py` is the executable version of this table. Run it rather than trusting the table:

```bash
python scripts/cloudflare_config.py --check   # diff live against declared, exit 1 on drift
python scripts/cloudflare_config.py --apply   # write the declared values back
python scripts/cloudflare_config.py --dump    # full live state, secrets redacted
```

The Docs workflow runs the same comparison with `repomatic cloudflare-pages --check`, in its `cloudflare-config-drift` job. The `site.*` keys in `pyproject.toml` declare the values it checks. That job reads `CLOUDFLARE_API_TOKEN` alone and derives the account from it. repomatic measured on 2026-08-16 that an account-owned token scoped to Pages Edit lists its own account through `GET /accounts`. The 403 hint in `scripts/cloudflare_config.py` says the opposite, and this repository's token has not been tried against that call yet: the job's first run settles it.

| Setting | Stock default | Here | Why |
| --- | --- | --- | --- |
| `deployment_configs.*.compatibility_date` | project creation date | `2026-06-16` | Pins the Workers runtime for Pages Functions. Inert while there are no Functions, which is exactly why it drifts unnoticed. |
| `deployment_configs.*.placement.mode` | `off` | `smart` | Smart Placement. Changes nothing measurable for a static site, costs nothing, and would otherwise look accidental. |
| `deployment_configs.*.build_image_major_version` | `3` | `3` | Already current. v1 auto-migrates 2026-09-15, v2 on 2027-02-23, then no further versions. |
| `source` | a `github` source block | `null` | Direct Upload only. A source block here would make Cloudflare a second publisher for the same project, with no build configuration capable of producing a usable site. |
| `build_config.build_command` | empty | empty | Cloudflare never builds this project. A value appearing here means someone reconnected Git. |

The "stock default" column is honest about its own confidence: the script tags each entry as `documented` or `inferred, unverified`. Only the build image row is quoted from Cloudflare's documentation. The rest are inferred from product behaviour and should be confirmed against a freshly created project before anyone relies on them.

`wrangler.toml` is **not** part of this. Its `compatibility_date` said `2023-03-01` for years while the live value was `2026-06-16`, and nothing noticed, because Cloudflare reads the server-side `deployment_configs` and the file only matters to a build that never runs. `pages_build_output_dir` and `compatibility_date` stay in the file because wrangler requires both for a Pages config: dropping either downgrades it to local-development-only.

## Certificates renew themselves

Nothing here manages TLS. Cloudflare issues and renews the certificate for `kevin.deldycke.com` as part of Pages custom domains, and Universal SSL covers the proxied zones. Both are internal to Cloudflare: it controls the DNS and the edge, so it never authenticates as the account holder and no API token is involved at any point.

This matters mainly because of how it looks in the audit log. Renewal shows up as a repeating cycle, several times a month across the zones:

```
Certificate pack created
Certificates ordered from the Certificate Authority
Certificate pack deployed
```

and each one is bracketed by `dns record` create and delete pairs. Those are the validation records Cloudflare writes to prove domain control and then cleans up. **It is not DNS drift and it is not anything of ours.** Every one of those entries has actor `system` and an empty Actor Context, which is the signature of Cloudflare acting on its own.

A Cloudflare DNS API token would only ever be needed for TLS if a certificate were required somewhere Cloudflare is not terminating: a wildcard certificate, or an origin that never passes through the edge. Neither exists here. If a real origin is ever added, Cloudflare Origin CA is the answer, and it is issued by Cloudflare with a 15-year life and no ACME, so it would not reintroduce a DNS token either.

## Reading the audit log

**Manage account → Audit logs** is the tool for answering "what is using this account". The **Actor Context** column is the one that matters:

| Actor Context | Means |
| --- | --- |
| `dash` | A human in a browser |
| `api` | Dashboard-driven API calls: `LOGIN`, `TOKEN_CREATE` |
| `api_token` | A scoped API token |
| *(empty)*, actor `system` | Cloudflare itself, mostly certificate renewal |

Account-owned and user-owned tokens are distinguishable: an account-owned token logs actor `account` with an empty Actor Email, a user-owned one logs the owner's address. That is how a credential migration can be confirmed after the fact rather than assumed. They are also distinguishable at the API, and [in a way that looks like a broken credential](#the-rule-is-readable-over-the-api-after-all): an account-owned token is rejected outright by the user-scoped `/user/tokens/verify`.

Two limits worth knowing before drawing conclusions. The log records **changes only**, so a credential that only ever reads leaves no trace no matter how far back you look. And reading it through the API needs `Account → Audit Logs → Read`, which the `wrangler login` OAuth token does not carry, so in practice this is a dashboard exercise.

## The deploy token

`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are GitHub Actions repository secrets.

`CLOUDFLARE_ACCOUNT_ID` is not a credential. It is a stable identifier visible in every dashboard URL, it never expires, and it never needs rotating.

`CLOUDFLARE_API_TOKEN` needs exactly one permission: **Account → Cloudflare Pages → Edit**. Nothing else.

Open the [**pre-filled token form**](https://dash.cloudflare.com/?to=/:account/api-tokens&permissionGroupKeys=%5B%7B%22key%22%3A%22page%22%2C%22type%22%3A%22edit%22%7D%5D&name=kevin-deldycke-blog-deploy), which arrives with the permission and name already set. Two things the URL cannot carry, so they stay manual: append `-{YYYY-MM}` to the name, and set the one-year TTL. The link format is Cloudflare's [account token template URL](https://developers.cloudflare.com/fundamentals/api/how-to/account-owned-token-template/): a `permissionGroupKeys` JSON array in the query string, where `page` is the documented key for Cloudflare Pages.

If creating it by hand instead, at `https://dash.cloudflare.com/?to=/:account/api-tokens` under Custom token: the permission row's first dropdown defaults to *User*, where `Cloudflare Pages` does not appear; switch it to *Account* first.

The token carries a one-year TTL. That bounds the damage if the project is ever abandoned, but on its own it creates a silent failure: `deploy.yaml` otherwise runs only on content pushes, so an expired token would surface whenever the next article happened to land, which for an abandoned blog is never. Cloudflare sends no expiry warning for account API tokens; the "expiring token" notification in their docs covers Access service tokens, a different product.

The monthly `schedule:` trigger on `deploy.yaml` closes that gap. It re-runs the full build, fails loudly on an expired token, and GitHub emails about the failed run. It also re-proves the build against whatever `uv` and `npm` resolve that month, which is the part that rots fastest.

Caveat: GitHub disables scheduled workflows in public repositories after 60 days of no repository activity. The weekly `autofix.yaml` run makes that unlikely here, but it is not a guarantee.

### Rotating it

Create the replacement before revoking the incumbent, so no window exists where a push cannot deploy.

1. Create the new token as above, with a fresh one-year TTL. Name it with a date, like `kevin-deldycke-blog-deploy-2026-08`.
2. Update the secret without the value entering a shell history or a terminal transcript:
   ```bash
   pbpaste | gh secret set CLOUDFLARE_API_TOKEN --repo kdeldycke/blog
   ```
3. Verify with a real deploy before revoking anything:
   ```bash
   gh workflow run deploy.yaml --repo kdeldycke/blog
   gh run watch --repo kdeldycke/blog
   ```
   Watch the `Publish` step for `Deployment complete`. A too-narrow scope fails there, and the previous deployment keeps serving.
4. Only then delete the old token.

### Other credentials

The deploy token is deliberately the **only** long-lived credential this site depends on. The standing rule for any credential that ever joins it: the narrowest permission that works, an expiry whenever the product allows one, and a name that says what it is and when it was made. Anything discovered without those gets replaced rather than kept.

Two ephemeral credentials appear in this document and are not exceptions to the rule: the DNS snapshot token (short TTL, deleted after use) and the local `wrangler login` OAuth token, which is broad but short-lived and notably carries no DNS scope at all — the reason the snapshot needs its own token in the first place.

The wider Cloudflare account carries credentials and history that are not this blog's business; that inventory lives in the private infrastructure knowledge base, alongside the other domains and the mail wiring.

## Rebuilding from nothing

If the Cloudflare project is deleted or the account is lost:

1. Create a Pages project named `kevin-deldycke-blog`. Choose **Direct Upload**, not a Git connection, for the reasons under [no source repository](#no-source-repository).
2. Create the API token and set both repository secrets as above.
3. Run `python scripts/cloudflare_config.py --apply` to write the compatibility date, Smart Placement and build image floor.
4. Push to `main`, or run the workflow manually, to produce the first deployment.
5. Attach `kevin.deldycke.com` as a custom domain, then recreate its DNS record from [`dns.md`](dns.md), in the `deldycke.com` zone.
6. Re-enable Cloudflare Web Analytics. The token is regenerated per project and is not recoverable from this repository.
7. Recreate the `blog-files` R2 bucket, re-upload its objects from git history, and attach the `files.deldycke.com` custom domain: see [oversized files](#oversized-files-live-in-r2).

## DNS

[`dns.md`](dns.md) is a generated snapshot of the records that serve this site. Regenerate it whenever DNS changes:

```bash
python scripts/cloudflare_dns.py --write docs/dns.md
```

**It is deliberately partial.** The script keeps only the `deldycke.com` zone, and within it only the records that serve the site: mail wiring is filtered out entirely, and other zones on the account never appear. That boundary is enforced by `BLOG_ZONE` and `is_mail_record()` in the script rather than by anyone remembering to prune the output. The full picture goes to a private infrastructure knowledge base via `--scope full`, which is the same command with the filters off.

Within what remains, TXT values are fingerprinted rather than published: the record's purpose survives along with a SHA-256 prefix, so a changed fingerprint reveals drift without publishing the value. Every other record type is verbatim, because a rebuild needs those exactly.

This needs its own credential. The token `wrangler login` stores cannot do it: wrangler's OAuth client offers no DNS scope at all, and its `zone:read` covers only the zone objects, so record enumeration returns 403. Open the [**pre-filled token form**](https://dash.cloudflare.com/?to=/:account/api-tokens&permissionGroupKeys=%5B%7B%22key%22%3A%22zone%22%2C%22type%22%3A%22read%22%7D%2C%7B%22key%22%3A%22dns%22%2C%22type%22%3A%22read%22%7D%5D&name=dns-snapshot), which arrives with both read permissions and the name set; the URL cannot carry the resource scope or the TTL, so set Zone Resources to all zones and give it a short expiry by hand. Both permissions are required: `Zone → Read` lists the zones, `DNS → Read` reads their records, and either alone fails on one half. Then:

```bash
CLOUDFLARE_API_TOKEN={token} python scripts/cloudflare_dns.py --write docs/dns.md
```

Give that token a short TTL and delete it afterwards. It exists to take a snapshot, not to sit in CI.

### What the snapshot turned up

**The apex carries dead records from a pre-Cloudflare setup.** `deldycke.com` has four A and four AAAA records pointing into `99.86.0.0/16` and `2600:9000::/28`, which AWS publishes as CloudFront ranges (verified against `ip-ranges.amazonaws.com`, not assumed). They are left over from before the site moved to Cloudflare.

Nothing reaches them. `https://deldycke.com` returns `301` to `https://kevin.deldycke.com/`, and that response carries `server: cloudflare` and a `cf-ray` with no `x-amz-cf-id`, no `x-amz-cf-pop` and no `Via: CloudFront`. Cloudflare forwards origin headers rather than stripping them, so an origin-generated redirect would show them. The redirect is produced at the edge and the CloudFront distribution is never contacted.

They still cannot simply be deleted. A proxied hostname needs at least one DNS record for Cloudflare to answer for it at all; with none, the apex returns NXDOMAIN and the redirect never fires. Replacing them with a single proxied `AAAA` pointing at the discard address `100::` keeps the edge answering while guaranteeing no origin exists to reach.

### Canonicalizing the apex and www

Every spelling of the site's root reaches `https://kevin.deldycke.com` in **one** redirect. That is done by a single edge rule, in the zone's `http_request_dynamic_redirect` phase, described as `canonical host redirect`:

```
expression: (http.host in {"deldycke.com" "www.deldycke.com"})
target:     concat("https://kevin.deldycke.com", http.request.uri.path)
            301, preserve_query_string
```

Three details in that rule are load-carrying, and all three were wrong before 2026-08-10:

- **It matches on `http.host`, not on the full URI.** The previous expression was `starts_with(http.request.full_uri, "https://deldycke.com/")`, which can only ever match HTTPS. A plain `http://` request had to be upgraded by Always Use HTTPS first and then redirected, costing two hops. Matching the host makes the rule scheme-independent, so one response does both jobs.
- **It names `www` explicitly.** There is no wildcard here. `www.deldycke.com` CNAMEs to `kevin.deldycke.com`, which is a Pages custom domain, and Pages rejects any `Host` it does not serve. Before the rule named `www`, the hostname answered an error while the apex redirected correctly: the two had nothing in common but a suffix. The same is still true of every other subdomain the `*.deldycke.com` wildcard covers.
- **The target uses `uri.path`, not `uri`.** `http.request.uri` already carries the query string, so concatenating it while `preserve_query_string` is also set risks appending the query twice. Taking the path from the expression and letting the flag own the query keeps each part sourced once.

`tests/test_redirects.py::test_domain_canonicalization` asserts the hop count for all twelve spellings, and `test_non_canonical_host_preserves_path` asserts that a deep link keeps its path rather than dumping visitors on the homepage. Both run against production, so a regression in this rule fails the suite rather than going unnoticed.

This could not have been done in `content/extra/_redirects`. That file is served by Pages for `kevin.deldycke.com`, and Pages redirects match on **path**, never on host: a `/*` rule there would fire on the canonical hostname too and redirect the site to itself forever. Host canonicalization has to happen at the edge, before Pages sees the request.

#### The rule is readable over the API after all

An edge rule of this kind can be snapshotted and reconciled the way `scripts/cloudflare_config.py` handles the Pages project, and an account-owned token is enough. Measured on 2026-08-15, against the sibling `mpm.run` zone rather than this one, with a token carrying `Zone → Read` and `Dynamic URL Redirects → Edit`:

| Call | Result |
| --- | --- |
| `GET /zones?name={zone}` | zone resolved |
| `GET /zones/{zone_id}/rulesets` | phases listed, `http_request_dynamic_redirect` among them |
| `GET /zones/{zone_id}/rulesets/{ruleset_id}` | full rule bodies, expression and target included |
| `PATCH /zones/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}` | target expression rewritten, live within seconds |
| `GET /user/tokens/verify` | **HTTP 401**, error `1000` "Invalid API Token" |

The last row is the trap, and it is about the endpoint rather than the token: `/user/tokens/verify` is user-scoped, so an account-owned token (the `cfat_` prefix) fails it while every zone call above succeeds. A verify step is therefore the wrong thing to gate a script on — prove the credential against the zone it is meant to touch instead.

This does not contradict [what is recorded below](#known-gaps) about Page Rules: that is the **legacy** `/zones/{id}/pagerules` endpoint, and nothing here re-tested it. Single Redirects live in the newer `rulesets` API, which is what these calls exercise.

Reconciling this rule from the repository is therefore possible and not yet done. It would need a `Dynamic URL Redirects → Read` token in the same short-TTL, delete-after-use shape as the DNS snapshot one, and the same `--check`/`--apply`/`--dump` verbs `cloudflare_config.py` already offers.

Two things stay unrecoverable from this repository alone: the Web Analytics token, which is regenerated per project, and the TXT record values, which are fingerprinted here by design. Everything else in a rebuild is reproducible from what is committed.

### The pages.dev subdomain

`kevin-deldycke-blog.pages.dev` is not optional and cannot be deleted: it is the CNAME target `kevin.deldycke.com` resolves to, so the site is served *through* it. Cloudflare assigns one `<project>.pages.dev` per Pages project and keeps it for the life of the project. The [documented](https://developers.cloudflare.com/pages/configuration/custom-domains/) ways to keep the public off it are Cloudflare Access over previews, or redirecting it to the custom domain. That redirect needs host matching, which neither `_redirects` nor `_headers` can do since both match on path only, so it would take a Pages Function running on every request: a Worker invocation added to a site that is otherwise pure static asset serving.

Not worth it here, because the duplicate it exposes is already inert. Checked 2026-08-11:

- A web search for the hostname returns only this repository on GitHub, never a page of the site. The copy is not indexed.
- Every generated document carries `<link rel="canonical">` pointing at `https://kevin.deldycke.com/…`. Served from either hostname, a page names the canonical one.
- `sitemap.xml` lists canonical URLs only, and every internal link in the HTML is absolute to `kevin.deldycke.com`, so a crawler landing on the `pages.dev` copy leaves it on the first click.

Full canonical coverage took a patch. The `seo` plugin decorates articles and pages only: its `run_html_enhancer` returns early unless the render context holds an `article` or a `page`, which no listing template supplies, so 810 of the 1074 generated documents had nothing naming their host. `canonicalize_listings()` in `pelican_patches.py` fills them in from the same `content_written` signal the plugin uses, deriving each URL from its output path, since Pages resolves a directory to its `index.html` and strips `.html` from everything else. Paginated pages point at themselves rather than at the first page, which is what Google asks for. The tag is spliced in as text rather than through BeautifulSoup: re-serializing 800-odd documents full of hand-written HTML for one line is a risk the corpus would notice. A build now yields 1074 of 1074 documents carrying exactly one canonical, all on `kevin.deldycke.com`, and `tests/test_pelican_patches.py` covers the URL mapping, the skip conditions and the signal registration.

## What the test suite checks against production

Three of this site's behaviours exist only at the edge. They are configured in files here, but nothing in a build proves they work: `_headers` and `_redirects` are copied verbatim into `output/` and only mean anything once Cloudflare is serving them, and the host canonicalization is not in this repository at all. So the suite fetches the live site.

- **`tests/test_headers.py`** parses `content/extra/_headers` and fetches one real URL per rule, asserting the declared header actually arrives. A `test_every_rule_has_a_sample` guard fails when a rule is added without a sample URL, so coverage cannot quietly decay as the file grows. Wildcard rules need a hand-written sample because a pattern like `/*.numbers` matches infinitely many paths and the site serves exactly one.
- **`tests/test_redirects.py::test_domain_canonicalization`** asserts the hop count for all twelve spellings of the site's root, and `test_non_canonical_host_preserves_path` asserts deep links keep their path. These guard the edge rule described above, which no file here can express.
- **`tests/test_redirects.py`** audits `content/extra/_redirects` offline against a faithful replica of Cloudflare's parser (`tests/pages_redirects_engine.py`), then probes every rule against production with replica-computed expectations. The engine's undocumented budget accounting once silently killed the last 18 rules of the file; [`redirects.md`](redirects.md) is the full story and the twenty-year URL inventory behind the file.

These tests hit the network, which is unusual for a suite and deliberate here: a redirect that works in principle and 404s in production is exactly the failure this is for. The cost is that the suite is only as available as the site, and that a run takes about two minutes.

## Open items

Things known to be wrong or unfinished, as opposed to the gaps below which are limits of the tooling.

- **The apex still carries eight dead CloudFront records.** Replacing them is described under [what the snapshot turned up](#what-the-snapshot-turned-up). Add the discard record before deleting the rest, or the apex goes dark in between.
- **`www.deldycke.com` returns 403**, along with every other subdomain the wildcard covers. Needs either a second Pages custom domain or an edge redirect.
- **The firmware mirror's R2 migration awaits deployment.** The `blog-files` bucket, its one object and the `files.deldycke.com` custom domain exist since 2026-09-30, per [oversized files](#oversized-files-live-in-r2). Until a deploy ships the article's new link and the `_redirects` rule, the old download link 404s as before, and `tests/test_redirects.py` fails on the two cases covering the rule. [`dns.md`](dns.md) also lacks the record the attachment wrote. Delete this bullet once the deploy is live and the snapshot is regenerated.
- **The reordered `content/extra/_redirects` and the `.patch`/`.xcf` header rules await deployment.** Until the next deploy ships them, `tests/test_redirects.py` fails on the 35 cases covering the previously-dead rules and `tests/test_headers.py` on the two new content types; all flip green once live. A push touching `content/**` triggers `tests.yaml` and `deploy.yaml` in parallel, so a test run racing the deploy may fail once and pass on rerun; this is inherent to testing edge files against production.
- **Two drift checks run side by side.** Once the Docs workflow's `cloudflare-config-drift` job has run green, delete `scripts/cloudflare_config.py`, the `config-drift` job in `deploy.yaml`, and the `CLOUDFLARE_ACCOUNT_ID` secret if the deploy step no longer needs it. Then point this page's commands at `repomatic cloudflare-pages`.

## Known gaps

- The stock-default column is mostly inferred, as noted above. Confirming it means creating a throwaway Pages project and diffing its config against this one.
- `dns.md` is a snapshot, not a reconciler. Nothing detects DNS drift automatically the way `cloudflare_config.py --check` does for the Pages project, because that would mean a DNS-scoped token living in CI. Regenerating after any DNS change is manual.
- `scripts/cloudflare_config.py` reconciles the Pages project only. Zones, DNS, Web Analytics and zone-level rules are untouched by it.
- Zone-level settings (SSL mode, minimum TLS version, always-use-HTTPS, cache rules) are not captured anywhere. They are unlikely to matter for a static site on Cloudflare defaults, but they are not verified to be on defaults either.
- The rule producing the apex redirect is recorded here by hand, and nothing reconciles it. It is no longer dashboard-only: [the rulesets API reads and writes it with an account-owned token](#the-rule-is-readable-over-the-api-after-all), so the gap is now the missing script rather than a missing capability. The legacy Page Rules endpoint is a separate thing and still refuses those tokens as far as anyone here has tested.

## Keeping this current

This file is the account's memory, not a snapshot of one afternoon. Anything learned about the hosting that is not already derivable from the repository belongs here, including the negative results: a permission that turned out not to exist, an endpoint that refuses a token type, a setting that looked alarming and was not. Those are the findings most likely to be rediscovered the expensive way.

Record what was checked and how, not just the conclusion, so a later reader can tell a verified fact from a plausible assumption. The `documented` versus `inferred, unverified` tagging in `scripts/cloudflare_config.py` exists for the same reason.
