# WeChat TikHub Notes

Use this reference only when the main workflow is not enough: API response drift, failed searches, table/formula preservation, historical clipping failures, or detailed Markdown cleanup.

## TikHub Boundary

TikHub is a third-party provider. Do not describe it as an official WeChat API. This skill targets arbitrary public WeChat Official Account articles and differs from WeChat Official Account owner APIs, which are mainly for managing the authenticated account's own materials, drafts, and publishing workflow.

Current default article-detail path uses TikHub v2; older `wechat_mp/web` detail endpoints returned 404 in July 2026:

- `GET /api/v1/wechat_mp/web/fetch_search_official_account`
- `GET /api/v1/wechat_mp/web/fetch_official_account_detail`
- `GET /api/v1/wechat_mp/web/fetch_mp_article_list`
- `GET /api/v1/wechat_mp/web/fetch_search_article`
- `POST /api/v1/wechat_mp/v2/fetch_article_detail` with JSON body `{ "url": "https://mp.weixin.qq.com/s/...", "raw": false }`

Documentation is under:

```text
https://docs.tikhub.io/
```

Inspect cached JSON when the script cannot parse expected fields. Do not guess response shape from memory.

## Resolution Path From Live Runs

The 2026-05-26 live run showed this path was most reliable:

1. If direct article URLs exist, skip search and call detail endpoints.
2. If only account/title clues exist, call `fetch_search_official_account`.
3. Prefer `jumpInfo.userName` values shaped like `gh_...` as `fetch_mp_article_list` `ghid`.
4. Do not prefer `__biz`, numeric `bizuin`, or base64 `Mz...` identifiers for article lists unless a future response proves they work. A wrapper HTTP 200 can still contain a provider-level `gzid` error.
5. Fetch article-list pages with `ghid` and `offset`.
6. The next page token is usually `data.offset.Offset`; stop when `data.offset.IsEnd == 1`.
7. Match requested articles by exact title or strong OCR/title keywords.
8. Treat list records as candidate metadata only. Call detail endpoints for final full text.
9. Prefer TikHub v2 article detail for normal clipping. It returns parsed `data.content` including `title`, `nick_name`, `author`, `create_time`, `content_noencode`, and `content_text`.

Direct long-title `fetch_search_article` can return 400 even for real articles. Use account-list discovery first for screenshot title batches.

## Search And Failure Handling

Some TikHub WeChat search endpoints document limited resources and recommend client-side retries. Use script retry settings with short randomized backoff. Avoid tight manual retry loops.

Treat account/search endpoint 400 or timeout as retryable during discovery if the query is ordinary and the request shape is valid. Do not retry nonrecoverable detail failures such as 400/401/403/404/422 in a loop.

Short `https://mp.weixin.qq.com/s/...` links can redirect to a WeChat captcha page when accessed without a valid WeChat browser context. TikHub detail endpoints may return 404 for those links. In that case, do not fabricate content; ask for a fresh direct article URL, a Sogou result link convertible through TikHub, or a local archived fulltext file.

If TikHub returns usable body content but no title, recover titles from screenshot/OCR text, explicit `--title-source`, or nearby article prompt text. Keep generic "untitled article" labels only in staging/debug output when no reliable title can be inferred.

If TikHub JSON detail includes `article.full_text`, `article.sections`, or `content.raw_content`, run a tail-completeness QA. The final Markdown must include the last substantive section titles and the last 2-3 non-promo text blocks from the source. If output is much shorter than `full_text` or misses tail markers, rebuild from `raw_content` or local raw cache.

## Local Archive Fallback

Searching local `01.raw/01.Inbox`, `01.raw/05.Wechat`, and `02.wiki/sources` can reduce cost. Use local exact URL/title matches only when:

- All requested articles are locally matched.
- The local body is readable UTF-8 full text.
- The user did not ask specifically to test TikHub/provider behavior.

If only mojibake old clippings exist, preserve links/metadata if useful but do not use corrupted body text as final content unless the user accepts a degraded fallback.

## Markdown Structure

Generated bundles use:

- YAML frontmatter.
- No in-body document title.
- Article headings as `## 0x01. Title`, `## 0x02. Title`.
- Major article sections as `###`.
- Nested numbered subsections as `#### parent.local`.

Do not use Chinese article numbering such as `## 一.` or `## 二.`. Do not promote every numbered line to a heading. Under a major section, short local enumerations should remain ordered-list items unless the source clearly marks them as subsections.

If a major section is followed by restarted local headings, inherit the parent number. For example, under `### 4. Engineering implementation`, local items `1. KV Cache`, `2. PagedAttention` become `#### 4.1 KV Cache`, `#### 4.2 PagedAttention`.

Final QA patterns:

```powershell
rg -n "^# " output.md
rg -n "^#{1,6}\s*$" output.md
rg -n "^###\s+\d+\.\d+" output.md
rg -n "\{'title':|item_count|metadata|images':|\}], 'images'" output.md
```

Any match is a failure unless it is inside a fenced code block that intentionally demonstrates those strings.

## Cleanup Rules

Remove WeChat page chrome, share/open-app prompts, preview controls, and permission prompts. Examples include "continue scrolling", "open in WeChat", "cancel", "allow", and "got it" style page text.

Remove suspected QR-code promotion or private-contact acquisition tails. Common signs include calls to follow an account, add a WeChat contact, join a group, scan a QR code, or a QR/contact-card image at the end. If the boundary is ambiguous, remove only the promotional tail and keep article content.

Remove repeated article table-of-contents blocks before publishing. These often appear immediately after an article title/source block as a list of repeated `### ...` entries or a "today's topics" block before the real body.

Clean CSS residue leaked from WeChat HTML styles. Remove standalone `unset` tokens around headings and split glued headings onto their own line.

Normalize standalone URL labels into Markdown links. Convert `label: https://...` or `label:` followed by a URL into `[label](https://...)`; do not leave the URL detached from its label.

Normalize inline emphasis produced by HTML conversion. Convert spaced bold/italic markers such as `** text **` to `**text**`, and remove obvious extra spaces before punctuation after emphasis.

Remove empty Markdown artifacts:

- Empty headings such as `#`, `##`, `###`.
- Empty list items such as a standalone `-`.
- Extra blank lines immediately before or after images, fenced code blocks, and display math.
- Blank lines immediately after headings.

Keep adjacent bullet and ordered-list items compact. Do not insert blank lines between ordinary `- ...` items or `1. ...`, `2. ...`, `3. ...` sequences.

Normalize circled Chinese numerals and full-width punctuation only when meaning is clear. Convert list markers to `1.`, `2.`, `3.` and full-width parentheses to ASCII parentheses.

## Tables, Code, And Formulas

Preserve real data tables as Markdown pipe tables. A WeChat HTML table with at least 2 rows and at least 2 columns must not be linearized into one-value-per-line text.

Do not force layout/code tables into Markdown tables. A 1-row/1-column table, especially one wrapping `<pre>` content, should become a fenced code block or blockquote-style text.

Prefer TikHub detail HTML fields that preserve table structure, especially `source`, over plain `content` text when the HTML contains `<table>` tags. After clipping a table-heavy article, compare source multi-row/multi-column HTML table count with Markdown table count.

Audit fenced code blocks before publishing. Infer language labels from code content:

- `def`, `class`, `import`, `from ... import`, `async def`, `return` -> `python`
- `async function`, `const`, `let`, `fetch`, `JSON.stringify`, `TextDecoder`, `crypto.randomUUID`, `=>` -> `javascript` or `typescript`
- `curl`, `grep`, `docker`, `kubectl`, `npm`, `pnpm`, `git`, `pytest` -> `bash`
- quoted object/array keys -> `json`
- `key: value` config -> `yaml`
- `SELECT`, `CREATE TABLE` -> `sql`
- Mermaid diagram starts -> `mermaid`
- `__global__`, `cudaMalloc`, `#include`, `std::` -> `cuda` or `cpp`

Fenced code block markers must be on their own lines. If extraction glues a marker to preceding prose, split it before publishing.

Preserve formulas from the source. If formulas appear as text, avoid Markdown emphasis normalization that corrupts underscores or braces. If formulas appear as SVG/MathJax/images, convert to LaTeX when recoverable, preserve an image/link when possible, or insert a clear formula-loss marker near the original location.

Wrap only short standalone formula expressions in display math. Do not wrap explanatory Chinese sentences just because they contain symbols such as `M_ij` or `d_k`.

Display math should be tight:

```markdown
Intro:
$$
Attention(Q, K, V) = ...
$$
Next paragraph.
```

## Readable Mode Details

Default `plain` mode should stay faithful. `--format-mode readable` may only perform conservative, meaning-preserving formatting:

- Bold fixed information labels.
- Split explicit enumerations into readable blocks.
- Convert consecutive definition-style paragraphs after a clear intro into compact Markdown lists.
- Convert narrow comparisons into Markdown tables only when each cell remains short.
- Fix heading-summary glue before applying any other enhancement.

Readable mode must not summarize, delete, rewrite, invent headings, or add conclusions. If unsure, leave the source prose alone.

## Windows And Editing Notes

PowerShell here-strings can fail when large Chinese/Markdown/LaTeX blocks are embedded directly. Use `apply_patch` for skill edits, or scripts that read/write target files instead of pasting long Markdown through PowerShell.

Python on this Windows setup can throw `OSError: [Errno 22] Invalid argument` when a pasted Chinese path is mojibake-corrupted by the console. Prefer `Get-Content -LiteralPath` for quick inspection, or use Node's UTF-8 filesystem APIs with explicit absolute paths for Chinese filenames.

JavaScript replacement strings treat `$$` specially, so `text.replace(..., "$$")` can accidentally write a single `$`. Use a function replacement when inserting Markdown display-math delimiters.

## Compliance Boundary

Use the output for personal knowledge management. Do not bypass access controls, login walls, paywalls, captcha, or copyright restrictions. If an article is unavailable from TikHub, report the limitation instead of scraping a logged-in browser session.
