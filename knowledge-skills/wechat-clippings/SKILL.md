---
name: wechat-clippings
description: Clip arbitrary WeChat Official Account articles through TikHub into Obsidian Web Clipper-style Markdown bundles. Use when the user provides a WeChat public account author/name, mp.weixin.qq.com article URL, article title, screenshot/OCR text, or asks to fetch one to four selected WeChat public-account articles and save Markdown clippings into a local Obsidian vault folder.
---

# WeChat Clippings

## Default Mode

Use TikHub-first mode. This skill is for arbitrary public WeChat Official Account articles, not only the user's own official account. Read `TIKHUB_API_KEY`, locate candidate accounts/articles with TikHub WeChat endpoints, fetch article detail HTML/JSON when available, then write Markdown bundles compatible with the user's Obsidian clipping style.

Accepted input can be a WeChat public account name, author/nickname, `mp.weixin.qq.com` article URL, article title, screenshot OCR text, copied search/page text, or a mixed instruction such as "抓取作者 A 最近三篇关于 Agent 的文章".

For nontrivial clipping tasks, use a multi-agent workflow when useful:

- Agent A: identify the target account/author and candidate article titles from the user input or screenshot.
- Agent B: choose TikHub endpoint mode, inspect response fields, and verify article URL/title/publish time.
- Agent C: QA Markdown output: heading hierarchy, images, code fences, frontmatter, filename, and source URL.

Do not describe TikHub as an official WeChat API. Treat it as a third-party provider whose response shape, quota, and coverage may drift.

## Fixed Strategy

Use this path after the live 2026-05-26 test run:

1. If the user provides one or more `mp.weixin.qq.com` article URLs, skip search and call the article detail endpoints directly.
2. If the user provides a公众号名、作者名、截图标题或 OCR 文本 but no article URL, first search the official account with `fetch_search_official_account`.
3. From account search results, prefer `jumpInfo.userName` values like `gh_...` as the article-list `ghid`. Do not prefer `__biz`, numeric `bizuin`, or base64 `Mz...` ids for `fetch_mp_article_list` unless a future response proves they work.
4. Fetch the account article list with `fetch_mp_article_list`, and paginate with `data.offset.Offset` until enough requested titles are found or the endpoint says `IsEnd == 1`.
5. For screenshot/OCR title lists, avoid depending on long-title `fetch_search_article` hits. The more reliable route is account list plus fuzzy title/keyword matching.
6. Use article list records only for candidate metadata. Even when the list response contains `ori_content`, still call article detail for final fulltext output when a source URL is available.
7. Use `fetch_mp_article_detail_html` first for normal clipping, then fall back to JSON only if HTML cannot provide usable content. In the live test, JSON returned 400 for valid article URLs while HTML returned full pages.
8. Extract the article body from `#js_content` when present, convert to Markdown, then remove WeChat page chrome such as `继续滑动看下一个`, `微信扫一扫`, `允许`, `取消`, and `知道了`.

## Cost Control

TikHub calls are billed. Prefer inputs in this order:

1. Best: direct `mp.weixin.qq.com` article URLs. This skips account search and article-list pagination; one article usually needs one detail call.
2. Good: known `gh_...` account id plus target titles. This skips account search and only needs article-list pagination plus detail calls.
3. Acceptable: account name plus visible titles/OCR. This needs account search, article-list pagination, and detail calls.
4. Most expensive: only broad author/topic clues. This may require more list pages and uncertain matching.

Do not call long-title `fetch_search_article` before the account-list route for screenshot batches. Do not retry nonrecoverable HTTP 400/401/403/404/422 responses. For normal public-article clipping, use HTML detail first because the live test showed JSON detail can fail while HTML succeeds.

## Typical Commands

Fetch selected articles by account/author clue:

```powershell
python .\scripts\clip_wechat_tikhub.py "作者名或公众号名 文章主题" --count 3
```

Fetch from a known article URL:

```powershell
python .\scripts\clip_wechat_tikhub.py "https://mp.weixin.qq.com/s/xxxx" --count 1 --ranges "1"
```

Use screenshot OCR text or copied page text as title discovery source:

```powershell
python .\scripts\clip_wechat_tikhub.py "公众号名" --title-source "<ocr-title-file>" --count 4 --ranges "1-4"
```

Custom output directory:

```powershell
python .\scripts\clip_wechat_tikhub.py "公众号名" --count 3 --output-dir "<clippings-folder>\WeChat"
```

The default filename template is:

```text
微信_{author}_公众号文章剪藏_{date}_{range}.md
```

Override it with:

```powershell
--filename-template "微信_{author}_{date}_{range}.md"
```

## Workflow

1. Parse the user's clue into article URLs, account clues, title keywords, and optional screenshot/OCR title candidates.
2. If direct `mp.weixin.qq.com` URLs are present, use TikHub article-detail endpoints for those URLs. Do not fetch with a logged-in browser or undocumented WeChat web APIs.
3. If only an author/account clue is present, search the account first, keep the `gh_...` `userName`, then fetch the account article list and paginate with `data.offset.Offset`.
4. Match the requested one to four articles by exact title when possible, otherwise by title keywords from the screenshot/OCR text.
5. Fetch final article detail through TikHub, prefer HTML for normal clipping to reduce failed JSON calls, then convert the `#js_content` body to Markdown.
6. Clean WeChat page chrome, preserve source URLs, images, and readable text, then write grouped Markdown bundles.
7. Cache raw TikHub responses under the cache directory for reproducible QA, but do not expose the API key in logs or Markdown.

When the article tail contains suspected QR-code promotion or private-contact acquisition, remove that tail block. Typical signs include `欢迎关注`, `加我微信`, `交个朋友`, `二维码`, `扫码`, followed by a QR/contact-card image. If the boundary is ambiguous, use LLM judgment to remove only the promotional tail and keep article content.

Normalize standalone URL labels into Markdown links. Convert `项目开源地址: https://...` or a label ending with `地址/官网/链接/开源地址:` followed by a URL on the next line into `[项目开源地址](https://...)`. Remove the colon and avoid leaving the URL detached from its label.

Normalize Markdown inline emphasis produced by WeChat HTML. Convert `** 关键词 **` into `**关键词**`, and remove obvious extra spaces before punctuation after bold text.

Keep article-internal headings tight. For `###` to `#####` headings, remove the blank line immediately after the heading so the heading is directly followed by its paragraph.

Keep media and technical blocks tight as well. Remove extra blank lines immediately before or after Markdown images, fenced code blocks, and display math blocks.

Remove empty Markdown list items generated by WeChat HTML, such as standalone `-` lines. They usually come from empty `<li>` wrappers around code, images, or layout elements.

## Heading Rules

Use a正文型剪藏 layout:

- YAML frontmatter is allowed for Obsidian metadata.
- Do not add an in-body document title, source note, author note, capture date, query list, or per-article metadata block.
- Level 2 heading `##` is only for each clipped WeChat article: `## 一、文章标题`, `## 二、文章标题`, `## 三、文章标题`.
- Level 3 heading `###` is for major sections inside an article.
- Level 4 heading `####` is for numbered subsections inside a major section.
- Do not use level 1 heading `#` in generated clipping body.
- Keep adjacent bullet-list items compact: do not insert blank lines between ordinary `- ...` list items.
- For unlabeled fenced code blocks, infer and add a language tag when obvious. Prioritize `python`, `bash`, `json`, `javascript`, and `typescript`.
- Preserve images as Markdown image links when URLs are available. Preserve tables as Markdown tables when the HTML structure is simple enough.

## Output Format

The script writes one Markdown bundle per group, five results per file by default:

```markdown
---
title: "微信_author_公众号文章剪藏_2026-05-26_1-3"
source: "https://api.tikhub.io/..."
author:
  - "author"
published:
created: 2026-05-26
description: "TikHub 命中的微信公众号文章候选，共 3 条，本文档收录 3 条"
tags:
  - "clippings"
  - "wechat"
  - "author"
---

## 一、Article title

> 发布日期：2026-05-26  
> 原文链接：[Article title](https://mp.weixin.qq.com/...)

正文

### Article section

正文
```

## TikHub Boundary

TikHub has documented WeChat public-account capabilities such as account search, account article list, article search, and article detail in JSON/HTML form. Current default paths use `wechat_mp/web`, including `fetch_search_official_account`, `fetch_mp_article_list`, `fetch_search_article`, `fetch_mp_article_detail_json`, and `fetch_mp_article_detail_html`. Response shapes may change, so inspect cached raw responses when the script cannot parse expected fields.

Some TikHub WeChat search endpoints document limited server resources and recommend client-side retries. Use the script retry settings rather than tight loops.

Long Chinese article-title search may return TikHub 400 even for real articles. If the user gives screenshots with visible titles, prefer account search plus article-list pagination and title matching over direct article search.

For cost control, direct article URLs are the cheapest reliable input. If the user can provide URLs, ask for or prefer them before running account/title discovery. The expected call count is roughly: direct URLs = one detail call per article; known `gh_...` + titles = list pages plus detail calls; account name + screenshots = account search plus list pages plus detail calls.

If TikHub cannot return a full article body for a candidate, write only a clear failure summary in the terminal and do not fabricate article content from snippets.

## Authentication

Set the user environment variable before use:

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

If the current process cannot read it yet, restart the terminal/Codex or pass it explicitly:

```powershell
python .\scripts\clip_wechat_tikhub.py "query" --tikhub-api-key "<tikhub_api_key>"
```

Never print the API key in normal output.

## Deprecated Browser Scraping

Do not use Playwright, cookies, captcha handling, WeChat logged-in browser state, or undocumented browser scraping for this skill unless the user explicitly asks for a separate browser-based fallback.
