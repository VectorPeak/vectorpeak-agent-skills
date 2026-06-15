# Paper Fetcher Notes

Use this reference when the main `SKILL.md` contract is not enough: field classification, filename-prefix choices, source verification, Zotero handling, or postprocess troubleshooting.

## Local Research Taxonomy

Default local root:

```text
E:\LLM_wiki\LLM_wiki\01.raw\08.Research
```

Recommended structure:

```text
01.raw/08.Research/
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
01.raw/08.Research/00.Agent/Survey_Example Paper.pdf
01.raw/08.Research/_metadata/Survey_Example Paper.metadata.json
```

When `--target-dir` is supplied, treat it as the exact PDF destination directory. In that case, metadata and optional BibTeX sidecars go into `<target-dir>/_metadata`.

## Field Classification

Choose exactly one `field` by reading the title, abstract, introduction, method, and conclusion. The field determines the destination under `01.raw/08.Research`, not the filename prefix.

- `RAG`: retrieval-augmented generation, vector retrieval, dense/sparse retrieval, indexing, query rewriting, reranking, knowledge-grounded generation, long-context retrieval.
- `Agent`: LLM agents, tool use, planning, agent benchmarks, multi-agent systems, browser/computer-use agents, workflow automation, agent memory.
- `SFT`: supervised fine-tuning, instruction tuning, alignment datasets, preference data preparation before RL, domain/task fine-tuning.
- `RL`: reinforcement learning, RLHF, RLAIF, PPO, DPO-style preference optimization, reward models, policy optimization, decision-making agents when RL is central.
- `Training_Systems`: training/inference systems, distributed training, compilers, CUDA kernels, PyTorch/TensorFlow/JAX/runtime work, model serving infrastructure, and model architecture papers that are primarily about training behavior or systems implications.
- `DL_Frameworks`: legacy alias for `Training_Systems`; prefer `Training_Systems` in new outputs.
- `Personal`: personal/local-interest papers that the user wants retained outside the main research taxonomy.
- `Other`: use only when none of the above fields is a reasonable fit.

## Filename Prefixes

Separate the coarse research `field` from the PDF filename prefix:

- Use `field` only to choose the destination folder and metadata taxonomy.
- Use `--name-prefix` for a more specific method, paper type, or topic.
- Avoid repeating broad folder categories in filenames when the folder already says the category, such as `Agent_...`, `Training_Systems_...`, or `Personal_...`.
- If no useful specific prefix is clear, fall back to the field name.

Preferred filename pattern:

```text
{specific_prefix}_{short sanitized paper title}.pdf
```

Useful prefixes:

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
01.raw/08.Research/00.Agent/Survey_Agent Harness Engineering- A Survey.pdf
01.raw/08.Research/00.Agent/RepoContext_Evaluating AGENTS.md Are Repository-Level Context Files Helpful.pdf
01.raw/08.Research/02.PostTraining/SFT/QLoRA_Efficient Finetuning of Quantized LLMs.pdf
01.raw/08.Research/02.PostTraining/RL/DPO_Direct Preference Optimization- Your Language Model is Secretly a Reward Model.pdf
01.raw/08.Research/03.Training_Systems/DistributedTraining_PyTorch Distributed-Experiences on Accelerating Data Parallel Training.pdf
01.raw/08.Research/03.Training_Systems/LLMTraining_Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM.pdf
01.raw/08.Research/04.Personal/PrivacyDeletion_CAREFUL a Secure and Privacy-preserving Deletion Notification Framework.pdf
```

## Source Priority

Prefer official sources in this order:

1. arXiv
2. OpenReview
3. ACL Anthology, NeurIPS, ICML, ICLR, ACM, IEEE, Springer, Elsevier, or other official publisher pages
4. Official project page
5. GitHub README that links to the paper

Avoid non-official mirrors unless no official PDF is available. Do not bypass paywalls or access controls.

If multiple candidate papers match, list candidates and choose the one with the strongest title/source match. If no reliable match is found, ask for a clearer screenshot/title/URL instead of guessing.

## Zotero Handling

Use Zotero's Add Item by Identifier behavior as the primary import path. The user can paste the returned arXiv ID or DOI into Zotero so Zotero fetches canonical metadata from supported resolvers.

Identifier priority:

1. arXiv ID
2. DOI
3. `not available`, with another source ID such as OpenReview ID for reference

Do not store Zotero API credentials in this skill. Use Zotero Web API or MCP only for lookup, duplicate checks, updates after a canonical item exists, or attachment management when explicitly needed.

Do not create hand-written Zotero metadata entries through the Web API and never edit Zotero's local database files directly.

## Postprocess Helper

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
  --target-dir "E:\LLM_wiki\LLM_wiki\01.raw\08.Research\02.PostTraining\RL" `
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

## Failure Handling

If the PDF cannot be verified, delete or ignore the invalid file and report the failed source.

Treat generated notes, summaries, synthesis, and wiki-ready interpretation as downstream material. Do not create them in `01.raw/08.Research` during fetch/postprocess.
