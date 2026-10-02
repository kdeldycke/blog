# Redirects

[Cool URIs don't change](https://www.w3.org/Provider/Style/URI). This site has been publishing since 2004, and every URL scheme it ever answered to is still answered today: `content/extra/_redirects` is the inventory, this document is why it looks the way it does, and `tests/test_redirects.py` is what keeps both honest against production.

## Twenty years of URL debt, four carriers

The URLs predate every piece of the current stack. The redirect rules have been translated intact across each hosting move, and the git history records every hop:

| Era       | Backend                     | Redirects carried by   | Evidence                                                                                                                         |
| --------- | --------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 2004–2012 | WordPress                   | WordPress itself       | The URL schemes below                                                                                                            |
| 2012–2020 | Pelican on Apache           | `.htaccess` directives | [`2013-01-24` "Add redirects…"](https://github.com/kdeldycke/blog/commits/main), "Massive rework of feed redirects" `2013-01-25` |
| 2020–2023 | Pelican on S3               | S3 routing rules       | "Replace old Apache directives to S3 redirection rules" `2020-10-30`                                                             |
| 2023–     | Pelican on Cloudflare Pages | `_redirects`           | "Translate S3 redirects to Cloudflare's" `2023-03-02`                                                                            |

The URL schemes the file keeps alive, oldest first:

- **WordPress permalinks**: `/YYYY/MM/slug/`, always with a trailing slash. Today's canonical form is `/YYYY/slug`, so the month must be stripped: `/:year/:month/*` shapes.
- **WordPress plumbing**: `/wp-content/uploads/*`, `/author/*`, comment pagination (`…/comment-page-N/`), monthly and yearly archive pages with their own pagination (`/YYYY/MM/page/N`).
- **WordPress feeds**: `/feed/`, `/feed/atom/`, per-post and per-category `…/feed/rss`, `rss2`, `rdf` variants — WordPress distinguished three RSS dialects, Pelican serves one. The site-wide comments feed, `/comments/feed/`, lands on the articles feed since comments left Disqus.
- **Early Pelican reorganizations**: `/uploads/:year/:month/:slug` flattened (filenames are globally unique), `/static/*` and `/documents/*` moves, `/pages/*` flattening, hierarchical categories (`/category/lang/en`) flattened.
- **Attachments that moved between articles** and articles that were absorbed into others: the long static tail.

## The engine, as it actually is

Cloudflare's [documentation](https://developers.cloudflare.com/pages/configuration/redirects/) describes the file format. The behaviour that decides whether rules *exist* is only in the implementation, transcribed on 2026-08-10 from `parseRedirects.ts` and `rules-engine.ts` in [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk) (the same code wrangler and Miniflare bundle). `tests/pages_redirects_engine.py` is a faithful Python replica; everything below is encoded there and enforced by the suite.

**The accounting.** A rule counts as *static* (budget: 2000) only while it appears **before the first rule containing `*` or `:placeholder`**. From that rule on, every line — however static it looks — burns the *dynamic* budget of 100. At rule 101 of that mixed stream the parser does not skip a line, it **stops reading the file**. Everything after is silently discarded, and nothing in the deploy pipeline reports it.

**The matching.** Sources compile to anchored regexes: `:name` becomes `[^/]+` (at least one character, never a slash, never empty), `*` becomes `.*` (may be empty), the whole source is wrapped `^…$`. Consequences:

- `/a` and `/a/` are **different sources**. Neither matches the other.
- A rule ending in `/*` also answers the bare trailing-slash URL, through an empty splat. Since every WordPress URL ended in a slash, this is what keeps the oldest links alive.
- Exact-source rules are probed first at runtime (a hash lookup), then pattern rules in file order.

**Parse details worth knowing**: inline comments after a rule are stripped (`/a /b 301  # why`); duplicate sources are dropped silently, first one wins; statuses are limited to 200, 301, 302 (default), 303, 307, 308, where 200 proxies a relative path instead of redirecting; a rule whose destination ends in `/index` or `/index.html` is refused as an infinite loop with the engine's own `.html`-stripping; lines over 2000 characters are ignored.

## The 2026-08-10 incident

The file carried 125 rules with statics and dynamics interleaved by theme. Only **7** rules preceded the first dynamic source, so 57 later statics burned the dynamic budget, the parser aborted at line 172, and the last **18 rules had been silently dead for years** — all the `/:year/NN` and `/:year/NN/*` monthly-archive rules. The failure was invisible: wrangler prints nothing about it on deploy, and a dead redirect looks exactly like a URL nobody visits.

The replica predicted the dead set from the file alone; probing production confirmed it case for case (35 failing test cases, all of them and only them). The fix is the file's current shape:

1. **All exact rules first, all pattern rules second.** 64 statics ride free, 66 dynamics fit the budget with 34 slots of headroom.
2. The thematic sections survive in both halves; order within each half is preserved, which keeps first-match precedence for the overlapping feed rules.
3. The contract is enforced by `test_statics_first_contract`, and `test_file_survives_the_engine` fails the suite if the engine would drop or stop at anything.

The reorder is behaviour-preserving for the two sources that both an exact and a pattern rule can match (`/comments/feed`, `/feed/atom`): the runtime already probed exact rules first regardless of file position.

## The test architecture

- **Offline** (`test_file_survives_the_engine`, `test_statics_first_contract`, `test_sources_are_sane`, `test_destinations_are_sane`): the file against the replica. Catches budget death, duplicate sources, splat misuse and destination-placeholder typos before anything ships.
- **Online** (`test_rule_is_live`): one production request per rule — plus the empty-splat twin for every `/*` rule, because that is the historically loaded case — with the expected `Location` computed by the replica. Redirects are not followed: the first response is the whole verdict.
- **End to end** (`test_historical_wordpress_url_chain`): one real 2010 permalink with a comment-page suffix, followed through its full multi-rule chain to the canonical article. Chains are legitimate here; history is layered.
- **The corpus** (`test_corpus`): the human-readable layer. A literal table of real URLs from the site's whole history — one WordPress permalink per publication month mined from today's frontmatter, a 2005 upload followed through every era of its URL, the feed dialects, the dead pagination — each paired with where it must land, followed to the end. `test_corpus_covers_every_rule` asserts every rule in the file is the *first* match of at least one entry, so the table can neither miss a rule nor mask one behind another. Read the table to see what the inventory promises; run it to see the promises kept.
- Host canonicalization and the apex live in the same file but belong to DNS and the zone edge rule; see [`infrastructure.md`](infrastructure.md).

## Alternatives deliberately not used

- **Bulk Redirects** operate at the account level and are essentially static: no placeholders, no splats, no string replacement. They could absorb the static half if the budget ever tightened, at the cost of splitting the inventory across two systems and an account-level API. The 35 free dynamic slots make this unnecessary today.
- **Single Redirects** (zone rulesets) already handle what `_redirects` cannot see: host canonicalization, documented in `infrastructure.md`. Pages redirects match on path only.

## Lineage of the tooling

- The findings in [Cloudflare commands § Pages redirects](https://kevin.deldycke.com/2022/cloudflare-commands#pages-redirects) (2022) documented the serving normalizations and the empty-folder double-rule idiom; the budget accounting was unknown then.
- [`cloudflare-redirects-linter`](https://github.com/kdeldycke/cloudflare-redirects-linter) (2024) was the test suite extracted into a standalone project. It never grew beyond the extraction: a diff on 2026-08-10 showed zero lines not already in this repository's suite. Its learnings are absorbed here — the engine replica supersedes its parser, the suite supersedes its checks — and the project can be archived.
- `content/extra/_redirects-backup` was the 2024-05-17 snapshot taken while the inventory work was in flight. Its content is a strict subset of today's file; deleted 2026-08-10.
