---
name: profile-readme-vp
description: Trigger and verify VectorPeak's personal GitHub profile README automation. Use when the user asks to manually run, rerun, test, check, or validate the VectorPeak/VectorPeak profile README GitHub Actions workflow, especially the Update profile README workflow or update-profile.yml.
---

# Profile README VP

Use this skill as a thin operator guide for the remote GitHub Actions workflow that regenerates VectorPeak's profile README. Do not generate the README locally from this skill.

## Source of Truth

- Skill repository: `VectorPeak/vectorpeak-agent-skills`
- Target repository: `VectorPeak/VectorPeak`
- Default branch: `main`
- Workflow file: `.github/workflows/update-profile.yml`
- Workflow name: `Update profile README`
- Automation branch: `automation/update-profile-readme`
- Expected PR title when README changes: `chore: update profile README`

The README generation, GitHub fact collection, translation, project classification, contribution classification, star formatting, PR override handling, and pull request reuse logic all live in `VectorPeak/VectorPeak`. Do not copy or recreate that logic in this skill.

## Preflight

Confirm GitHub CLI access before triggering:

```bash
gh auth status
gh workflow list --repo VectorPeak/VectorPeak
```

If `Update profile README` or `update-profile.yml` is not listed, stop and report that the remote workflow name or file path may have changed.

## Manual Trigger

Prefer GitHub CLI when available:

```bash
gh workflow run update-profile.yml --repo VectorPeak/VectorPeak --ref main
```

If using the GitHub web UI:

1. Open `VectorPeak/VectorPeak`.
2. Go to `Actions`.
3. Select `Update profile README`.
4. Choose `Run workflow`.
5. Select branch `main`.
6. Start the run.

## Verification

After triggering, verify the run instead of assuming success:

```bash
gh run list --repo VectorPeak/VectorPeak --workflow update-profile.yml --event workflow_dispatch --limit 5
```

Watch the selected run:

```bash
gh run watch <run-id> --repo VectorPeak/VectorPeak
gh run view <run-id> --repo VectorPeak/VectorPeak --log
```

Success means:

- The run finishes with `completed` / `success`.
- If generated README content changed, the workflow pushes `automation/update-profile-readme` and creates or updates a PR titled `chore: update profile README`.
- If generated content did not change, the workflow exits successfully without opening a noisy PR.

## Required Remote Configuration

The remote workflow is expected to own these settings:

- Permissions: `contents: write` and `pull-requests: write`
- Secret: `WORKFLOW_PUSH_PAT` for checkout, GitHub fact collection, branch push, and PR create/update
- Secret: `DASHSCOPE_API_KEY` for translation
- Translation model: `PROFILE_TRANSLATION_MODEL=qwen-plus`
- Schedule: `17 23 * * *`, which is 07:17 Beijing time

If a run fails because one of these is missing, report the missing remote configuration and do not patch README generation logic inside this skill.

## Failure Handling

- If `gh auth status` fails, ask the user to authenticate or switch to an account with access to `VectorPeak/VectorPeak`.
- If the workflow is missing, inspect `VectorPeak/VectorPeak` for a renamed workflow before changing this skill.
- If the run fails in generation, translation, branch push, or PR creation, fix the workflow or scripts in `VectorPeak/VectorPeak`.
- If the automation PR has conflicts, resolve the PR or automation branch in `VectorPeak/VectorPeak`; keep this skill unchanged unless the trigger procedure itself is outdated.
- If profile content is wrong, update the source data or generation logic in `VectorPeak/VectorPeak`, then trigger the workflow again.

## Boundaries

Do not add local README renderer scripts, sample profile data, GitHub fact collectors, or contribution taxonomy tables to this skill. Keep it as a durable trigger-and-verify guide so there is only one implementation of profile generation.

When the user asks to change profile content, first make the change in `VectorPeak/VectorPeak`, then use this skill to trigger and verify the remote workflow.
