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
E:\LLM_wiki\LLM_wiki\raw\01.Inbox
```

Generated raw WeChat clipping Markdown should land in `raw/01.Inbox` by default as unprocessed source material. Do not classify, summarize, rewrite, or compile it into the wiki at clipping time unless the user explicitly asks for that downstream step. If `--output-dir` is supplied, write final Markdown bundles to that directory instead.

Default filename template:

```text
微信_{author}_{summary}_公众号文章剪藏_{date}_{range}.md
```

`{summary}` should be a short filename-safe topic inferred from selected article titles. Keep it human-readable and free of provider/debug labels.

The script writes one Markdown bundle per group, five articles per file by default. If a target filename already exists, the script must publish to a unique sibling path such as `name-2.md` rather than overwrite existing output.

## Cost And Safety

TikHub calls are billed. Prefer inputs in this order:

1. Direct article URLs: usually one detail call per article.
2. Known `gh_...` account id plus target titles: list pages plus detail calls.
3. Account name plus visible titles/OCR: account search, list pages, and detail calls.
4. Broad author/topic clues only: highest uncertainty and likely highest cost.

Do not retry nonrecoverable HTTP `400`, `401`, `403`, `404`, or `422` detail failures in tight loops. Some TikHub search endpoints may time out or return `400`; use the script retry settings and short randomized backoff rather than manual repeated calls.

Before spending TikHub calls, it is acceptable to search local vault folders such as `raw/01.Inbox`, `raw/05.Wechat`, or `wiki/sources` for exact URL/title matches. Only skip TikHub when all requested articles already exist locally as readable UTF-8 full text and doing so matches the user's intent.

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

Output must be UTF-8 Markdown with Obsidian-compatible YAML frontmatter and article sections using the script's real schema:

```markdown
---
title: "微信_author_topic_公众号文章剪藏_2026-05-26_1-3"
source: "https://api.tikhub.io/..."
author:
  - "author"
published: "2026-05-26"
created: 2026-05-26
description: "TikHub returned 3 WeChat article candidates; this bundle includes 3."
tags:
  - "clippings"
  - "wechat"
  - "author"
---

## 0x01. Article title
> 发布日期：2026-05-26
> 原文链接：[Article title](https://mp.weixin.qq.com/...)
Article body.

## 0x02. Another article title
Article body.
```

Do not add an in-body document title, query list, capture note, or per-article metadata block beyond the blockquote source lines. Do not use level-1 headings in generated clipping body.

Use heading levels consistently:

- `## 0x01. ...`, `## 0x02. ...` for clipped articles.
- `###` for major sections inside an article.
- `####` for numbered subsections inside a major section, using hierarchical numbers such as `#### 2.1 ...`.

Final QA must fail if body Markdown contains `^# `, empty headings, `^###\s+\d+\.\d+`, raw TikHub/Python structures such as `{'title':`, `item_count`, `metadata`, `images':`, or leaked API/debug payloads.

Preserve full cleaned article text by default. Do not summarize, rewrite, delete article sections, invent missing questions/headings, or add new conclusions unless the user explicitly asks for a summary or rewrite.

## Markdown Cleanup

Keep SKILL.md lean; load `references/wechat-tikhub-notes.md` when an article needs detailed cleanup, API failure handling, formula/table preservation, or historical debugging guidance.

Always apply these core cleanup rules before publishing:

- Remove WeChat page chrome, share/open-app prompts, preview controls, and QR/private-contact promotion tails.
- Remove article table-of-contents blocks that repeat the same headings before the body.
- Delete standalone empty heading markers and empty list items.
- Keep headings tight: no blank line immediately after any heading.
- Keep adjacent ordinary list items compact, with no blank line between `- ...` or numbered items.
- Preserve real data tables as Markdown pipe tables; do not linearize multi-row/multi-column data tables.
- Preserve formulas when possible as LaTeX, Markdown images, or explicit formula-loss markers. Do not silently drop SVG/MathJax formulas.
- Infer code-fence languages from content when obvious; fix empty, `text`, or wrong labels for Python, JavaScript/TypeScript, Bash, JSON, YAML, SQL, Mermaid, C++/CUDA.
- Escape literal HTML tag examples in prose so Markdown renderers do not execute them.

## Reading Enhancement Mode

`--format-mode readable` is optional. Default `plain` mode must remain faithful clipping and must not add emphasis, tables, list restructuring, summaries, or invented headings.

Readable mode may apply only conservative, meaning-preserving formatting such as bolding fixed labels, splitting obvious enumerations, compacting definition-style lists, and converting narrow comparisons into Markdown tables when cells stay short. If a rule is uncertain, leave the original prose alone.

## Concurrency

For concurrent or high-risk runs, write first to a unique staging directory such as:

```powershell
.\.codex-work\wechat-<slug>-<timestamp>\out
```

Use a matching isolated cache directory, QA the staged Markdown, then publish exactly the intended final artifact into `raw/01.Inbox` or the user-supplied `--output-dir`. Avoid sweeping deletions or broad filename rewrites.

## Deprecated Browser Scraping

Do not use Playwright, cookies, captcha handling, WeChat logged-in browser state, or undocumented browser scraping for this skill unless the user explicitly asks for a separate browser-based fallback.
