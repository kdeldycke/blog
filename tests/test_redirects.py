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

"""Validate ``content/extra/_redirects`` the way production will actually read it.

Two layers, and both are needed:

- **Offline**, against the engine replica in ``pages_redirects_engine``: the file
  must survive parsing whole. Cloudflare's parser silently discards rules past its
  budgets and the deploy pipeline surfaces none of it, so this suite is the only
  place a regression can fail loudly before it ships. This is where the file's
  statics-first contract is enforced.
- **Online**, against the live site: one request per rule, expectations computed by
  the same replica. Production is the referee; the replica only predicts it.

See: https://developers.cloudflare.com/pages/configuration/redirects/
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from pathlib import Path
from string import ascii_letters, digits
from typing import TYPE_CHECKING
from urllib.parse import quote, urljoin, urlsplit

if TYPE_CHECKING:
    # What `pytest.param()` returns. pytest exposes the factory but not the type it
    # produces, so the annotation has to reach into the private module. Behind
    # TYPE_CHECKING it costs nothing at runtime and cannot break collection if the
    # module ever moves.
    from _pytest.mark.structures import ParameterSet

import pytest
import requests
from pages_redirects_engine import (
    MAX_DYNAMIC_RULES,
    PLACEHOLDER_REGEX,
    apply_rule,
    evaluate,
    parse_redirects,
)

DOMAIN = "deldycke.com"
SUB_DOMAIN = f"kevin.{DOMAIN}"
ROOT_URL = f"https://{SUB_DOMAIN}"
# Anchored on this file rather than the working directory, so the suite can be run from
# anywhere now that it no longer sits at the repository root.
REDIRECT_FILE = Path(__file__).parent.parent / "content/extra/_redirects"

PARSED = parse_redirects(REDIRECT_FILE.read_text(encoding="utf-8"))


# ----- Offline: the file versus the engine


def test_file_survives_the_engine():
    """Every rule in the file must come out the other side of the parser.

    The engine does not fail on a bad file: it drops what it dislikes and, past the
    dynamic budget, discards everything that follows. This site ran for years with
    its last 18 rules silently dead that way. Nothing downstream will ever report
    it, so this assertion is the tripwire.
    """
    assert PARSED.aborted_at_line is None, (
        f"The engine stopped reading the file at line {PARSED.aborted_at_line}: "
        f"{PARSED.invalid[-1].message}"
    )
    assert not PARSED.invalid, [invalid.message for invalid in PARSED.invalid]


def test_statics_first_contract():
    """All exact rules precede all pattern rules, with dynamic budget to spare.

    A static rule is only free while it appears before the first dynamic one; after
    that every line burns the 100-rule dynamic budget. Keeping the halves separated
    is what keeps 64 rules free and leaves headroom for decades more URL debt.
    """
    kinds = [rule.is_dynamic for rule in PARSED.rules]
    first_dynamic = kinds.index(True)
    assert all(kinds[first_dynamic:]), (
        "Static rule found after the first dynamic rule: it would silently consume "
        "the dynamic budget."
    )
    dynamic_count = sum(kinds)
    assert dynamic_count <= MAX_DYNAMIC_RULES, (
        f"{dynamic_count} dynamic rules exceed the engine cap of {MAX_DYNAMIC_RULES}."
    )


def test_sources_are_sane():
    """Constraints the engine enforces by silently dropping, promoted to failures."""
    seen: set[str] = set()
    for rule in PARSED.rules:
        assert rule.source not in seen, f"Duplicate source: {rule.source}"
        seen.add(rule.source)
        assert rule.source.count("*") <= 1, (
            f"Only one splat is allowed per source: {rule.source}"
        )
        if "*" in rule.source:
            assert ":splat" not in rule.source, (
                f"A source cannot mix * with :splat: {rule.source}"
            )


def test_destinations_are_sane():
    """Typos in destinations are not engine errors, they are broken redirects.

    The replacer substitutes only the placeholders the source captured; anything
    else stays in the URL as a literal ``:typo``. The engine will never complain,
    the visitor will.
    """
    for rule in PARSED.rules:
        assert "*" not in rule.destination, (
            f"Splats are written :splat in destinations: {rule.destination}"
        )
        available = {name[1:] for name in PLACEHOLDER_REGEX.findall(rule.source)}
        if "*" in rule.source:
            available.add("splat")
        used = {name[1:] for name in PLACEHOLDER_REGEX.findall(rule.destination)}
        assert used <= available, (
            f"{rule.source} -> {rule.destination}: destination uses placeholders "
            f"the source never captures: {sorted(used - available)}"
        )


# ----- Online: every rule exercised against production


def token(seed: str) -> str:
    """An arbitrary but stable stand-in for a placeholder or splat value.

    Arbitrary is the point: a rule matching ``/2007`` proves nothing a rule matching
    ``/O9TECB5ZM7`` does not, and the noise is what shows the placeholder accepts any
    segment rather than something the corpus happens to contain.

    Drawn from a generator seeded on the rule instead of the global random state, so
    every process that collects this module produces the same parameter list. xdist
    compares collected test IDs across workers and aborts the run outright when they
    disagree, which is exactly what a value redrawn per process causes. Stability
    also makes a failure reproducible: the URL in the report is the URL that failed,
    not one shape of it that will never occur again.
    """
    return "".join(random.Random(seed).choices(ascii_letters + digits, k=10))


def fill(source: str, splat: str | None, seed: str) -> str:
    """Materialize a rule source into a concrete request path."""
    path = source
    for index, name in enumerate(dict.fromkeys(PLACEHOLDER_REGEX.findall(source))):
        path = path.replace(name, token(f"{seed}/{index}/{name}"))
    if splat is not None:
        path = path.replace("*", splat)
    return path


def cases() -> Iterator[ParameterSet]:
    """One live case per rule, plus the empty-splat twin where history demands it.

    Expected destinations come from the replica, not from re-reading the rule: the
    test then breaks either when production diverges from the file or when the
    replica diverges from production, and both are findings.

    The empty-splat twin exists because every WordPress URL ended in a slash. A rule
    ending in ``/*`` is what answers those bare slashed URLs today, via a splat that
    matches nothing, and that behaviour is load-bearing enough to pin per rule.
    """
    for rule in PARSED.rules:
        seed = f"{rule.line_number}:{rule.source}"
        splat = token(f"{seed}/splat") if "*" in rule.source else None
        variants = [fill(rule.source, splat, seed)]
        if rule.source.endswith("/*"):
            empty = fill(rule.source, "", seed)
            if apply_rule(rule, empty):  # Skip twins whose destination collapses to "".
                variants.append(empty)
        for path in variants:
            expected = apply_rule(rule, path) if rule.is_dynamic else rule.destination
            assert expected, f"Replica failed to resolve {path} for {rule.source}"
            yield pytest.param(
                path,
                expected,
                rule.status,
                id=f"{path} -> {expected} | rule L{rule.line_number}: {rule.source}",
            )


@pytest.mark.parametrize(("path", "expected", "status"), cases())
def test_rule_is_live(path, expected, status):
    """The rule must fire on production, with the exact destination the file states.

    Redirects are checked without following: the first response carries the whole
    verdict, and not following keeps randomly-generated placeholder values from
    turning into misleading 404s three hops later.
    """
    with requests.get(f"{ROOT_URL}{path}", allow_redirects=False) as response:
        assert response.status_code == status, (
            f"{path} answered {response.status_code} instead of {status}: "
            "the rule did not fire."
        )
        location = urljoin(f"{ROOT_URL}{path}", response.headers["location"])
        assert location == urljoin(ROOT_URL, expected)


def test_historical_wordpress_url_chain():
    """The URL that motivated the comment-page rules, end to end.

    A real 2010 WordPress permalink with a comment-pagination suffix. It needs two
    rules to come home: one strips ``/comment-page-1/``, the next strips the month.
    Chains are allowed here, unlike in the per-rule tests: history is layered and
    each layer redirects independently.
    """
    url = (
        f"{ROOT_URL}/2010/09/ultimate-guide-lotus-notes-mail-migration/comment-page-1/"
    )
    with requests.get(url) as response:
        assert response.ok
        assert (
            response.url == f"{ROOT_URL}/2010/ultimate-guide-lotus-notes-mail-migration"
        )
        for hop in response.history:
            assert hop.status_code == 301


# ----- The corpus: twenty years of real URLs, one human-readable table
#
# Where the generated tests above verify the machine, this table is for people: every
# entry is a URL that really existed at some point in this site's history, paired with
# where it must land today. Read it top to bottom to see what the redirect inventory
# actually promises. Chains are followed to the end, because history is layered: a 2005
# WordPress upload URL crosses three eras of rules before it comes home.
#
# ``test_corpus_covers_every_rule`` guarantees the table exercises every rule in
# ``_redirects`` as its *first* match, so a rule can neither go uncovered nor be
# silently shadowed by an earlier one.

CORPUS: tuple[tuple[str, str], ...] = (
    # -- WordPress permalinks (2004-2012): /YYYY/MM/slug/, always slashed. One real
    #    article per publication month, taken from today's content frontmatter.
    (
        "/2007/01/mandriva-20070-screenshots-3d-desktop/",
        "/2007/mandriva-20070-screenshots-3d-desktop",
    ),
    (
        "/2007/02/delayed-cd-tracks-publishing-with-php/",
        "/2007/delayed-cd-tracks-publishing-with-php",
    ),
    (
        "/2007/03/how-to-recover-a-raid-array-after-having-zero-ized-superblocks/",
        "/2007/how-to-recover-a-raid-array-after-having-zero-ized-superblocks",
    ),
    (
        "/2005/04/creer-un-espace-de-stockage-fiable-avec-raid-5-et-lvm-sous-linux/",
        "/2005/creer-un-espace-de-stockage-fiable-avec-raid-5-et-lvm-sous-linux",
    ),
    (
        "/2005/05/how-to-mount-a-file-system-binary-image/",
        "/2005/how-to-mount-a-file-system-binary-image",
    ),
    (
        "/2004/06/mise-en-place-paserelle-adsl-mandrake-10/",
        "/2004/mise-en-place-paserelle-adsl-mandrake-10",
    ),
    (
        "/2005/07/easy-mirroring-without-raid-the-poor-mans-disk-array/",
        "/2005/easy-mirroring-without-raid-the-poor-mans-disk-array",
    ),
    (
        "/2006/08/ajouter-une-entree-jack-universelle-sur-un-telephone-sagem-my700xi/",
        "/2006/ajouter-une-entree-jack-universelle-sur-un-telephone-sagem-my700xi",
    ),
    (
        "/2006/09/cd-templates-for-jewel-case-in-svg/",
        "/2006/cd-templates-for-jewel-case-in-svg",
    ),
    ("/2006/10/archives-commands/", "/2006/archives-commands"),
    ("/2006/11/audio-commands/", "/2006/audio-commands"),
    ("/2006/12/all-my-command-lines/", "/2006/all-my-command-lines"),
    # -- WordPress monthly archives, bare form. The slashed form rides the /* rules
    #    above through an empty splat.
    ("/2007/01", "/2007/"),
    ("/2007/02", "/2007/"),
    ("/2007/03", "/2007/"),
    ("/2005/04", "/2005/"),
    ("/2005/05", "/2005/"),
    ("/2004/06", "/2004/"),
    ("/2005/07", "/2005/"),
    ("/2006/08", "/2006/"),
    ("/2006/09", "/2006/"),
    ("/2006/10", "/2006/"),
    ("/2006/11", "/2006/"),
    ("/2006/12", "/2006/"),
    # -- Archive pagination. /2010/09/page is the exact URL from the 2024 experiment
    #    notes that exposed the trailing-slash asymmetry: its rule was budget-dead then.
    ("/2010/page", "/2010/"),
    ("/2010/page/2", "/2010/"),
    ("/2010/09/page", "/2010/"),
    ("/2010/09/page/safsfsdf", "/2010/"),
    # -- WordPress comment pagination, slashed with month, and its Pelican-era bare
    #    form. The first entry is the real URL from a 2010 comment permalink.
    (
        "/2010/09/ultimate-guide-lotus-notes-mail-migration/comment-page-1/",
        "/2010/ultimate-guide-lotus-notes-mail-migration",
    ),
    ("/2006/12/all-my-command-lines/comment-page-2/", "/2006/all-my-command-lines"),
    (
        "/2010/ultimate-guide-lotus-notes-mail-migration/comment-page-1",
        "/2010/ultimate-guide-lotus-notes-mail-migration",
    ),
    ("/2006/all-my-command-lines/comment-page-2", "/2006/all-my-command-lines"),
    # -- One real 2005 upload through every era of its URL. The .htaccess history shows
    #    the actual lineage: /wp-content/uploads -> /static/uploads (2013) -> /uploads
    #    (month flattened) -> alongside its article (today).
    ("/uploads/2005/06/photo_f3.png", "/2005/photo_f3.png"),
    ("/uploads/2005/photo_f3.png", "/2005/photo_f3.png"),
    ("/static/uploads/2005/06/photo_f3.png", "/2005/photo_f3.png"),
    ("/wp-content/uploads/2005/06/photo_f3.png", "/2005/photo_f3.png"),
    ("/static/documents/cd-template-cd-face.svg", "/2006/cd-template-cd-face.svg"),
    # -- Categories and tags: the hierarchical lang/ scheme, and dead pagination.
    ("/category/lang/en/page/2", "/category/english/"),
    ("/category/lang/fr/page/2", "/category/francais/"),
    ("/category/english/page/2", "/category/english/"),
    ("/tag/python/page/2", "/tag/python/"),
    # -- Feeds. WordPress served rss, rss2, rdf and atom dialects per page; Pelican
    #    serves one RSS and one Atom, so every dialect folds into those.
    ("/feed/", "/feed.rss"),
    ("/feed/atom/", "/feed.atom"),
    ("/category/english/feed", "/category/english/feed.rss"),
    ("/category/english/feed/", "/category/english/feed.rss"),
    ("/category/english/feed/index/", "/category/english/feed.rss"),
    ("/category/francais/feed/atom", "/category/francais/feed.atom"),
    ("/category/francais/feed/atom/", "/category/francais/feed.atom"),
    ("/category/francais/feed/atom/index/", "/category/francais/feed.atom"),
    ("/tag/python/feed/rss", "/tag/python/feed.rss"),
    ("/tag/python/feed/rss/", "/tag/python/feed.rss"),
    ("/tag/python/feed/rss2", "/tag/python/feed.rss"),
    ("/tag/python/feed/rss2/", "/tag/python/feed.rss"),
    ("/tag/python/feed/rdf", "/tag/python/feed.rss"),
    ("/tag/python/feed/rdf/", "/tag/python/feed.rss"),
    ("/comments/feed/atom/", "https://kevin-deldycke-blog.disqus.com/latest.rss"),
    # -- Pre-WordPress corners of the site and old top-level pages.
    ("/pages/about", "/about"),
    ("/about-me/", "/about"),
    ("/code/", "https://github.com/kdeldycke/"),
    ("/linux-scripts/", "https://github.com/kdeldycke/scripts"),
    ("/wordpress-stuff/", "/themes"),
    ("/mandriva-rpm-repository/", "https://github.com/kdeldycke/mandriva-specs"),
    ("/static/repository/", "https://github.com/kdeldycke/mandriva-specs"),
    ("/author/kevin/", "/"),
    (
        "/2013/simplify-amazon-affiliate-links/",
        "/2006/text-date-document-processing-commands",
    ),
    # -- The exact-rename inventory, one entry per static rule, verbatim.
    ("/extra", "/"),
    ("/extra/", "/"),
    ("/page", "/"),
    ("/page/", "/"),
    ("/theme", "/"),
    ("/theme/", "/"),
    ("/category/lang/en", "/category/english/"),
    ("/category/lang/fr", "/category/francais/"),
    ("/category/lang", "/categories"),
    ("/category/lang/", "/categories"),
    ("/category", "/categories"),
    ("/category/", "/categories"),
    ("/tag", "/tags"),
    ("/tag/", "/tags"),
    ("/page/1", "/"),
    ("/page/1/", "/"),
    (
        "/2008/film-fanatix-com-maintenance-page.png",
        "/2011/film-fanatix-com-maintenance-page.png",
    ),
    ("/2008/pict4818.jpg", "/2006/pict4818.jpg"),
    ("/2008/pict4822.jpg", "/2006/pict4822.jpg"),
    ("/2008/pict4826.jpg", "/2006/pict4826.jpg"),
    ("/2008/pict4837.jpg", "/2006/pict4837.jpg"),
    ("/2012/export.png", "/2013/export.png"),
    ("/2012/redux-generation.png", "/2013/redux-generation.png"),
    ("/2012/tale-of-two-timelapse.png", "/2013/tale-of-two-timelapse.png"),
    (
        "/2013/simplify-amazon-affiliate-links",
        "/2006/text-date-document-processing-commands",
    ),
    ("/documents/cd-template-cd-face.svg", "/2006/cd-template-cd-face.svg"),
    (
        "/documents/cd-template-jewel-case-back-print-margin.svg",
        "/2006/cd-template-jewel-case-back-print-margin.svg",
    ),
    (
        "/documents/cd-template-jewel-case-back.svg",
        "/2006/cd-template-jewel-case-back.svg",
    ),
    (
        "/documents/cd-template-jewel-case-front-back-composition.svg",
        "/2006/cd-template-jewel-case-front-back-composition.svg",
    ),
    (
        "/documents/cd-template-jewel-case-inside-back-cover.svg",
        "/2006/cd-template-jewel-case-inside-back-cover.svg",
    ),
    (
        "/documents/cd-template-jewel-case-leaflet-print-margin.svg",
        "/2006/cd-template-jewel-case-leaflet-print-margin.svg",
    ),
    (
        "/documents/cd-template-jewel-case-leaflet.svg",
        "/2006/cd-template-jewel-case-leaflet.svg",
    ),
    ("/documents/flame.qtz", "/2010/flame.qtz"),
    ("/documents/glowing-cool-cavemen.qtz", "/2010/glowing-cool-cavemen.qtz"),
    ("/documents/kaleidoscope-000.qtz", "/2010/kaleidoscope-000.qtz"),
    ("/documents/kaleidoscope-001.qtz", "/2010/kaleidoscope-001.qtz"),
    ("/documents/kaleidoscope-002.qtz", "/2010/kaleidoscope-002.qtz"),
    (
        "/documents/midi-controlled-playground.qtz",
        "/2010/midi-controlled-playground.qtz",
    ),
    ("/documents/putty-template.reg", "/2010/putty-template.reg"),
    ("/documents/sharp-scan-lines.qtz", "/2010/sharp-scan-lines.qtz"),
    ("/documents/snow.qtz", "/2010/snow.qtz"),
    ("/documents/squared-lava-lamp.qtz", "/2010/squared-lava-lamp.qtz"),
    ("/documents/text-zoom-in-out.qtz", "/2010/text-zoom-in-out.qtz"),
    ("/documents/blue-curve.otp", "/2012/blue-curve.otp"),
    ("/documents/fancy-window-frame.otp", "/2012/fancy-window-frame.otp"),
    ("/documents", "/"),
    ("/documents/", "/"),
    ("/pages", "/"),
    ("/static/documents", "/"),
    ("/static/uploads", "/"),
    ("/uploads", "/"),
    ("/mandriva-rpm-repository", "https://github.com/kdeldycke/mandriva-specs"),
    ("/static/repository", "https://github.com/kdeldycke/mandriva-specs"),
    ("/video", "https://www.youtube.com/@kdeldycke/videos"),
    ("/video/", "https://www.youtube.com/@kdeldycke/videos"),
    ("/comments/feed", "https://kevin-deldycke-blog.disqus.com/latest.rss"),
    ("/feed/atom", "/feed.atom"),
    ("/feed", "/feed.rss"),
    ("/wp-content/uploads", "/"),
    ("/author", "/"),
    ("/about-me", "/about"),
    ("/code", "https://github.com/kdeldycke/"),
    ("/linux-scripts", "https://github.com/kdeldycke/scripts"),
    ("/wordpress-stuff", "/themes"),
)


def test_corpus_covers_every_rule():
    """Every rule in ``_redirects`` must be the first match of a corpus entry.

    First match, not any match: an entry that only reaches a rule through an earlier
    one proves nothing about that rule, and a rule nothing reaches first is either
    shadowed or untested. Both are findings.
    """
    credited: set[int] = set()
    for url, _ in CORPUS:
        hit = evaluate(PARSED.rules, url)
        if hit:
            credited.add(hit[0].line_number)
    uncovered = [
        f"L{rule.line_number}: {rule.source}"
        for rule in PARSED.rules
        if rule.line_number not in credited
    ]
    assert not uncovered, f"Rules no corpus entry reaches first: {uncovered}"


@pytest.mark.parametrize(
    ("old_url", "landing"),
    (pytest.param(url, landing, id=f"{url} => {landing}") for url, landing in CORPUS),
)
def test_corpus(old_url, landing):
    """The old URL must land exactly where the table says, however many hops it takes."""
    if landing.startswith("https://"):
        # External landings are asserted on the first hop rather than followed:
        # third-party availability is not this site's promise.
        with requests.get(f"{ROOT_URL}{old_url}", allow_redirects=False) as response:
            assert response.status_code in (301, 302)
            assert response.headers["location"] == landing
        return

    with requests.get(f"{ROOT_URL}{old_url}") as response:
        assert response.ok, f"{old_url} ended {response.status_code} at {response.url}"
        assert response.url == f"{ROOT_URL}{landing}", (
            f"{old_url} landed on {response.url.removeprefix(ROOT_URL)} "
            f"instead of {landing}"
        )
        for hop in response.history:
            # 301/302 come from the rules, 308 from Pages' own URL normalization.
            assert hop.status_code in (301, 302, 308)


# ----- Files over the Pages size limit, which the deploy serves from R2

PAGES_MAX_FILE_SIZE = 25 * 1024 * 1024
"""Largest file Cloudflare Pages Direct Upload accepts, in bytes."""

R2_HOST = f"files.{DOMAIN}"
"""Custom domain of the R2 bucket, per `[tool.repomatic] site.cloudflare-r2-domain`."""

CONTENT_DIR = Path(__file__).parent.parent / "content"

OVERSIZED = sorted(
    path
    for path in CONTENT_DIR.rglob("*")
    if path.is_file() and path.stat().st_size > PAGES_MAX_FILE_SIZE
)
"""Content files the deploy's offload moves to R2 instead of uploading to Pages."""


@pytest.mark.parametrize("path", OVERSIZED, ids=lambda path: path.name)
def test_oversized_file_redirects_to_r2(path):
    """The file's own URL must hand over to the copy the deploy put in R2.

    The rule doing it exists only in the built `_redirects`, never in
    `content/extra/_redirects`, so no test above ever sees it. Only the first hop
    is asserted, like the corpus's external landings: its target is a key named by
    the file's hash, which changes with the file.
    """
    url = f"{ROOT_URL}/{quote(path.relative_to(CONTENT_DIR).as_posix())}"
    with requests.get(url, allow_redirects=False) as response:
        assert response.status_code == 302, (
            f"{url} answered {response.status_code}: the offload rule is not live."
        )
        location = urlsplit(response.headers["location"])
        assert location.netloc == R2_HOST
        assert location.path.endswith(f"/{quote(path.name)}")


# ----- The entry points DNS and the edge own, which no file here can express


def domain_cases() -> Iterator[tuple[str, int]]:
    """Every way of spelling the site's root, with the hops it should take to canonize.

    Exactly one hop unless the request is already canonical, because the edge rule that
    moves traffic off ``deldycke.com`` and ``www.deldycke.com`` matches on host alone and
    always targets HTTPS. A plain ``http://`` request to a non-canonical host is therefore
    corrected in a single response rather than being upgraded and then moved.

    The one remaining hop belongs to the canonical host itself: ``http://kevin`` is
    upgraded by Always Use HTTPS, which no redirect rule is involved in.

    ``www`` earns its place here rather than being assumed equivalent to the apex. It is
    served by a different DNS record and, until the rule was widened to name it, answered
    a 5xx while the apex redirected correctly: the two hosts had nothing in common but a
    suffix.
    """
    for scheme in ("http", "https"):
        for host in (DOMAIN, f"www.{DOMAIN}", SUB_DOMAIN):
            for path in ("", "/"):
                canonical = scheme == "https" and host == SUB_DOMAIN
                yield f"{scheme}://{host}{path}", int(not canonical)


@pytest.mark.parametrize(("url", "hops"), domain_cases())
def test_domain_canonicalization(url, hops):
    """Any spelling of the root must land on the canonical URL, over HTTPS.

    Guards the entry point the redirect rules above never see: these are resolved by DNS
    and the zone's edge rule, not by the ``_redirects`` file.
    """
    with requests.get(url) as response:
        assert response.ok
        # requests always normalizes a bare domain to a trailing slash.
        assert response.url == f"{ROOT_URL}/"

        assert len(response.history) == hops, (
            f"{url} took {len(response.history)} redirects instead of {hops}: "
            f"{[h.url for h in response.history]}"
        )
        # Permanent, so browsers and search engines stop asking.
        for hop in response.history:
            assert hop.status_code == 301

        # No hop may leave the site, and none may downgrade a secured request.
        for hop in response.history:
            assert hop.headers["Location"].startswith((
                "/",
                f"https://{DOMAIN}",
                f"https://www.{DOMAIN}",
                ROOT_URL,
            ))


@pytest.mark.parametrize("host", (DOMAIN, f"www.{DOMAIN}"))
def test_non_canonical_host_preserves_path(host):
    """A deep link to a non-canonical host keeps its path instead of dumping on the root.

    The apex and ``www`` accumulated inbound links over two decades and several site
    migrations. A redirect that discarded the path would turn every one of them into a
    visit to the homepage, which reads as working right up until someone checks where the
    links actually went.
    """
    path = "/2016/falsehoods-programmers-believe-about-falsehoods-lists"

    with requests.get(f"https://{host}{path}") as response:
        assert response.ok
        assert response.url == f"{ROOT_URL}{path}"
        assert len(response.history) == 1
        assert response.history[0].status_code == 301
