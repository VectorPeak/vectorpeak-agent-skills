---
name: image-to-md-vp
description: Use when the user provides screenshots or images and wants them OCRed, converted, continued, or written into a specified Markdown file, especially for notes with headings, tables, formulas, emoji, highlighted text, or multi-batch image input.
---

# Image To Markdown VP

## Purpose

Convert one or more user-provided images into a human-readable Markdown document while preserving the visible structure as faithfully as practical.

This skill is for image/screenshot-to-Markdown capture. It is not for rewriting, summarizing, polishing, or omitting details unless the user explicitly asks.

## Required Inputs

Before writing a file, the user must explicitly provide:

- Output directory path
- Output Markdown filename, including `.md`
- One or more images or screenshots
- A generation signal, such as "生成", "为我生成一下", "图片给完了", "输出到文件", or equivalent

If the output directory or filename is missing, ask for it before writing. Do not invent the destination.

## Multi-Batch Image Handling

The user may provide images across multiple messages.

- Treat newly provided images as part of the current capture set when the user says they are continuing the same document.
- Do not assume the image set is complete just because one message contains images.
- Wait for an explicit generation signal before writing the Markdown file.
- Preserve image order by conversation order and attachment order. If order is ambiguous, ask before writing.
- If the user adds more images after a file has already been generated, update the same file only when they explicitly ask to continue that file.

## Workflow

1. Confirm the target path and filename are explicit.
2. Read all provided images in order.
3. OCR the visible text and reconstruct the document hierarchy:
   - Main title as `#`
   - Major numbered sections as `##`
   - Subsections as `###` / `####`
   - Lists as Markdown bullets or numbered lists
   - Simple tables as Markdown tables
   - Formulas as LaTeX
4. Preserve original wording, numbers, examples, equations, labels, and section order.
5. Preserve emoji. If the exact emoji cannot be identified, use the closest reasonable emoji or a short placeholder such as `[emoji]`.
6. Convert visual highlighting into Markdown emphasis only when it carries meaning:
   - Important highlighted sentence: `**...**`
   - Warning/correction examples: use bullets, blockquotes, or labels instead of color-only meaning.
7. Write the Markdown file.
8. Validate the written file.
9. Report the exact file path and a concise summary.

## Output Style

Prefer clean Markdown over decorative formatting.

Use:

- `#`, `##`, `###`, `####` for visible heading hierarchy
- Blockquotes for callout-like remarks
- Markdown tables for comparison tables
- Fenced code blocks only for code, commands, or literal text blocks
- LaTeX for mathematical formulas

Avoid:

- Removing emoji just because it is decorative
- Adding analysis not visible in the image
- Turning raw OCR into a rewritten article
- Creating extra README files or sidecar notes unless requested
- Adding timestamps unless they are visible in the image

## Formula Rules

Use robust Markdown/LaTeX that renders well in common Markdown tools such as Obsidian, GitHub-style preview, and KaTeX-like renderers.

### Delimiters

- Use inline math for short symbols: `$k_1$`, `$b$`, `$IDF(t)$`
- Use display math for standalone equations:

```markdown
$$
IDF(t)=\log_{10}\left(\frac{N}{n(t)}\right)
$$
```

- Ensure every `$$` delimiter is paired.
- Put display math delimiters on their own lines.

### Safer Syntax

- In formulas, prefer `D_1`, `D_2`, `D_3` over `D1`, `D2`, `D3` when used as symbols.
- Avoid raw vertical bars for document length or absolute value because they can break Markdown tables or previews:
  - Use `\lvert D\rvert`
  - Use `\lvert D_1\rvert`
  - Use `\lVert x\rVert` for norms
- Avoid Chinese inside LaTeX when possible. Put Chinese explanation outside the formula, or use short English variable labels.
- For multi-line calculations, use `aligned`:

```markdown
$$
\begin{aligned}
Score(D_1,Q)
&=TermScore(\text{apple},D_1)+TermScore(\text{banana},D_1) \\
&\approx0.6935+0.4919=1.1854
\end{aligned}
$$
```

- In Markdown tables, avoid formulas containing `|`. Use `\lvert...\rvert` or move the formula outside the table.
- Escape literal underscores in normal text when they are not meant as Markdown emphasis.

### OCR Formula Policy

- Preserve the formula as shown when it is readable.
- If a formula is partially unreadable, mark only the uncertain part with `[?]` rather than guessing.
- If the source has an obvious arithmetic correction or note, preserve that note.
- Do not silently change formulas to a "better" version unless the user asks for correction; if correction is necessary for readability, add `注：...`.

## Tables

Use Markdown tables when:

- The table has a clear rectangular structure
- Cells are short enough to remain readable
- Formulas inside cells do not contain risky raw `|`

If the table is complex, prefer sectioned bullets:

```markdown
### 对比

- **理论基础**
  - TF-IDF：...
  - BM25：...
```

## Validation Checklist

After writing, inspect the file for:

- Target file exists at the requested path
- Main title and major sections are present
- Image order is reflected in section order
- `$$` count is even
- No obvious raw OCR debris such as duplicated `$f$`, broken `$|D|$`, or dangling formula delimiters
- No unintended omission of emoji; uncertain emoji are replaced rather than deleted
- Markdown tables are not broken by unescaped pipes

When practical, use quick searches such as:

```text
$$
|D
$f$
TODO
[?]
```

## Final Response

Keep the final response short. Include:

- The written file path
- Whether formulas and tables were checked
- Any unresolved OCR uncertainty, if present

Example:

```text
已生成到 .../RAG基础_02_TF-IDF&BM25.md。已检查公式分隔符和裸 |D|，没有发现明显渲染风险。
```
