---
name: init-agent-docs-vp
description: Use when initializing or refreshing project-level agent documentation, AGENTS.md, README.md, hidden .docs files, progressive disclosure, coding-agent onboarding, repo facts, development commands, testing notes, conventions, or agent boundaries.
---

# Init Agent Docs VP

## Overview

Initialize a lightweight agent documentation system for any project. Keep the root `AGENTS.md` as the single agent entry point, then disclose deeper context through focused `.docs/*.md` files.

## Workflow

1. Confirm the target directory is the intended project root. If the user does not specify a path, use the current working directory.
2. Run the bundled script:

```bash
python <skill-dir>/scripts/init_agent_docs.py --target <project-root>
```

3. Preserve existing files by default. Use `--force` only when the user explicitly asks to overwrite generated docs.
4. Use `--update-facts` when only repository facts should be refreshed.
5. Report created, updated, and skipped files.

## Generated Structure

```text
README.md
AGENTS.md
.docs/
  project-overview.md
  development.md
  architecture.md
  testing.md
  conventions.md
  agent-boundaries.md
  progressive-disclosure.md
  system/
    repo-facts.md
    generation-notes.md
```

Do not generate `.docs/AGENTS.md` by default. The root `AGENTS.md` must remain the only global agent entry point.

## Responsibilities

| File | Purpose |
| --- | --- |
| `README.md` | Human-facing project entry |
| `AGENTS.md` | Agent-facing router and highest-priority working rules |
| `.docs/project-overview.md` | Project goal, users, terms, and context |
| `.docs/development.md` | Install, run, build, lint, format, environment notes |
| `.docs/architecture.md` | Modules, boundaries, data flow, external systems |
| `.docs/testing.md` | Test commands, strategy, fixtures, CI notes |
| `.docs/conventions.md` | Naming, code style, project patterns, contribution style |
| `.docs/agent-boundaries.md` | Always / Ask First / Never rules |
| `.docs/progressive-disclosure.md` | Which document to read for each task |
| `.docs/system/repo-facts.md` | Machine-maintained repository fact snapshot |
| `.docs/system/generation-notes.md` | Generation source, assumptions, and unknowns |

## Progressive Disclosure Rules

- Keep `AGENTS.md` short enough to scan quickly.
- Put task-specific detail in `.docs/`.
- Put generated or inferred facts in `.docs/system/`.
- Read only the smallest relevant document before acting.
- Avoid duplicate instructions across files; link instead.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Creating both `AGENTS.md` and `.docs/AGENTS.md` | Keep root `AGENTS.md` as the single entry |
| Putting long manuals in `AGENTS.md` | Move detail into `.docs/*.md` |
| Mixing generated facts with human guidance | Put generated facts under `.docs/system/` |
| Overwriting user files silently | Preserve by default; require `--force` |
