---
name: pr-case-collector-vp
description: Collect concise GitHub Pull Request examples into the user's Obsidian vault for LLM reference. Use when the user provides one or more GitHub PR links, mentions collecting PR cases, asks to rate PR difficulty, or wants PR examples saved for future LLM/code-agent reference.
---

# PR Case Collector

Use this skill to append concise [[Pull Request]] cases to the vault note:

`E:\LLM_wiki\LLM_wiki\01.raw\10.GitHub\LLM_PR案例参考库.md`

## Workflow

1. Read the vault root `_CLAUDE.md` if working inside `E:\LLM_wiki\LLM_wiki`.
2. Ensure the target file exists. If missing, create it with AI-first frontmatter, a `## For future Claude` preamble, a short purpose section, the rating table, and the PR cases table.
3. For each PR URL, fetch or inspect the PR enough to fill a single concise table row.
4. Append only one row per PR. Do not write a long dossier unless the user asks.
5. Keep the note in Chinese.

## Target Table Format

Append rows under `## PR 案例`:

```markdown
| PR | 项目 | 改动类型 | 评级 | 备注 |
|---|---|---|---|---|
| [owner/repo#123](https://github.com/owner/repo/pull/123) | [[Repo]] | 依赖补充 / 配置改动 | 简单 | 小型 PR，主要改 `pyproject.toml`；适合作为 [[LLM]] 判断简单 PR 的参考案例。 |
```

## Rating Rules

- `简单`: 改动很小，通常 1-2 个文件，风险低。
- `中等`: 需要读上下文，可能影响行为。
- `困难`: 涉及架构、多个模块、迁移或复杂逻辑。

Prefer the user's explicit rating if provided. Otherwise infer from changed files, line count, and behavioral risk.

## Notes

- Preserve the PR URL verbatim.
- Use `[[wikilinks]]` for the repo/project and key concepts such as `[[LLM]]` or `[[Pull Request]]` when mentioned in prose.
- Mark volatile GitHub observations with date wording in the note if adding prose outside the table.
- If a PR is already listed, update the existing row only when the user asks or when the new information is clearly a correction.

