"""Snapshot DNS records, split along the boundary between this blog and everything else.

`kevin.deldycke.com` resolves because of records this repository does not contain, which
makes DNS the one part of a rebuild that cannot be reconstructed from what is committed
here. This script closes that gap without turning a public repository into a map of a
personal network.

Two scopes, because two audiences:

    --scope blog    what belongs in this repository: the `deldycke.com` zone, minus every
                    record that exists to run email. TXT values are fingerprinted.
    --scope full    everything, verbatim, for a private infrastructure knowledge base.

The blog scope is deliberately narrow. Other zones on the same Cloudflare account have
nothing to do with this site, and the mail records on `deldycke.com` describe a mail
provider rather than a website. Neither helps anyone rebuild the blog, and both say more
about their owner than a public repository needs to.

    python scripts/cloudflare_dns.py --write docs/dns.md
    python scripts/cloudflare_dns.py --scope full --write {private}/dns-records.md

The wrangler OAuth token cannot be used: its scope list has no DNS entry at all, and its
`zone:read` covers only the zone objects. Create a token with two read-only permissions
over all domains, then export it as `CLOUDFLARE_API_TOKEN` or point `--token-file` at a
file holding it:

    Zone -> Read      to enumerate the zones
    DNS  -> Read      to enumerate each zone's records

Both are needed. `DNS -> Read` alone cannot list zones, so the run fails on the first call
before reading a single record. See docs/infrastructure.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any

API_ROOT = "https://api.cloudflare.com/client/v4"

BLOG_ZONE = "deldycke.com"
"""The only zone that serves this site. Everything else belongs in the private notes."""

# Record types whose content is a hostname, an address or a public policy value. These
# are reproduced verbatim: a rebuild needs them exactly, and none carries key material.
VERBATIM_TYPES = frozenset({
    "A",
    "AAAA",
    "ALIAS",
    "CAA",
    "CNAME",
    "MX",
    "NS",
    "PTR",
    "SRV",
})

# Value prefixes that identify a protocol rather than a secret, and so survive redaction.
PUBLIC_DIRECTIVES = frozenset({"spf1", "DKIM1", "DMARC1", "STSv1", "TLSRPTv1"})


def is_mail_record(record: dict) -> bool:
    """Does this record exist to run email rather than to serve the site?

    Mail wiring names a provider, carries its per-account identifiers, and states a policy
    about who may send as the domain. All of that is infrastructure about a person, not
    about a blog, so it is filtered out of the public scope entirely rather than merely
    redacted.
    """
    name = str(record.get("name", ""))
    content = str(record.get("content", ""))
    if record.get("type") == "MX":
        return True
    if "_domainkey." in name or name.startswith("_dmarc."):
        return True
    if record.get("type") == "TXT":
        return content.startswith(("v=spf1", "v=DMARC1", "protonmail-verification="))
    return False


def _token(token_file: str | None) -> str:
    if token_file:
        path = pathlib.Path(token_file)
        if not path.is_file():
            raise SystemExit(f"No such token file: {token_file}")
        secret = path.read_text().strip()
        if not secret:
            raise SystemExit(f"Token file is empty: {token_file}")
        return secret
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if token:
        return token
    raise SystemExit(
        "No credential. Create a token with `Zone -> Read` and `DNS -> Read` over all "
        "domains, then export CLOUDFLARE_API_TOKEN or pass --token-file. The token "
        "stored by `wrangler login` will not work: wrangler requests no DNS scope."
    )


def _call(path: str, token: str) -> Any:
    request = urllib.request.Request(
        f"{API_ROOT}{path}", headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:300]
        if error.code == 403:
            missing = "`DNS -> Read`" if "dns_records" in path else "`Zone -> Read`"
            detail += (
                f"\n\nA 403 here usually means the token lacks {missing}, or its "
                "resource scope does not cover this domain. Both permissions are "
                "required: one to list zones, the other to read their records."
            )
        raise SystemExit(f"GET {path} failed: HTTP {error.code}\n{detail}")
    return payload["result"]


def _paged(path: str, token: str) -> list[dict]:
    """Walk Cloudflare's pagination, which caps out at 100 records per response."""
    records: list[dict] = []
    page = 1
    while True:
        joiner = "&" if "?" in path else "?"
        batch = _call(f"{path}{joiner}page={page}&per_page=100", token)
        records.extend(batch)
        if len(batch) < 100:
            return records
        page += 1


def redact(record: dict) -> str:
    """Return a publishable rendering of a record's content."""
    content = str(record.get("content", ""))

    # DKIM delegation targets are CNAMEs, so they would otherwise be published verbatim,
    # but they embed an opaque per-account identifier at the mail provider. Nothing in a
    # rebuild needs the literal value: it is reissued when the domain is re-verified. The
    # provider suffix is kept, because knowing which provider to go back to is the part
    # that matters and that part is not an identifier.
    if "_domainkey." in str(record.get("name", "")):
        digest = hashlib.sha256(content.encode()).hexdigest()[:12]
        provider = ".".join(content.rsplit(".", 3)[-3:])
        return f"`….{provider}` `sha256:{digest}`"

    if record["type"] in VERBATIM_TYPES:
        return content

    digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    key, separator, remainder = content.partition("=")
    if not separator:
        # No `key=value` shape at all, so there is no safe prefix to keep.
        return f"`sha256:{digest}`"
    if key == "v":
        directive = remainder.split(";")[0].split()[0] if remainder.strip() else ""
        if directive in PUBLIC_DIRECTIVES:
            return f"`v={directive}` … `sha256:{digest}`"
    return f"`{key}=` … `sha256:{digest}`"


def table(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> list[str]:
    """Lay a table out the way `mdformat` does.

    The `format-markdown` job formats `docs/dns.md` after this script writes it. A table
    written any other way is rewritten by that job, then rewritten back by the next
    snapshot. `mdformat` pads each column to its widest cell, and counts the three dashes
    of the delimiter row as a cell.

    Width is counted in characters. That holds while every cell is ASCII, plus the `…`
    that `redact` writes, which `mdformat` also counts as one column.
    """
    widths = [
        max(3, *(len(row[column]) for row in (header, *rows)))
        for column in range(len(header))
    ]

    def line(cells: tuple[str, ...]) -> str:
        padded = (cell.ljust(width) for cell, width in zip(cells, widths))
        return f"| {' | '.join(padded)} |"

    delimiter = tuple("-" * width for width in widths)
    return [line(header), line(delimiter), *(line(row) for row in rows)]


def render(zones: list[tuple[dict, list[dict]]], scope: str) -> str:
    if scope == "blog":
        lines = [
            "# DNS",
            "",
            "Generated by `scripts/cloudflare_dns.py`. Do not hand-edit: regenerate it.",
            "",
            (
                f"Scoped to the records that serve this site. The `{BLOG_ZONE}` zone also "
                "carries mail records, and the account carries other zones; neither is "
                "needed to rebuild the blog and neither belongs in a public repository, "
                "so both live in a private infrastructure knowledge base instead. "
                "`--scope full` is what writes that copy."
            ),
            "",
            (
                "TXT values are fingerprinted, not published. A changed fingerprint means "
                "the record changed; the value itself has to come from the Cloudflare "
                "dashboard. Everything else is verbatim and enough to recreate the record."
            ),
            "",
        ]
    else:
        lines = [
            "# DNS records",
            "",
            (
                "Generated by `scripts/cloudflare_dns.py --scope full` in the blog "
                "repository. Do not hand-edit: regenerate it. Values are verbatim, "
                "including mail wiring, which is why this lives here and not in that "
                "public repository."
            ),
            "",
        ]

    for zone, records in zones:
        lines += [
            f"## {zone['name']}",
            "",
            f"{len(records)} records, zone status `{zone['status']}`.",
            "",
        ]
        rows: list[tuple[str, ...]] = []
        for record in sorted(records, key=lambda r: (r["type"], r["name"])):
            ttl = "auto" if record.get("ttl") == 1 else str(record.get("ttl", ""))
            priority = record.get("priority")
            content = (
                redact(record) if scope == "blog" else str(record.get("content", ""))
            )
            if priority is not None:
                content = f"({priority}) {content}"
            rows.append((
                record["type"],
                f"`{record['name']}`",
                content,
                "yes" if record.get("proxied") else "no",
                ttl,
            ))
        lines += table(("Type", "Name", "Content", "Proxied", "TTL"), rows)
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", metavar="PATH", help="write markdown to this file")
    parser.add_argument("--token-file", metavar="PATH", help="file holding the token")
    parser.add_argument(
        "--scope",
        choices=("blog", "full"),
        default="blog",
        help="blog: this site's zone minus mail records. full: everything, verbatim.",
    )
    arguments = parser.parse_args()

    token = _token(arguments.token_file)
    zones = sorted(_paged("/zones", token), key=lambda z: z["name"])
    if arguments.scope == "blog":
        zones = [z for z in zones if z["name"] == BLOG_ZONE]
        if not zones:
            raise SystemExit(
                f"The token cannot see {BLOG_ZONE}. Check its Zone Resources."
            )
    elif not zones:
        raise SystemExit("The token sees no zones. Check its Zone Resources.")

    collected = []
    for zone in zones:
        records = _paged(f"/zones/{zone['id']}/dns_records", token)
        if arguments.scope == "blog":
            records = [r for r in records if not is_mail_record(r)]
        collected.append((zone, records))

    document = render(collected, arguments.scope)

    if arguments.write:
        pathlib.Path(arguments.write).write_text(document)
        total = sum(len(records) for _, records in collected)
        print(
            f"Wrote {arguments.write}: {len(zones)} zones, {total} records "
            f"({arguments.scope} scope)."
        )
    else:
        print(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
