---
name: xquik-research-vp
description: Use when planning, collecting, normalizing, or summarizing Xquik REST API data for X/Twitter research, trend tracking, profiles, communities, timelines, or monitor outputs.
---

# xquik-research-vp

Use this skill when a user wants to turn Xquik REST API data into research notes, structured summaries, comparison tables, or dashboard-ready rows.

## Inputs

- Research goal, such as tweet search, profile lookup, timelines, trends, communities, or monitors.
- Xquik endpoint path or public OpenAPI reference.
- User-provided API response JSON, export files, or permission to fetch data with credentials already configured in the runtime.

## Workflow

1. Clarify the research goal and the exact X/Twitter entity or query.
2. Select the matching public Xquik endpoint or ask for the endpoint path.
3. Keep API keys in the runtime environment or approved credential store.
4. Fetch data only when credentials and user approval are already available, or parse user-provided JSON.
5. Normalize IDs as strings, preserve source timestamps, and record the capture time.
6. Group records by the question being answered: author, topic, trend, community, timeline position, or monitor event.
7. Summarize findings with clear evidence fields and mark any inferred labels as analysis.

## Output

- Endpoint path and capture time.
- Short findings summary.
- Structured rows or a Markdown table for the selected entities.
- Notes on missing fields, pagination limits, or assumptions.

## Guardrails

- Do not print, paste, or store API keys.
- Do not claim private pricing, capacity, or implementation details.
- Do not perform write actions unless the user explicitly requests a write workflow.
- Do not treat inferred labels or sentiment as facts.
