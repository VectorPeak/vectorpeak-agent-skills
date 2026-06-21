---
name: opensense-pr-attempt-vp
description: Use OpenSense to find, evaluate, and prepare one safe open-source PR attempt from watched GitHub repositories. Use when the user wants daily issue recommendations, LLM-assisted issue planning, context packs, sandboxed agent apply, test evidence capture, PR draft generation, attempt status, or read-only OpenSense MCP/Skill integration.
---

# OpenSense PR Attempt VP

Use this skill when the user wants to use OpenSense as an agent-assisted open-source contribution workflow: find a realistic issue, inspect it, prepare local evidence, run a sandboxed coding attempt, capture tests, and draft a PR.

OpenSense is a local-first CLI. It prepares evidence and drafts; it does not automatically commit, push, open PRs, or comment on GitHub.

## Preconditions

- Confirm `opensense` is installed, or install it with `pip install opensense-vp`.
- Work in a normal local workspace. OpenSense stores state under `.opensense/`.
- Prefer a GitHub token for stable API limits.
- LLM config is optional. Without it, OpenSense still uses deterministic scoring.

## Main Workflow

Start broad, then narrow to one issue:

```bash
opensense init
opensense daily
opensense issue <owner/repo#number> --plan
```

If the issue looks worth trying, build the local PR attempt:

```bash
opensense pack <owner/repo#number>
opensense patch <owner/repo#number> --dry-run
opensense propose <owner/repo#number>
opensense sandbox create <owner/repo#number>
opensense agent handoff <owner/repo#number>
```

Only after the user agrees to execute code, run the implementation command inside the sandbox:

```bash
opensense agent apply <owner/repo#number> -- <agent command>
opensense test run <owner/repo#number> -- <test command>
opensense pr draft <owner/repo#number>
opensense agent status <owner/repo#number>
```

Use these for review, integrations, or resuming work:

```bash
opensense agent status <owner/repo#number> --json
opensense attempt list
opensense attempt list --json
opensense attempt open <owner/repo#number>
```

## Choosing an Issue

Prefer issues that are small, recent, unassigned, testable, and likely to become one focused PR.

Be cautious when an issue is closed, already assigned, covered by an existing PR, blocked on design decisions, requires private context, touches security/payment/legal/licensing areas, or looks like a broad architecture rewrite.

When unsure, stop at `issue --plan` or `propose` and ask the user before moving into `agent apply`.

## Safety Rules

- Do not run `agent apply` until the user has chosen a specific issue and approved an implementation attempt.
- Do not create commits, push branches, open PRs, or comment on GitHub unless the user explicitly asks outside this OpenSense workflow.
- Do not claim tests passed unless `opensense test run` captured a zero exit code or the raw test evidence clearly proves it.
- Treat `pr draft` as a local draft only. It is not a GitHub PR.
- Keep generated code changes inside the OpenSense sandbox worktree unless the user asks to integrate them elsewhere.
- The OpenSense MCP surface is read-only. Do not use it as a write channel.

## Expected Output

For normal user-facing summaries, report:

- the selected issue and why it is a good or risky attempt;
- the generated pack/proposal/handoff/test/draft artifacts;
- the exact test command and result;
- the next human decision: abandon, revise, run more tests, or manually open a PR.

Keep the final answer concise. Link local artifact paths when useful.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
