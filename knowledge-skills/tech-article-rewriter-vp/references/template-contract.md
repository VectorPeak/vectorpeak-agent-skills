# Template Contract

## Accepted Template Forms
The user may provide:

- a local `.md` file path
- pasted Markdown
- a short section list
- a natural-language description of the desired article shape

If the template contains placeholders like `{{title}}`, `{{summary}}`, or `{{references}}`, replace them. If it contains headings only, fill under those headings.

## Default Template
Use this when no template is provided:

```markdown
# {{title}}

## 0x01. 先把坑摆出来

## 0x02. Prompt 能救急，但别把它当保险

## 0x03. 真正稳的是把格式约束前移

## 0x04. 线上系统还要有最后一层兜底

## 0x05. 到底该怎么选

## 0x06. 总结一下

## 参考资料
```

This default is intentionally blog-like: a few large sections, conversational transitions, and enough code inside the sections to feel practical. Do not split every method into a top-level heading unless the user asks for a documentation-style article.

## Template Priority
Preserve required headings unless:

- the heading duplicates another section
- the heading order makes the article incoherent
- the heading asks for unsupported claims

When adjusting the template, keep the user's intent and mention the adjustment in the final response.

## Per-Line Instructions
If the template describes what each line or section should contain, treat those descriptions as constraints, not text to copy into the final article. Remove instructional comments from the final article unless the user asks to keep them.
