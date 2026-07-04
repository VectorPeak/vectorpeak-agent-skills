# PR Examples Reference

Use these examples as style anchors for concise, evidence-driven bug-fix PRs.

## Anchor Examples

- `langgenius/dify#37799`: `fix(web): prevent ssePost error handler from throwing`
- `AstrBotDevs/AstrBot#8971`: `fix: prevent path traversal vulnerability in knowledge base upload filenames`

## Writing Structure

Use the repository template as the outer shell, then fit the bug story into its sections.

```markdown
<one-sentence summary>

## What Problem This Solves

<State the concrete bug first.>
<Name the entry point, parser, handler, endpoint, or helper that fails.>
<Explain who sees the breakage and why it matters.>

## Change

<Describe the narrow fix in 1-3 short paragraphs or bullets.>
<Call out the behavior that stays unchanged.>

## Evidence

<Show the reproduction path, payload, snippet, or failing command.>
<Include expected vs actual behavior.>
<Use logs, screenshots, or output only as support, not as the whole explanation.>

## Possible call chain / impact

<Trace from user action/API/CLI to the faulty branch or expression.>
<State which nearby paths are not affected.>

## Testing / Validation

- `<targeted command>`
- `<focused test or repro>`
- `<lint/type/compile command if relevant>`
```

## Candidate Types

Prefer PRs that fit one of these shapes:

- Real bug: deterministic runtime failure, bad exception handling, broken state transition, null/undefined access, or wrong branch.
- Compatibility: Windows/Linux path behavior, casing, newline handling, version drift, encoding, or dependency API changes.
- API contract: wrong parameter semantics, return shape, status codes, optional vs required fields, or caller mismatch.
- Parser edge case: empty input, escaping, nested structures, partial parsing, malformed but common input, or whitespace/newline handling.
- Tool calling: schema mismatch, required/optional field mistakes, tool result parsing, stream ordering, or provider quirks.
- Serialization: JSON/YAML/TOML/env parsing, round-trip loss, numeric conversion, or time conversion.
- Path / URL handling: traversal, normalization, encoding, separator behavior, or unsafe joins.
- Diagnostics: swallowed failures, misleading errors, or exceptions that hide the root cause.

## Few-Shot Lessons

### `langgenius/dify#37799`

Use this as the model for a small frontend/runtime bug fix.

- Show the exact failing expression or branch.
- Explain the runtime type mismatch plainly.
- Compare with a nearby correct implementation when one exists.
- Prove the old path throws or cascades into a second error.
- Keep the fix tiny and list focused lint/test commands.
- Preserve the project PR template exactly as required.

### `AstrBotDevs/AstrBot#8971`

Use this as the model for a narrow path-handling or security-adjacent fix.

- Show the dangerous path construction and the user-controlled input.
- Provide concrete payloads such as `../../../evil.txt` and `..\..\..\evil.txt`.
- Explain before/after resolution without overstating exploitation.
- Distinguish the affected upload/parse path from unrelated indexing or permission logic.
- State clearly what does not change.

## Evidence Rules

- Prefer concrete reproduction over inference whenever possible.
- For bugs, show the trigger, the observed failure, and the expected behavior.
- For parser/API/tool-calling issues, include the exact payload, request, or snippet.
- For path or URL bugs, include before/after resolution or normalized output.
- For compatibility issues, show the platform, version, or environment difference.
- For security-adjacent claims, name the control point, the payload, and the practical impact.
- Never claim a script, test, screenshot, or log unless it was actually produced or is present in the diff.
- Do not rely on screenshots alone; pair them with a text reproduction.

## PR Template Rules

- Read the target repository PR template before drafting prose.
- Treat the template as the outer container; do not append a second generic template.
- Preserve required checklists, warning callouts, issue-link language, CLA notes, and AI-disclosure text.
- Fit the bug narrative into the existing headings when possible.
- Use the repository's preferred `Testing`, `Validation`, or equivalent heading name.

## Anti-Patterns

- Do not write a theory-only cleanup as if it were a confirmed bug.
- Do not say "tested locally" without exact commands and results.
- Do not inflate a small fix into a broad refactor.
- Do not label behavior as a vulnerability unless the payload, control point, and impact support it.
- Do not omit before/after behavior for parser, path, URL, validation, API, or tool-calling bugs when reproduction is feasible.
- Do not ignore the repo template in favor of a generic PR shape.

## Summary Rule

Small PRs should convince maintainers of three things: the bug is real, the change is narrow, and validation is reproducible.
