---
name: wechat-clippings
description: Clip arbitrary WeChat Official Account articles through TikHub into Obsidian Web Clipper-style Markdown bundles. Use when the user provides a WeChat public account author/name, mp.weixin.qq.com article URL, article title, screenshot/OCR text, or asks to fetch selected WeChat public-account articles and save Markdown clippings into a local clippings directory or Obsidian vault folder.
---

# WeChat Clippings
## Default Mode
Use TikHub-first mode. This skill is for arbitrary public WeChat Official Account articles, not only the user's own official account. Read `TIKHUB_API_KEY`, locate candidate accounts/articles with TikHub WeChat endpoints, fetch article detail HTML/JSON when available, then write Markdown bundles compatible with the user's Obsidian clipping style.

Accepted input can be a WeChat public account name, author/nickname, `mp.weixin.qq.com` article URL, article title, screenshot OCR text, copied search/page text, or a mixed instruction such as "clip the latest three articles about Agent from this public account".

For nontrivial clipping tasks, use a multi-agent workflow when useful:

- Agent A: identify the target account/author and candidate article titles from the user input or screenshot.
- Agent B: choose TikHub endpoint mode, inspect response fields, and verify article URL/title/publish time.
- Agent C: QA Markdown output: heading hierarchy, images, code fences, frontmatter, filename, and source URL.

Do not describe TikHub as an official WeChat API. Treat it as a third-party provider whose response shape, quota, and coverage may drift.

## Fixed Strategy
Use this path after the live 2026-05-26 test run:

1. If the user provides one or more `mp.weixin.qq.com` article URLs, skip search and call the article detail endpoints directly.
2. If the user provides a public account name, author name, screenshot title, or OCR text but no article URL, first search the official account with `fetch_search_official_account`.
3. From account search results, prefer `jumpInfo.userName` values like `gh_...` as the article-list `ghid`. Do not prefer `__biz`, numeric `bizuin`, or base64 `Mz...` ids for `fetch_mp_article_list` unless a future response proves they work.
4. Fetch the account article list with `fetch_mp_article_list`, and paginate with `data.offset.Offset` until enough requested titles are found or the endpoint says `IsEnd == 1`.
5. For screenshot/OCR title lists, avoid depending on long-title `fetch_search_article` hits. The more reliable route is account list plus fuzzy title/keyword matching.
6. Use article list records only for candidate metadata. Even when the list response contains `ori_content`, still call article detail for final fulltext output when a source URL is available.
7. Use `fetch_mp_article_detail_html` first for normal clipping, then fall back to JSON only if HTML cannot provide usable content. In the live test, JSON returned 400 for valid article URLs while HTML returned full pages.
8. Extract the article body from `#js_content` when present, convert to Markdown, then remove WeChat page chrome such as `缁х画婊戝姩鐪嬩笅涓€涓猔, `寰俊鎵竴鎵玚, `鍏佽`, `鍙栨秷`, and `鐭ラ亾浜哷.

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
python scripts\clip_wechat_tikhub.py "浣滆€呭悕鎴栧叕浼楀彿鍚?鏂囩珷涓婚" --count 3
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
python scripts\clip_wechat_tikhub.py "鍏紬鍙峰悕" --title-source ".\examples\screenshot-ocr.txt" --count 4 --ranges "1-4"
```

Custom output directory:

```powershell
python scripts\clip_wechat_tikhub.py "鍏紬鍙峰悕" --count 3 --output-dir ".\clippings\wechat"
```

The default filename template is:

```text
微信_{author}_{summary}_公众号文章剪藏_{date}_{range}.md
```

Override it with:

```powershell
--filename-template "微信_{author}_{summary}_{date}_{range}.md"
```

`{summary}` is a concise filename-safe content topic inferred from the selected article titles, such as `大模型架构与注意力机制`. Keep it short, human-readable, and free of provider/debug labels. Older custom templates without `{summary}` remain valid, but the default final artifact must look like `微信_乔木mq_大模型架构与注意力机制_公众号文章剪藏_2026-05-27_1-4.md`.

## Workflow
1. Parse the user's clue into article URLs, account clues, title keywords, and optional screenshot/OCR title candidates.
2. If direct `mp.weixin.qq.com` URLs are present, use TikHub article-detail endpoints for those URLs. Do not fetch with a logged-in browser or undocumented WeChat web APIs.
3. If only an author/account clue is present, search the account first, keep the `gh_...` `userName`, then fetch the account article list and paginate with `data.offset.Offset`.
4. Match the requested one to four articles by exact title when possible, otherwise by title keywords from the screenshot/OCR text.
5. Fetch final article detail through TikHub, prefer HTML for normal clipping to reduce failed JSON calls, then convert the `#js_content` body to Markdown.
6. Clean WeChat page chrome, preserve source URLs, images, and readable text, then write grouped Markdown bundles.
7. Cache raw TikHub responses under the cache directory for reproducible QA, but do not expose the API key in logs or Markdown.

When the user provides an explicit URL batch, treat those URLs as the complete scope. Do not expand the task by scanning all local files from the same author/account unless the user explicitly asks for a wider local merge.

For clipping and merge requests, default to preserving the full article text for every selected URL/article. Do not compress, summarize, rewrite, or turn articles into review notes unless the user explicitly asks for a summary/鎽樿/鎬荤粨/澶嶄範鐗? "鍚堟垚涓€绡?md 鏂囨。" means concatenate the full cleaned articles into one Markdown file.

For concurrent runs, write first to a unique staging directory such as `.\.codex-work\wechat-<slug>-<timestamp>\out` with a matching isolated cache directory. QA the staged Markdown, then copy or move exactly one final artifact into `Clippings`; never write a broad final filename directly while another process may be clipping articles.

If TikHub article detail returns usable body content but no title, recover titles from user-provided screenshot/OCR, explicit title-source text, or the article's own numbered prompt (`绗?棰榒, `浠婃棩棰樼洰`) before publishing. Keep `鏈懡鍚嶅叕浼楀彿鏂囩珷` only in staging/debug output, not in final user-facing files when a reliable title can be inferred.

When the article tail contains suspected QR-code promotion or private-contact acquisition, remove that tail block. Typical signs include `娆㈣繋鍏虫敞`, `鍔犳垜寰俊`, `浜や釜鏈嬪弸`, `浜岀淮鐮乣, `鎵爜`, followed by a QR/contact-card image. If the boundary is ambiguous, use LLM judgment to remove only the promotional tail and keep article content.

Normalize standalone URL labels into Markdown links. Convert `椤圭洰寮€婧愬湴鍧€: https://...` or a label ending with `鍦板潃/瀹樼綉/閾炬帴/寮€婧愬湴鍧€:` followed by a URL on the next line into `[椤圭洰寮€婧愬湴鍧€](https://...)`. Remove the colon and avoid leaving the URL detached from its label.

Normalize Markdown inline emphasis produced by WeChat HTML. Convert `** 鍏抽敭璇?**` into `**鍏抽敭璇?*`, and remove obvious extra spaces before punctuation after bold text.

Normalize list-like article text without changing meaning. Convert Chinese circled numerals such as `鈶?鈶?鈶 to plain ordered markers `1. 2. 3.`; convert Chinese full-width parentheses `锛?锛塦 to ASCII parentheses `( )`; convert top-level Chinese numeric headings like `1銆佹爣棰榒 to `1. 鏍囬`. For consecutive ordered items, keep them compact with no blank lines between `1. ...`, `2. ...`, `3. ...`.

For parallel bullet-list material, remove blank lines between adjacent items even when WeChat HTML serialized each bullet as a separate paragraph. Treat consecutive short `- ...` items as one compact list, especially after phrases like `典型场景包括：`, `包括：`, `如下：`, or `主要有：`. Convert this:

```markdown
- 复杂问题分析；

- 业务异常归因；

- 跨系统调查；
```

into this:

```markdown
- 复杂问题分析；
- 业务异常归因；
- 跨系统调查；
```

Preserve formulas from the source article. If formulas appear as text, avoid Markdown emphasis normalization that corrupts underscores or braces such as `q虄_m` or `R_{n-m}`. If formulas appear as SVG/MathJax, do not silently drop them; convert to LaTeX when recoverable, preserve an image/link when possible, or insert a clear `[鍘熸枃鍏紡涓?SVG锛岄渶鍥炵湅鍘熸枃]` marker near the original location.

Keep all headings tight. For every Markdown heading level from `#` through `######`, remove the blank line immediately after the heading so the heading is directly followed by its paragraph, list, image, code block, quote, or next heading.

Remove empty heading artifacts before publishing. Any standalone Markdown heading marker with no title text, such as `#`, `##`, `###`, `####`, `#####`, or `######`, is an HTML conversion artifact and must be deleted. Final QA must confirm there are no body-level `#` headings and no empty heading lines.

Remove repeated article table-of-contents blocks before publishing. Consecutive lines like `### • ViT的结构`, `### • 不同形状的图片，位置编码怎么设计`, or other `### • ...` entries immediately after an article title/source block are navigation TOC, not body headings. Also delete plain repeated directory blocks such as `今日全部题目` followed by `1. 大模型算法：...`, `2. 大模型算法：...`, and the same TOC glued into one long line before the real article body. Delete the whole TOC block in every article section.

Clean CSS residue leaked from WeChat HTML styles before publishing. Remove standalone `unset` tokens around headings, especially patterns like `### unset unset 浜屻€佹爣棰?unset unset`, and normalize them to `### 浜屻€佹爣棰榒. If a heading was glued to the previous sentence, such as `**缁撹銆?* ### unset unset 涔濄€佹爣棰?unset unset`, split it into a new heading line:

```markdown
**缁撹銆?*

### 涔濄€佹爣棰?```
Keep media and technical blocks tight as well. Remove extra blank lines immediately before or after Markdown images, fenced code blocks, and display math blocks. Display math should be adjacent to the preceding formula-introduction line and the following paragraph/heading, with no blank spacer lines around `$$`.

Remove empty Markdown list items generated by WeChat HTML, such as standalone `-` lines. They usually come from empty `<li>` wrappers around code, images, or layout elements.

## Reading Enhancement Mode

`--format-mode readable` is optional. Default `plain` mode must remain a faithful clipping mode and should not add emphasis, tables, or list restructuring.

Readable mode is for long interview-note or technical-explainer clippings that are hard to scan. It may apply only conservative, meaning-preserving formatting:

- Bold fixed information labels such as `考察意图：`, `回答框架：`, `关键设计要点：`, and `核心设计原则：`.
- Split obvious `第一/第二/第三` enumerations into ordered-looking readable blocks only when boundaries are explicit.
- Convert consecutive definition-style paragraphs after a clear intro such as `包含`, `包括`, `拆成`, `步骤`, `模块`, `机制`, or `环节` into compact Markdown lists.
- Treat blank lines between an intro sentence and definition-style items as cosmetic spacing. If the previous non-empty line says something like `一个典型 Agent 系统包含四个核心模块：` or `ReAct 的核心循环可以拆成五个步骤：`, the following `术语：解释` paragraphs should still become parallel bullets.
- When a sequence is rendered as Markdown bullets, do not keep an internal numeric prefix inside the bold label. Use `- **目标驱动性：** text`, not `- **1. 目标驱动性：** text`; otherwise Obsidian visually crowds the bullet dot and number.
- Always keep one space after a bold label such as `**回答框架：** text`; do not emit `**回答框架：**text`, because Obsidian may render the following text as part of the bold span.
- Convert narrow, well-aligned comparisons such as `CoT / ReAct / ToT` into Markdown tables only when each cell can stay short.
- Fix heading-summary glue first. A line like `### 1. 标题这是说明句` must become a heading plus a normal paragraph before any other enhancement.

Readable mode must not summarize, delete, rewrite, add new conclusions, or invent headings. If a formatting rule is uncertain, leave the original prose alone. Final QA for readable output must still confirm no raw TikHub structures, no `### 1.1` heading failures, no glued `-**` list artifacts, and no broken table/bold artifacts such as `**|**`.

## Heading Rules
Use a姝ｆ枃鍨嬪壀钘?layout:

- YAML frontmatter is allowed for Obsidian metadata.
- Do not add an in-body document title, source note, author note, capture date, query list, or per-article metadata block.
- Level 2 heading `##` is only for each clipped WeChat article. Use hexadecimal-style article numbering: `## 0x01. 文章标题`, `## 0x02. 文章标题`, `## 0x03. 文章标题`. Do not use Chinese article numbering such as `## 一.`, `## 二.`, `## 三.`.
- Level 3 heading `###` is for major sections inside an article. Do not use Chinese numbering such as `### 一.`, `### 一、`, `### 二.`, or `### 三、`. Convert Chinese-numbered section headings to Arabic numbering with a dot, for example `### 一、核心流程` -> `### 1. 核心流程`, `### 二、关键问题` -> `### 2. 关键问题`. Unnumbered original headings may remain unnumbered.
- Do not promote every numbered line to a heading. Under an article section, short local enumerations such as `1. 注意力机制的稀疏化...`, `2. KV Cache 的截断...`, or `1. 增强上下文建模能力` are ordinary ordered-list items unless the source clearly marks them as subsections with a hierarchical number. A major section may be `### 1. 问题来源与典型场景`; its children should be either compact ordered-list items or `#### 1.1 ...`, `#### 1.2 ...`, never sibling `### 1. ...`, `### 2. ...`.
- If a major section uses `### 2. ...`, then nested numbered sections under it must inherit the parent number and become level 4 headings such as `#### 2.1 ...`, `#### 2.2 ...`, `#### 2.3 ...`. Never leave nested items as sibling `### 1. ...`, `### 2. ...`, or plain `#### 1. ...` under that parent.
- In technical articles where a new major section is followed by a restarted local sequence such as `### 4. 工程实现...` then `1. KV Cache...`, treat the restarted local sequence as subsections and render it with the parent prefix, e.g. `#### 4.1 KV Cache...`, rather than another `### 1.` major section or `#### 1. KV Cache...`.
- Final QA must grep for `^###\s+\d+\.\d+` before publishing. Any match is a heading-level failure; fix it to `####` even if the article came from plain-text JSON or a manual postprocess path.
- Level 4 heading `####` is for numbered subsections inside a major section. Its visible number should be hierarchical (`parent.local`), so under `### 3. 主流框架` the local items `1、DeepSpeed`, `2、Megatron-LM`, `3、FSDP` become `#### 3.1 DeepSpeed`, `#### 3.2 Megatron-LM`, `#### 3.3 FSDP`. Do not add numbering to unnumbered original headings.
- Do not use level 1 heading `#` in generated clipping body.
- Do not leave a blank line after any heading level. `##`, `###`, `####`, `#####`, and `######` headings must be immediately followed by the next content line.
- Never stringify TikHub list/dict content directly into Markdown. If a response field such as `content.raw_content` is a list of objects, render each object's `title` and `text` fields structurally. Final QA must fail if Markdown contains extraction residue such as `{'title':`, `'item_count':`, `'}]`, or promo tails like `加入DailyLLM社群(见文末二维码))写在前面`.
- For TikHub JSON detail responses that include `article.full_text`, `article.sections`, or `content.raw_content`, run a tail-completeness QA before publishing. The final Markdown must contain the last substantive section titles and the last 2-3 non-promo text blocks from the source; if it is much shorter than `full_text` or missing source tail markers, treat it as truncated and rebuild from `raw_content`/local RAW rather than publishing.
- Keep adjacent bullet-list items compact: do not insert blank lines between ordinary `- ...` list items.
- For unlabeled fenced code blocks, infer and add a language tag when obvious. Prioritize `python`, `bash`, `json`, `javascript`, and `typescript`.
- Before publishing any generated Markdown file, audit every fenced code block and correct its language label from the code content, not from the source wrapper. Blocks containing `async function`, `const`, `let`, `fetch`, `JSON.stringify`, `TextDecoder`, `crypto.randomUUID`, or `=>` should be labeled `javascript`/`typescript`, not `text`; blocks containing `def`, `class`, `import`, `from ... import`, or `return` should be labeled `python`.
- Also fix wrong generic code-fence labels caused by extraction, especially `text`, `txt`, or empty fences. Infer the language from content and relabel the fence; for example, code containing `def ...(`, `class ...:`, `import ...`, `from ... import ...`, `async def`, or `return ...` should use `python` rather than `text`.
- If extracted code content begins with a leaked marker such as `'''text`, ```text, or similar fence residue, remove that marker and set the outer fence to the inferred language.
- Fenced code block markers must be on their own lines. If extraction glues a marker to preceding prose, such as `**阶段 2:GRPO 训练** ```text`, split it into `**阶段 2:GRPO 训练**` followed by a standalone ```text fence on the next line. Likewise, move any content after an opening fence onto the following line.
- Use these quick language cues: `function`/`const`/`let`/`=>`/`interface` -> `javascript` or `typescript`; `curl`/`grep`/`docker`/`kubectl`/`npm`/`pnpm` -> `bash`; `SELECT`/`CREATE TABLE` -> `sql`; `{` or `[` with quoted keys -> `json`; `key: value` config -> `yaml`; `__global__`/`cudaMalloc`/`#include`/`std::` -> `cuda` or `cpp`.
- Preserve images as Markdown image links when URLs are available.
- If TikHub JSON detail returns structured article content such as `content.article.sections`, render only human-facing fields. Each section `title` becomes an article-internal heading and each section `text` becomes body text. Do not stringify Python/JSON structures into Markdown; final output must not contain raw debug keys such as `item_count`, `metadata`, `{'title'`, `images':`, or `}], 'images'`.
- If TikHub JSON detail contains both `content.raw_content` and `content.article.sections`, prefer `raw_content` for formula-heavy or technical articles because it often preserves finer paragraph and section boundaries. Filter `None` titles, render `type=section` or heading-like short paragraphs as Markdown headings, and wrap short formula-like standalone lines such as `Attention(Q, K, V) = ...` or block matrices in `$$` display math.
- For dense numbered question-list articles such as `Prompt??60?` or `Harness??20?`, preserve numbered entries as plain ordered-list lines instead of converting each item into `###` headings or display math. If the article title promises N questions but TikHub `raw_content` exposes fewer verified numbered items, do not invent missing questions; add a short completeness note or report the discrepancy before publishing.
- Some TikHub `raw_content[0]` entries are long aggregate/fulltext blocks rather than real headings. If the first raw-content item is very long and there are later paragraph items, skip that aggregate block; only short `type=section` entries should become headings.
- Once structured JSON has been rendered into Markdown headings or display-math blocks, do not send it through the plain-text WeChat normalizer again. Treat it as structured Markdown and only run chrome cleanup, heading repair, and Markdown spacing cleanup; otherwise technical articles can be truncated or have headings glued back into prose.
- Formula-line detection must be conservative. Do not wrap explanatory Chinese sentences in `$$` just because they contain symbols like `M_ij` or `d_k`; only short standalone formula expressions should become display math.
- Standalone attention formulas must be display math even when written without LaTeX syntax. Match lines such as `Attention(Q, K, V) = softmax...`, `Attention_i(...) = ...`, `MultiHead(Q, K, V) = ...`, and `head_i = Attention(...)`, then wrap them with `$$` while keeping no blank spacer lines around the block.
- Apply standalone-formula wrapping as a global Markdown postprocess too, not only during JSON `raw_content` rendering, because formulas can also arrive through TikHub HTML fallback.
- Preserve real data tables as Markdown pipe tables. A WeChat HTML table with at least 2 rows and at least 2 columns must not be linearized into one-value-per-line text; convert it to a Markdown table with the first row as the header.
- Do not force layout/code tables into Markdown tables. A 1-row/1-column table, especially one wrapping `<pre>` content, should become a fenced code block or blockquote-style text instead of a pipe table. Infer the fence language when obvious, including `python`, `bash`, `json`, `mermaid`, and `text`.
- Prefer TikHub detail HTML fields that preserve table structure, especially `source`, over plain `content` text when the HTML contains `<table>` tags. Plain `content` often loses the table grid.
- After clipping a table-heavy article, compare source multi-row/multi-column HTML table count with Markdown table count. If source data tables exist but no Markdown table is emitted, treat it as a table preservation failure and inspect the cached HTML before publishing.
- Escape or inline-code literal HTML tag examples in prose so Markdown renderers do not execute them. For example, convert `<h1>`, `<h6>`, `<table>`, `<tr>`, and `<td>` in explanatory text to `` `<h1>` ``, `` `<h6>` ``, `` `<table>` ``, `` `<tr>` ``, and `` `<td>` ``. Do not apply this to actual HTML source blocks or generated Markdown tables.

## Output Format
The script writes one Markdown bundle per group, five results per file by default:

```markdown
---
title: "寰俊_author_鍏紬鍙锋枃绔犲壀钘廮2026-05-26_1-3"
source: "https://api.tikhub.io/..."
author:
  - "author"
published:
created: 2026-05-26
description: "TikHub 鍛戒腑鐨勫井淇″叕浼楀彿鏂囩珷鍊欓€夛紝鍏?3 鏉★紝鏈枃妗ｆ敹褰?3 鏉?
tags:
  - "clippings"
  - "wechat"
  - "author"
---

## 涓€銆丄rticle title
> 鍙戝竷鏃ユ湡锛?026-05-26  
> 鍘熸枃閾炬帴锛歔Article title](https://mp.weixin.qq.com/...)

姝ｆ枃

### Article section
姝ｆ枃
```

## Failure Notes
Live WeChat clipping runs exposed several failure modes that should shape future runs:

- `fetch_search_official_account` and `fetch_search_article` can return HTTP 400 or timeout even for ordinary Chinese queries and documented example-style parameters. The TikHub OpenAPI description explicitly says these search endpoints have limited resources and recommends 3-5 client-side retries with short randomized backoff. Treat 400/timeout from these two search endpoints as retryable during discovery, but avoid tight loops.
- Passing only the positional `input` account name to the current script may skip account search unless `--author` is also set. For screenshot batches, pass both `input` and `--author`, or update the script so a non-URL input is automatically used as an account clue before article search.
- When a screenshot/OCR title list is present, never fill the requested count with broad account-name search results. Require meaningful title overlap before accepting a candidate; otherwise report that no exact candidates were found. This prevents unrelated recent account articles from being bundled as if they were the visible screenshot titles.
- `fetch_mp_article_list` requires a real `gh_...` account id. A WeChat `__biz` value such as `MzI2Mjg3NTY5MQ==` may produce an HTTP 200 wrapper whose `data` says `gzid閿欒`; do not treat wrapper code 200 as a valid article list unless `data` is a structured object/list with article records.
- Short `https://mp.weixin.qq.com/s/...` links can redirect to `wappoc_appmsgcaptcha` when accessed without a valid WeChat browser context. TikHub detail endpoints may return 404 for those links. In that case, do not fabricate content; prefer a fresh direct article URL copied from WeChat, a Sogou result link convertible through `fetch_mp_article_url`, or an already archived local fulltext file.
- Before spending TikHub calls, search the local vault for existing author/source material under `RAW/09.Wechat` and `Wiki/sources`. If exact titles already exist locally, merge from local UTF-8 Markdown instead of refetching. If only mojibake old clippings exist, preserve links/metadata but do not use corrupted body text as final content unless the user accepts a degraded local fallback.
- Local `RAW/09.Wechat` exact-URL matches are an optional fallback/cost optimization, not the default assumption. Most future requests will not have local archives, so explicit URL batches should still default to TikHub article-detail fetching. Only skip TikHub and build from local files when all requested URLs are already locally matched, the local body is readable UTF-8 fulltext, and this shortcut does not hide a provider/API failure the user asked to test.
- TikHub `fetch_mp_article_detail_html` may return a structured `data` object containing clean fields such as `title`, `author`, `content`, `description`, `url`, and a separate full-page HTML field such as `source`. Prefer `data.content` plus `data.title` for final Markdown. Do not choose the longest HTML field first, because full-page HTML can preserve page chrome and may cause the script to lose the structured title.
- TikHub structured `data.content` can be plain text rather than HTML or Markdown. Do not write it directly as body text. Run WeChat chrome cleanup and a plain-text normalizer first: remove header chrome such as `鍘熷垱 浣滆€?鍏紬鍙穈, cut tail chrome such as `缁х画婊戝姩鐪嬩笅涓€涓猔 and `寰俊鎵竴鎵玚, convert Chinese section markers like `涓€銆佹爣棰榒 into `###`, convert numeric subsection markers like `1銆佹爣棰榒 into `####`, and split `(1)` / `(2)` item markers onto readable lines.
- Some WeChat article styles leak CSS default values into text during conversion. The live `鍚村笀鍏?Text2SQL` clipping produced headings like `### unset unset 浜屻€佸湪 Agent 鏋舵瀯閲岋紝Text2SQL 鐨勬纭畾浣?unset unset` and glued headings like `**鍏滃簳閫昏緫姘歌繙涓嶅湪 Tool 閲屻€?* ### unset unset 涔濄€侀潰璇曚腑锛屾€庝箞鎶婅繖浠朵簨璁叉竻妤氾紵 unset unset`. Treat these `unset` tokens as style residue, delete them, and split the heading onto its own line before publishing.
- When TikHub returns mojibake in `message_zh` or `data`, try decoding as `s.encode("gbk").decode("utf-8")` for diagnostics only. Keep generated Markdown UTF-8.
- If the user asks to merge articles into one Markdown file, preserve full cleaned article text by default. Do not produce a compressed summary/review-note version unless the user explicitly asks for `summary`, `鎽樿`, `鎬荤粨`, or `澶嶄範鐗坄. If a summary was accidentally produced, delete or replace it with the full-text bundle so the user does not open the wrong artifact.
- In concurrent Codex sessions, broad filenames such as `寰俊_浣滆€卂鏂囩珷鍚堥泦...md` are collision-prone. Always stage in a unique `.codex-work/wechat-<slug>-<timestamp>` directory and publish exactly one final artifact only after QA. If other agents may be running, list recent `Clippings` outputs before publishing and avoid sweeping deletions.
- PowerShell here-strings can fail with `The string is missing the terminator: '@` when large Chinese/Markdown/LaTeX blocks are embedded directly. Use `apply_patch` for file edits, or use Node/Python scripts that read/write target files instead of embedding long Markdown in PowerShell.
- Python on this Windows setup can throw `OSError: [Errno 22] Invalid argument` when a pasted Chinese path is mojibake-corrupted by the console. Prefer `Get-Content -LiteralPath` for quick inspection, or use Node's UTF-8 filesystem APIs with an explicit absolute path for Chinese filenames.
- JavaScript replacement strings treat `$$` specially, so `text.replace(..., "$$")` can accidentally write a single `$`. Use a function replacement such as `text.replace(regex, () => "$$...")` when inserting Markdown display-math delimiters.
- WeChat/MathJax formulas may be represented as inline text, SVG, or images. The parser currently skips generic `svg`, so inspect cached HTML around formula-heavy passages before claiming formulas were preserved. For SVG formulas, either reconstruct simple LaTeX manually, preserve a linked image when possible, or insert a clear marker instead of silently dropping the formula.
- Markdown emphasis normalization can corrupt formula-like underscores or braces, for example turning `q虄_m` or `R_{n鈭抦}` into stray `*` emphasis fragments. After clipping technical articles, grep for patterns such as `q虄\s+\*`, `R\s+\*`, unmatched `$`, and circled numerals before publishing.
- Display-math blocks should not leave visual spacer rows. If a formula block appears as `intro:\n\n$$...$$\n\nnext`, normalize it to `intro:\n$$...$$\nnext`.
- WeChat HTML often serializes list-like text as separate paragraphs with full-width punctuation, Chinese circled numerals, and extra blank lines. Postprocess ordered material into compact Markdown: `1. ...`, `2. ...`, `3. ...`; convert `鈶犫憽鈶 to numeric markers; convert `锛?锛塦 to `( )`; and remove blank lines between consecutive ordered items.

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
python scripts\clip_wechat_tikhub.py "query" --tikhub-api-key "<tikhub_api_key>"
```

Never print the API key in normal output.

## Deprecated Browser Scraping
Do not use Playwright, cookies, captcha handling, WeChat logged-in browser state, or undocumented browser scraping for this skill unless the user explicitly asks for a separate browser-based fallback.



