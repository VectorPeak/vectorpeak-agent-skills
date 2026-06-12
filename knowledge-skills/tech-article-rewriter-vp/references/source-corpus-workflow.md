# Source Corpus Workflow

## Purpose
Use this workflow when the user gives article URLs, Zhihu/WeChat screenshots, OCR text, copied page snippets, or mixed clues instead of an existing `source-corpus-clean.md`.

The goal is to turn source clues into verified full text before rewriting. Do not write the article from screenshot-visible text alone when full text can be fetched.

## Staging
Use a task-local staging folder:

```text
<workspace>/.codex-work/source-corpus/<slug>-<yyyymmdd-hhmmss>/
  cache/
  out/
  notes/
```

For an already scoped task, `<workspace>/.codex-work/<task-slug>/cache` and `<workspace>/.codex-work/<task-slug>/out` are acceptable.

## General Flow
1. Parse the input into direct URLs, platform clues, visible author names, question/title text, OCR text, and target count.
2. Create the staging folder before paid/network calls.
3. Prefer direct URLs over search:
   - WeChat `mp.weixin.qq.com` URL: call TikHub article detail directly.
   - Zhihu `question/<id>/answer/<id>` URL: call TikHub question answers with exact ids.
   - Zhihu zhuanlan article URL: call TikHub column article detail by article id.
4. For screenshots, use visible text only as positioning clues: title, author, vote count, first paragraph, and section headings.
5. Use official/search APIs for coarse positioning when available. Treat search results as candidates, not final body text.
6. Use TikHub for final full text and save raw responses to `cache/`.
7. Produce:
   - `out/source-corpus-clean.md`
   - `out/source-corpus-raw.json`
   - `notes/matching-decisions.md` when screenshots or ambiguous candidates are involved.

## Zhihu Notes
For Zhihu question answers, recover both `question_id` and `answer_id`.

If only screenshots are provided:

1. Extract the Zhihu question title and visible author names.
2. Search the web or official API for the exact question title to recover `question_id`.
3. Call TikHub `zhihu/web/fetch_question_answers`.
4. Page through answers and match by author, vote count, first paragraph, and distinctive headings.
5. Fetch exact answers by `question_id + answer_id`.

Verified example:

```text
Question: 如何让大语言模型输出JSON格式？
question_id: 656512469
武辰 answer_id: 2048454138544009698
Soulflare answer_id: 1994134127503496676
Woo Tzins answer_id: 1983844551971080064
```

Pitfall: existing clipping scripts may render mojibake Markdown even when TikHub raw cache contains valid UTF-8 Chinese. If this happens, rebuild Markdown from cached JSON/HTML such as `target.content`; do not publish the mojibake file.

## WeChat Notes
Prefer direct `mp.weixin.qq.com` article URLs. If only account/title clues are available, search the account first, prefer `gh_...` identifiers, fetch the article list, then call article detail for full text.

Always cache detail HTML/JSON. Prefer clean structured content when available; fall back to extracting article body from `#js_content`.

## QA Checklist
Before handing the corpus to the rewrite phase:

- Every requested source appears in `source-corpus-clean.md`.
- Raw JSON/HTML exists for every source.
- Every item has a source URL.
- No `content_need_truncated: true`.
- Markdown is readable UTF-8, not mojibake.
- No raw dict/list stringification such as `{'title':` or `}],`.
- No API keys or secrets appear in output.
- Any image, formula, or table loss is noted.
