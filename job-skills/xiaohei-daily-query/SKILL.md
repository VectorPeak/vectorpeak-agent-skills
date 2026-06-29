---
name: xiaohei-daily-query
description: Query the local Xiaohei Daily Assistant HTTP service for work timelines, Markdown work reports, 24-hour heat maps, and app usage duration statistics. Use when the user asks about 小黑日报助手, 日报, 工作时间线, 工作报告, 时段热力图, 应用使用时长, app usage, or productivity records from the local service at 192.168.11.212:8088.
---

# Xiaohei Daily Query

## Core Rule

Before every user request, fetch the latest API Markdown document from:

```text
GET http://192.168.11.212:8088/
```

Do not rely on a memorized endpoint list. Read the live Markdown, parse the available endpoint paths, methods, parameters, request examples, and response shape, then choose the correct endpoint for the user's request.

## Supported User Intents

Handle natural-language requests for:

- Work timeline records for a date or date range.
- Work reports for a date or date range, returned as Markdown content.
- Hourly heat-map data for a date range.
- App usage duration summaries for a date or date range.

If the user does not specify a date, omit `startDate` and `endDate` so the service uses its current default. For timeline, report, and app usage this normally means today; for heat-map this normally means the recent default window described in the live docs.

Use `YYYY-MM-DD` dates unless the user explicitly asks for a precise time range.

## Recommended Script

Use the bundled helper:

```powershell
& "C:\Users\ZXY\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\ZXY\.codex\skills\xiaohei-daily-query\scripts\query_xiaohei.py" `
  --intent report --start-date 2026-06-29 --end-date 2026-06-29
```

The script always fetches `GET /` first, extracts the live GET endpoints from the Markdown, maps the requested intent to the currently documented path, calls the selected endpoint, validates the unified JSON envelope, and prints a compact Markdown summary.

Intent values:

- `timeline`
- `report`
- `heat-map`
- `app-usage`

The script also accepts `--query` for lightweight natural-language intent detection:

```powershell
& "<python>" "<skill>\scripts\query_xiaohei.py" --query "查一下今天应用使用时长"
```

## Response Style

Summarize the returned data directly for the user:

- For reports, preserve useful Markdown report content and mention report titles/date ranges.
- For timelines, group records by time and category.
- For heat maps, highlight focus minutes, active period, top category, and hourly distribution if relevant.
- For app usage, convert seconds into readable hours/minutes and list apps in returned order.

If the service returns `code != 0`, explain the error message and include the endpoint that was attempted.
