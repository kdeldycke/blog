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

"""Checks on the comments archived from Disqus, and on the code that renders them.

``content/comments.toml`` is curated by hand, so the first test runs the build's own
loader over it: a curation slip fails here, without waiting for a full build.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from pelican import signals
from pelican.contents import Article
from pelican.settings import DEFAULT_CONFIG

import pelican_patches

CONTENT = Path(__file__).parent.parent / "content"

COMMENT = """
[[comment]]
article = "2020/apricot-tart"
id = 1
author = "Alice"
date = 2020-07-14T09:30:00Z
body = '''
Works with peaches too.
'''
"""

REPLY = """
[[comment]]
article = "2020/apricot-tart"
id = 2
parent = 1
author = "Bob"
date = 2020-07-15T18:00:00Z
body = '''
And with plums.
'''
"""


def load(tmp_path, toml):
    """Run the loader over a comments file holding ``toml``."""
    path = tmp_path / pelican_patches.COMMENTS_FILE
    path.write_text(toml, encoding="UTF-8")
    return pelican_patches.load_comments(path)


def walk(comments):
    for comment in comments:
        yield comment
        yield from walk(comment.replies)


def test_archive_is_consistent():
    threads = pelican_patches.load_comments(CONTENT / pelican_patches.COMMENTS_FILE)
    assert threads
    for article, comments in threads.items():
        assert (CONTENT / f"{article}.md").is_file(), f"No article at {article}."
        # A mention links to another comment of the same thread, which must still exist.
        ids = {comment.id for comment in walk(comments)}
        for comment in walk(comments):
            for anchor in re.findall(r"\]\(#comment-(\d+)\)", comment.body):
                assert int(anchor) in ids, (
                    f"Comment {comment.id} links to missing {anchor}."
                )


def test_wordpress_anchors_stay_unique():
    """Comments imported from WordPress carry its anchor next to the Disqus one."""
    threads = pelican_patches.load_comments(CONTENT / pelican_patches.COMMENTS_FILE)
    comments = [comment for top in threads.values() for comment in walk(top)]
    ids = [comment.id for comment in comments]
    wp_ids = [comment.wp_id for comment in comments if comment.wp_id is not None]
    assert len(set(wp_ids)) == len(wp_ids)
    assert not set(wp_ids) & set(ids)


def test_replies_nest_under_their_parent(tmp_path):
    # Out of order on purpose: the loader sorts by date, not by position in the file.
    later = COMMENT.replace("id = 1", "id = 3").replace("2020-07-14", "2020-07-16")
    threads = load(tmp_path, later + REPLY + COMMENT)
    first, second = threads["2020/apricot-tart"]
    assert (first.id, second.id) == (1, 3)
    assert [reply.id for reply in first.replies] == [2]
    assert (first.thread_size, second.thread_size) == (2, 1)
    assert first.html == "<p>Works with peaches too.</p>\n"


@pytest.mark.parametrize(
    ("toml", "message"),
    (
        (COMMENT.replace('author = "Alice"', 'author = "Alice"\nrating = 5'), "rating"),
        (COMMENT.replace('author = "Alice"\n', ""), "lacks fields: author"),
        (COMMENT.replace("id = 1", 'id = "1"'), "id is str, not int"),
        (COMMENT.replace("09:30:00Z", "09:30:00"), "UTC offset"),
        (COMMENT + COMMENT, "repeats the ID"),
        (REPLY, "replies to 1, which is not in the file"),
        (
            COMMENT + REPLY.replace("apricot-tart", "lemon-pie"),
            "filed under another article",
        ),
    ),
)
def test_curation_slips_are_caught(tmp_path, toml, message):
    with pytest.raises(ValueError, match=message):
        load(tmp_path, toml)


@pytest.mark.parametrize(
    ("body", "expected"),
    (
        # Raw HTML comes out as text, whoever typed it.
        ("<script>alert(1)</script>", "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>\n"),
        # A single newline is a line break, the way Disqus displayed comments.
        ("Sunny\nthen rain", "<p>Sunny<br />\nthen rain</p>\n"),
        (
            "[Forecast](https://example.com)",
            '<p><a href="https://example.com" rel="nofollow ugc">Forecast</a></p>\n',
        ),
        # A mention links to another comment on the page, and needs no rel.
        ("[@Alice](#comment-1)", '<p><a href="#comment-1">@Alice</a></p>\n'),
        (
            "<https://example.com>",
            '<p><a href="https://example.com" rel="nofollow ugc">https://example.com</a></p>\n',
        ),
        # Code blocks come out of Pygments, in the container the theme's styling
        # hangs off. Without a language, or with one Pygments lacks, as plain text.
        (
            "```\nif rain:\n    take(umbrella)\n```",
            (
                '<div class="highlight"><pre><span></span>if rain:\n    take(umbrella)\n'
                "</pre></div>\n"
            ),
        ),
        (
            "```klingon\nqapla\n```",
            '<div class="highlight"><pre><span></span>qapla\n</pre></div>\n',
        ),
        (
            "    indented < code",
            '<div class="highlight"><pre><span></span>indented &lt; code\n</pre></div>\n',
        ),
    ),
)
def test_rendering(body, expected):
    assert pelican_patches.render_comment(body) == expected


@pytest.mark.parametrize(
    ("body", "token"),
    (
        ('```python\nprint("sun")\n```', '<span class="nb">print</span>'),
        # PHP snippets rarely open with <?php: the lexer must start inline.
        ("```php\n$rain = true;\n```", '<span class="nv">$rain</span>'),
    ),
)
def test_code_blocks_are_highlighted(body, token):
    assert token in pelican_patches.render_comment(body)


def article(source_path):
    settings = DEFAULT_CONFIG.copy()
    settings["PATH"] = "/content"
    return Article(
        content="<p>Body</p>",
        metadata={"title": "Apricot tart"},
        settings=settings,
        source_path=source_path,
    )


def generator(tmp_path, *articles):
    """The parts of an ``ArticlesGenerator`` the hook reads."""
    lists = ("translations", "hidden_articles", "hidden_translations", "drafts")
    return SimpleNamespace(
        settings={"PATH": str(tmp_path)},
        articles=list(articles),
        drafts_translations=[],
        **{name: [] for name in lists},
    )


def test_comments_attach_on_source_path(tmp_path):
    (tmp_path / pelican_patches.COMMENTS_FILE).write_text(
        COMMENT + REPLY, encoding="UTF-8"
    )
    tart = article("/content/2020/apricot-tart.md")
    pie = article("/content/2020/lemon-pie.md")
    pelican_patches.attach_comments(generator(tmp_path, tart, pie))
    assert [comment.id for comment in tart.comments] == [1]
    assert not hasattr(pie, "comments")


def test_comments_on_a_missing_article_stop_the_build(tmp_path):
    (tmp_path / pelican_patches.COMMENTS_FILE).write_text(COMMENT, encoding="UTF-8")
    pie = article("/content/2020/lemon-pie.md")
    with pytest.raises(ValueError, match="filed under 2020/apricot-tart"):
        pelican_patches.attach_comments(generator(tmp_path, pie))


def test_no_comments_file_is_fine(tmp_path):
    tart = article("/content/2020/apricot-tart.md")
    pelican_patches.attach_comments(generator(tmp_path, tart))
    assert not hasattr(tart, "comments")


def test_hook_is_registered():
    """Guards the import side effect in pelicanconf.py, as the image patch test does."""
    receivers = signals.article_generator_finalized.receivers.values()
    resolved = {
        r() if callable(r) and not hasattr(r, "__name__") else r for r in receivers
    }
    assert pelican_patches.attach_comments in resolved
