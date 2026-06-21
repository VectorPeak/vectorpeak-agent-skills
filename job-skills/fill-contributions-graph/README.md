# Fill Contributions Graph

Explicit-only Codex skill for planning GitHub maintenance activity across repositories.

This skill is intentionally conservative: it plans first, writes an Excel review file, waits for explicit approval, and records every pushed commit in manifests before any withdrawal or recovery step.

```text
GitHub account -> repo scan -> existing commit deduction -> Excel review -> approved execution
```

## What It Does

- Scans repositories owned by a target GitHub account or organization.
- Requires more than 10 eligible repositories before planning.
- Generates a deterministic activity plan for a date range.
- Subtracts commits that already exist on GitHub for each planned date.
- Writes an Excel review file before any execution.
- Supports manifest-driven push, withdrawal, and history-rewrite recovery workflows.

## Safety Rules

- Trigger only when the user explicitly names `fill-contributions-graph`.
- Do not create empty commits.
- Do not create fake placeholder code.
- Do not execute until the Excel plan is explicitly approved.
- Do not rewrite Git history unless the user explicitly confirms the affected repositories.
- Prefer one cleanup PR per affected repository. GitHub PRs cannot span multiple repositories.

## Planning

Generate a daily Excel review file:

```powershell
python .\scripts\generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --profile vibe_coding_builder `
  --excel-out plan.xls
```

Generate one row per planned commit:

```powershell
python .\scripts\generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --granularity commit `
  --excel-out commit-detail.xls `
  --out commit-detail.tsv
```

`--end` is exclusive. To include `2026-03-31`, pass `--end 2026-04-01`.

## Existing Commit Deduction

The plan counts existing author commits on GitHub for each active day:

```text
author:<author> author-date:<YYYY-MM-DD>..<YYYY-MM-DD> user:<account>
```

Then it plans only the remainder:

```python
planned_new_commit_count = max(0, target_commit_count - existing_author_commit_count)
```

## Recovery Workflow

If a `git revert` withdrawal was pushed and the user later asks to remove the revert commits from GitHub-visible history, do not revert the reverts. That creates additional current-day commits.

Use history-rewrite recovery only after explicit confirmation:

1. Load the push and withdrawal manifests.
2. Verify affected repositories, branches, `pre_withdraw_head`, `post_withdraw_head`, source SHAs, and revert SHAs.
3. For branches still at `post_withdraw_head`, reset to `pre_withdraw_head`.
4. For branches with legitimate later commits, replay only those later commits on top of `pre_withdraw_head`.
5. Push with `git push --force-with-lease`.
6. Verify no recorded revert SHA remains reachable from the remote default branch.
7. Open cleanup PRs that delete restored generated docs.

Generated docs commonly live under:

```text
docs/notes/
docs/testing/
docs/config/
docs/maintenance/
docs/evaluation/
docs/editorial/
docs/experiments/
docs/review/
```

Delete manifest-owned generated files from those directories, and remove directories when they become empty.

## Files

```text
fill-contributions-graph/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- activity-profiles.md
`-- scripts/
    `-- generate_plan.py
```
