import re
import sys
from pathlib import Path
from typing import Any

# Pelican loads this file by path, which does not put its folder on the import path. The
# `pelican` console script leaves sys.path[0] pointing at the venv's bin, so a plain
# `import pelican_patches` below would only resolve when the interpreter happened to be
# started from this directory. Anchoring on __file__ keeps it working whatever the
# working directory or entry point.
sys.path.insert(0, str(Path(__file__).parent))

import plumage

# Imported for its side effect: the module connects this repo's local workarounds to
# Pelican's signals on import. See claude.md for why they are not loaded via PLUGINS.
import pelican_patches  # noqa: F401

SITEURL = "http://localhost:8000"
RELATIVE_URLS = False

DELETE_OUTPUT_DIRECTORY = True

AUTHOR = SITENAME = "Kevin Deldycke"

PATH = "content"

TIMEZONE = "Europe/Paris"

TYPOGRIFY = True

# https://github.com/ashwinvis/myst-reader#docutils-renderer
# Annotated because the values are of mixed types, which otherwise leaves the dict as
# dict[str, object] and makes the set() copy below unresolvable.
MYST_DOCUTILS_SETTINGS: dict[str, Any] = {
    # Allow to use the ```mermaid (...)``` directive:
    # "myst_fence_as_directive": {"python", "shell-session", "mermaid"},
    "myst_number_code_blocks": ["python", "shell-session"],
    # 7 is the max value:
    # https://github.com/executablebooks/MyST-Parser/blob/5f03f5c/myst_parser/config/main.py#L291
    "myst_heading_anchors": 7,
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
    "myst_enable_extensions": {
        "attrs_block",
        "attrs_inline",
        # A Sphinx-side default, named here because the two dicts below are merged over
        # the reader's defaults key by key: a set given here replaces the stock one
        # outright rather than adding to it, so anything left out is switched off.
        "colon_fence",
        "deflist",
        "replacements",
        "smartquotes",
        "strikethrough",
        "tasklist",
    },
}

# The same configuration, handed to the other renderer. The reader keeps one settings key
# per renderer and falls back to its own defaults for whichever is missing, so with
# MYST_FORCE_SPHINX below and no entry here every option above would be silently dropped:
# code blocks lose their line numbers, heading anchors go back to the default depth, and
# the extension list shrinks to colon_fence and deflist.
MYST_SPHINX_SETTINGS = {
    **MYST_DOCUTILS_SETTINGS,
    # Copied rather than shared, so that the reader mutating one renderer's extension set
    # cannot reach the other's.
    "myst_enable_extensions": set(MYST_DOCUTILS_SETTINGS["myst_enable_extensions"]),
    # Sphinx hangs a ¶ permalink off every heading. The theme already links its own
    # headings, and the character leaks into feed summaries and the search index.
    "html_permalinks": False,
}

# Render every document with the Sphinx renderer, instead of letting the reader pick.
#
# Left to itself, pelican-myst-reader falls back to the lighter docutils renderer unless
# the file contains one of "{filename}", "{static}" or "{attach}". That makes an image
# marker decide how the whole page is parsed: dropping one from a post whose only other
# links were "{tag}" or "{category}" markers silently demotes it, and docutils then fails
# to resolve those and rejects the Pygments lexers Sphinx accepts.
#
# Pinning the renderer decouples the two, so how a page is written no longer changes how
# it is parsed.
MYST_FORCE_SPHINX = True

# Plugins are deliberately not listed. Pelican auto-discovers everything in the
# pelican.plugins namespace for as long as PLUGINS is left unset, and naming even one
# there switches that off, silently dropping the rest. See claude.md.

# Allow MyST syntax in content metadata:
# https://github.com/ashwinvis/myst-reader/tree/main#specifying-file-metadata
FORMATTED_FIELDS = [
    "title",
]

# Do not publish articles set in the future
WITH_FUTURE_DATES = False

# Force Pelican to use the file name as the slug, instead of derivating it from
# the title.
SLUGIFY_SOURCE = "basename"

ARTICLE_URL = "{date:%Y}/{slug}"
ARTICLE_SAVE_AS = ARTICLE_URL + ".html"
# Select all yearly folders as containing articles and their attachments.
ARTICLE_PATHS = [
    d.name
    for d in (Path(__file__).parent / PATH).iterdir()
    if d.is_dir() and re.fullmatch("[0-9]{4}", d.name)
]

PAGE_URL = "{slug}"
PAGE_SAVE_AS = "{slug}.html"

TEMPLATE_PAGES = {
    "templates/themes.html": "themes.html",
}

TAG_URL = "tag/{slug}/"
TAG_SAVE_AS = TAG_URL + "index.html"

CATEGORY_URL = "category/{slug}/"
CATEGORY_SAVE_AS = CATEGORY_URL + "index.html"

# Only activates yearly archives. Keep monthly and daily archives deactivated.
YEAR_ARCHIVE_SAVE_AS = "{date:%Y}/index.html"

# Tags, categories and archives are Direct Templates, so they don't have a
# <NAME>_URL option.
# Note: ``DIRECT_TEMPLATES`` work a bit differently and only the ``_SAVE_AS`` settings
# are available. See: https://docs.getpelican.com/en/latest/settings.html#url-settings
ARCHIVES_SAVE_AS = "archives.html"
CATEGORIES_SAVE_AS = "categories.html"
TAGS_SAVE_AS = "tags.html"
# Deactivate author URLs. Empty strings rather than False: both are falsy, so the
# generators skip the pages and the theme's `{% if AUTHOR_SAVE_AS %}` guard still hides
# the byline links, but Pelican logs a warning for every non-string *_SAVE_AS it reads.
AUTHORS_SAVE_AS = ""
AUTHOR_SAVE_AS = ""

# Deactivate localization
ARTICLE_LANG_SAVE_AS = None
DRAFT_LANG_SAVE_AS = None
PAGE_LANG_SAVE_AS = None

FEED_RSS = "feed.rss"
FEED_ATOM = "feed.atom"
# Only the feeds Pelican would otherwise produce are switched off here. FEED_ALL_RSS and
# TRANSLATION_FEED_RSS are absent from Pelican's defaults, so they are already None.
FEED_ALL_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

TAG_FEED_RSS = "tag/{slug}/feed.rss"
TAG_FEED_ATOM = "tag/{slug}/feed.atom"

CATEGORY_FEED_RSS = "category/{slug}/feed.rss"
CATEGORY_FEED_ATOM = "category/{slug}/feed.atom"

FEED_MAX_ITEMS = 5
FEED_APPEND_REF = True
USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = "English"
DEFAULT_DATE_FORMAT = "%b. %d, %Y"
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False

# Pagination.
DEFAULT_ORPHANS = 2
DEFAULT_PAGINATION = 5
# Deactivate pagination everywhere but the index page.
PAGINATED_TEMPLATES = {
    "index": DEFAULT_PAGINATION,
}
PAGINATION_PATTERNS = (
    (1, "{url}", "{save_as}"),
    (2, "{base_name}/page/{number}", "{base_name}/page/{number}.html"),
)

THEME = plumage.get_path()

# Searched before the theme, so a template here can extend Plumage's own through the
# "!theme/" prefix instead of replacing it whole. article.html adds the comments
# archived from Disqus.
THEME_TEMPLATES_OVERRIDES = [str(Path(__file__).parent / PATH / "templates")]

# The yearly folders are listed here as well as in ARTICLE_PATHS, so that an image
# referenced by a plain relative path gets copied to the output. Pelican otherwise only
# copies what an {attach} marker points at, and that marker renders as a broken image
# anywhere outside Pelican: on GitHub, and in any editor preview. Article attachments
# land in the same place either way, because a post in content/2005/ is written to
# output/2005/, so the two forms coexist and content can migrate one file at a time.
#
# Only the article folders. Pages are written to the site root while their attachments
# would be copied to output/pages/, so listing "pages" here would duplicate every one of
# them under a path nothing links to.
STATIC_PATHS = ["extra", *ARTICLE_PATHS]

EXTRA_PATH_METADATA = {
    "extra/_headers": {"path": "_headers"},
    "extra/_redirects": {"path": "_redirects"},
    "extra/favicon.ico": {"path": "favicon.ico"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/profile-photo-square-thumbnail.jpg": {
        "path": "profile-photo-square-thumbnail.jpg"
    },
}


# ----- Plugin-specific settings

# pelican.plugins.webassets
#
# By default webassets drops its build cache inside the directory it writes to, which
# here is the published theme folder: six opaque hash-named files ended up live at
# /theme/.webassets-cache/* because the deploy ships output/ verbatim. The cache is a
# build accelerator, not content, so park it at the repository root, where .gitignore
# already covers it. Every deploy uploads the complete tree, so the stray copy already
# in production disappears on the first deploy carrying this setting.
#
# The directory must exist before webassets touches it: `get_cache()` only creates the
# default location, and a path handed to `FilesystemCache` is used as-is, with every
# cache miss swallowed as ENOENT. Without the mkdir the setting silently degrades to
# "no cache at all".
#
# This must be WEBASSETS_CONFIG, not the older ASSET_CONFIG. Plumage's
# `setup_webassets()` always writes a WEBASSETS_CONFIG into settings to inject its
# PostCSS filter, and the webassets plugin reads ASSET_CONFIG only as a fallback when
# WEBASSETS_CONFIG is absent, which under Plumage it never is. An ASSET_CONFIG here
# still triggers the plugin's deprecation warning, because that fires on the key's
# presence, while the value itself is never consulted: a config that looks wired and
# does nothing.
_WEBASSETS_CACHE = Path(__file__).parent / ".webassets-cache"
_WEBASSETS_CACHE.mkdir(exist_ok=True)
WEBASSETS_CONFIG = {"cache": str(_WEBASSETS_CACHE)}

# pelican.plugins.search
#
# Stork indexes the <main> element of every page, and that is where the comments
# archived from Disqus render. Excluding them keeps search results on what the
# articles themselves say.
STORK_INPUT_OPTIONS = {"exclude_html_selector": "#comments"}

# pelican.plugins.seo
SEO_REPORT = False
SEO_ENHANCER = True
SEO_ENHANCER_OPEN_GRAPH = True


# ----- Theme-specific settings

SITE_THUMBNAIL = "/profile-photo-square-thumbnail.jpg"
SITE_THUMBNAIL_TEXT = "Might come with a beard"

SITESUBTITLE = " — 🦬🪒🐇🕳 yak-shaving the rabbit holes"

MENUITEMS = (
    ("Home", "/"),
    ("Themes", "/themes"),
    ("About", "/about"),
)

CODE_STYLE = "monokai"

STORK_SEARCH = True

ARTICLE_EDIT_LINK = (
    "https://github.com/kdeldycke/blog/edit/main/content/posts/%(slug)s.md"
)

SOCIAL_WIDGET_NAME = "Online presence"
SOCIAL = (
    ("X", "https://x.com/kdeldycke"),
    ("GitHub", "https://github.com/kdeldycke"),
    ("Hacker News", "https://news.ycombinator.com/user?id=kdeldycke"),
)

LINKS_WIDGET_NAME = "Professional profiles"
LINKS = (("LinkedIn", "https://linkedin.com/in/kevindeldycke/en"),)

COPYRIGHT = """Unless contrary mentioned, the content of this site is published
under a <a class="text-body-secondary" rel="license"
href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International license</a>."""
