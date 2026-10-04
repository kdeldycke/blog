"""Local workarounds and additions for the Pelican behaviours this blog needs.

Fixes are collected here rather than pushed straight to Plumage or Pelican, so each one
gets exercised against the whole corpus before being proposed to whichever project it
belongs to. See ``claude.md`` for the policy.

The hooks install themselves on import: ``pelicanconf.py`` imports this module, and
Pelican reads its settings before it reads any content. Registering through the
``PLUGINS`` setting instead would be a trap, as ``load_plugins()`` only auto-discovers
the ``pelican.plugins`` namespace while ``PLUGINS`` is left unset. Naming one plugin
there would silently drop the six this blog relies on.
"""

from __future__ import annotations

import os
import posixpath
import re
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from itertools import chain
from operator import attrgetter
from pathlib import Path

import tomllib
from markdown_it import MarkdownIt
from pelican import signals
from pelican.contents import Article, Content
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Sequence

    from markdown_it.renderer import RendererHTML
    from markdown_it.token import Token
    from markdown_it.utils import EnvType, OptionsDict
    from pelican.generators import ArticlesGenerator

# The src of an <img>, captured in three pieces so the value can be swapped without
# disturbing the other attributes. Deliberately narrow: <img> is the only tag whose
# relative paths this blog writes by hand.
IMG_SRC = re.compile(r"""(<img\b[^>]*?\bsrc=["'])([^"']+)(["'])""", re.IGNORECASE)

# Anything carrying a scheme: http:, https:, data:, mailto: and friends.
HAS_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:", re.IGNORECASE)


def _is_source_relative(url: str) -> bool:
    """Is this a path a non-Pelican Markdown renderer would resolve on its own?"""
    # Already usable as-is: absolute, protocol-relative, site-rooted or a bare fragment.
    if not url or url.startswith(("/", "#")) or HAS_SCHEME.match(url):
        return False
    # An intra-site marker Pelican has yet to expand. `{attach}`, `{static}` and
    # `{filename}` are still literal at this point, because the substitution runs later
    # in `Content._update_content()`. Both delimiter styles are accepted by the default
    # INTRASITE_LINK_REGEX, so both are skipped. What they expand to is already absolute.
    return "{" not in url and "|" not in url


def absolutize_relative_images(instance: Content) -> None:
    """Turn image paths written relative to the Markdown file into absolute site URLs.

    Pelican only recognises its own ``{attach}`` marker, which nothing else understands:
    GitHub and editor previews render it as a broken image. A plain relative path renders
    everywhere, but Pelican has no reason to touch it, so it survives untouched into the
    tag and category feeds. There a reader resolves it against the feed's own URL rather
    than the article's, and 404s, because Pelican emits no ``xml:base``.

    Rewriting on ``content_object_init`` catches the content before the writer and the
    feed generator read it, so page and feed agree.

    Only articles qualify. For them the folder holding the Markdown file and the folder
    the page is written to are the same (``content/2005/`` becomes ``output/2005/``),
    which is exactly what lets a source-relative path survive into the output. Pages
    break that symmetry by being written to the site root, so they are left alone.
    """
    if not isinstance(instance, Article):
        return

    content = getattr(instance, "_content", None)
    source = getattr(instance, "relative_source_path", None)
    if not content or not source:
        return

    # Where the article's attachments land, relative to the site root. Taken from the
    # source path rather than from `save_as`, because that is what STATIC_PATHS mirrors
    # when it copies the files over.
    base = posixpath.dirname(source.replace(os.sep, "/"))
    siteurl = instance.settings.get("SITEURL", "").rstrip("/")

    def rewrite(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()
        if not _is_source_relative(url):
            return match.group(0)
        target = posixpath.normpath(posixpath.join(base, url)) if base else url
        return f"{prefix}{siteurl}/{target}{suffix}"

    instance._content = IMG_SRC.sub(rewrite, content)


# The href of an <a>, captured in the same three pieces as IMG_SRC above.
A_HREF = re.compile(r"""(<a\b[^>]*?\bhref=["'])([^"']+)(["'])""", re.IGNORECASE)


def unescape_link_ampersands(instance: Content) -> None:
    """Strip the second layer of escaping myst-parser leaves on the ``&`` of a link.

    myst-parser stores the target of a Markdown link already HTML-escaped, and the
    docutils writer escapes it again on the way out. A link to
    ``?kind=pear&colour=green`` therefore reaches the page as
    ``?kind=pear&amp;amp;colour=green``, which a browser decodes to
    ``?kind=pear&amp;colour=green``: the server gets a parameter named ``amp;colour``
    and never sees the one the author wrote.

    Only ``&`` comes out doubled, because markdown-it percent-encodes the other
    characters ``escapeHtml`` knows before the target gets that far. And only a link
    written in Markdown does: an ``<a>`` typed by hand in a post, an image and the
    archived comments are escaped once, so they hold no ``&amp;amp;`` for this to match.

    Runs on ``content_object_init`` for the reason given in
    ``absolutize_relative_images``, but on pages as well as articles: a target reads the
    same wherever the document is written.

    myst-parser 5.1.0 stores the target raw
    ([executablebooks/MyST-Parser#1126](https://github.com/executablebooks/MyST-Parser/pull/1126)),
    and this hook then matches nothing. pelican-myst-reader 1.4.0 requires
    ``myst-parser<5.0.0``, which keeps that release out of reach.

    ```{todo}
    Delete this hook, its tests and their canary once pelican-myst-reader ships a
    release that requires ``myst-parser>=5.1``. Its ``main`` branch does since
    [ashwinvis/myst-reader#49](https://github.com/ashwinvis/myst-reader/pull/49).
    ``test_myst_parser_escapes_link_targets_once`` fails the day that parser is
    installed.
    ```
    """
    content = getattr(instance, "_content", None)
    if not content:
        return

    def rewrite(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()
        return prefix + url.replace("&amp;amp;", "&amp;") + suffix

    instance._content = A_HREF.sub(rewrite, content)


# A canonical link already present in the document, whoever wrote it.
CANONICAL_LINK = re.compile(r"""<link\b[^>]*\brel=["']canonical["']""", re.IGNORECASE)


def _served_url(save_as: str) -> str:
    """Map a path under ``output/`` to the URL Cloudflare Pages serves it at.

    Pages resolves a directory to its ``index.html`` and strips ``.html`` from every
    other name, redirecting the suffixed spelling to the bare one. The output path
    therefore already carries the answer, and no generator state is needed to read it.
    """
    if save_as == "index.html":
        return ""
    if save_as.endswith("/index.html"):
        # Keep the trailing slash: TAG_URL and CATEGORY_URL both end in one.
        return save_as[: -len("index.html")]
    if save_as.endswith(".html"):
        return save_as[: -len(".html")]
    return save_as


def canonicalize_listings(path: str, context: dict) -> None:
    """Give every generated listing page a ``<link rel="canonical">``.

    The ``seo`` plugin writes one for articles and pages only: its ``run_html_enhancer``
    returns early unless the render context holds an ``article`` or a ``page``, which no
    listing template supplies. That leaves the homepage, the per-tag, per-category and
    per-year indexes, the ``archives``/``categories``/``tags`` summaries and the index
    pagination with nothing naming the host they belong to.

    It matters because the site answers on two hostnames. ``kevin.deldycke.com`` is a
    CNAME to ``kevin-deldycke-blog.pages.dev``, and Cloudflare keeps that subdomain
    publicly reachable for the life of the project: it cannot be deleted, and hiding it
    would take a Pages Function on every request, since neither ``_redirects`` nor
    ``_headers`` can match on host. Naming the canonical host in the markup costs
    nothing at request time and settles the question wherever the document is served
    from. See ``docs/infrastructure.md``.

    Paginated pages point at themselves rather than at the first page, which is what
    Google asks for: canonicalizing a sequence onto its head drops the rest of it.

    The tag is spliced in as text instead of through BeautifulSoup, the way the plugin
    does it. Re-serializing would round-trip 800-odd documents full of hand-written
    HTML through a parser for the sake of one line, and the corpus is exactly the kind
    that notices. Skipping documents that already carry a canonical keeps this safe to
    run over output the plugin has already touched.
    """
    if not path.endswith(".html"):
        return
    # Already handled by the seo plugin, whose receiver shares this signal.
    if context.get("article") or context.get("page"):
        return

    output_path = context.get("OUTPUT_PATH")
    siteurl = context.get("SITEURL", "").rstrip("/")
    if not output_path:
        return

    with open(path, encoding="utf-8") as document:
        markup = document.read()
    if CANONICAL_LINK.search(markup) or "</head>" not in markup:
        return

    url = _served_url(os.path.relpath(path, output_path).replace(os.sep, "/"))
    tag = f'<link href="{escape(f"{siteurl}/{url}", quote=True)}" rel="canonical">'
    with open(path, "w", encoding="utf-8") as document:
        document.write(markup.replace("</head>", f"{tag}</head>", 1))


# Where the comments archived from Disqus live, relative to the content root.
COMMENTS_FILE = "comments.toml"

# Every key a comment record may carry, with the type TOML must hand back for it.
COMMENT_FIELDS: dict[str, type] = {
    "article": str,
    "author": str,
    "body": str,
    "date": datetime,
    "id": int,
    "parent": int,
    "username": str,
    "wp_id": int,
}
REQUIRED_COMMENT_FIELDS = frozenset({"article", "author", "body", "date", "id"})

# Pygments' default HTML output: a <div class="highlight"> around a <pre>.
CODE_FORMATTER = HtmlFormatter()


def _render_code(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    """Highlight a code block with Pygments, the way the articles' code is highlighted.

    The fence names the lexer, and a missing or unknown name falls back to plain text.
    The output is Pygments' own ``.highlight`` container, which Plumage scopes its code
    styling and palette to. PHP snippets in comments rarely open with ``<?php``, so the
    lexer starts inline: other lexers ignore that option.
    """
    token = tokens[idx]
    name = token.info.split()[0] if token.info.strip() else ""
    try:
        lexer = get_lexer_by_name(name, startinline=True) if name else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    html: str = highlight(token.content, lexer, CODE_FORMATTER)
    return html


def _render_link_open(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    """Mark every link in a comment as one the site does not vouch for.

    Readers wrote these links, so they carry ``ugc``, the value search engines document
    for user-generated content, next to the older ``nofollow``. A link to another
    comment on the same page, like a mention, stays plain.
    """
    if not str(tokens[idx].attrGet("href") or "").startswith("#"):
        tokens[idx].attrSet("rel", "nofollow ugc")
    return self.renderToken(tokens, idx, options, env)


# Renders the body of archived comments: plain CommonMark, without the MyST extensions
# or the typographer articles go through. Raw HTML stays text, and a single newline is
# a line break, which is how Disqus displayed comments.
COMMENT_MARKDOWN = MarkdownIt("commonmark", {"breaks": True, "html": False})
COMMENT_MARKDOWN.add_render_rule("code_block", _render_code)
COMMENT_MARKDOWN.add_render_rule("fence", _render_code)
COMMENT_MARKDOWN.add_render_rule("link_open", _render_link_open)


def render_comment(body: str) -> str:
    """Render the Markdown body of an archived comment to HTML."""
    html: str = COMMENT_MARKDOWN.render(body)
    return html


@dataclass
class Comment:
    """A comment archived from Disqus, as curated in ``content/comments.toml``."""

    id: int
    """Disqus post ID. Also anchors the comment on its page."""
    article: str
    """Source path of the article under the content root, without its extension."""
    author: str
    date: datetime
    body: str
    """Markdown source of the comment."""
    parent: int | None = None
    """ID of the comment this one replies to."""
    username: str | None = None
    """Disqus account of a registered commenter."""
    wp_id: int | None = None
    """WordPress comment ID, for comments from before the move to Disqus."""
    html: str = ""
    """The rendered body."""
    replies: list[Comment] = field(default_factory=list)
    """Direct replies, oldest first."""

    @property
    def thread_size(self) -> int:
        """Number of comments in this thread, this one included."""
        return 1 + sum(reply.thread_size for reply in self.replies)


def load_comments(path: Path) -> dict[str, list[Comment]]:
    """Read the curated comments, render them, and thread each reply under its parent.

    Returns the top-level comments of every article, oldest first, keyed by the source
    path of the article. The file is edited by hand, so every record is checked. The
    first one a hand edit broke raises ``ValueError`` naming its ID: an unknown or
    missing field, a value of the wrong type, a repeated ID, or a reply whose parent is
    gone or sits under another article.
    """
    with path.open("rb") as data:
        records = tomllib.load(data).get("comment", [])

    comments: dict[int, Comment] = {}
    for record in records:
        label = f"Comment {record.get('id', '?')} in {path}"
        unknown = record.keys() - COMMENT_FIELDS.keys()
        if unknown:
            raise ValueError(
                f"{label} has unknown fields: {', '.join(sorted(unknown))}."
            )
        missing = REQUIRED_COMMENT_FIELDS - record.keys()
        if missing:
            raise ValueError(f"{label} lacks fields: {', '.join(sorted(missing))}.")
        mistyped = [
            f"{key} is {type(value).__name__}, not {COMMENT_FIELDS[key].__name__}"
            for key, value in record.items()
            if not isinstance(value, COMMENT_FIELDS[key])
        ]
        if mistyped:
            raise ValueError(f"{label}: {', '.join(mistyped)}.")
        if record["date"].tzinfo is None:
            raise ValueError(
                f"{label}: date needs a UTC offset, like 2011-03-14T09:26:53Z."
            )
        if record["id"] in comments:
            raise ValueError(f"{label} repeats the ID of another comment.")
        comment = Comment(**record)
        comment.html = render_comment(comment.body.strip())
        comments[comment.id] = comment

    threads: dict[str, list[Comment]] = {}
    for comment in sorted(comments.values(), key=attrgetter("date")):
        if comment.parent is None:
            threads.setdefault(comment.article, []).append(comment)
            continue
        parent = comments.get(comment.parent)
        if parent is None:
            raise ValueError(
                f"Comment {comment.id} in {path} replies to {comment.parent}, which is "
                "not in the file: delete the reply as well, or remove its parent key."
            )
        if parent.article != comment.article:
            raise ValueError(
                f"Comment {comment.id} in {path} replies to {comment.parent}, which is "
                "filed under another article."
            )
        parent.replies.append(comment)
    return threads


def attach_comments(generator: ArticlesGenerator) -> None:
    """Hang the comments archived from Disqus off the articles they were posted on.

    The theme override in ``content/templates/article.html`` renders ``comments`` below
    the article. Going through the template rather than the article's content keeps
    comments out of the feeds and the summaries, which reuse that content. The search
    index reads the rendered page instead, so ``STORK_INPUT_OPTIONS`` excludes them.

    Comments are matched to articles on the source path, never on the URL. The Disqus
    embed keyed its threads on the URL, so a change of URL scheme split threads in two.
    """
    path = Path(generator.settings["PATH"]) / COMMENTS_FILE
    if not path.is_file():
        return
    articles = {
        Path(article.relative_source_path).with_suffix("").as_posix(): article
        for article in chain(
            generator.articles,
            generator.translations,
            generator.hidden_articles,
            generator.hidden_translations,
            generator.drafts,
            generator.drafts_translations,
        )
    }
    for key, comments in load_comments(path).items():
        article = articles.get(key)
        if article is None:
            raise ValueError(
                f"Comment {comments[0].id} in {path} is filed under {key}, which "
                "matches no article."
            )
        article.comments = comments


def register() -> None:
    """Connect every patch above to the signal it hooks into.

    Safe to call more than once: Blinker keys receivers by identity, and this module is
    cached in ``sys.modules``, so a second call reconnects the same function objects.
    """
    signals.content_object_init.connect(absolutize_relative_images)
    signals.content_object_init.connect(unescape_link_ampersands)
    signals.content_written.connect(canonicalize_listings)
    signals.article_generator_finalized.connect(attach_comments)


register()
