<h1 align="center">
  PR Writer VP | Open Source PR Workflow Skill
</h1>

<p align="center">
  Fork projects, find small bug-fix PR candidates, draft evidence-driven PRs, and submit only after explicit confirmation.
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/agent-skills-blue" alt="agent skills"></a>
  <a href="../"><img src="https://img.shields.io/badge/category-dev--skills-brightgreen" alt="dev skills"></a>
  <a href="./"><img src="https://img.shields.io/badge/pr--writer--vp-github-black" alt="pr writer vp"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" alt="license Apache-2.0"></a>
</p>

```text
project name -> fork and clone -> small bug hunt -> evidence -> PR draft -> confirmed draft PR
```

---

## Why PR Writer?

Small open-source PRs are easiest to review when they are narrow, reproducible, and written in the target project's style. The hard part is not only changing code; it is proving that the bug is real, explaining the impact without exaggeration, and respecting each repository's contribution rules.

PR Writer VP turns that process into a repeatable agent workflow. It helps an agent fork and clone a repository, keep the fork's `main` synchronized, create a fix branch, search for simple bug-fix opportunities, gather evidence, and draft a PR body that is clear enough for maintainers to evaluate quickly.

The default posture is conservative: draft first, submit only after explicit user confirmation.

## Workflow

1. **Pull project and configure environment**
   - Resolve the upstream GitHub repository.
   - Fork it to the user's account.
   - Clone the fork under `E:\Github\<repo-name>`.
   - Add `upstream`.
   - Keep fork `main` synchronized with upstream `main`.
   - Create a `fix` or non-conflicting fix branch.

2. **Find a PR candidate**
   - Launch multi-agent review when available.
   - Default direction: find likely bugs with code changes under 20 lines.
   - Prefer deterministic edge cases such as path casing, URL encoding, validation mistakes, null handling, escaping, and small boundary errors.
   - Present candidates before editing unless the user delegated the choice.

3. **Draft PR by default**
   - Use multiple agents when possible:
     - one agent reads the target project's contribution and PR submission rules;
     - another agent checks the diff, evidence, and validation claims.
   - Draft title and body before submission.
   - Submit a draft PR only when the user explicitly asks.
   - Mark ready for review only when the user explicitly asks.

## PR Body Template

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

## Testing

- `<targeted command>`
- `<lint/type/compile command>`
- `<unit or focused test command>`
```

## References

The skill includes `references/pr-examples.md`, which summarizes common structure from small bug-fix PRs such as:

- `langgenius/dify#37799`
- `AstrBotDevs/AstrBot#8968`

The main rule is simple: small PRs should convince maintainers of three things: the bug is real, the change is narrow, and validation is reproducible.

## Directory Structure

```text
pr-writer-vp/
|-- SKILL.md
|-- README.md
|-- agents/
|   `-- openai.yaml
`-- references/
    `-- pr-examples.md
```

## Notes

- Do not open or update PRs in dry-run mode.
- Do not claim UI reproduction when only a CLI, unit, or installed-runtime reproduction was performed.
- Do not keep PR-body claims about tests or screenshots after those files or artifacts are removed.
- Keep changes scoped; avoid unrelated refactors and generated churn.
- Follow target repository contribution rules, but do not add a dedicated checklist section unless the project template requires it.
