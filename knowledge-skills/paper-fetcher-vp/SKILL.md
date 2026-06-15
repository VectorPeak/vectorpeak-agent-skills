---
name: paper-fetcher-vp
description: Use when the user provides a research paper screenshot, title, arXiv/OpenReview/publisher/project URL, or article excerpt and wants Codex to identify the paper, download and verify an official PDF, rename it with a research-field prefix, and report a Zotero Add Item by Identifier value such as arXiv ID or DOI.
---

# Paper Fetcher

## Purpose

Find the corresponding research paper from a screenshot, title, URL, or excerpt; download the verified official PDF into the local raw research source folder; and return the identifier the user can paste into Zotero's Add Item by Identifier dialog.

## Local Target Folder

For this user's local `LLM_wiki` vault, default and inferred paper storage is:

```text
E:\LLM_wiki\LLM_wiki\raw\08.Research
```

Use this folder when the user does not provide a destination. `scripts/paper_postprocess.py` also defaults to this path when `--target-dir` is omitted.

Allow explicit overrides with `--target-dir` whenever the user names a different destination.

Treat PDFs, `.metadata.json` sidecars, optional BibTeX sidecars, and paper metadata saved here as raw source material. Do not create generated reading notes, summaries, synthesis pages, outlines, or wiki-ready interpretations inside `raw\08.Research`; those belong later in the processed `wiki` area or another user-specified notes location.

## Source Priority

Prefer official sources in this order:

1. arXiv
2. OpenReview
3. ACL Anthology, NeurIPS, ICML, ICLR, ACM, IEEE, Springer, Elsevier, or other official publisher pages
4. Official project page
5. GitHub README that links to the paper

Avoid non-official mirrors unless no official PDF is available. Do not bypass paywalls or access controls.

## Workflow

1. Extract paper title, authors, visible IDs, source URL, project URL, and candidate PDF URL from the user input.
2. Search online when needed and verify the strongest official match.
3. Identify the best Zotero identifier:
   - Prefer arXiv ID.
   - Use DOI if no arXiv ID exists.
   - If neither exists, report `not available` and include another source ID such as OpenReview ID for reference.
4. Download the official PDF into `E:\LLM_wiki\LLM_wiki\raw\08.Research` or a temporary download path. Use another target only when the user provides one.
5. Read enough of the paper to classify it into exactly one filename prefix:
   - `RAG`
   - `Agent`
   - `SFT`
   - `RL`
   - `DL_Frameworks`
   - `Other`
6. Run `scripts/paper_postprocess.py` to verify and rename the PDF as `{field}_{original paper title}.pdf`, and write `{field}_{original paper title}.metadata.json` next to it.
7. Report Zotero identifier status in the final response.
8. Do not generate `.bib` files unless explicitly requested.
9. Do not create hand-written Zotero metadata entries through the Web API.
10. Never edit Zotero's local database files directly.

## Field Prefix Selection

Choose the filename prefix by reading the title, abstract, introduction, method, and conclusion. Use the closest field when a paper spans multiple areas:

- `RAG`: retrieval-augmented generation, vector retrieval, dense/sparse retrieval, indexing, query rewriting, reranking, knowledge-grounded generation, long-context retrieval.
- `Agent`: LLM agents, tool use, planning, agent benchmarks, multi-agent systems, browser/computer-use agents, workflow automation, agent memory.
- `SFT`: supervised fine-tuning, instruction tuning, alignment datasets, preference data preparation before RL, domain/task fine-tuning.
- `RL`: reinforcement learning, RLHF, RLAIF, PPO, DPO-style preference optimization, reward models, policy optimization, decision-making agents when RL is central.
- `DL_Frameworks`: training/inference systems, distributed training, compilers, CUDA kernels, PyTorch/TensorFlow/JAX/runtime work, model serving infrastructure.
- `Other`: use only when none of the above fields is a reasonable fit.

## Local Helper

Use `scripts/paper_postprocess.py` after downloading a PDF to sanitize the filename, verify `%PDF-`, move it into the raw research source folder, write a `.metadata.json` sidecar, and report Zotero identifier status.

Example:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --title "Agent Harness Engineering: A Survey" `
  --field Agent `
  --authors "Junjie Li and Xi Xiao and Yunbei Zhang" `
  --source-url "https://openreview.net/pdf?id=eONq7FdiHa" `
  --zotero
```

Optional legacy BibTeX sidecar generation exists only when explicitly requested:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "E:\LLM_wiki\LLM_wiki\raw\08.Research" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --authors "John Schulman and Filip Wolski and Prafulla Dhariwal and Alec Radford and Oleg Klimov" `
  --year 2017 `
  --arxiv-id "1707.06347" `
  --source-url "https://arxiv.org/pdf/1707.06347" `
  --zotero `
  --bib
```

## Zotero Handling

Use Zotero's Add Item by Identifier behavior as the primary import path. The user can paste the returned arXiv ID or DOI into Zotero so Zotero fetches canonical metadata from supported resolvers.

Do not store Zotero API credentials in this skill. Use Zotero Web API or MCP only for lookup, duplicate checks, updates after a canonical item exists, or attachment management when explicitly needed.

## Final Response

Always include:

- Paper title
- arXiv ID, or `arXiv: not found`
- DOI, or `DOI: not found`
- Zotero Add Item by Identifier value, or `not available`
- Other source ID when relevant, such as OpenReview ID
- PDF source URL
- Saved local path
- File size
- Zotero status

## Failure Handling

- If no reliable paper match is found, ask for a clearer screenshot/title/URL instead of guessing.
- If the PDF cannot be verified, delete or ignore the invalid file and report the failed source.
- If multiple candidate papers match, list candidates and choose the one with the strongest title/source match.
