# fill-contributions-graph

Explicit-only Codex skill for planning retrospective maintenance commits across the user's own GitHub repositories.

The current execution rule is:

```text
Excel review -> explicit approval -> commit -> push -> verify remote -> withdraw
```

The skill must not run a standalone local-only commit batch. A local commit is only a transient step inside the push-and-withdraw workflow.

## Core Rules

- Trigger only when the user explicitly names `fill-contributions-graph` or `$fill-contributions-graph`.
- Generate an Excel review file before any execution.
- Require explicit approval of that exact Excel file before creating commits.
- Subtract existing same-day author commits before finalizing the plan.
- Push created commits to GitHub default branches before withdrawal.
- Verify pushed commits are reachable from the remote default branch.
- Withdraw by `git revert` by default, then push the revert commits.
- Use force rewriting only after a separate explicit confirmation.

## Excel Review

The default review table is:

```text
date | target_commit_count | existing_commit_count | planned_new_commit_count | commit_details
```

The daily count is adjusted with:

```python
planned_new_commit_count = max(0, target_commit_count - existing_author_commit_count)
```

Example: if the profile generates 5 commits for 2026-03-25 and GitHub already has 2 matching author commits that day, the plan keeps only 3 new commit tasks.

## Generate A Plan

```powershell
python scripts/generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --profile vibe_coding_builder `
  --excel-out plan.xls
```

For downstream execution, export one row per planned commit:

```powershell
python scripts/generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --granularity commit `
  --excel-out commit-detail.xls `
  --out commit-detail.tsv
```

The script only plans. It does not commit, push, or withdraw.

## Push-And-Withdraw

After Excel approval, execution must:

1. Select clean local worktrees or isolated clones.
2. Record each repository's branch and pre-session HEAD.
3. Create durable maintenance commits with planned author and committer dates.
4. Push the commits to the repository default branch.
5. Verify the remote default branch contains each pushed commit.
6. Prepare withdrawal immediately.
7. Revert pushed commits by default and push the revert commits.

This keeps the operation auditable and avoids the previous failure mode where local-only commits never affected GitHub.

## Withdrawal

Default withdrawal uses `git revert`, not local reset:

```text
git revert <skill-created-sha>
git push origin <default-branch>
```

Do not force-push away pushed commits unless the user explicitly asks for history rewriting and confirms each affected repository. Removing commits from the remote default branch can make contribution graph attribution unstable because the original commits may no longer be reachable.

## Worktree Safety

- Prefer a clean local repository whose remote URL matches the target repository.
- If a matching repository is dirty, stop and ask the user whether to use an isolated clone.
- If multiple clones match, show candidates before selecting one.
- Record a manifest before creating commits.
- Never withdraw commits that are not listed in the manifest.

## Profiles

- `vibe_coding_builder` is the default high-frequency AI-assisted profile.
- `active_personal_builder` is a more conservative personal project profile.

See `references/activity-profiles.md` for exact distributions.
