# Blog guidelines

## Upstream fixes land here first

Pelican and Plumage behaviours that need changing are patched, hacked, or worked around **in this repository**, never by editing the theme or vendoring a fork.

**Why:** this repo is the only place where a fix meets the whole content corpus, so it is where the fix can be proven before anyone else has to live with it. Accumulating them in one place also keeps a reviewable list: each one can then be evaluated on its own merits and pushed to the project it belongs to, [kdeldycke/plumage](https://github.com/kdeldycke/plumage) for anything about presentation, [getpelican/pelican](https://github.com/getpelican/pelican) for anything about the engine. A fix applied directly upstream skips that evaluation and cannot easily be reverted here.

**How to apply:** put the workaround in `pelican_patches.py` and connect it to a Pelican signal from `register()`. `pelicanconf.py` imports that module, which is what installs the hooks.

Do not reach for the `PLUGINS` setting to load them. Pelican's `load_plugins()` only auto-discovers the `pelican.plugins` namespace while `PLUGINS` is unset:

```python
if settings.get("PLUGINS") is not None:
    ...  # load only what is named
else:
    plugins = list(namespace_plugins.values())
```

So naming a single plugin there silently drops the six this blog depends on: `myst_reader`, `neighbors`, `search`, `seo`, `sitemap` and `webassets`. The import side effect avoids that entirely, and is the same mechanism Plumage itself uses (`register_signals()` in its `__init__.py`).

When a patch graduates upstream, delete it here and tighten the dependency to the release that carries it.

## How a post is written must not decide how it is parsed

`pelican-myst-reader` chooses its renderer by scanning the file for markers:

```python
or any(syntax in content for syntax in ("{filename}", "{static}", "{attach}"))
```

Anything else falls back to the lighter docutils renderer, which rejects `{tag}` and `{category}` markers, refuses some of the Pygments lexers this corpus uses, and drops `attrs_inline` classes on the floor. So editing an image reference used to change how an entire article was parsed: removing the last `{attach}` from a post demoted it, and only the loudest three of 73 affected articles actually failed the build.

`MYST_FORCE_SPHINX = True` pins the renderer and severs that link. It costs roughly twice the build time.

Because the reader keeps **one settings key per renderer**, `MYST_SPHINX_SETTINGS` has to mirror `MYST_DOCUTILS_SETTINGS`. Configure only one and the other silently reverts to stock defaults: code blocks lose their line numbers, the heading anchor depth resets, and the extension list shrinks to `colon_fence` and `deflist`. Both keys are asserted equal in `test_pelican_patches.py`.

## Cooldown on every install

Nothing published in the last week gets installed, anywhere. `tests.yaml` and `deploy.yaml` both set `UV_EXCLUDE_NEWER: "1 week"` and `NPM_CONFIG_MIN_RELEASE_AGE: 7` at workflow level, and `[tool.uv] exclude-newer` carries the same window for anyone resolving locally. The three are kept equal to `[tool.repomatic] minimum-release-age`, which gates the `uvx` installs the reusable workflows run: a wider window here would lock a version those installs then refuse to resolve.

**Why:** a compromised release is caught and yanked in hours to days, and a week is long enough to sit out most of that without holding anything back meaningfully. It buys nothing against a package that was malicious from the start, so it is a delay, not a check: it is not a signature, a hash, or a review.

The window is set at workflow level rather than per command deliberately. A step added later inherits it without anyone remembering to flag it, which is the failure mode a per-command flag has.

Setting the variable is not the same as the cooldown being applied, and on the npm side it was not, from the day it was added until 2026-08-11. `min-release-age` reached npm in 11.10.0, both workflows installed npm from apt, and Ubuntu noble carries 9.2.0: an npm that old parses the setting as an unknown config key and drops it without a word. The window was declared, documented and inert, and it took reading the installed version out of a CI log to see it. Both workflows now upgrade the runner's own npm to a pinned release new enough to honour it, which also stops apt pulling Node 18 over the runner's Node 22. Before trusting any cooldown, check that the tool reading it is new enough to know the name.

**How to apply:** exemptions are per-package and explicit, never a widening of the window. `[tool.uv] exclude-newer-package` is the only one in use, holding `plumage` at zero days because I publish it myself, so the compromised-upstream case it guards against does not apply. Reach for `--exclude-newer-package` (uv) or `--min-release-age-exclude` (npm) if a second one is ever needed, and write down why next to it.

## Verify against a real build

A full `uv run -- pelican` is the only check that means anything: the corpus is 262 articles with plenty of hand-written HTML, and warnings surface only at build time. Compare before and after by hashing the whole `output/` tree, not by spot-checking a page.

Watch feeds specifically. Article markup is reused verbatim in `feed.rss`, `feed.atom` and every per-tag and per-category feed, where relative URLs resolve against the feed's own address instead of the article's. Something can look correct on the page and still be broken in nine feeds.
