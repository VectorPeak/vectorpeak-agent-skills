---
name: wechat-clippings-vp
description: Clip arbitrary WeChat Official Account articles through TikHub into Obsidian Web Clipper-style Markdown bundles. Use when the user provides a WeChat public account author/name, mp.weixin.qq.com article URL, article title, screenshot/OCR text, copied page/search text, or asks to fetch selected WeChat public-account articles and save Markdown clippings into a local clippings directory or Obsidian vault folder.
---

# WeChat Clippings

## When To Use

Use this skill for personal-knowledge clipping of public WeChat Official Account articles into Markdown. Accepted inputs include direct `mp.weixin.qq.com` URLs, a public-account name, author/nickname, article title, screenshot OCR text, copied search/page text, or mixed instructions such as "clip the latest three articles about Agent from this account".

Do not use this skill for WeChat Official Account owner APIs, draft/publishing workflows, logged-in browser scraping, captcha handling, or paywall/access-control bypasses.

## Core Workflow

Use TikHub-first mode. TikHub is a third-party provider, not an official WeChat API; response shape, quota, and coverage may drift.

1. Parse the request into article URLs, account clues, title keywords, optional screenshot/OCR titles, and output-directory requirements.
2. If direct `mp.weixin.qq.com` URLs are present, treat them as the complete scope and call TikHub article-detail endpoints directly.
3. If no direct URL is present, search the official account with `fetch_search_official_account`, prefer `jumpInfo.userName` values shaped like `gh_...`, then call `fetch_mp_article_list`.
4. Paginate article lists with `data.offset.Offset` until the requested titles are found, the requested count is satisfied, or `IsEnd == 1`.
5. For screenshot/OCR batches, prefer account list plus fuzzy title matching. Avoid long-title `fetch_search_article` until account-list discovery fails.
6. Use article-list records only as candidate metadata. Fetch final full text through article detail; prefer `fetch_mp_article_detail_html`, then fall back to JSON.
7. Convert the article body from `#js_content` or structured detail fields into Markdown, preserving source URLs, images, tables, formulas, code blocks, and readable text.
8. Cache raw TikHub responses for QA, but never print or write the API key.

For difficult runs, use parallel analysis if useful: one pass to identify account/title candidates, one pass to inspect TikHub response fields, and one pass to QA the staged Markdown.

## Defaults

Default final destination:

```powershell
E:\LLM_wiki\LLM_wiki\01.raw\01.Inbox
```

Generated WeChat clipping Markdown should land in `01.raw/01.Inbox` by default as unprocessed source material. Do not classify, summarize, rewrite, or compile it into 02.wiki at clipping time unless the user explicitly asks for that downstream step. If `--output-dir` is supplied, write final Markdown bundles to that directory instead.

Default filename template:

```text
微信_{author}_{summary}_公众号文章剪藏_{date}_{range}.md
```

`{summary}` should be a short filename-safe topic inferred from selected article titles. Keep it human-readable and free of provider/debug labels.

The script writes one Markdown bundle per group, five articles per file by default. If a target filename already exists, the script must publish to a unique sibling path such as `name-2.md` rather than overwrite existing output.

## WeChat Archive Rules

Default clipping output remains `01.raw/01.Inbox` as staging. When the user asks to archive or reorganize WeChat source material under `01.raw/05.Wechat`, use root-level author/account folders directly under `05.Wechat`:

```text
01.raw/05.Wechat/
  乔木mq/
    微信_乔木mq_大模型架构与注意力机制_2026-05-27_1-8.md
  波哥/
  阿东/
  ._Wechat_metadata/
  其他零散微信md.md
```

- Same account/author with 3 or more files, or an account the user explicitly names as a durable folder: move files under `01.raw/05.Wechat/<account-or-author>/`.
- Fewer than 3 files, uncertain author, or mixed source: leave the Markdown files loose in `01.raw/05.Wechat`.
- Cross-account collections can stay loose for now; create `Collections/` only when the user explicitly wants it or the volume justifies it.
- `._Wechat_metadata/` is a special metadata area for future indexes, aliases, logs, or cache manifests. Do not create placeholder metadata files unless there is real metadata to store.

## Cost And Safety

TikHub calls are billed. Prefer inputs in this order:

1. Direct article URLs: usually one detail call per article.
2. Known `gh_...` account id plus target titles: list pages plus detail calls.
3. Account name plus visible titles/OCR: account search, list pages, and detail calls.
4. Broad author/topic clues only: highest uncertainty and likely highest cost.

Do not retry nonrecoverable HTTP `400`, `401`, `403`, `404`, or `422` detail failures in tight loops. Some TikHub search endpoints may time out or return `400`; use the script retry settings and short randomized backoff rather than manual repeated calls.

Before spending TikHub calls, it is acceptable to search local vault folders such as `01.raw/01.Inbox`, `01.raw/05.Wechat`, or `02.wiki/sources` for exact URL/title matches. Only skip TikHub when all requested articles already exist locally as readable UTF-8 full text and doing so matches the user's intent.

Do not fabricate content from snippets. If TikHub cannot return a full article body, report the limitation and the best candidate metadata.

## Commands

Fetch selected articles by account/author clue:

```powershell
python scripts\clip_wechat_tikhub.py "AI 编程实验室" --author "AI 编程实验室" --count 3
```

Fetch from a known article URL:

```powershell
python scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --count 1 --ranges "1"
```

Fetch and apply conservative reading-enhancement formatting:

```powershell
python scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --count 1 --ranges "1" --format-mode readable
```

Use screenshot OCR text or copied page text as title discovery source:

```powershell
python scripts\clip_wechat_tikhub.py "AI 编程实验室" --author "AI 编程实验室" --title-source ".\examples\screenshot-ocr.txt" --count 4 --ranges "1-4"
```

Custom output directory:

```powershell
python scripts\clip_wechat_tikhub.py "AI 编程实验室" --count 3 --output-dir ".\clippings\wechat"
```

Override filename:

```powershell
python scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --filename-template "微信_{author}_{summary}_{date}_{range}.md"
```

Set authentication:

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

If the current process cannot read it yet, restart the terminal/Codex or pass it explicitly:

```powershell
python scripts\clip_wechat_tikhub.py "query" --tikhub-api-key "<tikhub_api_key>"
```

## Output Contract

Output must be UTF-8 Markdown with Obsidian-compatible YAML frontmatter and article sections using the script's real schema. Use `## 0x01. ...`, `## 0x02. ...` for clipped articles and source blockquotes for publish date/source URL. Do not add an in-body document title, query list, capture note, or per-article metadata block beyond the source lines. Do not use level-1 headings in generated clipping body.

Use `###` for major sections inside an article and `####` for numbered subsections inside a major section, using hierarchical numbers such as `#### 2.1 ...`.

Final QA must fail if body Markdown contains `^# `, empty headings, `^###\s+\d+\.\d+`, raw TikHub/Python structures such as `{'title':`, `item_count`, `metadata`, `images':`, or leaked API/debug payloads.

Preserve full cleaned article text by default. Do not summarize, rewrite, delete article sections, invent missing questions/headings, or add new conclusions unless the user explicitly asks for a summary or rewrite. Load `references/wechat-tikhub-notes.md` for detailed cleanup, table/formula/code preservation, API failure handling, and historical debugging guidance.

## Formatting Modes

`--format-mode readable` is optional. Default `plain` mode must remain faithful clipping and must not add emphasis, tables, list restructuring, summaries, or invented headings.

Readable mode may apply only conservative, meaning-preserving formatting such as bolding fixed labels, splitting obvious enumerations, compacting definition-style lists, and converting narrow comparisons into Markdown tables when cells stay short. If a rule is uncertain, leave the original prose alone.

## Concurrency

For concurrent or high-risk runs, write first to a unique staging directory such as:

```powershell
.\.codex-work\wechat-<slug>-<timestamp>\out
```

Use a matching isolated cache directory, QA the staged Markdown, then publish exactly the intended final artifact into `01.raw/01.Inbox` or the user-supplied `--output-dir`. Avoid sweeping deletions or broad filename rewrites.

## Browser Boundary

Do not use Playwright, cookies, captcha handling, WeChat logged-in browser state, or undocumented browser scraping for this skill unless the user explicitly asks for a separate browser-based fallback.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
