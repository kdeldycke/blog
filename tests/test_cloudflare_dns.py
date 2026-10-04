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

"""Hold the DNS snapshot generator to the layout its formatter writes.

`scripts/cloudflare_dns.py` writes `docs/dns.md`, and the `format-markdown` job then
formats that page with `mdformat`. If the two disagree on how a table is laid out, each
regeneration rewrites every row and the next autofix run rewrites them back. The
committed page is the formatter's version, so the generator must reproduce it.
"""

from __future__ import annotations

import re
from pathlib import Path

import cloudflare_dns

PAGE = Path(__file__).parent.parent / "docs" / "dns.md"


def zones_of(page: str) -> list[tuple[dict, list[dict]]]:
    """Rebuild the generator's input from a page it produced.

    Cell text is fed back as the record content, which the `full` scope prints verbatim.
    """
    zones = []
    for section in page.split("\n## ")[1:]:
        lines = section.splitlines()
        status = re.search(r"zone status `(.+?)`", section)
        assert status, section
        records = []
        for line in lines:
            if not line.startswith("| ") or line.startswith(("| Type", "| ---")):
                continue
            kind, name, content, proxied, ttl = (
                cell.strip() for cell in line.strip("|").split("|")
            )
            records.append({
                "type": kind,
                "name": name.strip("`"),
                "content": content,
                "proxied": proxied == "yes",
                "ttl": 1 if ttl == "auto" else int(ttl),
            })
        zones.append(({"name": lines[0], "status": status[1]}, records))
    return zones


def test_render_matches_committed_page():
    """Regenerating the page from its own records must give back the same tables."""
    page = PAGE.read_text(encoding="UTF-8")
    rendered = cloudflare_dns.render(zones_of(page), "full")
    assert rendered[rendered.index("\n## ") :] == page[page.index("\n## ") :]
