---
name: github-clippings-vp
description: Convert one or many GitHub repository, pull request, issue, discussion, commit, or code URLs into structured LLM_wiki GitHub raw-corpus Markdown. Use when the user invokes $github-clippings-vp, provides GitHub URL batches, asks to save GitHub material into 01.raw/10.GitHub, build GitHub source cards, organize repo/PR/issue URLs, or create engineering-case notes for later LLM/code-agent reference.
---

# GitHub Clippings VP

Use this skill to turn one or many GitHub URLs into structured raw-corpus cards under:

```text
E:\LLM_wiki\LLM_wiki\01.raw\10.GitHub
```

The goal is not to create a bookmark list. The goal is to preserve GitHub material as engineering learning material: repository context, cases, code-reading notes, and reusable patterns.

## Default Folder Scheme

Create missing folders when needed:

```text
10.GitHub
├── 00.Index.md
├── 01.Repositories
├── 02.Cases
├── 03.CodeReading
├── 04.Patterns
└── 99.Archive
```

Use this routing for each URL independently:

- Repository URL -> `01.Repositories/owner__repo.md`
- Pull request, issue, discussion, or commit URL -> `02.Cases/owner__repo__case-topic.md`
- Source file, directory, symbol, or architecture-reading URL -> `03.CodeReading/owner__repo__module-or-topic.md`
- Cross-case abstraction requested by the user -> `04.Patterns/pattern-topic.md`
- Low-value, duplicate, or temporary material -> `99.Archive/`

Do not create a separate `PullRequests` folder. PRs belong in `02.Cases` because the durable value is the engineering case, not the GitHub object type.

## Batch Input Rules

When the user provides multiple GitHub URLs:

1. Treat each URL as a separate source object, not as one combined article.
2. Parse and classify every URL before writing, then group by routed folder only for execution efficiency.
3. Create one Markdown card per URL unless the user explicitly asks to merge related URLs.
4. Preserve the original order in the final report and in `00.Index.md` additions.
5. Deduplicate exact repeated URLs. If two URLs point to the same repo object with different anchors, keep the more specific URL as the source and mention the alternate anchor in the card.
6. Avoid overwriting existing files. If a filename already exists, update it only when it represents the same source URL; otherwise append a short suffix.
7. If some URLs fail to fetch, still process the successful URLs and report failed URLs separately.

## Workflow

1. Parse every URL and identify `owner/repo`, object type, object id, branch/path, and topic.
2. Fetch only the necessary public GitHub context: README for repo cards, title/body/diff summary for PRs, issue discussion for issues, or source snippets for code-reading notes.
3. Preserve source URLs verbatim. Do not invent repository facts, maintainers' intent, benchmarks, or outcomes.
4. Write one Markdown card per URL into the routed folder using the templates in `references/github-card-templates.md`.
5. Update `00.Index.md` if it exists or create it if missing. Add one short row per generated card.
6. For large batches, prefer a concise final summary table: URL/object -> category -> output file -> status.

## Writing Rules

- Keep each card AI-first and future-agent friendly.
- Prefer concise but high-signal notes over long copied material.
- Use `[[wikilinks]]` for important projects, concepts, and patterns when they are obvious.
- Include a `## For future Claude` section explaining how future agents should use the card.
- For external claims, include the GitHub URL or cited source directly near the claim.
- If online fetching fails, create a minimal skeleton only when the user explicitly wants a placeholder; otherwise report the blocker.
- If the URL points to a PR/Issue but the content is mainly useful as interview or code-agent material, still save it in `02.Cases` and add tags such as `pr-case`, `bug-fix`, `review`, or `interview`.

## Filename Rules

Use filesystem-safe names:

```text
owner__repo.md
owner__repo__PR-1234__short-topic.md
owner__repo__Issue-567__short-topic.md
owner__repo__Commit-abcd123__short-topic.md
owner__repo__module-name.md
```

Chinese topic names are allowed when they improve readability:

```text
ragflow__ragflow__PR-1234__临时文件清理.md
langchain-ai__langchain__Issue-5678__工具调用回归.md
```

## Index Rules

`00.Index.md` should be lightweight. For every generated card, add or update one row:

```markdown
| Date | Type | Repo | Topic | Card | Source |
|---|---|---|---|---|---|
| YYYY-MM-DD | case | owner/repo | 临时文件清理 | [[owner__repo__PR-1234__临时文件清理]] | https://github.com/... |
```

Do not paste full summaries into the index. The index is a navigation surface, not the knowledge card itself.

## Output Expectations

After writing, report:

- How many URLs were processed, skipped as duplicates, or failed.
- The routed category for each generated card.
- The created or updated Markdown file paths.
- Any source-fetching limitations.
- Whether `00.Index.md` was updated.