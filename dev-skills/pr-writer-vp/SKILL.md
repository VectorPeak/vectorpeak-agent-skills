---
name: pr-writer-vp
description: Manage the user's external GitHub PR workflow from project name to fork/clone, multi-agent bug hunting, evidence-driven draft PR writing, and explicit submit/update. Use when the user asks to fork or clone a GitHub project, find small fixable PR opportunities, launch multi-agent source review, prepare or update a PR draft, align with project PR templates and contribution rules, or submit a PR after explicit confirmation.
---

# PR Writer

Use this skill for external open-source PR work. The workflow has four phases:

1. Step1 Fork & Clone
2. Step2 Find PR Chances
3. Step3 Make A Draft
4. Step4 Submit/Update

## Non-Negotiables

- Always start multi-agent work when this skill runs. Launch at least two agents before phase-specific work; use more for Step2 and Step3 when the repository is large or the task is ambiguous.
- Treat submission as dry-run by default. Do not commit, push, create, mark ready, or update a PR unless the user explicitly asks for that action.
- Do not modify `references/` files as part of ordinary PR workflow.
- Default clone path is `D:\ZXY\Github\<repo-name>` on this Windows machine unless the user gives another path.
- Prefer small, reviewable bug fixes. The default target is a production-code fix of 0-20 changed lines.
- Do not include unrelated refactors, generated churn, broad formatting, or `CHANGELOG.md` unless the project explicitly requires it.
- Keep evidence honest. Distinguish runtime reproduction, UI reproduction, package reproduction, focused unit reproduction, inferred risk, and unavailable validation.
- Read `references/pr-examples.md` before drafting or revising PR prose. Treat it as the few-shot style guide for concise, evidence-driven bug-fix PRs.

## Multi-Agent Baseline

At the start of every skill run:

1. Launch a coordinator/main pass in the current thread.
2. Launch at least two independent agents with separate scopes.
3. Ask agents for concrete findings with file paths, evidence, risks, and next actions.
4. Merge findings yourself. Do not paste raw agent output unless the user asks.
5. If subagents are unavailable in the runtime, state that the skill requires them and continue only after explaining the limitation to the user.

Mechanical gate:

- Before taking phase-specific actions in Step1, Step2, Step3, or Step4, at least two independent agents must have been successfully started for that phase or for the overall skill run.
- Before completing Step2, Step3, or Step4, collect outputs from at least two agents and reconcile them in the main thread.
- If two agents cannot be started or cannot return useful output, pause the phase, tell the user the exact blocker, and ask whether to continue with a degraded single-agent pass.
- Do not describe ordinary sequential self-review as "multi-agent" work.

Recommended agent roles:

- Repo rules agent: contribution guide, PR template, issue requirements, CLA, tests, AI disclosure, submission norms.
- Bug-hunt agents: independent source review by area, language, package, or feature surface.
- Evidence agent: reproduction path, failing payload, focused test, command output, before/after proof.
- Diff/body agent: actual diff review, PR-body claim audit, validation gap check.

## Step1 Fork & Clone

Use this phase when the user gives a project name, GitHub URL, or asks to prepare a local PR workspace.

1. Resolve the upstream repository.
   - Prefer the user-provided URL or official GitHub repository search.
   - Record upstream URL and fork URL in the response.

2. Start multi-agent setup review.
   - Assign one agent to inspect repository contribution/setup files.
   - Assign one agent to inspect package manager, build, test, and project-specific agent instructions.

3. Fork and clone.
   - Fork to the user's GitHub account when no suitable fork exists.
   - Clone the fork into `D:\ZXY\Github\<repo-name>` on this machine unless another path is requested.
   - Add `upstream` pointing to the original repository.

4. Synchronize `main`.
   - Fetch `upstream main`.
   - Fast-forward fork `main` to upstream when possible.
   - Do not force-push `main` unless the user explicitly approves and the reason is clear.

5. Create a work branch.
   - Use local branch `fix` if available and pushable.
   - If `fix` conflicts with existing refs, use `fix/<short-topic>` or `codex/<short-topic>`.
   - Keep `main` unchanged except for synchronization.

6. Bootstrap only what is needed.
   - Read README, CONTRIBUTING, AGENTS, package manager files, and project-specific instructions.
   - Install dependencies only when needed for targeted validation.
   - If install/build fails, capture exact commands and errors.

### Local Environment Bootstrap On This Machine

After cloning into `D:\ZXY\Github\<repo-name>`, inspect project files before installing dependencies. Configure only the minimum environment needed for reproduction and targeted validation.

Check these files first when present: `README*`, `CONTRIBUTING*`, `AGENTS.md`, `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `environment.yml`, `conda-lock.yml`, `.python-version`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `Dockerfile`, `docker-compose.yml`, `compose.yaml`, `.devcontainer/`, and CI workflow files.

Python projects:
- Use this machine's Miniforge first: `D:\ZXY\Dev\Miniforge3\condabin\mamba.bat`; fall back to `D:\ZXY\Dev\Miniforge3\condabin\conda.bat`.
- Create one isolated conda environment per repository, named `prw-<repo-name>-py<version>`.
- Infer the Python version from project files or CI config. Default to Python 3.12 only when the project does not specify a version.
- Prefer `mamba env create -n <env> -f environment.yml` when an environment file exists.
- Otherwise create a minimal environment with `mamba create -y -n <env> python=<version>`, then install dependencies with the project's declared tooling.
- Prefer `conda run -n <env> ...` or `mamba run -n <env> ...` for non-interactive commands instead of relying on shell activation.
- Keep the environment isolated to the PR candidate; do not reuse a shared base environment.

Node.js projects:
- Use this machine's Node.js installation at `D:\ZXY\Dev\nodejs`.
- Select the package manager from `packageManager` or lockfiles:
  - `pnpm-lock.yaml` -> `pnpm install`
  - `yarn.lock` -> `yarn install`
  - `package-lock.json` -> `npm ci`
  - no lockfile -> `npm install`
- If the selected package manager is missing, use Corepack when appropriate or report the missing tool and exact next command needed.
- Run only focused validation scripts needed for the PR candidate, such as targeted tests, lint, typecheck, or the narrow package build.

Docker and WSL projects:
- Use Docker only when the project requires service dependencies or its README, compose files, Dockerfile, or devcontainer requires it.
- This machine uses WSL2 with Ubuntu-22.04. Windows path `D:\ZXY\Github` maps to `/mnt/d/ZXY/Github` in WSL.
- If Docker CLI exists but the daemon is unavailable, report that Docker Desktop is not running and start Docker Desktop before running compose commands when feasible.
- Prefer Docker Desktop with the WSL2 backend. Do not install a second Docker Engine inside WSL unless the project explicitly requires it.
- Use WSL for Linux-only shell scripts, Makefile/bash-heavy workflows, Docker workflows, or projects that depend on Linux path semantics. Otherwise stay in the Windows project directory.
- Capture exact compose commands, service names, ports, and startup errors when Docker validation is required.

7. Finish with repository state.
   - Report local path, active branch, upstream remote, fork remote, whether `main` is synchronized, and bootstrap blockers.
   - Treat Step1 as complete only when the user can continue from a clean, explainable repository state.

## Step2 Find PR Chances

Use this phase when the user asks to find PR opportunities, inspect a project for small fixes, or launch bug hunting.

1. Start multi-agent bug hunting. This phase must use multiple agents.
   - Give agents different source areas or bug templates so they do not duplicate work.
   - Default prompt direction: "Find likely real bugs with fixes under 20 changed production-code lines, especially compatibility regressions, API contract mismatches, parser edge cases, tool/function calling schema issues, serialization/deserialization bugs, path/URL handling, validation bypasses, and small runtime failures with reproducible impact."
   - Require each agent to return candidates with file path, call chain, suspected failure mode, user impact, fix sketch, evidence plan, and risk.
   - Do not edit code in Step2 unless the user explicitly asks to implement a chosen candidate immediately.

2. Search for fixable bugs, not cleanup.
   - Prefer deterministic runtime errors, broken branches, bad exception handling, null/undefined access, incorrect state transitions, and realistic failing code paths.
   - Prefer compatibility bugs: Windows/Linux path differences, Python/Node/browser version drift, encoding differences, dependency API changes, case sensitivity, newline/path separator behavior, and fallback handling.
   - Prefer API contract bugs: returned fields, parameter names, default values, status codes, optional/required semantics, and type expectations that differ from documented or caller behavior.
   - Prefer parser and serialization bugs: empty input, escaping, nested structures, partial parsing, malformed structured data, JSON/YAML/TOML/env/config conversion, date/time conversion, numeric conversion, and round-trip loss.
   - Prefer tool/function-calling bugs: JSON schema mismatches, required/optional field mistakes, tool result parsing failures, streaming/tool-call ordering bugs, and provider-specific quirks.
   - Prefer path, URL, validation, diagnostics, and security-adjacent bugs when the evidence is concrete.

3. Filter candidates aggressively.
   - Return a set of concrete, fixable bug candidates, not a single vague lead.
   - Default to candidates whose production-code fix is likely 0-20 changed lines.
   - Treat production-code fixes over 20 lines as exceptions requiring explicit justification.
   - Tests, reproduction scripts, and PR body evidence can exceed 20 lines when they improve maintainer confidence.
   - Reject speculative style changes, broad refactors, large migrations, typing-only improvements, naming fixes, theoretical robustness, and issues requiring unavailable credentials or production services.
   - Prefer candidates reproducible with a focused script, unit test, console snippet, small payload, or narrow command.
   - Do not promote a candidate into the shortlist unless it has either a plausible executable reproduction entry point, a minimal payload/snippet, an existing failing path, or a clearly stated smallest-evidence plan.

4. Present a shortlist before editing.
   - Include rank, candidate type, file path, bug summary, why it matters, likely production-code fix size, evidence plan, validation approach, and risk.
   - Use candidate types such as runtime bug, compatibility, API contract, parser, tool calling, serialization, validation, path handling, diagnostics, or security-adjacent.
   - Rank by maintainer value, confidence, smallness, reproducibility, and reviewability.
   - Recommend the best candidate if one is clearly strongest, but separate recommendation from action.
   - Wait for the user to choose unless they explicitly delegated the choice.

5. Stop at the phase boundary by default.
   - Do not modify files, commit, push, or draft a PR body in Step2 unless explicitly asked to continue.
   - If no good candidates are found, report search areas covered, rejected options, and why they failed the fixable-bug bar.

## Step3 Make A Draft

Use this phase when the user chooses a candidate or asks to prepare/update PR wording.

1. Start multi-agent draft work. This phase must use multiple agents.
   - Assign one agent to inspect contribution rules, PR templates, `.github/`, docs, issue-link requirements, CLA, AI disclosure, and submission norms.
   - Assign one agent to inspect the actual diff, changed files, evidence, tests, and claim accuracy.
   - Add an evidence/reproduction agent for parser, path, URL, validation, tool-calling, security-adjacent, and boundary bugs.
   - Require every agent responsible for PR body wording, evidence wording, or final PR text review to read the mandatory few-shot PRs in step 4 before making wording recommendations.
   - Merge findings into one draft. Do not paste raw agent output unless asked.

2. Reconfirm the selected bug before editing.
   - Restate the bug, affected files, expected fix size, reproduction plan, validation plan, and risk.
   - If deeper inspection invalidates the candidate, stop and explain the mismatch before changing code.

3. Read the project PR template and rules before drafting prose.
   - Read `.github/PULL_REQUEST_TEMPLATE*`, `CONTRIBUTING.md`, AGENTS files, relevant docs, and linked contribution guidance when available.
   - Use the target project's original PR template text and heading structure as the outer shell for the PR body.
   - Do not append a second generic template below the project template.
   - Do not replace the repository template headings with this skill's default headings when a project template exists.
   - Keep required warning callouts, issue-link language, checklists, CLA notes, docs checkboxes, screenshots requirements, and AI-assistance disclosures.

4. Read mandatory few-shot PR examples before writing or updating PR text.
   - The main agent must read these two PRs for every new draft and every major PR-body revision:
     - `https://github.com/AstrBotDevs/AstrBot/pull/8971`
     - `https://github.com/HKUDS/LightRAG/pull/3324`
   - Use `gh pr view 8971 --repo AstrBotDevs/AstrBot --json title,body,url` and
     `gh pr view 3324 --repo HKUDS/LightRAG --json title,body,url` when `gh` is available; otherwise browse the PR pages.
   - Treat them as mandatory few-shot structure examples for concise bug-fix PRs: opening summary, concrete problem, exact vulnerable/failing construction, narrow change, evidence, possible call chain / impact, testing, and limitations.
   - Do not copy repository-specific wording, screenshots, security claims, or validation commands. Adapt the structure to the target repository's PR template and the actual diff/evidence.
   - Also read `references/pr-examples.md` when local examples are useful or when the user asks for more PR wording models.
   - Follow the shared persuasion order: make the bug believable first, show the narrow change second, provide reproducible evidence third, then trace the call chain and non-affected paths.

5. Reproduce before fixing when feasible.
   - Prefer realistic product/runtime reproduction.
   - For small frontend/backend fixes, create the smallest script, unit test, console snippet, or focused test that demonstrates old behavior first.
   - For path, URL, upload, validation, escaping, parser, tool-calling, or security-adjacent bugs, include concrete payloads and before/after behavior when safe.
   - If direct reproduction is not possible, state why and identify the alternative evidence used.

6. Implement narrowly.
   - Keep the production-code fix near the 0-20 line target unless the chosen candidate genuinely requires more.
   - Use local helpers and existing project patterns.
   - Avoid unrelated refactors, broad cleanup, formatting churn, generated files, and undocumented behavior changes.

7. Inspect the actual diff before writing final body.
   - Run `git status -sb`, `git diff --stat`, and the narrow relevant `git diff`.
   - Identify included tests, docs, generated files, and unrelated files.
   - Never claim a file, test, screenshot, log, or command exists unless it is present in the diff or verified output.

8. Draft using the project template as the shell.
   - Fill the repository's template sections with the required facts instead of replacing the template.
   - Always account for these facts somewhere in the target template:
     - Problem solved: concrete bug, vulnerability, failure mode, missing guard, or bad behavior.
     - What changed: exact implementation behavior, affected files, and intentionally unchanged behavior.
     - Evidence: reproduction script, focused test, command output, failing payload, log, screenshot, or clearly labeled reason direct reproduction was not possible.
     - Call chain / impact: entry point, affected function or module path, who can trigger it, practical impact, and non-affected paths when known.
   - Use this call-chain shape when possible: `User action/API/CLI -> route/component -> handler/helper -> faulty expression/branch -> observed impact`.
   - If the template has no matching headings, weave the facts into the closest sections rather than adding a bulky second structure.
   - If the project has no template, use the default body shape below.

9. Write a concise title.
   - Match the repository's title style when visible.
   - Prefer `fix(scope): summary` for small bug fixes.
   - Name the affected area and behavior.
   - Do not add agent branding unless the user or repository explicitly wants it.

10. Treat Step3 as complete when the draft is reviewable.
   - Output intended title, PR body, changed files, evidence, validation commands, limitations, and remaining risks.
   - Ask for explicit confirmation before creating or updating a GitHub PR.

## Step4 Submit/Update

Use this phase only when the user explicitly asks to submit, create, open, mark ready, or update a PR.

1. Start multi-agent final review.
   - Assign one agent to re-check branch state, diff scope, staged files, and validation claims.
   - Assign one agent to re-check the PR template, current PR body if updating, contribution rules, and required disclosures.

2. Re-check state.
   - Run `git status -sb`, `git diff --stat`, and `git diff --cached --stat` when staging has begun.
   - Re-read the repository PR template.
   - If updating an existing PR, read the current title/body and current diff before editing.
   - Verify the body still matches latest diff and validation output.

3. Commit, push, and submit intentionally.
   - Stage only intended files.
   - Use a clear commit message matching repository style.
   - Create a draft PR by default unless the user explicitly asks for a ready PR.
   - Use GitHub connector tools for PR metadata when `gh` lacks permission.

4. Update existing PRs carefully.
   - Remove references to deleted tests, deleted files, or outdated validation.
   - Preserve required AI disclosure, issue-link language, warning callouts, and checklist items.
   - Mark ready for review only when explicitly requested.

5. Report exact final state.
   - Include PR URL, branch, commit, changed files, validation commands and outcomes, CI status if known, and remaining review risks.
   - If the body deviated from this skill's default shape because of the project template, mention that briefly.

## Default Body Shape

Use this only when the target repository has no PR template. If a project template exists, it is the outer shell.

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
<Provide backend logs for backend issues when available.>
<Provide screenshots or videos when applicable.>
<Prefer before/after when possible.>
<For security/path/error-handling bugs, include the payload or exception.>

## Possible call chain / impact

<Trace from user entry point or module entry point to the affected function.>
<Explain which paths are affected and which paths are not affected.>

## Validation

- `<targeted command>`
- `<lint/type/compile command>`
- `<unit or focused test command>`
```

## Quality Checklist

- Multi-agent work was started for the skill run and for the active phase.
- Step2 returns a set of concrete, fixable bug candidates before editing.
- Step2 candidates default to production-code fixes of 0-20 changed lines.
- Step3 uses the target repository PR template as the outer shell.
- Step3 includes problem solved, what changed, evidence, and call chain/impact.
- `references/pr-examples.md` was read before drafting or major body revision.
- The title matches the actual diff.
- The body follows target contribution and PR submission rules.
- Evidence is reproducible or clearly labeled with limitations.
- Validation includes failures and gaps, not only successes.
- The PR is scoped to the requested change and avoids unrelated churn.
