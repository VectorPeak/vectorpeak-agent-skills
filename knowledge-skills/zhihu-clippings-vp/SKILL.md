---
name: zhihu-clippings-vp
description: Clip Zhihu content into Obsidian Web Clipper-style Markdown bundles. Use when the user provides a Zhihu person name or people URL, article URL/title, question URL, answer URL, screenshot/OCR text, copied snippet, or mixed clues and wants official-first identity/search verification, TikHub-final fulltext retrieval, answer clipping, grouped Markdown output, or raw Zhihu clippings saved to a local inbox/vault folder.
---

# Zhihu Clippings

## When To Use

Use this skill for Zhihu clipping tasks where the user needs saved Markdown source material, including:

- locating a Zhihu author or article from a person name, people URL, article URL, title, screenshot/OCR, copied snippet, or mixed clues
- clipping zhuanlan articles into grouped Obsidian-style Markdown files
- clipping a known Zhihu answer from a question/answer URL or explicit `--question-id` plus `--answer-id`
- using screenshot/OCR or copied text as search clues, while avoiding screenshot-only final clippings

Do not use this skill for browser scraping, captcha/cookie workflows, or downstream wiki rewriting/classification.

## Core Contract

Run official-first, TikHub-final:

1. Use Zhihu Developer Platform `zhihu_search` first for coarse positioning, author/content identity, article ID/source checks, and metadata cross-checks.
2. Use TikHub only as the final fulltext provider when official search returns summaries or when article/answer body fidelity matters.
3. Mark TikHub direct fetches as third-party content. `--article-id` and `--answer-id` can fetch through TikHub directly, but those paths are not official verification by themselves. Prefer official search verification before or after the direct fetch when possible; otherwise record/report that official verification was not completed.
4. Never create a final clipping from screenshot/OCR text, copied snippets, or official `ContentText` when the user expects a full article/answer body. Use those inputs as search/disambiguation clues only.
5. Stop and report clearly when neither official search can identify the target nor TikHub can return a complete untruncated body.

Generated Markdown should land in `01.raw/01.Inbox` by default as unprocessed source material. Do not summarize, rewrite, classify, or move it into 02.wiki unless the user explicitly asks for that downstream step.

For detailed Markdown QA rules, heading normalization, code fence cleanup, and provider notes, read `references/zhihu-notes.md` when preparing or reviewing final output.

## Key Commands

Default official-first search and grouped output:

```powershell
python scripts\clip_zhihu_official.py "https://www.zhihu.com/people/he-yufeng Kimi AI Agent 工程实践" --author "何宇峰" --count 10 --ranges "1-5,6-10"
```

Force TikHub fulltext for a known people URL token:

```powershell
python scripts\clip_zhihu_official.py "https://www.zhihu.com/people/he-yufeng Kimi AI Agent 工程实践" --author "何宇峰" --count 10 --group-size 5 --content-provider tikhub --user-url-token he-yufeng
```

Fetch a known long article through TikHub article detail:

```powershell
python scripts\clip_zhihu_official.py "LeetCode Hot 100 刷题笔记" --author "若尘797" --article-id 2014501815438291918 --count 1 --ranges "1" --filename-template "知乎_{author}_LeetCode Hot 100 刷题笔记_{date}.md"
```

Fetch a known answer:

```powershell
python scripts\clip_zhihu_official.py "https://www.zhihu.com/question/123456789/answer/987654321" --content-provider tikhub --ranges "1"
```

Use screenshot OCR, copied page text, or saved HTML as title/search clues:

```powershell
python scripts\clip_zhihu_official.py "何宇峰 Kimi Agent" --author "何宇峰" --title-source ".\examples\profile-page.txt" --content-provider tikhub --user-url-token he-yufeng
```

Add extra search probes:

```powershell
python scripts\clip_zhihu_official.py "何宇峰" --extra-query "何宇峰 Kimi Agent" --extra-query "何宇峰 月之暗面"
```

Custom output directory:

```powershell
python scripts\clip_zhihu_official.py "何宇峰 月之暗面 Kimi AI Agent 工程实践" --count 10 --group-size 5 --output-dir ".\clippings\zhihu"
```

Default output directory:

```text
E:\LLM_wiki\LLM_wiki\01.raw\01.Inbox
```

Default filename template:

```text
知乎_{author}_{summary}_知乎文章搜索剪藏_{date}_{range}.md
```

`{summary}` should be concise, filename-safe, human-readable, and free of provider/debug labels. Older templates without `{summary}` remain valid.

## Zhihu Archive Rules

Default clipping output remains `01.raw/01.Inbox` as staging. When the user asks to archive or reorganize Zhihu source material under `01.raw/06.Zhihu`, use root-level author/account folders directly under `06.Zhihu`:

```text
01.raw/06.Zhihu/
  何宇峰/
    知乎_何宇峰_知乎文章搜索剪藏_2026-05-26_1-5.md
  VoidOc/
    知乎_VoidOc_AI Agent 入门指南（一）：综述_2026-05-26_1.md
  苏三说技术/
  ._Zhihu_metadata/
  其他零散知乎md.md
```

- Same author/account with 3 or more files, or an author the user explicitly names as a durable folder: move files under `01.raw/06.Zhihu/<author-or-account>/`.
- Fewer than 3 files, uncertain author, mixed source, or temporary collection: leave the Markdown files loose in `01.raw/06.Zhihu`.
- Use the same direct author/account organization for both articles and answers unless the user later asks for separate `Articles/` and `Answers/` trees.
- `._Zhihu_metadata/` is a special metadata area for future indexes, aliases, logs, or cache manifests. Do not create placeholder metadata files unless there is real metadata to store.

## Answer Fast Path

For known answer URLs, use TikHub `fetch_question_answers` after official search verification when possible. Match by exact `answer_id` first, then author/title/body snippets. Accept the result only when `content_need_truncated` is false and HTML body is present. Never regenerate final output from screenshot text or official summaries.

## Official API Boundary

`zhihu_search` is a search API, not a complete user timeline API. Do not claim official-only output is every article from a Zhihu profile unless an official endpoint explicitly returns that complete set. TikHub can supply recent article lists, article detail HTML, and answer HTML, but it is a third-party provider; review frontmatter `content_provider` and `verification` before describing output as verified. Load `references/zhihu-notes.md` for detailed answer matching, query expansion, Markdown QA, and provider troubleshooting.

## Authentication

Set the user environment variable before use:

```powershell
[Environment]::SetEnvironmentVariable("ZHIHU_ACCESS_SECRET", "<access_secret>", "User")
```

If the current process cannot read it yet, restart the terminal/Codex or pass it explicitly:

```powershell
python scripts\clip_zhihu_official.py "query" --access-secret "<access_secret>"
```

Never print the secret in normal output.

Optional TikHub fulltext key:

```powershell
[Environment]::SetEnvironmentVariable("TIKHUB_API_KEY", "<tikhub_api_key_without_API_prefix>", "User")
```

## Safety Boundaries

Do not use Playwright, cookies, captcha handling, profile-page scraping, or undocumented Zhihu web APIs in this skill. If a requested object type is unsupported and no verified TikHub fulltext endpoint is available, stop and report that the current toolchain cannot produce a complete clipping.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
