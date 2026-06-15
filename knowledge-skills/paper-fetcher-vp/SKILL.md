---
name: paper-fetcher-vp
description: Use when the user provides a research paper screenshot, title, arXiv/OpenReview/publisher/project URL, or article excerpt and wants Codex to identify the paper, download and verify an official PDF, classify it into the raw/08.Research taxonomy, choose an optional filename prefix with --name-prefix, and report a Zotero Add Item by Identifier value such as arXiv ID or DOI.
---

# Paper Fetcher

## When To Use

Use this skill when the user wants to identify, fetch, verify, rename, and store an academic paper PDF from a screenshot, title, URL, project page, or excerpt. Also use it when the user asks for the Zotero Add Item by Identifier value for a paper.

## Purpose

Find the corresponding research paper from a screenshot, title, URL, or excerpt; download the verified official PDF into the local raw research source folder; and return the identifier the user can paste into Zotero's Add Item by Identifier dialog.

## Local Target Folder

For this user's local `LLM_wiki` vault, default and inferred paper storage is the numbered research taxonomy under:

```text
E:\LLM_wiki\LLM_wiki\raw\08.Research
```

Use the mapped numbered field folder when the user does not provide a destination:

| Field | PDF destination |
|---|---|
| `Agent` | `raw\08.Research\00.Agent` |
| `RAG` | `raw\08.Research\01.RAG` |
| `SFT` | `raw\08.Research\02.PostTraining\SFT` |
| `RL` | `raw\08.Research\02.PostTraining\RL` |
| `Training_Systems` or legacy `DL_Frameworks` | `raw\08.Research\03.Training_Systems` |
| `Personal` | `raw\08.Research\04.Personal` |
| `Other` | `raw\08.Research\05.Other` |

Allow explicit overrides with `--target-dir` whenever the user names a different destination. Treat `--target-dir` as an exact PDF destination directory, not as a root to append the field to.

Treat PDFs, `.metadata.json` sidecars, optional BibTeX sidecars, and paper metadata saved here as raw source material. Default metadata and BibTeX sidecars go into `raw\08.Research\_metadata`; if the user supplies `--target-dir`, sidecars go into `<target-dir>\_metadata`. Do not create generated reading notes, summaries, synthesis pages, outlines, or wiki-ready interpretations inside `raw\08.Research`; those belong later in the processed `wiki` area or another user-specified notes location.

Recommended local folder structure:

```text
raw/08.Research/
  00.Agent/
  01.RAG/
  02.PostTraining/
    SFT/
    RL/
  03.Training_Systems/
  04.Personal/
  05.Other/
  _metadata/
```

Keep PDFs in their field folder and sidecars in `_metadata/`:

```text
raw/08.Research/00.Agent/Survey_Example Paper.pdf
raw/08.Research/_metadata/Survey_Example Paper.metadata.json
```

## PDF Filename Prefixes

Separate the coarse research `field` from the PDF filename prefix:

- Use `field` only to choose the destination folder and metadata taxonomy.
- Use `--name-prefix` to choose the PDF filename prefix when a more specific method, paper type, or topic is clear.
- Avoid repeating large folder categories in filenames when the folder already says the category, such as `Agent_...`, `Training_Systems_...`, or `Personal_...`.
- If no useful specific prefix is clear, fall back to the field name.

Preferred filename pattern:

```text
{specific_prefix}_{short sanitized paper title}.pdf
```

Useful prefixes include:

```text
Survey
Benchmark
Framework
Method
Dataset
Architecture
DistributedTraining
LLMTraining
Inference
Serving
RAG
AgentEval
RepoContext
SFT
QLoRA
DPO
PPO
GRPO
RLHF
PreferenceOptimization
PrivacyDeletion
```

Examples:

```text
raw/08.Research/00.Agent/Survey_Agent Harness Engineering- A Survey.pdf
raw/08.Research/00.Agent/RepoContext_Evaluating AGENTS.md Are Repository-Level Context Files Helpful.pdf
raw/08.Research/02.PostTraining/SFT/QLoRA_Efficient Finetuning of Quantized LLMs.pdf
raw/08.Research/02.PostTraining/RL/DPO_Direct Preference Optimization- Your Language Model is Secretly a Reward Model.pdf
raw/08.Research/03.Training_Systems/DistributedTraining_PyTorch Distributed-Experiences on Accelerating Data Parallel Training.pdf
raw/08.Research/03.Training_Systems/LLMTraining_Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM.pdf
raw/08.Research/04.Personal/PrivacyDeletion_CAREFUL a Secure and Privacy-preserving Deletion Notification Framework.pdf
```

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
4. Download the official PDF into the matching field folder under `E:\LLM_wiki\LLM_wiki\raw\08.Research` or a temporary download path. Use another target only when the user provides one.
5. Read enough of the paper to classify it into exactly one research field:
   - `RAG`
   - `Agent`
   - `SFT`
   - `RL`
   - `Training_Systems`
   - `Personal`
   - `Other`
6. Choose a specific filename prefix using the PDF Filename Prefixes guidance. Prefer method/topic prefixes such as `DPO`, `PPO`, `QLoRA`, `Survey`, `RepoContext`, `DistributedTraining`, `LLMTraining`, or `PrivacyDeletion` over broad folder names.
7. Run `scripts/paper_postprocess.py` to verify and rename the PDF as `{name-prefix}_{original paper title}.pdf`, and write `{name-prefix}_{original paper title}.metadata.json` into `_metadata`.
8. Report Zotero identifier status in the final response.
9. Do not generate `.bib` files unless explicitly requested.
10. Do not create hand-written Zotero metadata entries through the Web API.
11. Never edit Zotero's local database files directly.

## Field Classification

Choose exactly one `field` by reading the title, abstract, introduction, method, and conclusion. The field determines the destination under `raw/08.Research`, not the filename prefix. Use the closest field when a paper spans multiple areas:

- `RAG`: retrieval-augmented generation, vector retrieval, dense/sparse retrieval, indexing, query rewriting, reranking, knowledge-grounded generation, long-context retrieval.
- `Agent`: LLM agents, tool use, planning, agent benchmarks, multi-agent systems, browser/computer-use agents, workflow automation, agent memory.
- `SFT`: supervised fine-tuning, instruction tuning, alignment datasets, preference data preparation before RL, domain/task fine-tuning.
- `RL`: reinforcement learning, RLHF, RLAIF, PPO, DPO-style preference optimization, reward models, policy optimization, decision-making agents when RL is central.
- `Training_Systems`: training/inference systems, distributed training, compilers, CUDA kernels, PyTorch/TensorFlow/JAX/runtime work, model serving infrastructure, and model architecture papers that are primarily about training behavior or systems implications.
- `DL_Frameworks`: legacy alias for `Training_Systems`; prefer `Training_Systems` in new outputs.
- `Personal`: personal/local-interest papers that the user wants retained outside the main research taxonomy.
- `Other`: use only when none of the above fields is a reasonable fit.

## Local Helper

Use `scripts/paper_postprocess.py` after downloading a PDF to sanitize the filename, verify `%PDF-`, move it into the raw research source folder, write a `.metadata.json` sidecar, and report Zotero identifier status.

Example:

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

Optional legacy BibTeX sidecar generation exists only when explicitly requested:

```powershell
python scripts\paper_postprocess.py `
  --pdf "<downloaded-pdf>" `
  --target-dir "E:\LLM_wiki\LLM_wiki\raw\08.Research\02.PostTraining\RL" `
  --title "Proximal Policy Optimization Algorithms" `
  --field RL `
  --name-prefix PPO `
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
