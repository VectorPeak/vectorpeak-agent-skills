---
name: image-to-markdown-vp
description: Use when the user provides screenshots or images and wants them OCRed, converted, continued, or written into a specified Markdown file, especially for notes with headings, tables, formulas, diagrams, charts, and multi-batch image input.
---

# Image To Markdown VP

## Purpose

Convert one or more screenshots into human-readable Obsidian-ready Markdown while preserving the visible structure as faithfully as practical.

This skill is for capture and reconstruction, not for rewriting or summarizing, unless the user explicitly asks.

## Execution Mode

This skill defaults to multi-agent execution for real screenshot-to-Markdown work.

- MUST use multi-agent execution whenever the task includes multiple screenshots, mixed region types, diagrams, charts, UI evidence, or continuation batches.
- MUST assign one dedicated screenshot-handling agent. This agent owns screenshot inspection, crop decisions, remote uploads, alt text, and insertion anchors.
- MUST assign one structure-reconstruction agent. This agent owns OCR hierarchy, tables, formulas, code fences, and Mermaid conversion.
- The main agent owns merge, final write, and final validation.
- If the batch is large, dense, or risky, add a validator agent to reconcile the region manifest against the final Markdown.
- Only skip multi-agent execution when the task is truly tiny: one small screenshot with plain prose or a simple code block and no meaningful visual evidence.

## Required Inputs

Before writing a file, the user must explicitly provide:

- Output directory path
- Output Markdown filename, or an unambiguous Markdown basename. If the basename is clear but `.md` is missing, append `.md` automatically.
- One or more screenshots or images
- A generation signal such as “生成”, “继续补充”, “输出到文件”, or equivalent

If the path or filename is missing, stop and ask. Do not invent the destination.

## Multi-Batch Handling

- Treat newly provided screenshots as part of the same capture set when the user clearly says they are continuing the same document.
- Preserve screenshot order by conversation order and attachment order unless the user corrects it.
- If the user says more images are coming, the final response MUST explicitly say the Markdown is still partial.
- If the user adds more images after a file already exists, update the same file only when they explicitly ask to continue that file.
- If a batch starts or ends in the middle of a section, table, formula, or code block, preserve only the visible content and do not invent the hidden continuation.

## Hard Requirements

These are mandatory.

- MUST wait for an explicit generation or continuation signal before writing a file.
- MUST confirm the output directory exists and is writable before writing.
- MUST use multi-agent execution by default for screenshot-to-Markdown work unless the task is truly tiny.
- MUST assign one dedicated screenshot-handling agent whenever the batch contains diagrams, charts, infographics, UI states, annotations, or other visual evidence whose meaning would degrade under OCR-only reconstruction.
- MUST inspect whether each image is truncated, incomplete, or a continuation before writing.
- MUST classify each visible region before conversion: prose, code, table, formula, process diagram, architecture diagram, quantitative chart or infographic, UI evidence, visual example, or ignorable chrome.
- MUST build a per-region manifest for any non-tiny batch. At minimum record `image_id`, `region_id`, `region_type`, `must_markdown`, `must_mermaid`, `must_insert_visual`, `reason`, `anchor_location`, `upload_status`, `final_url`, and `final_inserted`.
- MUST convert process diagrams, architecture diagrams, RAG pipelines, layered relationship graphs, and decision flows into Mermaid as the primary representation when Mermaid can preserve structure without dropping meaning.
- MUST distinguish relational diagrams from quantitative charts. Do not force a quantitative chart or infographic into flowchart Mermaid.
- MUST preserve high-information visual regions as cropped image evidence in addition to OCR or Mermaid whenever the original layout itself carries meaning. This includes cost-estimate infographics, benchmark charts, scorecards, dashboards, grouped formula cards, annotated panels, and dense comparison boards.
- MUST include the Obsidian-friendly Forest Mermaid init block in every Mermaid diagram unless the user explicitly asks for another theme or raw Mermaid:

```mermaid
%%{init: {"theme": "forest", "flowchart": {"nodeSpacing": 24, "rankSpacing": 34, "padding": 16, "htmlLabels": true, "curve": "basis"}}}%%
```

- MUST scale Mermaid so it reads in Obsidian without meaningful horizontal dragging. Shorten labels, add `<br/>`, group phases, switch layout, reduce side branches, or split one oversized graph into multiple focused Mermaid blocks when needed.
- MUST treat "the user can see the whole Mermaid at a glance on a normal desktop note view" as the default success bar. Do not stop at merely valid Mermaid if the result still requires obvious horizontal dragging to understand the full graph.
- MUST NOT replace a required Mermaid diagram with only a screenshot.
- MUST NOT omit a required cropped visual reference when the screenshot is the primary proof or when layout, color, legend, annotation, or spatial grouping carries meaning that Markdown cannot preserve well.
- MUST NOT insert whole-page continuation screenshots with generic labels such as `screenshot page 4`, `续页截图`, or `原始截图`.
- MUST NOT keep screenshots that are mostly prose or code after the content has been transcribed.
- MUST use remote image URLs for Obsidian or PicList output. Local `assets/`, temp paths, and absolute local image paths are forbidden unless the user explicitly asks for an offline copy.
- MUST validate uploaded URLs before writing them. Default approved host is `https://img.vectorpeak.cn/...`; any other CDN needs explicit user approval.
- MUST sanitize secrets before upload. If a required crop contains secrets, redact before upload. If redaction destroys the evidentiary meaning, stop and ask.
- MUST NOT silently downgrade required visual evidence to OCR-only because upload failed.
- MUST validate the written file before reporting completion.

## Mandatory Multi-Agent Execution

For non-tiny tasks, this topology is mandatory:

1. `Screenshot-Handling Agent`
   Owns crop boundaries, upload, alt text, and insertion anchors.
2. `Structure-Reconstruction Agent`
   Owns OCR, headings, formulas, tables, code fences, and Mermaid candidates.
3. `Main Agent`
   Owns merge, conflict resolution, file write, and final validation.
4. `Validator Agent` when helpful
   Reconciles the manifest against the final Markdown.

Rules:

- The screenshot-handling agent MUST NOT drift into OCR rewriting or Mermaid authoring.
- The main agent MUST NOT skip screenshot insertion for any manifest row marked `must_insert_visual = yes`.
- If subagents are unavailable for a non-tiny task, the workflow is blocked. Do not silently fall back to single-agent execution.

## Workflow

### 0. Orchestration Gate

Before detailed reading:

1. Decide whether the task is tiny. Default to `not tiny`.
2. Dispatch the screenshot-handling agent and structure-reconstruction agent.
3. Add a validator agent when the batch is large, dense, or high risk.
4. Create the per-region manifest before final writing starts.

### 1. Input Gate

1. Confirm the output directory and Markdown filename are explicit.
2. Append `.md` automatically if the basename is clear and the extension is missing.
3. Confirm the user gave a generation or continuation signal.
4. If appending to an existing file, read the tail first and locate the exact continuation point.

### 2. Image Inspection Gate

For every image, record:

- Is it truncated or a continuation?
- Which regions are prose, code, table, formula, diagram, quantitative chart, UI evidence, or ignorable chrome?
- Which regions should become Markdown text?
- Which regions must become Mermaid?
- Which regions must survive as cropped remote images?
- Which regions can be dropped because OCR already preserves them?
- What is the anchor location where the final content or crop must appear?

### 3. Representation Gate

#### Process / architecture diagrams

1. Write Mermaid first.
2. Match orientation, stage numbering, grouping, branches, and side examples as closely as Mermaid allows.
3. Use `flowchart TB` or `LR` as appropriate.
4. Preserve the original diagram as a tight cropped image after Mermaid when visual comparison or semantic fidelity depends on layout, color, or annotation.
5. Before finalizing, compress the Mermaid for viewport fit: shorten labels, move detail into nearby bullets, prefer top-to-bottom layering for tall flows, use `<br/>` inside long labels, and split dense diagrams into multiple Mermaid blocks if one block would still require horizontal dragging.

#### Quantitative charts / infographics

1. Transcribe all readable numbers, units, ranges, series names, assumptions, and footnotes into Markdown first.
2. Prefer a Markdown table as the canonical structured representation for dense or multi-series charts.
3. Use Mermaid chart syntax only when values, labels, and ordering remain exact and readable.
4. Preserve the original visual via a tight cropped remote image when layout, grouped cards, color mapping, legends, callout placement, or proportional geometry carries meaning.

#### Code / prose screenshots

1. Convert code to fenced blocks.
2. Convert prose to headings, paragraphs, lists, tables, and formulas.
3. Do not keep the original screenshot unless the user explicitly wants visual proof.

### 4. Screenshot Evidence Gate

1. Crop only meaningful visual evidence: diagrams, charts, dashboards, annotated panels, UI states, product pages, visual examples, and success or error proof.
2. Keep crops tight: include the evidence and necessary labels; exclude unrelated chrome, blank margins, repeated prose, and duplicate OCR text.
3. Any region marked `must_insert_visual = yes` is blocking work. It must end in a validated remote URL or an explicit blocked-state report.
4. Prefer Obsidian Image Auto Upload Plugin -> PicList/PicGo local server -> COS/CDN.
5. When PicList is running, upload through `http://127.0.0.1:36677/upload`.
6. If PicList cannot read a Chinese or non-ASCII path, copy to an ASCII-only temporary path and retry.
7. Validate every returned URL:
   - `https`
   - approved host
   - no credential-bearing query parameters
8. If upload fails for a non-required visual, continue with OCR or Mermaid only and report the failure.
9. If upload fails for a required visual, stop and ask unless the user explicitly accepted missing visual proof.
10. Temporary ASCII upload copies must never appear in Markdown and should be removed when practical.

### 5. Write Gate

1. Write only after the gates above are satisfied.
2. For non-tiny tasks, do not write until the manifest has a terminal state for every region and every `must_insert_visual = yes` item is either inserted or explicitly blocked.
3. For continuation updates, remove obsolete “partial document” notices only when the new content completes that continuation.

### 6. Mandatory Validation Gate

Run validation before the final response.

1. Target file exists.
2. Markdown fence count is even.
3. Mermaid fences are paired and Mermaid is present when required.
4. Markdown image syntax is complete.
5. For non-tiny tasks, the manifest exists and every row has a terminal state.
6. Every region with `must_insert_visual = yes` has `final_inserted = yes`, a validated remote URL, or an explicit blocked-state note surfaced to the user.
7. When charts or infographics were present, visible numbers, units, legend mappings, assumptions, and footnotes have been captured in Markdown, and the original crop is preserved when layout or color carried additional meaning.
8. No generic whole-page screenshot labels remain.
9. No forbidden local image paths remain unless explicitly requested.
10. Remote image URLs are approved and credential-free.
11. No unresolved OCR markers remain unless intentionally reported.
12. No obvious secrets remain.
13. Formula delimiters and `$$` counts are paired.
14. Markdown tables are not broken by raw unescaped `|`.
15. Every Mermaid diagram has been compacted enough that a reader can understand the global structure without needing obvious horizontal dragging in a typical Obsidian desktop view.

Recommended searches when practical:

```text
rg -n "续页截图|原始截图|Original Screenshot|screenshot page" <file.md>
rg -n "assets/|AppData|Temp|file://|[A-Za-z]:\\\\" <file.md>
rg -n "Authorization: Bearer|Cookie:|Set-Cookie:|eyJhbGciOi|api[_-]?key|secret[_-]?key|access[_-]?key|token\\s*[=:]|password\\s*[=:]|AKIA|ghp_|github_pat_|sk-" <file.md>
rg -n "piclist|picgo|tcyun|secretId|secretKey|bucket|endpoint|customUrl" <file.md>
```

### 7. Final Response Gate

Report only after validation. Keep it short. Include:

- exact written file path
- whether formulas and tables were checked
- whether Mermaid conversion was used
- whether image regions were cropped and uploaded, and which backend was used when known
- whether required visual evidence was preserved or blocked
- any unresolved OCR uncertainty
- any visibly truncated or continuation-only image
- whether the document is still partial

## Few-Shots

### 1. Diagram plus original crop

Use Mermaid first, then add a tight remote crop when the original layout still matters.

### 2. Code screenshot already transcribed

Keep only fenced code unless the user explicitly wants visual proof.

### 3. UI evidence

When the screenshot is proof of a UI state, keep a tight remote crop beside the related text.

### 4. High-information infographic

Preferred pattern:

````markdown
### CPT 数据量计算

先把核心数值整理成 Markdown 表格：

| 项目 | 数值 |
| --- | --- |
| 原始数据条数 | 约 6 亿条 |
| Stage 1 | 200B tokens, 32K 上下文 |
| Stage 2 | 100B tokens, 128K 上下文 |

再保留紧凑裁剪后的原始视觉图：

![CPT 数据量计算原图](https://img.vectorpeak.cn/obsidian/2026/06/cpt-token-estimate-board.png)
````

Do not:

```markdown
只写 OCR 文本，不保留原图
```

If the visual grouping itself explains the concept, the cropped remote image is mandatory.

## Output Style

Prefer clean Markdown over decorative formatting.

Use:

- `#`, `##`, `###`, `####`
- blockquotes for callout-like remarks
- Markdown tables for comparison tables
- fenced code blocks for code, commands, or literal text
- LaTeX for formulas
- cloud image links for preserved visual evidence
- Mermaid for true flows, architectures, pipelines, loops, and relationship diagrams

Avoid:

- rewriting the source into a new article
- dropping meaningful visual evidence that the screenshot is supposed to prove
- replacing layout-heavy charts or infographics with OCR text only
- embedding secrets or local temp paths
- creating Mermaid for plain command sequences or simple checklists

## Formula Rules

- Use inline math for short symbols like `$k_1$`, `$b$`, `$IDF(t)$`.
- Use display math for standalone equations and keep `$$` paired.
- In formulas, prefer `D_1`, `D_2`, `D_3` over `D1`, `D2`, `D3`.
- Avoid raw `|` inside Markdown tables. Use `\lvert...\rvert`.
- If a formula is partially unreadable, mark only the uncertain part with `[?]`.

## Validation Notes

The `Mandatory Validation Gate` is authoritative.

Additional checks:

- main title and major sections are present
- image order reflects source order
- cropped visual evidence appears beside the related step
- if multi-agent execution was required, the screenshot-handling agent's deliverables are visible in the final Markdown
- any visibly truncated or incomplete image has a corresponding user-facing note
- if the user said more images are coming, the final response says the document is still partial

## Final Response

Keep the final response short. Mention:

- the written file path
- whether formulas and tables were checked
- whether image regions were cropped or uploaded
- whether required visual evidence was preserved or blocked
- any unresolved OCR uncertainty
- whether the document is still partial
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
