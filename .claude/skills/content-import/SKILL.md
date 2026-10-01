---
name: content-import
description: Import content from a third-party service into the blog as static, hand-curated data, and curate it. Use when you migrate or re-curate data that came from an external platform (Disqus comments today; tweets or Instagram posts tomorrow), or when you audit what an earlier import produced.
argument-hint: "[path to the source export]"
---

# Import external content

The blog absorbs content from services it stops using. Each import follows the common rules below, then the section of its source. When you migrate a new source, add a section for it at the end, and move to the common rules whatever turns out to apply to every source.

## Common rules

### The raw export

- Keep the raw export outside git, and never commit it. Once the account is deleted, it is the only complete copy: it holds what the curation dropped, full names and account handles.
- Before the owner deletes the account, check the export against the live service (see the source's section), and ask the owner to check what no public endpoint shows, like a moderation queue.
- Never restore a field or an item from the export without the owner's go-ahead.

### Identity and storage

- Key each imported item on the blog's own stable identifier, the article source path, never on a URL: services key their data on URLs, so every change of URL scheme splits it.
- Store the curated data as TOML: multi-line literal strings for text, unless it holds `'''` or a control character. Read the file back with `tomllib` and compare it with the data.
- Keep dates to the minute. TOML 1.0 needs seconds in a datetime: write them as `:00`.
- Keep the structural IDs that threads and anchors need, and nothing else unique: no UUIDs, account handles or tokens.

### Converting text to Markdown

- Accept only the markup the source is known to produce, and reject anything else.
- Render with markdown-it in CommonMark mode, with `breaks` on and `html` off: a newline is a line break, and raw HTML shows as text.
- Escape what that renderer reads as syntax:
  - Anywhere in text: backslashes, backticks, `*`, brackets, `_` unless between two letters or digits, `<` before an autolink-shaped run, `&` before an entity-shaped run.
  - At the start of a line: `#`, `>`, `-` or `+` before a space, `1.` or `1)` before a space, `~~~`, and lines made only of `-` or `=`.
- Prove each conversion: render the Markdown with the production renderer, and compare the visible text, the link targets and the code blocks with the source. Write nothing if one item differs.
- Restore text an old HTML sanitizer stripped only when it is known exactly, like `<module>` after `, in` in a Python traceback. Leave a gap whose content is unknown, like a placeholder lost from a command.

### Code blocks

- Put logs, commands, configuration and code in fenced blocks, with no Markdown escapes and no inline backticks inside. A passage holding a live link stays prose: a code block cannot keep a link.
- Name the language in the spelling the articles use: `shell-session` for a terminal session with prompts, `bash` for commands without prompts, `text` for logs and output, then `ini`, `nginx`, `apache`, `diff`, `python`, `pycon`, `pytb`, `php`, `html`, `css`, `js` and the like.
- Pygments highlights these blocks, so the name must be a lexer it knows. Its `shell-session` lexer reads `$`, `#` and `user@host:path$` prompts, but not `~ $`. A Windows session with `CMD>` prompts takes `doscon`. Dedent a session pasted with an indent, or no prompt is found.
- Rejoin a line the source wrapped inside code, like a traceback frame's function name pushed to the next line.

### Curation policy the owner set

- **Keep by default**, thank-you notes and praise included.
- **Drop** spam, self-promotion, promotion of a commercial product, referral or affiliate posts, abusive replies, and items whose purpose is personal contact data. Keep IP addresses of attackers in logs.

### Privacy

- **Names:** first names only. An email address used as a name keeps its local part. Generated or disposable handles, and company names on generic praise, become "Anonymous". A business name on an item signed with a first name takes the signature. An account left on a generic name ("Utilisateur") takes the first name its handle spells. One account, one author string. Pseudonyms stay as written.
- **No account handles** in the published data.
- **Redact** email addresses, phone numbers and postal addresses. When an email address stands alone as a signature line, delete the line. A city and its state identify nobody: keep them.
- **IP addresses:** mask one that is the author's own as `x.x.x.x`. Keep attackers' addresses.
- **The owner's own data** in an example, like his email address, becomes an address on `example.com`.

### Links

- Use https where it works.
- Strip tracking parameters (`utm_*` and the like). Keep the IDs a site needs, like Slashdot's `?sid=`.
- Send internal links to their canonical URL through `_redirects`, with `tests/pages_redirects_engine.py`. Old fragments need no rule: browsers carry them through redirects.
- For a dead link, look for the content where it moved before anything else:
  - Search the site itself: an old CMS URL often survives as a post on the new one (greycube.com's e107 news item became a WordPress post).
  - The owner's own files live on as tags of his GitHub repositories (`kdeldycke/e107-importer` holds every release).
  - Code from a closed forge may survive on Software Heritage, which archived Bitbucket's Mercurial repositories.
- Else, link a Wayback Machine capture close to the item's date.
- Else, keep the address readable as inert code: a bare URL as `` `http://…` ``, a named link as `text (`http://…`)`. When the link text is itself the address, the inert form keeps that text as written.
- Keep a dead link that documents a past procedure ("the new link to the form is…") as it was, rather than pointing it at today's equivalent.
- Show text alone, without the address, for false links (a file name a service turned into a link) and affiliate links with no replacement.
- Remove file-sharing links (Dropbox, Google Drive, send.vis.ee). Drop an item that has nothing left once they are gone, and the replies that only ask for the removed file.
- Send affiliate links to the product's Wikipedia article in the item's language, else to the official product page.
- Keep links to an author's own site.

### The Wayback Machine

Use the CDX API: `https://web.archive.org/cdx/search/cdx?url={url}&closest={YYYYMMDD}&sort=closest&limit=1&filter=statuscode:200&output=json`. Space requests by several seconds. A burst earns HTTP 429 for hours, and each refused request can extend it: wait out a 429 for minutes, but retry a timeout after a few seconds. Strip `#fragments` before a lookup.

### Mass edits with agents

- Split the work by whole threads, so each agent sees a full conversation.
- Agents only reformat and redact. Names, links, mentions and drops belong in one script that always starts from the import commit, so a re-run never stacks edits.
- Give agents a checker that renders the old and the new body and compares their visible text, allowing only the redactions they declare.
- Check internal links against a complete build: a build in progress empties `output/`.

## Source: Disqus comments

The Disqus forum was deleted on 2026-10-01. Its export, `kevin-deldycke-blog-2026-10-01T11-16-51.713133-all.xml.gz`, sits outside git. `content/comments.toml` is the curated public subset: `pelican_patches.py` loads it, and `content/templates/article.html` renders it below each article.

### The export

- Gzipped XML, with the namespaces `http://disqus.com` and `http://disqus.com/disqus-internals` (for `dsq:id`).
- `<thread>`: `<id>` is the identifier the embed passed, `<link>` the page URL, `<title>` its title.
- `<post>`: `<message>` is HTML in CDATA, then `<createdAt>`, `<isDeleted>`, `<isSpam>`, `<author>` (`name`, `isAnonymous`, and `username` for registered accounts), `<thread dsq:id>`, and `<parent dsq:id>` on replies.
- Comments imported from WordPress in 2013 carry `<id>wp_id=N</id>`.
- No email addresses, IP addresses, avatars or votes. A deleted post loses its message and its author.

### Completeness

- The public counter `https://{forum}.disqus.com/count-data.js?1={identifier}&1={identifier}` answers JSONP: `DISQUSWIDGETS.displayCount({..., "counts": [{"id": ..., "comments": N}]})`. Compare each `N` with the posts of that identifier that are neither deleted nor spam. Send 25 identifiers per request.
- For the WordPress era, the live `wp_id` posts plus the deleted posts in the same `dsq:id` range must match the approved count of the WordPress export.

### Threads

- The embed keyed each thread on the page URL, so the 2023 change of URL scheme split threads in two. Merge all the threads of an article.
- Match the identifier, or else the link, on year and slug, then on slug alone when a single article carries it.

### Markup quirks

- The HTML uses `p`, `br`, `pre` with `code`, `code`, `a`, `blockquote`, `em` or `i`, and `strong` or `b`. `<br>` is the only line break, and inside `<pre><code>` it is a newline of the code. Inline `<code>` that spans lines reads better as a code block.
- Disqus cut link texts to 27 characters and `...`: show the full URL. Its autolinker took a closing `)` into the URL: move it back out. It also turned bare domain and file names into links. Drop links to `#`.

### Mentions and anchors

- A mention links to the comment it answers: `[@name](#comment-{id})`, with the name stripped of its family name. Such links carry no `rel`.
- Each comment has `#comment-{Disqus id}`, and WordPress-era ones also `#comment-{wp_id}`, so old WordPress deep links still land. The two ID ranges never overlap: WordPress IDs stay below 11000.
- WordPress printed `#comment-{ID}` for its whole life here. From version 2.7 it also paged comments (`…/comment-page-N/#comment-{ID}`), and `_redirects` folds pages 1 and 2 into the article. Its reply links (`?replytocom=N`) carry the ID in the query string, which no rule can match.
- Comments render inside `<main>`, so `STORK_INPUT_OPTIONS` keeps them out of the search index.
