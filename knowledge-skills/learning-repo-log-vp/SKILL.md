---
name: learning-repo-log-vp
description: Capture project-scoped learning notes, technologies, concepts, glossary terms, architecture decisions, implementation lessons, and review questions into a durable Markdown learning log. Use when the user says to remember, record, log, add to review notes, add to the learning doc, save this concept, keep this term for later, or update {{project_name}}_学习复盘_技术栈与概念记录.md while working in a repository.
---

# Learning Repo Log

## Purpose

Use this skill to maintain a per-repository learning log. It turns quick user requests such as "记一下这个概念" or "add this to the learning notes" into structured, durable Markdown entries.

This is not an interview-prep skill, resume-writing skill, or project marketing skill. Keep the output focused on learning review, concept retention, and project-grounded understanding.

## Default Log File

Use this filename in the current repository root unless the user specifies another path:

```text
{{project_name}}_学习复盘_技术栈与概念记录.md
```

Resolve `{{project_name}}` in this order:

1. Explicit project name from the user
2. Repository root folder name
3. `AGENTS.md` project title
4. `README.md` project title

If a legacy log exists, such as `学习复盘_技术栈与概念记录.md`, ask only when both files exist and the target is ambiguous. Otherwise prefer the project-prefixed filename and mention the choice.

## Workflow

1. Identify the learning item from the user's request.
2. Determine whether it belongs in the repo learning log.
3. Lightly inspect project context when needed:
   - `AGENTS.md`
   - `README.md`
   - `docs/`
   - relevant source/config files
4. Choose a category using `references/category-guide.md` when classification is not obvious.
5. Create the learning log if it does not exist.
6. Append a new dated entry using `references/entry-template.md`.
7. Keep the entry project-grounded and concise.
8. Report the file path and the entry title.

Use UTF-8 for Chinese content.

## What To Record

Record items such as:

- Technologies and frameworks
- Algorithms and models
- RAG, Agent, MCP, database, frontend, backend, deployment, or evaluation concepts
- Business/domain terminology
- Architecture decisions
- Implementation lessons
- Debugging lessons worth reviewing
- User corrections or preferences that affect future project work
- Questions the user wants to revisit later

Do not record:

- Secrets, API keys, private tokens, credentials, or personal identifiers
- Large copied source files
- Generic encyclopedia explanations with no project relevance
- Interview packaging unless the user explicitly asks for a separate interview document
- Speculative claims that are not grounded in the project or clearly marked as assumptions

## Entry Style

Prefer Chinese when the user uses Chinese.

Each entry should usually include:

1. One-sentence understanding
2. How it appears in the current project
3. Why it matters
4. Easy-to-confuse points or common traps
5. Follow-up review questions

For very small items, write a compact entry. For important concepts, use the full template.

## Updating Existing Entries

Before appending, search the log for the same concept or obvious aliases.

- If an entry already exists and the new information extends it, append a short "补充" subsection under the existing entry.
- If the old entry is weak or wrong, revise it carefully and note what changed.
- If the new item is distinct, create a new dated entry.

Never delete old learning notes unless the user explicitly asks.

## Relationship With Other Skills

If the user asks to explain a concept first, use a project concept explanation workflow before recording the distilled note.

If the user asks to fetch a paper, clip an article, or generate media, use the relevant specialized skill first, then record only the final learning takeaway when requested.

## Output Rules

- Modify files only when the user asks to record or save something.
- Link the updated local file in the final response.
- Keep the final response short: say what was recorded and where.
- Do not commit changes unless the user asks.

