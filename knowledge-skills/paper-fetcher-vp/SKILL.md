---
name: paper-fetcher-vp
description: Use when the user provides a research paper screenshot, title, arXiv/OpenReview/publisher/project URL, or article excerpt and wants Codex to identify the paper, download and verify an official PDF, classify it into the 01.raw/08.Research taxonomy, choose an optional filename prefix with --name-prefix, and report a Zotero Add Item by Identifier value such as arXiv ID or DOI.
---

# Paper Fetcher

## When To Use

Use this skill when the user wants to identify, fetch, verify, rename, and store an academic paper PDF from a screenshot, title, URL, project page, or excerpt. Also use it when the user asks for the Zotero Add Item by Identifier value for a paper.

Do not use this skill for generated reading notes, summaries, synthesis pages, Zotero database editing, paywall bypasses, or non-official mirror collection unless the user explicitly asks for a separate downstream task.

## Default Vault Contract

For this local `LLM_wiki` vault, default paper storage is the numbered raw research taxonomy under:

```text
E:\LLM_wiki\LLM_wiki\01.raw\08.Research
```

Use the mapped field folder when the user does not provide a destination:

| Field | PDF destination |
|---|---|
| `Agent` | `01.raw\08.Research\00.Agent` |
| `RAG` | `01.raw\08.Research\01.RAG` |
| `SFT` | `01.raw\08.Research\02.PostTraining\SFT` |
| `RL` | `01.raw\08.Research\02.PostTraining\RL` |
| `Training_Systems` or legacy `DL_Frameworks` | `01.raw\08.Research\03.Training_Systems` |
| `Personal` | `01.raw\08.Research\04.Personal` |
| `Other` | `01.raw\08.Research\05.Other` |

Treat PDFs, `.metadata.json` sidecars, optional BibTeX sidecars, and raw paper metadata saved here as `01.raw` source material. Default sidecars go into `01.raw\08.Research\_metadata`. If `--target-dir` is supplied, treat it as the exact PDF destination directory and put sidecars in `<target-dir>\_metadata`.

Do not create generated notes, summaries, outlines, or wiki-ready interpretations inside `01.raw\08.Research`; those belong later in `02.wiki` or another user-specified notes destination.

## Core Workflow

1. Extract title, authors, visible IDs, source URL, project URL, and candidate PDF URL from the user input.
2. Search online when needed and verify the strongest official match.
3. Prefer official sources in this order: arXiv, OpenReview, official publisher pages, official project pages, then GitHub READMEs that link to the paper.
4. Identify the best Zotero identifier: prefer arXiv ID, then DOI; if neither exists, report `not available` and include another source ID such as OpenReview ID.
5. Download the official PDF into a temporary path or the matching field folder under `01.raw\08.Research`.
6. Read enough of the paper to choose exactly one field: `RAG`, `Agent`, `SFT`, `RL`, `Training_Systems`, `Personal`, or `Other`.
7. Choose a specific filename prefix with `--name-prefix` when possible, such as `Survey`, `Benchmark`, `RepoContext`, `QLoRA`, `DPO`, `PPO`, `GRPO`, `DistributedTraining`, `LLMTraining`, or `PrivacyDeletion`.
8. Run `scripts/paper_postprocess.py` to verify `%PDF-`, rename the PDF as `{name-prefix}_{paper title}.pdf`, write metadata, and report Zotero status.
9. Do not generate `.bib` files unless explicitly requested.

Load `references/paper-fetcher-notes.md` for detailed field classification, filename-prefix guidance, source handling, Zotero notes, and troubleshooting.

## Key Commands

Postprocess a downloaded PDF into the default `08.Research` taxonomy:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --title "Agent Harness Engineering: A Survey" `
  --field Agent `
  --name-prefix Survey `
  --authors "Junjie Li and Xi Xiao and Yunbei Zhang" `
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" `
  --zotero
```

Use an explicit destination directory:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "E:\LLM_wiki\LLM_wiki\01.raw\08.Research\02.PostTraining\RL" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --name-prefix PPO `
  --arxiv-id "1707.06347" `
  --source-url "https://arxiv.org/pdf/1707.06347" `
  --zotero
```

Optional BibTeX sidecar generation exists only when explicitly requested:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --name-prefix PPO `
  --arxiv-id "1707.06347" `
  --source-url "https://arxiv.org/pdf/1707.06347" `
  --zotero `
  --bib
```

## Safety Boundaries

Avoid non-official mirrors unless no official PDF is available. Do not bypass paywalls, login walls, or access controls.

If no reliable paper match is found, ask for a clearer screenshot/title/URL instead of guessing. If the PDF cannot be verified, delete or ignore the invalid file and report the failed source.

Do not create hand-written Zotero metadata entries through the Web API, store Zotero credentials in this skill, or edit Zotero local database files directly. Use Zotero Add Item by Identifier behavior as the primary import path.

## Final Response

Always include paper title, arXiv ID or `arXiv: not found`, DOI or `DOI: not found`, Zotero Add Item by Identifier value or `not available`, other source ID when relevant, PDF source URL, saved local path, file size, and Zotero status.
## Sync Rule

????? skill ???????????? `VectorPeak/vectorpeak-agent-skills`?????????????
