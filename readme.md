# Kevin Deldycke's blog

Source and content to generate my static [blog](https://kevin.deldycke.com),
which is powered by [Pelican](https://getpelican.com) (engine) and
[Plumage](https://github.com/kdeldycke/plumage) (theme).

## Installation

- Fetch a copy of the repository:

  ```shell-session
  $ git clone https://github.com/kdeldycke/blog.git
  $ cd ./blog
  ```

- Install `uv`. There is no separate Python step: `uv` fetches and manages the interpreter itself.

  ```shell-session
  $ brew install uv
  ```

- Install Node.js, which brings `npm` along. Plumage's asset pipeline shells out to `npm` to install its PostCSS toolchain, and the build aborts on `npm CLI not found` without it:

  ```shell-session
  $ brew install node
  ```

- Install Stork, which builds the site's search index. There is no Homebrew formula for it, so it goes through `cargo`:

  ```shell-session
  $ brew install rust
  $ cargo install stork-search --locked
  ```

  The `pelican-search` plugin looks for `stork` on `$PATH` and raises `Stork must be installed and available on $PATH.` if it is missing. To build without it, set `STORK_SEARCH = False` in `pelicanconf.py`.

- Install this blog's dependencies, pinning Python to 3.13:

  ```shell-session
  $ uv venv --python 3.13
  $ uv sync --all-extras
  ```

  Pick 3.12 or 3.13, not 3.14: `watchfiles` ships no wheel for 3.14, so `uv` falls back to compiling it from source and the Rust build fails.

## Build and browse website

`uv run` resolves the virtualenv on its own, so none of the commands below need `source .venv/bin/activate`.

- To build the content, in one terminal, run:

  ```shell-session
  $ uv run -- pelican
  ```

  The very first build is the slow one: Plumage installs its Node.js dependencies before it can compile any CSS. Expect a `postcss CLI not found` warning on that run only. A full build of the site takes a couple of minutes.

- And to serve the website, in another terminal:

  ```shell-session
  $ uv run -- pelican --listen
  (...)
  Serving site at: 127.0.0.1:8000 - Tap CTRL-C to stop
  ```

- Then go to [http://localhost:8000](http://localhost:8000).

- While writing, a single terminal rebuilding on every change is more convenient than the two above:

  ```shell-session
  $ uv run -- pelican --autoreload --listen
  ```

## Hosting

The site is rendered by GitHub Actions and uploaded to Cloudflare Pages as a finished tree: Cloudflare never builds it. [`docs/infrastructure.md`](docs/infrastructure.md) covers how a deploy reaches readers, every setting that deviates from a stock Cloudflare project and why, how to rotate the deploy token, and how to rebuild the whole thing from nothing. [`docs/redirects.md`](docs/redirects.md) covers the twenty-year URL inventory in `content/extra/_redirects` and the engine subtleties that decide which of its rules exist.

Cloudflare keeps settings that no file here can express. To check the live project still matches what the repository declares:

```shell-session
$ python scripts/cloudflare_config.py --check
```

The same check runs on every deploy and monthly on a schedule.

## Theme development

The section above is enough to add and modify the website content.

Now if you need to work both on the content and the theme you need to:

- Get a local copy of the theme outside your `./blog` virtualenv:

  ```shell-session
  $ cd ..
  $ git clone https://github.com/kdeldycke/plumage.git
  $ cd ./blog
  ```

- Drop the version constraint on the `plumage` dependency in the blog's `pyproject.toml`, from:

  ```toml
  dependencies = [
      ...
      "plumage>=5.0.0",
      ...
  ]
  ```

  To:

  ```toml
  dependencies = [
      ...
      "plumage",
      ...
  ]
  ```

- Also add this new section in the same `pyproject.toml`, to [force `uv` to pick up the latest local copy](https://github.com/astral-sh/uv/issues/2844#issuecomment-2241196371):

  ```toml
  [tool.uv.sources]
  plumage = { path = "../plumage", editable = true }
  ```

- Then re-sync so the editable checkout replaces the released theme:

  ```shell-session
  $ uv sync --all-extras
  ```

  Both edits are local scaffolding, so revert them and re-sync before committing: leaving them in place pins the blog to a path that only exists on your machine. `uv.lock` records the switch too, so check it has gone back to the registry version.

## TODO

### Content

- Use ML to produce article's summaries.
- https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags
- https://github.com/getpelican/pelican-plugins/tree/master/post_stats
- https://github.com/getpelican/pelican-plugins/tree/master/filetime_from_git
- dark theme? https://github.com/alexandrevicenzi/Flex/blob/bbf47fe35473774d8a41478523cf4d3b21268e35/templates/base.html#L31-L44

### Plugins

- clean_summary
- https://github.com/getpelican/pelican-plugins/tree/master/representative_image
- https://github.com/jhshi/pelican.plugins.post_revision

### Theme

- Re-use previous artworks from Maomium ?
- Use https://github.com/getpelican/pelican-plugins/tree/master/footer_insert
  to add generation time / git SHA / github action workflow debug info to
  each HTML file?

## Dependencies

```mermaid docs/assets/dependencies.mmd
```

## License

The content of this repository is copyrighted © 2004-2024 Kevin Deldycke.

Unless contrary mention, the content of this repository is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC
BY-NC-SA 4.0) license](license).
