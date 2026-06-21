---
name: daily-notes-vp
description: Capture raw personal learning notes, short goals, questions, code notes, concepts, and pitfall lessons into 10-day Markdown files under E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes. Use when the user asks to record daily notes, learning goals, doubts, questions, code snippets, code ideas, commands, concepts, study fragments, review items, pitfall lessons, debugging lessons, deployment lessons, or says to put something into DailyNotes/raw daily notes.
---

# Daily Notes VP

## Purpose

Use this skill to append lightweight personal learning records into the raw daily-notes layer.

This skill is for raw capture, not polished Wiki writing. Preserve the user's intent, keep the entry easy to read, and avoid turning a quick note into a heavy template.

## Destination

Default destination:

```text
E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes\YYYY-MM-DD_YYYY-MM-DD.md
```

Use 10-day buckets:

- Day 01-10: `YYYY-MM-01_YYYY-MM-10.md`
- Day 11-20: `YYYY-MM-11_YYYY-MM-20.md`
- Day 21-end: use the actual last day of the month, such as `YYYY-MM-21_YYYY-MM-28.md`, `YYYY-MM-21_YYYY-MM-30.md`, or `YYYY-MM-21_YYYY-MM-31.md`

Examples:

```text
E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes\2026-06-01_2026-06-10.md
E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes\2026-06-11_2026-06-20.md
E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes\2026-06-21_2026-06-30.md
```

If `E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes` does not exist, ask the user before writing somewhere else. Do not silently fall back to the current workspace.

## File Header

When creating a new 10-day file, use this header:

```markdown
---
type: daily-notes
date_range: YYYY-MM-DD_YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - daily-notes
  - raw
  - learning
ai-first: true
---

## For future Claude

这是原始学习记录，后续可整理到 Wiki。
```

When appending to an existing file, update only the `updated` date. Do not rewrite older entries.

## Daily Structure

Each date uses this fixed order:

```markdown
## YYYY-MM-DD

### Goal-目标

### Question-疑问

### Code-代码

### Concept-概念

### Pitfall-踩坑
```

If the date section does not exist, create it with all five headings in this order. If a category heading is missing, add it in the correct order.

## Categories

Classify each item into exactly one category unless the user explicitly gives multiple items:

- `Goal-目标`: short-term learning goals, small study tasks, today's focus, review plans
- `Question-疑问`: doubts, questions, interview questions, things the user wants explained later
- `Code-代码`: code questions, code snippets, commands, tiny examples, API usage notes, implementation ideas, or code-shaped material the user wants to revisit later. Treat it as close to `Question-疑问`, but use it when the note is centered on code, command usage, function behavior, configuration snippets, or implementation details.
- `Concept-概念`: terms, definitions, methods, models, mechanisms, reusable conceptual notes
- `Pitfall-踩坑`: debugging lessons, deployment incidents, configuration traps, dependency or route conflicts, "what went wrong / why / how to avoid it next time" experience notes

If classification is uncertain between `Question-疑问` and `Code-代码`, prefer `Code-代码` when the title/body contains concrete code, commands, APIs, config, function names, file paths, stack traces, or implementation details; otherwise prefer `Question-疑问`.

## Entry Format

Use a compact entry. Do not include timestamps. Do not add subheadings like "原始记录", "快速整理", or "标签".

```markdown
#### N. 标题 #tag

正文记录或简短解释。

后续：可选。
```

Rules:

- `N` is the next number within the same category for that date.
- Put lightweight tags at the end of the title when useful.
- Keep the title as a natural question, goal, or concept name.
- Write in Chinese when the user writes in Chinese.
- Keep the user's original wording when it is concise; lightly polish only for readability.
- Add `后续：...` only when there is a real follow-up action.

## Example

```markdown
## 2026-06-17

### Goal-目标

#### 1. 搞清楚 RAG 分块策略 #rag

今天想把 chunk size、chunk overlap、语义边界这几个点串起来。

### Question-疑问

#### 1. 为什么 chunk size 不能固定成一个经验值？ #rag #chunking

固定经验值容易切得太小丢上下文，或切得太大降低召回精度。更合理的做法是结合语义边界、文档结构、embedding 表达能力和检索场景来定。

后续：整理成 Wiki/questions 页面。

### Code-代码

#### 1. FastAPI WebSocket 入口如何避免阻塞事件循环？ #python #fastapi #async

同步生成器或阻塞检索不能直接在 async handler 里跑，可以用 `asyncio.to_thread(...)` 推进一步，再把事件通过 WebSocket 发回前端。

后续：整理成 FastAPI 异步服务 checklist。

### Concept-概念

#### 1. Semantic Chunking #rag #concept

Semantic chunking 是按语义边界切分文本，而不是机械按 token 数切。它更适合问答和知识库场景，但实现成本更高。

### Pitfall-踩坑

#### 1. FastAPI `/docs` 与项目文档路由冲突 #fastapi #docs #pitfall

FastAPI 默认会把 Swagger UI 挂到 `/docs`。如果项目也想把 MkDocs 或静态课程文档挂到 `/docs`，需要显式把 Swagger 改到 `/api/docs`，否则线上访问 `/docs` 时会被 Swagger 抢占。

后续：部署前把路由约定写进 README 或 guardrail。
```

## Multi-item Input

If the user gives several items at once:

1. Split them into separate entries.
2. Classify each entry.
3. Append them under the same date.
4. Number each category independently.

## Safety

Do not record:

- API keys, passwords, tokens, credentials, or private identity data
- Large copied documents or source files
- Claims as final truth when the input is only a rough thought

Raw daily notes are source material. Do not create Wiki pages unless the user explicitly asks.

## Final Response

Keep the response short:

```text
已记录到 E:\LLM_wiki\LLM_wiki\01.raw\02.DailyNotes\YYYY-MM-DD_YYYY-MM-DD.md 的 Question-疑问。
```

If several categories were updated, list them briefly.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
