# PR Examples Reference

Use these examples as style references for concise, evidence-driven bug-fix PRs.

## Examples

- `langgenius/dify#37799`: `fix(web): prevent ssePost error handler from throwing`
- `AstrBotDevs/AstrBot#8968`: `fix: prevent path traversal vulnerability in plugin upload filenames`

## Shared Structure

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

## Common Traits

- The title names the bug and the affected area.
- The title is clear, descriptive, and specific enough for maintainers to understand the behavior at a glance.
- The first section explains the behavioral problem before describing code.
- Evidence includes reproduction steps, expected behavior, actual behavior, and concrete failure output.
- Backend issues include logs when available; docker-compose logs are especially valuable.
- Screenshots or videos are included when they help demonstrate the issue.
- The call-chain section helps maintainers see how the bug is reached.
- The impact section also states what is not affected.
- Testing uses focused commands rather than vague "tested locally" claims.

## Writing Rule

Small PRs should convince maintainers of three things: the bug is real, the change is narrow, and validation is reproducible.
