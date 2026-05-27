---
name: zhihu-clippings
description: Clip Zhihu official developer API author-search results into Obsidian Web Clipper-style Markdown bundles. Use when the user provides a person name, Zhihu people URL, Zhihu article URL, article title, or mixed author description and wants to locate the author through the official API, search Article results under that author, group every 5 results into one Markdown file, or save Zhihu clippings into D:\LLMWiki\LLMWiki\Clippings or another Obsidian vault folder.
---

# Zhihu Clippings

## Default Mode

Use official-first, TikHub-final mode. It reads `ZHIHU_ACCESS_SECRET`, calls Zhihu Developer Platform `zhihu_search`, infers or accepts the target author, and uses official results mainly for定位、article_id/source 验证和元信息交叉检查. For final正文剪藏, expect TikHub to be needed in most real cases because the official API often returns search summaries rather than full article HTML.

When `TIKHUB_API_KEY` and a Zhihu people `url_token` are available, `--content-provider auto` uses TikHub `fetch_user_articles` as the article-list/fulltext layer and then verifies or enriches each candidate through the official `zhihu_search` API. The output explicitly marks `official_matched` and `content_source` per article. This keeps the official API as the positioning/validation layer while using TikHub only to fill the正文 that the official API does not expose.

For known long articles, prefer official API lookup for article ID confirmation, then TikHub `fetch_column_article_detail` for final正文 output. Do not stop at official API `ContentText` when the user expects完整正文、公式、图片或代码块.

When allowed and useful, use a multi-agent workflow for nontrivial clipping tasks:

- Agent A: official API lookup, author/article identity, article_id/source confirmation.
- Agent B: TikHub endpoint selection and response inspection, including formula/image/content truncation checks.
- Agent C: Markdown output QA, heading hierarchy, code fence language, formula/image preservation, Obsidian frontmatter and filename checks.

Accepted input can be a person name, Zhihu people URL, Zhihu article URL, article title, or mixed author description.

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "https://www.zhihu.com/people/dan-mo-41-42 何宇峰 月之暗面 Kimi AI Agent 工程师" --count 10 --ranges "1-5,6-10"
```

Force the official + TikHub fulltext mode:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "https://www.zhihu.com/people/dan-mo-41-42 何宇峰 月之暗面 Kimi AI Agent 工程师" --author "何宇峰" --count 10 --group-size 5 --content-provider tikhub --user-url-token dan-mo-41-42
```

Custom clipping ranges:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "https://www.zhihu.com/people/dan-mo-41-42 何宇峰" --author "何宇峰" --content-provider tikhub --user-url-token dan-mo-41-42 --count 10 --ranges "1,2-3,4-8"
```

For long known articles, fetch each article detail by article id and write one Markdown per article:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "LeetCode Hot 100 刷题笔记 若尘797" --author "若尘797" --article-id 2014501815438291918 --count 1 --ranges "1" --filename-template "知乎_{author}_LeetCode Hot 100 刷题笔记_{date}.md"
```

The default filename template is:

```text
知乎_{author}_知乎文章搜索剪藏_{date}_{range}.md
```

Examples:

```text
知乎_何宇峰_知乎文章搜索剪藏_2026-05-25_1.md
知乎_何宇峰_知乎文章搜索剪藏_2026-05-25_2-3.md
知乎_何宇峰_知乎文章搜索剪藏_2026-05-25_1-5.md
```

Override it with:

```powershell
--filename-template "知乎_{author}_知乎文章搜索剪藏_{date}_{range}.md"
```

Default output directory:

```powershell
D:\LLMWiki\LLMWiki\Clippings
```

Custom output directory:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "何宇峰 月之暗面 Kimi AI Agent 工程师" --count 10 --group-size 5 --output-dir "D:\LLMWiki\LLMWiki\Clippings\Zhihu"
```

If author inference is ambiguous, pass the author explicitly:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "https://www.zhihu.com/people/dan-mo-41-42" --author "何宇峰"
```

Add more search probes when the default author queries are too narrow:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "何宇峰" --extra-query "何宇峰 Kimi Agent" --extra-query "何宇峰 月之暗面"
```

For a known profile article list, put visible article titles into a UTF-8 text file, one title per line, then use:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "何宇峰" --author "何宇峰" --extra-query-file "D:\LLMWiki\LLMWiki\Clippings\.llmwiki-cache\zhihu-clippings\he-yufeng-titles.txt"
```

If the user provides screenshot OCR text, copied page text, or an HTML file, use it as a title discovery source:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "何宇峰" --author "何宇峰" --title-source "D:\LLMWiki\LLMWiki\Clippings\.llmwiki-cache\zhihu-clippings\profile-page.txt"
```

## Heading Rules

Use a正文型剪藏 layout:

- YAML frontmatter is allowed for Obsidian metadata.
- Do not add an in-body document title, source note, author note, capture date, query list, or per-article metadata block.
- Level 2 heading `##` is only for each clipped Zhihu article. Use hexadecimal-style article numbering: `## 0x01. 文章标题`, `## 0x02. 文章标题`, `## 0x03. 文章标题`. Do not use Chinese article numbering such as `## 一、文章标题`, `## 二、文章标题`, or `## 三、文章标题`.
- Level 3 heading `###` is for major sections inside a Zhihu article. Do not use Chinese numbering such as `### 一.`, `### 一、`, `### 二.`, or `### 三、`. Convert Chinese-numbered major sections to Arabic numbering with a dot, for example `### 一、核心模板速查` -> `### 1. 核心模板速查`, `### 二、UI Agents技术路线` -> `### 2. UI Agents技术路线`. Unnumbered original headings may remain unnumbered.
- Level 4 heading `####` is for numbered subsections inside a major section, such as `1.1 哈希表模板`.
- Level 5 heading `#####` is for implementation variants or methods under a numbered subsection, such as `方法一：记忆化搜索`.
- Do not use level 1 heading `#` in generated clipping body.
- Do not use numeric headings like `## 1.` in the body; use `## 0x01.` for article-level headings.
- Keep adjacent bullet-list items compact: do not insert blank lines between ordinary `- ...` list items.
- For unlabeled fenced code blocks, infer and add a language tag when obvious. Prioritize `python`, `bash`, and `json`.
- Preserve formulas, images, and tables when present: Zhihu equation images become LaTeX `$...$` or `$$...$$`, normal images become Markdown images, and HTML tables become Markdown tables.
- Optional LLM review: pass `--llm-heading-review` to send only the extracted heading list to an OpenAI-compatible model for level corrections. The LLM must return JSON level changes and must not rewrite body text.

## Output Format

The script writes one Markdown bundle per group, five results per file by default:

```markdown
---
title: "知乎_author_知乎文章搜索剪藏_2026-05-25_1-5"
source: "https://developer.zhihu.com/api/v1/content/zhihu_search"
author:
  - "author"
published:
created: 2026-05-25
description: "知乎官方 API 搜索命中的作者文章候选，共 10 条，本文件收录 5 条。"
tags:
  - "clippings"
  - "zhihu"
  - "author"
---

## 0x01. Result title

正文

### Article section

正文
```

## Official API Boundary

`zhihu_search` is a search API. It can return Zhihu content records for a query, but it is not a complete user timeline API. Do not claim official-only output is every article from a Zhihu profile unless the official API explicitly returns that complete set.

The official API currently caps each `zhihu_search` query `Count` at 10 and does not document pagination. This skill runs several author-centered queries, deduplicates results, and writes the official API search hits. If the user can see a profile page with more articles than the default probes find, use screenshot/page text as `--title-source`, or add visible titles as `--extra-query` values or an `--extra-query-file`.

For fulltext mode, TikHub may return the user's recent article list and HTML正文. Treat TikHub as a third-party provider: results can incur charges, may drift, and should not be described as an official Zhihu API result. The Markdown bundle records whether each article was also matched through official search.

## Authentication

Set the user environment variable before use:

```powershell
[Environment]::SetEnvironmentVariable("ZHIHU_ACCESS_SECRET", "<access_secret>", "User")
```

If the current process cannot read it yet, restart the terminal/Codex or pass it explicitly:

```powershell
python C:\Users\ZXY\.codex\skills\zhihu-clippings\scripts\clip_zhihu_official.py "query" --access-secret "<access_secret>"
```

Never print the secret in normal output.

Optional TikHub fulltext key:

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

## Deprecated Browser Scraping

Browser scraping is intentionally removed. Do not use Playwright, cookies, captcha handling, profile-page scraping, or undocumented web APIs for this skill.
