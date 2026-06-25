---
name: pr-writer-vp
description: Manage the user's external GitHub PR workflow from project name to draft PR. Use when the user asks to fork/clone a project, find small bug-fix PR opportunities, launch multi-agent source review, draft a PR, update PR wording, align with contribution guidelines, collect evidence, or submit a draft PR after explicit confirmation.
---

# PR Writer

Use this skill for the user's open-source PR workflow. It covers project setup, small bug discovery, PR drafting, and confirmed draft submission. It complements GitHub publishing skills such as `github:yeet`; use those for final commit, push, and open-PR mechanics when needed.

## Operating Defaults

- Default mode is dry-run for PR submission. Do not open or update a PR unless the user explicitly says to submit, create, or update it.
- Default target directory is `E:\Github\<repo-name>` on Windows unless the user gives another path.
- Keep the fork's `main` synchronized with upstream `main`; do feature work on a separate `fix` branch or a non-conflicting `fix/<topic>` branch when the remote has namespace conflicts.
- Prefer small, reviewable bug fixes. For the user's default bug-hunting direction, target code changes of 0-20 lines.
- Do not include unrelated refactors, generated churn, or `CHANGELOG.md` unless the project explicitly requires it.
- Be honest about evidence: distinguish real runtime reproduction, UI reproduction, installed-package reproduction, unit reproduction, and inferred risk.

## Step 1 / Phase 1: Fork & Clone

When the user gives a project name or GitHub URL:

1. Resolve the upstream repository URL.
   - Prefer GitHub official repo search or the URL supplied by the user.
   - Record upstream URL and fork URL in the response.

2. Fork and clone.
   - Fork to the user's GitHub account when no suitable fork exists.
   - Clone the fork into `E:\Github\<repo-name>`.
   - Add `upstream` pointing to the original repository.

3. Synchronize `main`.
   - Fetch `upstream main`.
   - Fast-forward fork `main` to upstream when possible.
   - Do not force-push `main` unless the user explicitly approves and the reason is clear.

4. Create a work branch.
   - Use local branch `fix` if available and pushable.
   - If the fork already has `fix/...` refs that conflict with bare `fix`, use `fix/<short-topic>` or `codex/<short-topic>`.
   - Keep `main` unchanged locally except for synchronization.

5. Bootstrap only as much environment as needed.
   - Read README, CONTRIBUTING, package manager files, and project-specific agent instructions.
   - Install dependencies only when needed for targeted validation.
   - If install/build fails because of environment or network issues, capture exact commands and errors.

6. Leave the workspace ready for PR work.
   - Confirm current branch, upstream remote, fork remote, and whether `main` is synchronized.
   - Summarize the local path, active branch, upstream URL, fork URL, and any bootstrap blockers.
   - Treat this step as complete only when the user can continue from a clean, explainable repository state.

## Step 2 / Phase 2: Make A Draft

When the user asks to find a PR opportunity, prepare a PR candidate, or draft a PR:

1. Launch multi-agent review when available.
   - Ask agents to independently search for simple bug candidates in different areas.
   - Give the first direction by default: "Find likely bugs with fixes under 20 changed code lines."
   - Keep each candidate grounded in files, call chains, and a plausible user impact.

2. Filter candidates.
   - Prefer deterministic bugs, cross-platform edge cases, validation mistakes, null/undefined handling, path/URL encoding, casing, escaping, or simple boundary errors.
   - Avoid speculative style changes, broad refactors, large migrations, and issues requiring credentials or production services.
   - Estimate fix size, test size, risk, and evidence difficulty.

3. Present shortlist before editing.
   - Include file path, bug summary, why it matters, likely fix size, and validation approach.
   - Wait for the user to choose a candidate unless they explicitly delegated the choice.

4. Reproduce before fixing when feasible.
   - Prefer realistic product/runtime reproduction.
   - If full UI reproduction is not feasible, say why and use the closest honest reproduction.
   - Keep logs, commands, screenshots, or output snippets for PR Evidence.
   - For one-line or small frontend/backend fixes, create the smallest script, unit test, console snippet, or focused test that demonstrates the old behavior first.
   - For path, URL, upload, validation, escaping, or security-adjacent bugs, include concrete payloads and before/after behavior when safe.
   - When there is a nearby correct implementation in the same file, compare against it as evidence that the fix follows local intent.

5. Draft first, do not submit by default.
   - Prepare the proposed title, body, evidence, validation plan, and expected diff.
   - Ask for explicit confirmation before creating or updating a GitHub PR.

6. Launch multi-agent PR drafting review when available.
   - This phase must use multiple agents when the runtime supports subagents.
   - Assign at least one agent to inspect the target project's contribution and PR submission rules.
   - Assign at least one agent to inspect the actual diff, evidence, and validation claims.
   - Ask the contribution-rules agent to read project-specific sources such as `CONTRIBUTING.md`, PR templates, `.github/`, docs, and linked contribution pages.
   - Example targets:
     - Dify: `langgenius/dify`, contribution page `https://github.com/langgenius/dify?tab=contributing-ov-file`
     - OpenClaw: `openclaw/openclaw`, contribution page `https://github.com/openclaw/openclaw?tab=contributing-ov-file`
   - Merge the agents' findings into one PR draft; do not paste raw agent output unless the user asks.
   - If subagents are unavailable, explicitly say so and perform the contribution-rules and diff/evidence passes sequentially yourself.

7. Inspect the actual diff before writing.
   - Run `git status -sb`, `git diff --stat`, and the narrow relevant `git diff`.
   - Identify whether tests, docs, generated files, or unrelated files are included.
   - Never claim a file, test, screenshot, or log is included unless it is present in the diff or verified output.

8. Read project contribution rules when available.
   - Prefer repository files such as `CONTRIBUTING.md`, `AGENTS.md`, PR templates, and `.github/`.
   - If the user links contribution guidance, read the linked page before drafting.
   - Preserve project-specific required sections and disclosure requirements.
   - If contribution rules conflict with this skill's default body shape, follow the project's rules.
   - Note unusual submission constraints, such as required issue links, screenshots, test commands, sign-off text, CLA expectations, AI disclosure, or labels.
   - Treat the repository's PR template as the outer container, then fit this skill's required content into the closest matching sections.
   - If the template does not have matching headings, weave the required facts into the existing sections instead of appending a bulky second template.
   - Keep required project checklist items exactly when the template needs them, and add honest checked/unchecked states based on real validation.
   - Do not delete warning callouts, required issue-link language, CLA notes, documentation checkboxes, or AI-assistance disclosures from the target template.

9. Write a concise title.
   - Use the repository's title style when visible.
   - Make the title clear, descriptive, and specific enough to show the affected area and behavior.
   - Prefer `fix(scope): summary` for small bug fixes.
   - Do not add agent branding such as `[codex]` unless the user or repo explicitly wants it.

10. Write the body around facts.
   - Start with the user-visible or maintainer-visible problem.
   - Explain the root cause only as far as the diff supports it.
   - Describe the change in one short section.
   - Add realistic Evidence with commands, logs, screenshots, or reproduction steps.
   - Add Validation with exact commands and outcomes.
   - State limitations plainly, for example dependency failures, timed-out tests, or paths not exercised.
   - Follow the target project's contribution rules, but do not add a dedicated "project checklist" section unless the project template requires it.
   - Always account for these four facts, even when the target template uses different section names:
     - What problem was solved: concrete bug, vulnerability, failure mode, missing guard, or bad behavior.
     - What changed: exact implementation behavior, affected files, and intentionally unchanged behavior.
     - Evidence: reproduction script, focused test, command output, failing payload, log, screenshot, or a clearly labeled reason why direct reproduction was not possible.
     - Call chain / impact: entry point, affected function or module path, who can trigger it, and the practical impact.
   - Prefer creating a small local reproduction script for bugs, vulnerabilities, parser issues, path handling, URL handling, validation bypasses, and boundary cases.
   - For vulnerabilities, include a minimal payload and before/after behavior when safe to disclose under the project's norms.
   - Do not inflate the body with generic claims; every claim should be backed by a diff line, command, test, or observed output.
   - Follow the few-shot persuasion order from `references/pr-examples.md`: make the bug believable first, show the narrow change second, provide reproducible evidence third, then trace the call chain and non-affected paths.
   - When useful, include a short investigation note that explains why the old behavior is likely accidental, especially for copy/paste slips or confusing nearby abstractions.
   - State "what this does not change" for narrow fixes so maintainers can quickly judge blast radius.

11. Submit only after explicit instruction.
   - On an explicit request to submit a draft PR, commit, push, and create a draft PR.
   - On an explicit request to submit a ready PR, mark ready for review or create a non-draft PR.
   - Stage only intended files.
   - Use GitHub connector tools for PR metadata when `gh` lacks permission.

## Step 3 / Phase 3: Submit Or Update The PR

When the user explicitly asks to submit, create, or update a PR:

1. Re-check the branch, diff, and template.
   - Run `git status -sb`, `git diff --stat`, and `git diff --cached --stat` when staging has begun.
   - Re-read the repository PR template and current PR body if updating an existing PR.
   - Verify the body still matches the latest diff and validation output.

2. Commit, push, and submit intentionally.
   - Stage only intended files.
   - Use a clear commit message matching the repository style.
   - Create a draft PR by default unless the user explicitly asks for a ready PR.
   - Include the final PR URL and branch in the response.

3. After submission, report the exact state.
   - Include PR URL, branch, commit, changed files, validation commands, and CI/review risks.
   - If the PR body had to deviate from this skill's default body shape because of a project template, mention that briefly.

## PR Body Guidance

Keep evidence honest.

- Distinguish "real product/runtime reproduction" from "isolated unit/function reproduction".
- Do not imply UI reproduction when only a CLI, module import, or installed package reproduced the bug.
- Remove outdated claims after the diff changes, especially test coverage statements.

Update existing PRs carefully.

- Re-read current title/body and current diff before editing.
- If tests or files are removed, remove all PR-body references to them.
- Preserve required AI-assistance disclosure if the project asks for it.
- Use GitHub connector tools for PR metadata when `gh pr edit` lacks permission.

## Default Body Shape

Use this as the default concise bug-fix PR body. Do not add a separate project checklist section by default.

```markdown
<one-sentence summary>

## What Problem This Solves

<Explain the concrete bug; do not only say "fixes an issue".>
<Point to the failing function, path, endpoint, or entry point.>
<Explain why it affects users, developers, security, or diagnostics.>

## Change

<Describe the actual change in 1-3 bullets or short paragraphs.>
<Emphasize the narrow scope: only affects one fallback path, filename parser, edge case, etc.>

## Evidence

<Steps to reproduce the bug.>
<Expected behavior.>
<Actual behavior or failure output.>
<Provide backend logs for backend issues when available; docker-compose logs are especially useful.>
<Provide screenshots or videos when applicable.>
<Prefer before / after when possible.>
<For security/path/error-handling bugs, include the payload or exception.>

## Possible call chain / impact

<Trace from user entry point or module entry point to the affected function.>
<Explain which paths are affected and which paths are not affected.>

## Validation

- `<targeted command>`
- `<lint/type/compile command>`
- `<unit or focused test command>`
```

Omit or rename sections only when the repository template requires a different structure.

## References

- Read `references/pr-examples.md` when the user asks to derive PR templates from examples or wants a model for small bug-fix PR wording.

## Quality Checklist

- The title matches the actual diff.
- The body follows the target project's contribution and PR submission rules.
- The body does not mention removed tests or removed files.
- Evidence is reproducible or clearly labeled as observed locally.
- Validation includes failures and gaps, not just successes.
- The PR is scoped to the requested change and avoids unrelated refactors.
- The final summary to the user includes PR URL, branch, commit, changed files, and remaining CI or review risks.
