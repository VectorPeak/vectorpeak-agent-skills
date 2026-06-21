---
name: tech-article-rewriter-vp
description: Deep rewrite authorized technical source corpora into polished Markdown blog posts using a user-provided topic and template. Use when the user provides source-corpus Markdown, WeChat/Zhihu URLs, screenshots, OCR text, or mixed materials and wants a logic-first technical article, iterative rewrite, blog-style draft, template-filled Markdown, or source-backed technical documentation with references.
---

# Tech Article Rewriter

## Purpose
Create one polished technical blog Markdown from a topic, 1-5 source materials, and a Markdown template. The skill performs logic-first deep rewriting: extract technical facts, rebuild the article flow, add practical examples when supported, then write a coherent original article with source references.

If the user gives URLs, screenshots, OCR text, or copied page clues instead of a clean corpus file, follow `references/source-corpus-workflow.md` first to fetch and cache full source material before writing.

## Input Routing
Choose the path before writing:

1. Clean corpus path exists, such as `source-corpus-clean.md`: read it and write directly.
2. URLs or screenshots only: use `references/source-corpus-workflow.md` to produce a staged corpus, then continue from that corpus.
3. User pasted raw source text: save or treat it as ad hoc corpus, preserve visible source links if present, then write.
4. No template provided: use a minimal technical blog template and state the assumption.

Do not write from screenshot-visible text alone when full text can be fetched. Screenshots are positioning clues for source collection.

## Default MVP
Default to:

```text
topic + 1-5 WeChat/Zhihu sources + Markdown template -> one Markdown blog post
```

The output is one article, not one article per source, unless the user asks otherwise.

## End-to-End Flow
Use this flow as the backbone for rewrite tasks:

```text
User input
├─ topic
├─ URL / screenshot / OCR / source-corpus Markdown
└─ Markdown template or style request
   ↓
Source collection
├─ If URLs/screenshots/OCR are provided, follow references/source-corpus-workflow.md
├─ Locate exact source pages or answer/article ids
├─ Fetch full text through TikHub or the platform-specific workflow
├─ Save raw JSON/HTML into cache
└─ Produce source-corpus-clean.md
   ↓
Material understanding
├─ Extract facts, concepts, examples, tools, code, caveats, and failure modes
├─ Keep source URL and author/title metadata
├─ Identify overlap across sources
└─ Identify unique value from each source
   ↓
Logic reconstruction
├─ Choose the clearest reader path
├─ Merge repeated points
├─ Place source-specific details into the right section
├─ Keep professional headings and a readable body voice
└─ Avoid following any single source's structure too closely
   ↓
Draft generation
├─ Fill the Markdown template
├─ Use concrete code examples when useful
├─ Preserve references
└─ Write one coherent article, not source-by-source notes
   ↓
Iteration
├─ Adjust title professionalism
├─ Adjust body tone
├─ Expand or compress coverage
├─ Add diagrams, tree views, examples, or checklists
└─ Produce the final Markdown
```

One-sentence principle: first turn sources into trustworthy corpus, then turn corpus into a logic path, then turn that path into an iterative Markdown article.

## Workflow
1. Collect corpus:
   - If needed, run the source-corpus workflow first.
   - Keep `cache/`, `out/source-corpus-clean.md`, and `out/source-corpus-raw.json`.
2. Parse the user's template:
   - Identify required sections and any per-line instructions.
   - Preserve the requested heading order unless it clearly breaks logic.
3. Extract source notes:
   - problem background
   - key concepts
   - solution layers
   - examples and code snippets
   - tradeoffs, failure modes, and caveats
   - source URLs and author/title metadata
4. Rebuild logic before drafting:
   - Prefer "problem -> why naive methods fail -> solution layers -> examples -> engineering checklist -> summary".
   - Merge duplicate points.
   - Explain conflicts by scenario instead of picking one blindly.
   - Do not follow any single source's order too closely.
5. Draft Markdown:
   - Follow the template.
   - Use original phrasing and transitions.
   - Include concrete code examples when the topic needs them.
   - Keep references at the end unless the template says otherwise.
6. QA the article:
   - It reads as a complete blog, not a stitched summary.
   - Headings are coherent.
   - Code fences have languages.
   - Technical claims are supported by the corpus or clearly marked as general engineering practice.
   - Source links are preserved.
   - No TikHub/OCR/cache/debug details leak into the article body.

## Deep Rewrite Boundary
Use deep rewrite only for source material the user owns, is authorized to adapt, or wants to use with attribution. Default to preserving references.

Allowed:

- restructure section order
- rewrite explanations in a new voice
- combine multiple sources
- remove fluff and repetition
- add concise background needed for comprehension
- add implementation examples consistent with the source topic

Avoid:

- line-by-line paraphrase
- retaining distinctive source phrasing
- presenting third-party material as unattributed original work
- fabricating benchmarks, production incidents, or API behavior
- removing references unless the user says the sources are self-owned and asks for no references

## Output Location
Write drafts under the same staging root used by the corpus when possible:

```text
<staging>/out/article-draft.md
<staging>/out/article-notes.md
```

If no staging root exists, use:

```text
<workspace>/.codex-work/tech-article-rewriter/<slug>-<yyyymmdd-hhmmss>/out/
```

When the user approves or finalizes an article, publish the final Markdown to:

```text
E:\LLMWiki\LLMWiki\Clippings
```

Treat `.codex-work` as staging/cache only. Do not treat it as the permanent home for final articles.

## Iteration Protocol
When the user asks for revisions, preserve the source corpus and update the draft rather than refetching. Common revision intents:

- "logic is not smooth": rebuild outline and transitions first.
- "more code": add runnable or near-real examples in the relevant sections.
- "more like a blog": improve narrative flow and section openings.
- "more technical": add schema, API parameters, edge cases, and validation logic.
- "shorter": remove repeated explanations, not core constraints or references.

## References
Read `references/source-corpus-workflow.md` when source URLs, screenshots, OCR, or article clues need to be turned into full text first.
Read `references/cache-and-corpus.md` for staging/cache rules.
Read `references/rewrite-rules.md` for detailed rewrite rules.
Read `references/template-contract.md` when the user provides a custom Markdown template.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
