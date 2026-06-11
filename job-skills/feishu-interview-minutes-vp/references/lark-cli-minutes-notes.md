# lark-cli Minutes Notes

## Authorization

Always start with:

```powershell
lark-cli auth status --verify
```

If `User identity: ready` and `tokenStatus: valid`, continue. Do not create a new authorization URL by default.

Request incremental authorization only for explicit `missing_scope` errors.

Common scopes:

| Capability | Scope |
|---|---|
| Docx intelligent notes / transcript docs | `docx:document:readonly` |
| Minutes metadata/search | `minutes:minutes.basic:read minutes:minutes.search:read` |
| Native transcript export | `minutes:minutes.transcript:export` |
| Minutes artifacts / VC notes | `vc:note:read minutes:minutes:readonly minutes:minutes.artifacts:read` |
| Media download | `minutes:minutes.media:export` |

If the API returns `permission_denied`, `user lacks permission`, `No permission to operate on this document`, or code `3380004`, the current user lacks object-level access. Ask the owner to grant access; do not repeatedly reauthorize.

## Docx Intelligent Note

Fetch Markdown:

```powershell
lark-cli docs +fetch --api-version v2 --doc "<docx_url>" --as user --doc-format markdown --json
```

Parse the final `相关链接` section. In Feishu AI meeting notes it often contains:

- `妙记`: original minutes/recording link.
- `文字记录`: transcript Docx link.

If the transcript Docx is denied, preserve that status and fall back to the minutes transcript.

## Minutes Metadata

Extract `minute_token` from:

```text
https://example.feishu.cn/minutes/<minute_token>?from=ai_minutes
```

Fetch metadata:

```powershell
lark-cli api GET /open-apis/minutes/v1/minutes/<minute_token> --as user --json
```

Important fields:

- `title`
- `duration` in milliseconds
- `create_time`
- `owner_id`
- `note_id`
- `url`

## Native Transcript Export

`lark-cli api ... --output` requires a relative output path under the current directory. If the user wants a specific directory, `cd` there first.

```powershell
'{"need_speaker":true,"need_timestamp":true,"file_format":"txt"}' |
  lark-cli api GET /open-apis/minutes/v1/minutes/<minute_token>/transcript --as user --params - --output "minutes\<minute_token>\native_transcript.txt" --json
```

This path is preferred for full verbatim transcript.

## VC Notes Fallback

Use when native export is unavailable or when AI artifacts are useful:

```powershell
lark-cli vc +notes --minute-tokens <minute_token> --as user --overwrite --json
```

This may write:

```text
minutes\<minute_token>\transcript.txt
```

Do not assume this transcript is complete. Compare it with duration and timestamp coverage.

## Tested Failure Pattern

A common real-world pattern:

1. Intelligent note Docx is accessible.
2. Its `相关链接` contains both `妙记` and `文字记录`.
3. The `文字记录` Docx may return code `3380004` because the current user lacks document access.
4. Minutes metadata and transcript export may still be accessible through the `妙记` link.

In that case, record:

```text
related_source_status: "文字记录 Docx 无权限；已使用妙记原生逐字稿。"
```

Then continue instead of stopping.
