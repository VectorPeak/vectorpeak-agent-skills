---
name: profile-readme-github-vp
description: Use when creating or updating VectorPeak's personal GitHub profile README with Chinese-first/English-second bilingual sections, badges, identity line, own public project summary, own merged upstream PR summary, stars-sorted personal Projects table, stars-sorted Open Source Contributions tables, and LinkedIn link.
---

# Profile README GitHub VP

## Overview

Generate VectorPeak's personal GitHub profile `README.md` from GitHub facts plus curated notes. The profile is bilingual, with the Chinese section first and the English section second. It has two evidence surfaces: `Projects` for repositories developed or maintained by VectorPeak, and `Open Source Contributions` for merged upstream PRs authored by VectorPeak.

Both project tables sort by `Area` alphabetically, then repository stars descending within the same area. Contribution tables still sort by upstream repository stars descending.

## Workflow

1. Confirm the target profile repository is `VectorPeak/VectorPeak`.
2. Optionally collect GitHub account facts:

```bash
python <skill-dir>/scripts/collect_profile_data.py --out github-facts.json
```

3. Prepare or update a JSON data file with:
   - `projects`: VectorPeak-owned or VectorPeak-maintained public projects with curated `area` and `notes`
   - optional `contributions`: VectorPeak-authored merged upstream PRs with curated `area` and `fixed`
   - optional `public_repos`, `public_project_count`, `merged_pr_count`
   - optional `linkedin`
4. Run:

```bash
python <skill-dir>/scripts/render_profile_readme.py --data profile-data.json --facts github-facts.json --out README.md
```

5. Inspect the generated README.
6. Commit and push only the intended README/data changes.

## README Order

Generate content in this order:

1. Heading:
   `## Hey, I'm VectorPeak 👋`
2. Technology badges line, with LinkedIn badge placed before Python when provided:
   `Python Go TypeScript React Node.js FastAPI RAG Hugging Face LangChain GitHub`
3. Identity line:
   `AI Programmer | BS CS @ Xidian University | 2x CCF-C`
4. Chinese summary bullets:
   - upstream PR bullet, only when contribution records exist:
     `- {{N}}+ 个 merged upstream PR，覆盖 {{top repos...}}。`
   - public project bullet:
     `- {{N}} 个公开项目，代表项目包括 {{top projects...}}。`
5. `### 项目`
6. Chinese section project table uses English headers and English Area labels: `Area | Project | Stars | Notes`
7. `### 开源贡献`, only when contribution records exist
8. Separator `---`
9. English heading:
   `## Hey, I'm VectorPeak 👋`
10. Identity line
11. English summary bullets:
   - upstream PR bullet, only when contribution records exist:
     `- {{N}}+ merged upstream PRs, including fixes in {{top repos...}}.`
   - public project bullet:
     `- {{N}} public projects, led by {{top projects...}}.`
12. `### Projects`
13. English project table: `Area | Project | Stars | Notes`
14. `### Open Source Contributions`, only when contribution records exist
15. Contribution sections as `####` headings:
   - `AI infrastructure / model systems`
   - `Agent frameworks / protocols / evals`
   - `Applied AI / RAG / observability`
   - `Recommender systems`
16. Do not render LinkedIn at the bottom; keep the LinkedIn badge first in the top badge row, before Python

## Project Table Rules

- Sort project table rows by `Area` alphabetically, then numeric stars descending within the same `Area`, then project name alphabetically for ties.
- Projects must be VectorPeak-owned or VectorPeak-maintained public repositories.
- Exclude forked repositories from `Projects` and from the public project summary.
- Exclude the `VectorPeak/VectorPeak` profile README repository itself from `Projects` and from public project counts; it is infrastructure for the profile, not a portfolio project.
- Render stars as `1,081+`, `167+`, or `0+`.
- Link project names when `url` is present.
- Keep notes concise and outcome-oriented.
- For bilingual output, keep `Area` values in English in both sections. Use optional `zh_notes` and `en_notes` fields for localized notes. Fall back to `notes` when localized fields are not provided.
- Use only these area labels unless the user explicitly expands the taxonomy:
  - `Coding agents`
  - `CI / PR tooling`
  - `MCP / protocol tooling`
  - `Codebase maps`
  - `Applied agents`
  - `LLM tooling`
  - `Research`

## Contribution Table Rules

- Group contributions by `area`.
- Preserve the configured contribution area order.
- Within each contribution group, sort by upstream repository stars descending, then PR number descending.
- Table columns are `Project | PR | What I Fixed`.
- Render project as `[Name (81.8k★)](repo_url)` when `repo_url` exists.
- Render PR as `[#40789](pr_url)` when `pr_url` exists.
- Count all contribution rows for the merged upstream PR summary.
- Only count upstream PRs whose target repository has at least 500 stars by default.
- If `merged_pr_count` is provided, use it for the summary count instead of the visible table row count.
- If `public_project_count` and `public_repos` are provided, use them for the public project summary instead of the curated table row count.
- If there are no contribution rows, omit the merged upstream PR line and the entire `Open Source Contributions` section.
- If all upstream PRs are below the minimum star threshold, omit the merged upstream PR line and the entire `Open Source Contributions` section.
- Contribution rows must be PRs authored by VectorPeak and merged into upstream open-source repositories.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Hard-coding inflated project or PR counts | Count rows from data |
| Writing an upstream PR line without contribution data | Omit it |
| Sorting project rows by input order | Sort by stars descending |
| Mixing projects made by others into `Projects` | Keep only VectorPeak-owned/maintained projects |
| Mixing non-authored PRs into contributions | Keep only VectorPeak-authored merged upstream PRs |
| Mixing contribution and project area labels | Use separate allowed taxonomies |
| Making the README a long essay | Let tables carry the detail |
| Putting English first | Keep Chinese first, then English |
| Translating Area labels in the Chinese section | Keep Area labels in English in both sections |
| Adding a visible English jump link | Do not render `[English](#english-version)` |
| Rendering Chinese text through the terminal in a broken encoding | Write files as UTF-8 and verify with a UTF-8 reader |

## Table Layout Rules

- Keep `Area` visually wider than the default markdown table would make it.
- Render spaces inside `Area` values as `&nbsp;` so labels such as `Coding agents` stay on one line in narrow GitHub profile tables.
- Left-align `Stars`; do not right-align numeric stars.
- Prefer markdown tables first. Switch to HTML tables only if GitHub wrapping becomes too cramped.
