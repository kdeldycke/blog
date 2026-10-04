# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""Regression tests for the local Pelican workarounds.

Every case below goes through a real ``Article``, not a stand-in, because the patch hangs
off ``content_object_init``, which Pelican fires from ``Content.__init__``. Building the
object therefore exercises the registration and the rewrite together: if the import side
effect in ``pelicanconf.py`` ever stops installing the hook, these fail.
"""

from __future__ import annotations

import re

import pytest
from myst_parser.parsers.docutils_ import to_html5_demo
from pelican.contents import Article, Page
from pelican.settings import DEFAULT_CONFIG

import pelican_patches

SITEURL = "https://kevin.deldycke.com"

# Somewhere under the content root. Only the folder matters: it is what the rewritten
# URL is built from, and what STATIC_PATHS mirrors when copying attachments over.
CONTENT_ROOT = "/content"
ARTICLE_SOURCE = f"{CONTENT_ROOT}/2005/post.md"


def build(content, cls=Article, source_path=ARTICLE_SOURCE, siteurl=SITEURL):
    """Instantiate a piece of Pelican content, which fires the signal the patch is on."""
    settings = DEFAULT_CONFIG.copy()
    settings["SITEURL"] = siteurl
    settings["PATH"] = CONTENT_ROOT
    return cls(
        content=content,
        metadata={"title": "Title"},
        settings=settings,
        source_path=source_path,
    )


@pytest.mark.parametrize(
    ("src", "expected"),
    (
        # Paths relative to the Markdown file are the whole point: they render in GitHub
        # and editor previews, and get anchored to the article's folder here.
        ("photo.jpg", f"{SITEURL}/2005/photo.jpg"),
        ("nested/photo.jpg", f"{SITEURL}/2005/nested/photo.jpg"),
        ("./photo.jpg", f"{SITEURL}/2005/photo.jpg"),
        ("../2004/photo.jpg", f"{SITEURL}/2004/photo.jpg"),
        # Anything already resolvable on its own is left exactly as it was.
        (f"{SITEURL}/2005/photo.jpg", f"{SITEURL}/2005/photo.jpg"),
        ("http://example.com/photo.jpg", "http://example.com/photo.jpg"),
        ("//example.com/photo.jpg", "//example.com/photo.jpg"),
        ("/rooted.jpg", "/rooted.jpg"),
        ("data:image/gif;base64,R0lGOD", "data:image/gif;base64,R0lGOD"),
        ("#fragment", "#fragment"),
        # Pelican's own markers are still literal at this point: they are expanded later,
        # by Content._update_content(), and come out absolute on their own. Both
        # delimiter styles of the default INTRASITE_LINK_REGEX have to survive.
        ("{attach}photo.jpg", "{attach}photo.jpg"),
        ("|attach|photo.jpg", "|attach|photo.jpg"),
        ("{static}/img/photo.jpg", "{static}/img/photo.jpg"),
        ("{filename}/2004/other.md", "{filename}/2004/other.md"),
    ),
)
def test_image_src_rewriting(src, expected):
    assert build(f'<img src="{src}"/>')._content == f'<img src="{expected}"/>'


@pytest.mark.parametrize(
    ("markup", "expected"),
    (
        # Quoting style, attribute order and every other attribute have to come out
        # untouched: only the value of src is the patch's business.
        (
            "<img src='photo.jpg'/>",
            f"<img src='{SITEURL}/2005/photo.jpg'/>",
        ),
        (
            '<img class="a" src="photo.jpg" alt="Some caption"/>',
            f'<img class="a" src="{SITEURL}/2005/photo.jpg" alt="Some caption"/>',
        ),
        (
            '<IMG SRC="photo.jpg"/>',
            f'<IMG SRC="{SITEURL}/2005/photo.jpg"/>',
        ),
        # An alt text mentioning a filename must not be mistaken for a src.
        (
            '<img src="photo.jpg" alt="named photo.jpg"/>',
            f'<img src="{SITEURL}/2005/photo.jpg" alt="named photo.jpg"/>',
        ),
        # Several images in one document, mixing forms.
        (
            '<img src="a.png"/><p>x</p><img src="{attach}b.png"/><img src="c.png"/>',
            (
                f'<img src="{SITEURL}/2005/a.png"/><p>x</p>'
                f'<img src="{{attach}}b.png"/><img src="{SITEURL}/2005/c.png"/>'
            ),
        ),
    ),
)
def test_surrounding_markup_is_preserved(markup, expected):
    assert build(markup)._content == expected


def test_rewrite_is_idempotent():
    """A second pass must be a no-op, since the first one produced absolute URLs."""
    article = build('<img src="photo.jpg"/>')
    once = article._content
    pelican_patches.absolutize_relative_images(article)
    assert article._content == once


def test_pages_are_left_alone():
    """Pages are written to the site root, so a source-relative path cannot resolve.

    Their attachments would also land in output/pages/, which is why the folder is kept
    out of STATIC_PATHS. Rewriting them would invent a URL nothing serves.
    """
    page = build(
        '<img src="photo.jpg"/>', cls=Page, source_path=f"{CONTENT_ROOT}/pages/p.md"
    )
    assert page._content == '<img src="photo.jpg"/>'


def test_article_at_content_root():
    """No folder to anchor to: the URL is built straight off the site root."""
    article = build('<img src="photo.jpg"/>', source_path=f"{CONTENT_ROOT}/post.md")
    assert article._content == f'<img src="{SITEURL}/photo.jpg"/>'


def test_siteurl_trailing_slash_does_not_double_up():
    article = build('<img src="photo.jpg"/>', siteurl=f"{SITEURL}/")
    assert article._content == f'<img src="{SITEURL}/2005/photo.jpg"/>'


@pytest.mark.parametrize("content", ("", "<p>No image here.</p>"))
def test_content_without_images_is_untouched(content):
    assert build(content)._content == content


def test_article_without_source_path_is_safe():
    """Content built in memory has no source path to anchor against, and must not raise."""
    article = build('<img src="photo.jpg"/>', source_path=None)
    assert article._content == '<img src="photo.jpg"/>'


@pytest.mark.parametrize(
    "hook",
    (
        pelican_patches.absolutize_relative_images,
        pelican_patches.unescape_link_ampersands,
    ),
)
def test_hook_is_registered(hook):
    """Guards the import side effect in pelicanconf.py, which is what installs the hooks.

    Nothing else in the build references these functions by name, so a lost import would
    otherwise only show up as silently broken images in the feeds, or as links that lose
    their parameters.
    """
    from pelican import signals

    receivers = signals.content_object_init.receivers.values()
    resolved = {
        r() if callable(r) and not hasattr(r, "__name__") else r for r in receivers
    }
    assert hook in resolved


# A link the way myst-parser and the docutils writer lay it out.
LINK = '<a class="reference external" href="{}">pears</a>'


@pytest.mark.parametrize(
    ("href", "expected"),
    (
        # What a Markdown link comes out as: every & of its target escaped twice.
        (
            "https://example.com/fruit?kind=pear&amp;amp;colour=green",
            "https://example.com/fruit?kind=pear&amp;colour=green",
        ),
        (
            "https://example.com/fruit?kind=pear&amp;amp;colour=green&amp;amp;ripe=1",
            "https://example.com/fruit?kind=pear&amp;colour=green&amp;ripe=1",
        ),
        # A parameter named like the entity loses one layer as well, and keeps its name.
        (
            "https://example.com/fruit?kind=pear&amp;amp;amp=1",
            "https://example.com/fruit?kind=pear&amp;amp=1",
        ),
        # Escaped once, the way a hand-written <a> is, or with nothing to escape: left
        # exactly as it was.
        (
            "https://example.com/fruit?kind=fig&amp;colour=brown",
            "https://example.com/fruit?kind=fig&amp;colour=brown",
        ),
        ("https://example.com/fruit", "https://example.com/fruit"),
        ("{filename}/2004/other.md#ripe", "{filename}/2004/other.md#ripe"),
    ),
)
def test_link_target_unescaping(href, expected):
    assert build(LINK.format(href))._content == LINK.format(expected)


@pytest.mark.parametrize(
    ("markup", "expected"),
    (
        # Quoting style, attribute order and every other attribute have to come out
        # untouched, a doubled entity in a title included: only the target is the
        # patch's business.
        (
            "<a href='https://example.com/fruit?kind=pear&amp;amp;colour=green'>x</a>",
            "<a href='https://example.com/fruit?kind=pear&amp;colour=green'>x</a>",
        ),
        (
            '<a title="pears &amp;amp; figs" href="/fruit?kind=pear&amp;amp;ripe=1">x</a>',
            '<a title="pears &amp;amp; figs" href="/fruit?kind=pear&amp;ripe=1">x</a>',
        ),
        (
            '<A HREF="https://example.com/fruit?kind=pear&amp;amp;colour=green">x</A>',
            '<A HREF="https://example.com/fruit?kind=pear&amp;colour=green">x</A>',
        ),
        # Several links in one document, mixing forms.
        (
            (
                '<a href="/fruit?kind=pear&amp;amp;ripe=1">x</a><p>y</p>'
                '<a href="/fruit?kind=fig&amp;ripe=0">z</a>'
            ),
            (
                '<a href="/fruit?kind=pear&amp;ripe=1">x</a><p>y</p>'
                '<a href="/fruit?kind=fig&amp;ripe=0">z</a>'
            ),
        ),
    ),
)
def test_markup_around_link_target_is_preserved(markup, expected):
    assert build(markup)._content == expected


@pytest.mark.parametrize(
    "markup",
    (
        # A doubled entity shown to the reader on purpose, in prose or in a code sample.
        "<p>Escaped twice, an ampersand reads &amp;amp;.</p>",
        '<pre>&lt;a href="/fruit?kind=pear&amp;amp;ripe=1"&gt;</pre>',
        # myst-parser escapes an image source once, so a doubled entity there is the
        # author's own.
        '<img src="https://example.com/pear.png?w=10&amp;amp;h=20"/>',
    ),
)
def test_doubled_entities_outside_link_targets_are_untouched(markup):
    assert build(markup)._content == markup


def test_link_unescaping_is_idempotent():
    """A second pass must be a no-op, since the first one left single entities."""
    article = build(LINK.format("/fruit?kind=pear&amp;amp;colour=green"))
    once = article._content
    pelican_patches.unescape_link_ampersands(article)
    assert article._content == once


def test_pages_get_their_link_targets_unescaped_too():
    """Unlike an image path, a link target reads the same wherever the page lands."""
    page = build(
        LINK.format("/fruit?kind=pear&amp;amp;colour=green"),
        cls=Page,
        source_path=f"{CONTENT_ROOT}/pages/p.md",
    )
    assert page._content == LINK.format("/fruit?kind=pear&amp;colour=green")


@pytest.mark.xfail(
    reason=(
        "myst-parser escapes a link target that the docutils writer escapes again, "
        "until 5.1.0. Once this passes, delete unescape_link_ampersands()."
    )
)
def test_myst_parser_escapes_link_targets_once():
    """Tells the day the workaround has graduated upstream and can go.

    Renders a link through the installed myst-parser, with no patch involved, and expects
    what a fixed release produces. ``xfail_strict`` turns the first pass into a failure.
    """
    html = to_html5_demo("[pears](https://example.com/fruit?kind=pear&colour=green)")
    assert 'href="https://example.com/fruit?kind=pear&amp;colour=green"' in html


LISTING = "<html><head><title>Tag: Python</title></head><body>x</body></html>"

HREF = re.compile(r"""<link\s+href="([^"]+)"\s+rel="canonical">""")


def render(tmp_path, relative, markup=LISTING, **context):
    """Lay a rendered document under a fake ``output/`` tree and fire the signal on it."""
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markup, encoding="utf-8")
    pelican_patches.canonicalize_listings(
        str(target),
        {"OUTPUT_PATH": str(tmp_path), "SITEURL": SITEURL, **context},
    )
    return target.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("save_as", "url"),
    (
        # A directory index is served at the directory, trailing slash and all: that is
        # the exact spelling of TAG_URL, CATEGORY_URL and YEAR_ARCHIVE_SAVE_AS.
        ("index.html", ""),
        ("tag/python/index.html", "tag/python/"),
        ("category/english/index.html", "category/english/"),
        ("2004/index.html", "2004/"),
        # Everything else loses the suffix, because Pages redirects the .html spelling
        # to the bare one and serving both under one canonical is the whole point.
        ("archives.html", "archives"),
        ("categories.html", "categories"),
        ("tags.html", "tags"),
        ("page/2.html", "page/2"),
    ),
)
def test_served_url(save_as, url):
    assert pelican_patches._served_url(save_as) == url


@pytest.mark.parametrize(
    ("save_as", "expected"),
    (
        ("index.html", f"{SITEURL}/"),
        ("tag/python/index.html", f"{SITEURL}/tag/python/"),
        ("archives.html", f"{SITEURL}/archives"),
        # Pagination points at itself. Canonicalizing a sequence onto its first page is
        # what makes search engines drop the rest of it.
        ("page/2.html", f"{SITEURL}/page/2"),
        ("page/13.html", f"{SITEURL}/page/13"),
    ),
)
def test_listing_gets_canonical(tmp_path, save_as, expected):
    assert HREF.search(render(tmp_path, save_as)).group(1) == expected


def test_canonical_lands_inside_head(tmp_path):
    markup = render(tmp_path, "tags.html")
    assert markup.index('rel="canonical"') < markup.index("</head>")
    assert markup.startswith("<html><head><title>")


@pytest.mark.parametrize(
    "context",
    ({"article": object()}, {"page": object()}),
    ids=("article", "page"),
)
def test_seo_plugin_territory_is_left_alone(tmp_path, context):
    """Articles and pages already get a canonical from the plugin, on this same signal."""
    assert render(tmp_path, "2005/post.html", **context) == LISTING


def test_existing_canonical_is_not_doubled(tmp_path):
    """Safe to run over output the plugin has already touched, whatever the hook order."""
    already = LISTING.replace(
        "</head>", f'<link href="{SITEURL}/elsewhere" rel="canonical"></head>'
    )
    assert render(tmp_path, "tags.html", markup=already) == already


@pytest.mark.parametrize("markup", ("", "<html><body>no head</body></html>"))
def test_document_without_head_is_skipped(tmp_path, markup):
    assert render(tmp_path, "tags.html", markup=markup) == markup


def test_non_html_is_skipped(tmp_path):
    assert render(tmp_path, "feed.rss", markup="<rss/>") == "<rss/>"


def test_siteurl_trailing_slash_does_not_double_up_in_canonical(tmp_path):
    markup = render(tmp_path, "tags.html", SITEURL=f"{SITEURL}/")
    assert HREF.search(markup).group(1) == f"{SITEURL}/tags"


def test_canonical_hook_is_registered():
    """Guards the import side effect, same as the images hook above."""
    from pelican import signals

    receivers = signals.content_written.receivers.values()
    resolved = {
        r() if callable(r) and not hasattr(r, "__name__") else r for r in receivers
    }
    assert pelican_patches.canonicalize_listings in resolved


def test_myst_renderer_is_pinned():
    """Dropping {attach} from a post must not change how that post is parsed.

    pelican-myst-reader picks the Sphinx renderer only when it spots "{filename}",
    "{static}" or "{attach}" in the file, and falls back to docutils otherwise. Migrating
    an image away from the marker therefore used to demote whole articles, and docutils
    then rejects the "{tag}" and "{category}" markers and some of the Pygments lexers the
    corpus uses. Pinning the renderer is what decouples the two.
    """
    import pelicanconf

    assert pelicanconf.MYST_FORCE_SPHINX is True


def test_myst_settings_reach_both_renderers():
    """Every documented MyST option has to apply whichever renderer ends up running.

    The reader keeps one settings key per renderer and silently falls back to its own
    defaults for whichever is missing. Configuring only the docutils side while forcing
    Sphinx would drop the code-block line numbers, reset the heading anchor depth, and
    cut the extension list down to colon_fence and deflist.
    """
    import pelicanconf

    for key, value in pelicanconf.MYST_DOCUTILS_SETTINGS.items():
        assert pelicanconf.MYST_SPHINX_SETTINGS[key] == value, key
