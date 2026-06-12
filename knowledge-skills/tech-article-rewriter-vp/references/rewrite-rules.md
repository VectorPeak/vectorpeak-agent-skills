# Rewrite Rules

## Logic-First Prompt Contract
Use this mental contract for each article:

```text
Given a topic, source corpus, and Markdown template:
1. Extract source facts and examples.
2. Build the clearest reader path.
3. Fill the template with a coherent original article.
4. Preserve references.
```

Do not expose the extraction notes unless the user asks for them.

## Article Shape
For engineering topics, prefer this progression:

1. Why the problem matters in real applications.
2. Why the naive solution fails.
3. The simplest workable approach.
4. Stronger API/framework support.
5. Runtime validation and repair.
6. Production checklist and tradeoffs.
7. Summary and references.

## Preferred Blog Voice
Default to a vivid, conversational technical-blog voice unless the user asks for formal documentation.

- Use concrete work scenes before abstract concepts.
- Prefer "你会遇到..." and "真正麻烦的是..." style transitions when writing Chinese.
- Keep paragraphs substantial and readable instead of making every idea a tiny heading.
- Use a few memorable section titles, not many fragmented textbook headings.
- Make the article feel like an experienced engineer explaining the decision path at a desk, not a stitched list of notes.
- Keep the technical claims precise even when the tone is casual.

For Chinese blog drafts, prefer hexadecimal section numbering for major sections:

```markdown
## 0x01. 先把坑摆出来
## 0x02. Prompt 能救急，但别把它当保险
## 0x03. 真正稳的是把格式约束前移
## 0x04. 线上系统还要有最后一层兜底
## 0x05. 到底该怎么选
```

Use unnumbered subheads sparingly inside each large section only when they improve scanning.

## Code Examples
Include examples when the topic is implementation-heavy. Code should be:

- short enough to read in a blog
- realistic enough to copy into a project after adaptation
- fenced with language tags
- explained before or after the block

Do not invent exact SDK options that may have changed unless they are present in the corpus or verified from official docs. If unsure, write framework-agnostic pseudocode or mark it as illustrative.

## Source Use
Use source material as evidence, not as prose to imitate.

- Preserve facts, methods, caveats, and links.
- Combine repeated points into one stronger explanation.
- Translate informal claims into precise engineering language.
- Keep disagreements as "use X when..., use Y when..." decisions.

## Reference Section
Default reference format:

```markdown
## 参考资料
- [作者 - 标题](source-url)
```

If a corpus item lacks an author, use the platform or title.

## Quality Bar
The final article should not read like:

- "本文根据几篇文章整理..."
- a list of article summaries
- a Q&A answer
- a loose outline
- a model prompt dump

It should read like a standalone technical blog backed by sources.
