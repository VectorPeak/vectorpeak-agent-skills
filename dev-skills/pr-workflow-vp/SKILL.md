---
name: pr-writer-vp
description: Manage the user's external GitHub PR workflow from project name to fork/clone, multi-agent bug hunting, PR-value validation, formal PR creation, reviewer feedback, and detailed PR comment section expansion. Use when the user asks to fork or clone a GitHub project, find small fixable PR opportunities, launch multi-agent source review, evaluate whether a candidate is real and PR-worthy, create or update a formal PR, expand a specified section in the first PR comment, or align with project PR templates and contribution rules.
---

# PR Writer

Use this skill for external open-source PR work. The workflow has six phases:

1. Step1 Fork & Clone
2. Step2 Find PR Chances
3. Step3 Validate PR Value
4. Step4 Implement & Create Formal PR
5. Step5 Address Reviewer Feedback
6. Step6 Refine PR Comment Section

## Non-Negotiables

- Always start multi-agent work when this skill runs. Launch at least two agents before phase-specific work; use more for Step2, Step3, Step4, Step5, and Step6 when the repository is large, the task is ambiguous, reviewer feedback touches behavior-sensitive code, or a PR comment section needs stronger evidence.
- Treat submission as dry-run by default outside Step4 and Step5. Do not commit, push, create, mark ready, or update a PR unless the user explicitly asks for that action. When the user invokes Step4 by asking to create or submit a PR, treat that as permission to commit, push, and create a formal ready-for-review PR by default, unless the user explicitly asks for a draft PR.
- Do not modify `references/` files as part of ordinary PR workflow.
- Default clone path is `D:\ZXY\Github\<repo-name>` on this Windows machine unless the user gives another path.
- Prefer small, reviewable bug fixes. The default target is a production-code fix of 0-20 changed lines.
- Do not include unrelated refactors, generated churn, broad formatting, or `CHANGELOG.md` unless the project explicitly requires it.
- Keep evidence honest. Distinguish runtime reproduction, UI reproduction, package reproduction, focused unit reproduction, inferred risk, and unavailable validation.
- For every commit created while using this skill, explicitly include the relevant Codex/GitHub bot as a `Co-authored-by` trailer when a valid bot noreply identity can be verified. Prefer the active reviewer bot identity when responding to bot review feedback, for example `Co-authored-by: chatgpt-codex-connector[bot] <199175422+chatgpt-codex-connector[bot]@users.noreply.github.com>`. Do not guess bot IDs or emails; verify them with GitHub user metadata such as `gh api users/<bot-login>` before committing.
- When a commit implements a substantive human reviewer's requested change, best-effort include that reviewer as an additional `Co-authored-by` trailer using a valid GitHub noreply or otherwise verified public email. Never guess private emails; skip the human trailer if the identity cannot be verified or if the repository's norms discourage human co-authorship.
- Read `references/pr-examples.md` before drafting or revising PR prose. Treat it as the few-shot style guide for concise, evidence-driven bug-fix PRs.

## Multi-Agent Baseline

At the start of every skill run:

1. Launch a coordinator/main pass in the current thread.
2. Launch at least two independent agents with separate scopes.
3. Ask agents for concrete findings with file paths, evidence, risks, and next actions.
4. Merge findings yourself. Do not paste raw agent output unless the user asks.
5. If subagents are unavailable in the runtime, state that the skill requires them and continue only after explaining the limitation to the user.

Mechanical gate:

- Before taking phase-specific actions in Step1, Step2, Step3, Step4, Step5, or Step6, at least two independent agents must have been successfully started for that phase or for the overall skill run.
- Before completing Step2, Step3, Step4, Step5, or Step6, collect outputs from at least two agents and reconcile them in the main thread.
- If two agents cannot be started or cannot return useful output, pause the phase, tell the user the exact blocker, and ask whether to continue with a degraded single-agent pass.
- Do not describe ordinary sequential self-review as "multi-agent" work.

Recommended agent roles:

- Repo rules agent: contribution guide, PR template, issue requirements, CLA, tests, AI disclosure, submission norms.
- Bug-hunt agents: independent source review by area, language, package, or feature surface.
- Evidence agent: reproduction path, failing payload, focused test, command output, before/after proof.
- Diff/body agent: actual diff review, PR-body claim audit, validation gap check.
- Reviewer-feedback agent: all review threads, requested changes, maintainer intent, comment-to-diff traceability, and reply wording.
- CI agent: repository CI workflow discovery, local full-CI command selection, remote check monitoring, and failure triage.
- Comment-section agent: expands a user-specified section of the first PR comment with concrete problem framing, narrow changes, reproducible evidence, and call-chain impact while preserving the surrounding PR body.

### Mandatory Patch-Generation Review Lenses

Whenever agents are asked to generate, review, or integrate PR patch code, their prompts and final findings must explicitly consider these five lenses. The main agent must reconcile the answers before accepting a patch as reviewable:

- Correctness: Is the code logic right? Does the patch actually fix the bug, and can it introduce a new bug?
- Ownership boundary: Is the change placed in the correct module/file/package? Does it cross a boundary that should be owned by another layer?
- Completeness: Did the review cover the whole decision surface, not just the changed diff lines? Include callers, callees, sibling modules, fallback paths, and adjacent feature variants.
- Best-fix judgment: Is this the best fix, not merely a workable fix? Prefer the smallest durable fix that removes the real failure mode, follows established local patterns, and avoids whack-a-mole patches.
- Risk awareness: Does the patch touch compatibility-sensitive behavior such as configuration, authentication, routing, rollback, persistence, parsing, platform paths, or provider behavior? If yes, include a concrete risk assessment and targeted validation plan.

Patch-producing agents must report their conclusion for each lens using the labels `Correctness`, `Ownership`, `Completeness`, `Best fix`, and `Risk`. If a lens is not applicable, they must say why. A patch is not ready for commit, PR body drafting, or submission until the main agent has checked these five lenses against the actual diff.

### Mandatory PR Evidence Review Lenses

When drafting a PR, updating a PR body, or addressing reviewer-requested changes, agents must also consider these evidence lenses. These lenses answer whether the PR proves the change, not just whether the patch looks plausible:

- Behavior proof: Is there a screenshot, screen recording, log, terminal output, before/after trace, or live/API result showing that the change actually works? Use the smallest proof that demonstrates the user-visible or runtime behavior.
- Media proof bonus: If the change is visual, UI, interactive, terminal/TUI, browser, desktop, or workflow-facing, prefer video or screen recording evidence when feasible. Treat media proof as extra reviewer confidence, not a substitute for tests.
- Test/CI proof: Are relevant tests added or updated? Is CI green, or are any failing/skipped checks explained? If the change cannot be covered by tests, explain why and provide the closest focused validation.
- Dependency contract proof: If the patch changes or relies on an external dependency, provider, SDK, API, protocol, CLI, or documented behavior, read the upstream documentation, source, schema, changelog, or captured response and cite the exact contract being relied on.
- Sibling surface proof: If one path/channel/surface was changed, check sibling paths and explain whether they are affected. Examples: changed route A, check B/C routes; changed CLI path, check TUI/ACP/desktop equivalents; changed one provider, check similar providers.

Evidence agents and diff/body agents must report these labels as `Behavior proof`, `Media proof`, `Test/CI proof`, `Dependency contract`, and `Sibling surfaces`. If a lens is not applicable, they must say why. The main agent must include the relevant evidence in the PR body or reviewer reply, and must not claim evidence that was not actually gathered.

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
  - Node executable: `D:\ZXY\Dev\nodejs\node.exe` (currently observed as Node.js `v24.15.0`).
  - npm executable: `D:\ZXY\Dev\nodejs\npm.cmd` (currently observed as npm `11.12.1`).
  - When a repository's CI requires a different major version (for example Node 22.x), report the mismatch before treating local build results as CI-equivalent evidence.
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

## Step3 Validate PR Value

Use this phase when the user points to a specific candidate and asks whether it has PR value, whether the bug is real, whether the current fix idea uses the right abstraction, or what the best next move is.

Treat Step3 as the PR candidate diligence gate, not as an automatic prelude to implementation. Its job is to decide whether the candidate deserves Step4 at all: confirm the bug is real, the proposed fix matches the right abstraction, the evidence is strong enough for maintainers, and the review risk is acceptable.

1. Start multi-agent candidate validation. This phase must use multiple agents.
   - Assign one agent to inspect code semantics, call chains, construction sites, ownership boundaries, sibling surfaces, and whether the suspected failure is actually reachable.
   - Assign one agent to inspect duplicate PRs/issues, maintainer comments, project history, docs, API contracts, and whether maintainers have already rejected the same idea.
   - Manually start two independent skeptic/counterargument agents to argue against the current candidate. They must work from separate prompts or scopes rather than sharing one generic objection pass.
   - Require both skeptic agents to test whether the behavior could be intentional, an accepted abstraction boundary, diagnostic-only polish, already occupied by a better PR, too broad for a small fix, or unlikely to meet the maintainer review bar.
   - Add an evidence/reproduction agent for parser, path, URL, validation, HTTP status, serialization, security-adjacent, platform, or compatibility candidates.
   - Require each agent to answer the same decision questions: Is it real? Is it PR-worthy? Is it the right abstraction? Is there a narrower or better fix? What is the risk? What should we do next?
   - Require each skeptic agent to provide the strongest no-go case, the best alternative interpretation of the observed behavior, an intentional-abstraction risk score, and a recommendation to proceed, downgrade, or reject.
   - Treat Step3 as incomplete until at least two independent agents return useful findings that the main agent reconciles.
   - Treat Step3 as incomplete until both skeptic/counterargument findings have been explicitly reconciled against the supporting findings and executable evidence.
   - If the two agents disagree, do not average their conclusions. Resolve the disagreement by checking the underlying code path, maintainer history, or executable evidence.

2. Reconfirm the candidate before any editing.
   - Restate the suspected bug, affected files, proposed production-code fix size, reproduction plan, validation plan, and risk.
   - Search for duplicate issues and PRs before recommending implementation.
   - Inspect the actual production construction points and caller behavior instead of relying on enum names, function names, or surface-level status-code symmetry.
   - If deeper inspection invalidates the candidate, stop and explain the mismatch before changing code.

3. Evaluate abstraction quality explicitly.
   - Identify whether the proposed fix addresses the real failure mode or only the visible symptom.
   - Check for overloaded enum variants, shared helper behavior, retry semantics, provider/API contracts, state-machine signals, and cross-surface mappings.
   - Compare at least two options when relevant: minimal patch, narrower patch, split abstraction, metadata/classification change, documentation-only clarification, or no PR.
   - Prefer the smallest durable fix that matches maintainers' existing model; reject one-line fixes when the bug is actually an abstraction boundary problem.

4. Produce a recommendation before editing.
   - Output a clear decision: proceed to Step4, reject as not PR-worthy, redesign into a larger issue, or keep as a lower-priority candidate.
   - Include a compact decision matrix with these fields: `Reality`, `PR value`, `Abstraction fit`, `Skeptic view`, `Intentional-abstraction risk`, `Duplicate risk`, `Fix size`, `Evidence strength`, `Maintainer risk`, and `Recommendation`.
   - Include file paths, call chain, concrete evidence, duplicate/history findings, likely production-code fix size, test plan, and risks.
   - If the recommendation is `proceed to Step4`, explain why the candidate clears the diligence gate and what exact implementation path should be used.
   - If the recommendation is not to proceed, explain the strongest blocking reason, such as weak reality proof, poor abstraction fit, duplicate maintainer rejection, oversized fix scope, or unacceptable review risk.
   - Do not modify files, commit, push, or draft a PR body in Step3 unless the user explicitly asks to continue into Step4.

## Step4 Implement & Create Formal PR

Use this phase only when the user explicitly asks to implement, create, submit, open, or update a PR for a chosen candidate. This phase combines the old draft and submit phases: implement the narrow fix, validate it, write the PR body, commit, push, and create a formal ready-for-review PR by default. Create a draft PR only when the user explicitly asks for a draft.

1. Start multi-agent implementation and final review. This phase must use multiple agents.
   - Assign one agent to inspect contribution rules, PR templates, `.github/`, docs, issue-link requirements, CLA, AI disclosure, and submission norms.
   - Assign one agent to inspect the actual diff, changed files, evidence, tests, validation claims, and whether the patch still matches the selected candidate.
   - Add an evidence/reproduction agent for parser, path, URL, validation, HTTP status, tool-calling, security-adjacent, platform, or boundary bugs.
   - Require every patch-producing or diff-reviewing agent to apply the Mandatory Patch-Generation Review Lenses.
   - Require every PR-body or evidence-reviewing agent to apply the Mandatory PR Evidence Review Lenses.

2. Reconfirm the selected bug before editing.
   - Restate the bug, affected files, expected fix size, reproduction plan, validation plan, risk, and why Step3/Step2 evidence supports creating a PR.
   - Confirm the chosen abstraction is still correct after reading callers, callees, sibling surfaces, fallback paths, and project history.
   - If deeper inspection invalidates the candidate, stop and explain the mismatch before changing code or creating a PR.

3. Read the project PR template, rules, and examples.
   - Read `.github/PULL_REQUEST_TEMPLATE*`, `CONTRIBUTING.md`, AGENTS files, relevant docs, and linked contribution guidance when available.
   - Use the target project's original PR template text and heading structure as the outer shell for the PR body.
   - Do not append a second generic template below the project template.
   - Do not replace the repository template headings with this skill's default headings when a project template exists.
   - Keep required warning callouts, issue-link language, checklists, CLA notes, docs checkboxes, screenshots requirements, and AI-assistance disclosures.
   - Read mandatory few-shot PR examples before writing or updating PR text:
     - `https://github.com/AstrBotDevs/AstrBot/pull/8971`
     - `https://github.com/HKUDS/LightRAG/pull/3324`
   - Use `gh pr view 8971 --repo AstrBotDevs/AstrBot --json title,body,url` and `gh pr view 3324 --repo HKUDS/LightRAG --json title,body,url` when `gh` is available; otherwise browse the PR pages.
   - Also read `references/pr-examples.md` when local examples are useful or when the user asks for more PR wording models.

4. Reproduce before fixing when feasible.
   - Prefer realistic product/runtime reproduction.
   - For small frontend/backend fixes, create the smallest script, unit test, console snippet, or focused test that demonstrates old behavior first.
   - For path, URL, upload, validation, escaping, parser, tool-calling, or security-adjacent bugs, include concrete payloads and before/after behavior when safe.
   - If direct reproduction is not possible, state why and identify the alternative evidence used.
   - Apply the Mandatory PR Evidence Review Lenses while deciding what proof is needed for the PR and for any reviewer-requested change.

5. Implement narrowly.
   - Keep the production-code fix near the 0-20 line target unless the chosen candidate genuinely requires more.
   - Use local helpers and existing project patterns.
   - Avoid unrelated refactors, broad cleanup, formatting churn, generated files, and undocumented behavior changes.
   - Before finalizing the implementation, apply the Mandatory Patch-Generation Review Lenses to the actual patch and revise the code if the lenses reveal a correctness, boundary, completeness, best-fix, or risk gap.

6. Validate and inspect the actual diff before PR creation.
   - Run focused tests first, then the closest practical local CI subset for the touched area.
   - Run `git status -sb`, `git diff --stat`, `git diff --cached --stat` when staging has begun, and the narrow relevant `git diff`.
   - Identify included tests, docs, generated files, and unrelated files.
   - Never claim a file, test, screenshot, log, or command exists unless it is present in the diff or verified output.
   - If validation fails or is unavailable, record exact commands, errors, skipped checks, platform differences, and remaining risk.

7. Draft the PR body using the project template as the shell.
   - Fill the repository's template sections with the required facts instead of replacing the template.
   - Always account for these facts somewhere in the target template:
   - Problem solved: concrete bug, vulnerability, failure mode, missing guard, or bad behavior.
   - What changed: exact implementation behavior, affected files, and intentionally unchanged behavior.
   - Evidence: reproduction script, focused test, command output, failing payload, log, screenshot, or clearly labeled reason direct reproduction was not possible.
   - Call chain / impact: entry point, affected function or module path, who can trigger it, practical impact, and non-affected paths when known.
   - Evidence lenses: include behavior proof, media proof when useful, test/CI proof, dependency contract proof when relevant, and sibling-surface reasoning when the change could affect adjacent paths.
   - Use this call-chain shape when possible: `User action/API/CLI -> route/component -> handler/helper -> faulty expression/branch -> observed impact`.
   - If the template has no matching headings, weave the facts into the closest sections rather than adding a bulky second structure.
   - If the project has no template, use the default body shape below.

8. Write a concise title.
   - Match the repository's title style when visible.
   - Prefer `fix(scope): summary` for small bug fixes.
   - Name the affected area and behavior.
   - Do not add agent branding unless the user or repository explicitly wants it.

9. Commit, push, and create/update the PR intentionally.
   - Stage only intended files.
   - Use a clear commit message matching repository style.
   - Include the verified Codex/GitHub bot `Co-authored-by` trailer in the commit message, following the Non-Negotiables co-author rule.
   - Push to the intended PR head branch.
   - Create a formal ready-for-review PR by default. Create a draft PR only when the user explicitly asks for a draft.
   - If updating an existing PR, remove references to deleted tests, deleted files, or outdated validation and preserve required template content.
   - Use `gh` for PR creation/update when available; use other GitHub capabilities only when `gh` lacks permission or cannot perform the required action.

10. Report exact final state.
   - Include PR URL, branch, commit, changed files, validation commands and outcomes, CI status if known, and remaining review risks.
   - If the body deviated from this skill's default shape because of the project template, mention that briefly.

## Step5 Address Reviewer Feedback

Use this phase when the user gives an existing PR link and asks to address reviewer feedback, fix requested changes, respond to review comments, or request re-review. A PR link alone is not enough; the user must ask to act on the review feedback. When the user asks for this phase, treat it as permission to make the minimal necessary code/test/doc changes, commit, push to the PR branch, update PR prose when needed, and reply to review comments for that PR, unless the user explicitly limits the scope.

1. Start multi-agent reviewer-response work. This phase must use multiple agents.
   - Assign one agent to collect and classify all reviewer feedback: inline comments, review summaries, unresolved conversations, bot comments, maintainer comments, and CI failures.
   - Assign one agent to inspect the code ownership boundary and propose the smallest correct fix for each actionable reviewer concern.
   - Assign one agent to inspect tests, full CI commands, GitHub Actions workflow requirements, and project contribution rules.
   - When UI, TUI, browser, desktop, provider/API, platform, or workflow behavior is involved, add an evidence agent to identify the right before/after proof.
   - Require every patch-producing agent to apply the Mandatory Patch-Generation Review Lenses.
   - Require every reviewer-reply or PR-body agent to apply the Mandatory PR Evidence Review Lenses.
   - Merge findings into one action plan before editing. Do not paste raw agent output unless the user asks.

2. Read the PR and reviewer context before editing.
   - Use `gh pr view <number> --repo <owner>/<repo> --comments --json ...` and the pull request review-comments API/CLI to collect inline comments, review summaries, requested-change state, commit IDs, file paths, and conversation URLs.
   - Read the current PR title/body, current diff, branch/head repo, base branch, status checks, and latest commit.
   - Read contribution rules, PR template, AGENTS files, CI workflows, and package/test scripts if not already loaded in the current run.
   - Build a short reviewer-feedback map: comment URL, reviewer, severity/request, affected file/line, required change, planned response, and whether code, test, docs, or explanation is needed.

3. Decide actionability and scope.
   - Separate actionable reviewer requests from questions, suggestions, nits, stale comments, bot noise, and already-fixed feedback.
   - If a reviewer suggestion is wrong or conflicts with project behavior, verify with code/tests and plan a polite evidence-backed reply instead of blindly changing code.
   - If feedback reveals a larger design issue, prefer the smallest durable fix that satisfies the reviewer intent; ask the user before broad refactors, force-push rewrites, or scope expansion beyond the PR's original purpose.
   - Do not add unrelated cleanup while addressing review. Every changed file must map to reviewer feedback, failing CI, or required evidence.

4. Implement reviewer-requested changes narrowly.
   - Edit only the files needed to resolve the review concerns.
   - Add or update tests for every behavior change when feasible; if not feasible, explain why and provide the closest focused validation.
   - Apply the Mandatory Patch-Generation Review Lenses against the actual diff before committing.
   - Re-read the changed diff after edits and verify every reviewer concern has either a code/test/doc change or a planned written reply.

5. Run complete local CI before pushing.
   - Infer the repository's full local CI from `package.json`, lockfiles, `pyproject.toml`, `tox.ini`, `noxfile.py`, `Makefile`, `.github/workflows/*`, `CONTRIBUTING*`, and prior PR validation.
   - Prefer the closest local equivalent of required GitHub Actions: format check, lint, typecheck, unit tests, integration tests, build, bundle/package, and `git diff --check`.
   - If the repository defines a single preflight/ci command, run it unless it requires unavailable credentials or production services.
   - If full CI is too expensive, unavailable, platform-incompatible, or requires secrets, run the maximum feasible local subset, record exact blockers, and do not describe it as full CI.
   - Capture exact commands and outcomes, including warnings, skipped tests, flaky retries, and environmental differences such as Node/Python/OS version mismatches.

6. Commit, push, and monitor remote CI.
   - Run `git status -sb`, `git diff --stat`, and relevant diffs before staging.
   - Stage only intended files and commit with a clear message matching project style.
   - Always include the verified Codex/GitHub bot `Co-authored-by` trailer for commits produced while addressing review feedback, following the Non-Negotiables co-author rule. When the actionable feedback came from a bot review, use that bot identity if it can be verified.
   - When changes are made in response to a human GitHub reviewer's substantive suggestion, best-effort also include that real reviewer as a commit co-author using a valid `Co-authored-by: Name <email>` trailer. Prefer a GitHub-verified or noreply email when it can be discovered from public GitHub context; do not guess private emails, and skip the human trailer when the reviewer identity/email cannot be validated or the repository's norms discourage co-authorship.
   - Push to the PR head branch, not a different branch.
   - After pushing, monitor GitHub status checks until they pass, fail, skip, or require external authorization. Use `gh pr checks --watch` or equivalent when available.
   - If CI fails because of the new changes, inspect logs, fix, rerun the relevant local validation, commit, push, and monitor again.
   - If CI failure is unrelated, flaky, skipped, or blocked by missing permissions/secrets, record evidence and explain it honestly in the reviewer reply and final report.

7. Update PR prose when the reviewer-facing facts changed.
   - Update the PR body only when the change altered scope, tests, evidence, limitations, screenshots, risk, or CI status.
   - Preserve the project PR template, required checklists, issue-link language, CLA notes, screenshots requirements, and AI-assistance disclosures.
   - Remove stale validation claims or outdated limitations.

8. Reply to reviewers and request re-review.
   - Reply directly on each relevant inline thread when possible, linking the fix commit or naming the exact change and validation.
   - Post one concise top-level PR comment summarizing the reviewer feedback addressed, changed files/behavior, full local CI results, remote CI status, and any remaining limitations.
   - Politely at-mention the human reviewer(s) who requested changes or asked for follow-up, and ask them to re-review only after local validation is complete and remote CI has reached a clear state.
   - Do not at-mention bots unless the project explicitly uses bot mentions to trigger review.
   - Never include API keys, secrets, private logs, or local credential paths in reviewer replies. Use placeholders or describe private live-validation credentials without disclosing them.

9. Report exact final state.
   - Include PR URL, branch, latest commit, review threads replied to, PR body changes, local CI commands and outcomes, remote CI status, reviewer(s) mentioned, and remaining review risks.
   - If the phase was degraded because subagents, credentials, full CI, or remote checks were unavailable, state that clearly and explain the best next action.

## Step6 Refine PR Comment Section

Use this phase when the user gives an existing PR and asks to refine, expand, strengthen, polish, or rewrite a specified section of the PR's first/top-level comment. The user may name the section by heading, visible text, screenshot, or description. This phase is for comment prose and evidence packaging; it does not change code unless the user explicitly asks for a patch.

1. Start multi-agent comment-section work. This phase must use multiple agents.
   - Assign one agent to inspect the current PR first comment/body, repository template, contribution rules, and any required headings or checkboxes.
   - Assign one agent to inspect the current PR diff, changed files, validation output, screenshots/logs, and claim accuracy.
   - Add an evidence agent when the requested section concerns path traversal, URL handling, upload handling, validation, parsing, security-adjacent behavior, terminal/TUI output, browser/UI behavior, or any before/after proof.
   - Require agents to apply the Mandatory PR Evidence Review Lenses before recommending wording.
   - Merge findings into one replacement section. Do not paste raw agent output unless the user asks.

2. Locate the exact section to refine before writing.
   - Read the current first PR comment/body with `gh pr view <number> --repo <owner>/<repo> --json body,title,url` or the equivalent available GitHub tooling.
   - Identify the user-specified section boundaries by heading and neighboring headings.
   - If the section is ambiguous, ask the user for the exact heading or paste only when no reasonable section boundary can be inferred.
   - Preserve all unrelated sections, issue-link language, checklist items, screenshots, warning callouts, and required template text.

3. Read the PR context and evidence before editing prose.
   - Inspect the current PR diff and changed files enough to make every claim traceable.
   - Read validation commands, CI results, reproduction scripts, screenshots, videos, logs, or uploaded images that the user wants included.
   - If the user provides screenshots as few-shot examples, use them as style and structure references, not as evidence for the current PR unless they are from the current PR.
   - Do not invent screenshots, command output, paths, CVEs, CWEs, security labels, affected users, or exploitability claims.

4. Expand the target section using this required inner structure unless the user requests another shape:

   - Keep the user-specified target section as the outer heading. If the user asks to refine `## Why it's needed`, do not replace that heading with Step6's four headings. Instead, preserve `## Why it's needed` and nest the four required Step6 subsections inside it.
   - The four Step6 subsections must be explicit Markdown headings, not merely concepts woven into prose, unless the user explicitly asks for prose-only output.
   - If the target repository template or existing PR body already mentions one of these concepts elsewhere, still include the four Step6 subsections inside the requested target section when the user asks to Step6-refine that section.
   - For a `## Why it's needed` refinement, use this nesting shape:

```markdown
## Why it's needed

### What Problem This Solves

...

### Changes

...

### Evidence

...

### Possible call chain / impact

...
```

```markdown
## What Problem This Solves

<Explain the concrete bug first. Name the failing function, route, endpoint, parser, helper, or path.>
<Show the dangerous expression, missing guard, malformed input, bad fallback, or protocol mismatch.>
<Explain why the input is attacker-controlled, user-controlled, provider-controlled, or realistically triggerable.>
<For security-adjacent issues, state the control point and practical boundary impact without overstating exploitation.>

## Changes

<Describe the narrow fix in 1-3 short paragraphs or bullets.>
<Mention intentionally unchanged behavior, nearby flows, auth, parsing, indexing, installation, or validation paths when relevant.>

## Evidence

<Show a concrete payload, reproduction, before/after path, console output, test, screenshot, log, or focused command.>
<Prefer before/after evidence: old vulnerable/failing construction, fixed construction, and the verdict.>
<For path/upload issues, include both POSIX-style and Windows-style separator payloads when applicable.>
<For validation/API/parser issues, include the exact request or malformed value and the resulting status/error behavior.>

## Possible call chain / impact

<Trace from user action/API/CLI to route/component/helper to the faulty branch or expression.>
<State what this PR changes and what it does not change.>
<List sibling surfaces checked or explain why sibling surfaces are not affected.>
```

5. Follow the section style shown by the few-shot examples.
   - Start with a one-sentence summary when the surrounding PR comment section needs it.
   - Use crisp headings: `What Problem This Solves`, `Changes`, `Evidence`, and `Possible call chain / impact`.
   - Use fenced code blocks for payloads, path constructions, request traces, and call chains.
   - In the `Changes` subsection, when the main production-code diff is under 20 changed lines excluding tests, prefer showing a compact fenced `diff` block with the core production change first, then follow it with one short paragraph explaining what changed and what intentionally stayed unchanged. Do not include long test diffs or unrelated context in this mini-diff.
   - For path traversal or upload filename issues, explain raw user-controlled filename construction, payloads such as `../../../evil.zip` and `..\\..\\..\\evil.zip`, before/after resolved paths, basename normalization, fallback filename behavior, and unaffected parsing/auth/install behavior.
   - For screenshots, include them only if they already exist in the PR comment/body or the user supplied current evidence to upload/reference; otherwise describe the console evidence textually.
   - Keep security language proportionate: "path traversal risk", "can resolve outside the intended directory", or "weakens the path boundary" are usually safer than broad compromise claims unless the evidence proves more.

6. Update or draft the PR first comment carefully.
   - If the user asked to update the live PR, replace only the specified section in the first comment/body and preserve everything else.
   - If the user asked for a draft only, output the replacement section and clearly label it as not yet applied.
   - If the requested section already contains useful evidence, retain it unless it is stale, false, duplicated, or contradicted by the current diff.
   - Remove stale validation claims, old branch names, deleted files, outdated screenshots, or claims no longer supported by the PR.

7. Validate the comment update.
   - Re-read the updated first PR comment/body after editing.
   - Verify the required four inner headings are present in the target section.
   - Verify every code path, filename, payload, command, screenshot, and validation claim is supported by the current PR diff or provided evidence.
   - Report the PR URL, updated section heading, whether the live PR comment was changed, evidence included, and any limitations.

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
- Step3 validates whether a candidate is real, PR-worthy, and based on the right abstraction before editing.
- Step3 manually starts two independent skeptic/counterargument agents that argue against the current candidate and test whether the behavior may be intentional, diagnostic-only, already occupied, too broad, or below the maintainer review bar.
- Step3 explicitly reconciles both skeptic views before recommending Step4, downgrading, or rejecting the candidate.
- Step3 includes multi-agent evidence on call chains, duplicate/history risk, likely fix size, test plan, and recommendation.
- Step4 uses the target repository PR template as the outer shell.
- Step4 includes problem solved, what changed, evidence, and call chain/impact.
- Step4 commits, pushes, and creates a formal ready-for-review PR when the user explicitly asks to create or submit the PR.
- Step5 collects reviewer comments, review summaries, unresolved threads, current diff, and CI status before editing.
- Step5 maps every code/test/doc change to reviewer feedback, failing CI, or required evidence.
- Step5 runs full local CI when feasible, then monitors remote CI after push.
- Step5 replies to reviewer threads and politely at-mentions human reviewers only after validation reaches a clear state.
- Commits produced by this skill include a verified Codex/GitHub bot `Co-authored-by` trailer when a valid bot noreply identity is available.
- Step5 best-effort adds a real human reviewer as an additional `Co-authored-by` when their substantive review suggestion shaped the committed change, while avoiding guessed emails and fake co-authorship.
- Step6 identifies the exact first-comment section boundary before editing.
- Step6 preserves unrelated PR body/template content while expanding only the requested section.
- Step6 includes `What Problem This Solves`, `Changes`, `Evidence`, and `Possible call chain / impact` as explicit nested headings inside the requested target section unless the user requests another structure.
- Step6 verifies that every evidence and impact claim is backed by the current PR diff, validation output, or user-provided current evidence.
- `references/pr-examples.md` was read before drafting or major body revision.
- The title matches the actual diff.
- The body follows target contribution and PR submission rules.
- Evidence is reproducible or clearly labeled with limitations.
- Validation includes failures and gaps, not only successes.
- The PR is scoped to the requested change and avoids unrelated churn.
- Patch-producing agents explicitly covered correctness, ownership boundary, completeness, best-fix judgment, and risk awareness before the patch was accepted.
- Drafting and reviewer-response work explicitly covered behavior proof, media proof where useful, test/CI proof, dependency contract proof, and sibling-surface proof before the PR body or reviewer reply was finalized.
