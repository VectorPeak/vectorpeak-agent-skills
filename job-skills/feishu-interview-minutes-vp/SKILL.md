---
name: feishu-interview-minutes-vp
description: Use when a task involves Feishu/Lark Minutes, Docx intelligent meeting notes, transcript documents, or Feishu source-routing for Chinese interview review, coaching, or preparation reports. Pasted transcripts are supported only as a fallback when Feishu transcript sources are unavailable.
---

# Feishu Interview Minutes

## Purpose

Turn Feishu interview materials into a structured Chinese Markdown report focused on interviewer questions, follow-ups, challenges, boundary checks, and coaching directions.

Do not summarize the candidate's answers unless needed to understand why a follow-up was asked. Do not keep raw transcript text in the final report unless the user explicitly requests it.

## Workflow

1. Check user authorization with `lark-cli auth status --verify`. Do not create an authorization link unless there is a clear `missing_scope` or expired user token.
2. Identify the source type: `/docx/`, `/wiki/`, `/minutes/`, transcript file, or pasted text.
3. For Docx/Wiki intelligent notes, fetch Markdown with:

   ```powershell
   lark-cli docs +fetch --api-version v2 --doc "<doc_url>" --as user --doc-format markdown --json
   ```

4. Parse the final `相关链接` section with `scripts/extract_feishu_links.py`. Intelligent notes often include:
   - `妙记`: original recording/minutes.
   - `文字记录`: transcript Docx.
5. Prefer sources in this order:
   - `文字记录` transcript Docx when accessible.
   - native Minutes transcript export.
   - `lark-cli vc +notes` transcript artifact.
   - intelligent-note body.
   - pasted transcript text.
6. Record inaccessible related sources instead of pretending they were used. `permission_denied` means the current user lacks document/minute access; do not repeatedly reauthorize.
7. Run completeness checks before analysis: duration, character count, timestamp span, speaker turns, and large gaps. If a long recording yields only a few hundred characters, mark the report incomplete.
8. Build a question-chain prompt with `scripts/build_interview_prompt.py` when a transcript file is available, then produce the final report from that prompt.
9. Validate the Markdown with `scripts/validate_interview_report.py` before replying.
10. On Windows, verify Chinese output with explicit UTF-8 before deciding a generated file is corrupted:

   ```powershell
   Get-Content -LiteralPath "<report.md>" -Encoding UTF8 -TotalCount 40
   ```

   Default PowerShell rendering can show mojibake for a valid UTF-8 Markdown file.

## References

- Read `references/lark-cli-minutes-notes.md` when configuring `lark-cli`, handling scopes, or routing Docx/Minutes/VC commands.
- Read `references/interview-question-chain-format.md` before writing the final report or repairing output format.

## Minutes Commands

For a `/minutes/<minute_token>` URL, fetch metadata:

```powershell
lark-cli api GET /open-apis/minutes/v1/minutes/<minute_token> --as user --json
```

Export native transcript:

```powershell
'{"need_speaker":true,"need_timestamp":true,"file_format":"txt"}' |
  lark-cli api GET /open-apis/minutes/v1/minutes/<minute_token>/transcript --as user --params - --output "minutes\<minute_token>\native_transcript.txt" --json
```

Read VC artifacts as fallback:

```powershell
lark-cli vc +notes --minute-tokens <minute_token> --as user --overwrite --json
```

`--output` must be a relative path under the current directory for `lark-cli`; `cd` to the target directory first if needed.

## Metadata Rules

Extract:

- `candidate`: candidate/person name from title or metadata, not the operator name.
- `date`: event date from the note/transcript, not necessarily Docx revision time.
- `event_time`: full time range when available.
- `company`: real company if known; otherwise use `面试` for coaching/interview materials.
- `position`: role from title or body.
- `related_source_status`: what was accessible, denied, or used as fallback.

Feishu Docx APIs may return title and revision but not true creation time. Prefer explicit body text such as `录音时间：2026年6月6日 14:11 - 14:34`.

If a source title contains a real person name, use that name as `candidate` and filename prefix. Do not fall back to a default operator name such as `VectorPeak` unless the user explicitly requests it.

If a related transcript Docx is inaccessible but native Minutes transcript export is accessible, use the native transcript as the main source and record the denied Docx in `related_source_status`.

## Output Rules

Default filename:

```text
姓名_日期_公司_岗位.md
```

Frontmatter:

```yaml
---
source: "<original Feishu URL>"
source_type: "feishu-docx-ai-minutes"
date: "YYYY-MM-DD"
event_time: "<optional time range>"
company: "面试"
position: "<position>"
candidate: "<candidate>"
duration: "HH:MM:SS"
feishu_title: "<title>"
related_minutes: "<optional>"
related_transcript_doc: "<optional>"
source_priority: "优先读取文字记录 Docx；其次读取妙记原生逐字稿；最后使用智能纪要正文。"
related_source_status: "<what was accessible or denied>"
tags:
  - interview
  - feishu
  - question-chain
type: "interview-question-chain"
---
```

Allowed `source_type` values:

- `feishu-docx-ai-minutes`
- `feishu-minutes`
- `transcript-doc`
- `pasted`

Body:

```markdown
# 日期：公司/岗位/主题

## 一、考察主题
1. **主问题：** ...
   - **追问1：** ...
   - **追问2：** ...
```

## Do Not

- Do not regenerate auth links after one valid device-flow link has been issued; wait for the user unless it expires.
- Do not treat `permission_denied` as a scope problem.
- Do not invent questions from pure evaluations.
- Do not publish private Feishu tokens, local absolute paths, or raw transcripts in public docs.

## Git Handoff

When the user asks to push a generated interview report:

- Push the report repository, not this skill repository, unless the skill files themselves changed.
- Stage only the intended Markdown file. Do not stage the whole output directory when it contains unrelated interview files.
- Confirm the staged scope with:

  ```powershell
  git diff --cached --name-only
  git diff --cached --stat
  ```

- Large wiki worktrees may contain unrelated modified, deleted, and untracked files. Leave them untouched.
- If `.git/index.lock` reports permission denied but no lock file exists, treat it as a sandbox/filesystem permission issue and retry the Git operation with normal user privileges. Do not delete lock files unless a stale lock is actually present and no Git process is running.
